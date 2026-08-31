"""Ver.4 trial-level GLM-HMM pipeline.

1 data point = 1 trial (not a 0.1 s time bin). See docs/requirements_ver4.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import zscore

import config
import src.data_loader as dl

GAP_FILL_LIMIT = 2
NOISE_REMOVE_LIMIT = 2
MERGE_TOLERANCE_SEC = 0.034
ONSET_MATCH_TOLERANCE_SEC = 0.05

# 顔特徴の pull onset 固定窓（"onset_fixed"）の前後幅。合計1.0秒は音提示ウィンドウと同じ長さで、
# 動画30Hzなので常時30フレーム前後が入る。
FACE_FIXED_PRE_SEC = 0.2
FACE_FIXED_POST_SEC = 0.8

# Midpoints of the ranges in requirements_ver4.md
ALPHA_ACT = 0.65
ALPHA_REW = 0.80

NUM_STATES = 3
PRIOR_SIGMA = 2.0

BEHAVIOR_COLS = ["x_bias", "x_stim", "x_hist", "x_rew"]
FACE_PARTS = ("eartip", "medialcorner", "nosetip", "lowerjaw")
FACE_COLS = [
    "x_ear_pos", "x_ear_spd",
    "x_eye_pos", "x_eye_spd",
    "x_nose_pos", "x_nose_spd",
    "x_jaw_pos", "x_jaw_spd",
    "x_pupil",
]
ALL_INPUT_COLS = BEHAVIOR_COLS + FACE_COLS

TRIAL_TYPE_COLORS = {
    "Success": "limegreen",
    "No Reaction": "indigo",
    "Short Pull": "deeppink",
    "Second Pull": "mediumpurple",
    "No Sound Pull": "darkorange",
}

# 非成功試行の trial_type は trial_outcome の文字列（miss/failure）ではなく pull_onset の
# 有無で決める。NWB公式trialsテーブルとハッカソンCSVの trial_outcome 列は miss/failure の
# 使い方が正反対（NWBのmiss=無反応/failure=短い押下、CSVはその逆）で、文字列→タイプの
# 固定辞書ではどちらか一方のソースで必ずラベルが入れ替わってしまうため。pull_onset の有無は
# 両ソースで一貫して「実際に引いたかどうか」を表す（VG1GC-66全日で確認: 押下ありの群は
# pull_onset保有率100%、無反応の群は0%）。


def filter_consecutive_runs(series: pd.Series, target_val: int, max_len: int, fill_val: int) -> pd.Series:
    out = series.copy()
    groups = (out != out.shift()).cumsum()
    counts = out.groupby(groups).transform("count")
    mask = (out == target_val) & (counts <= max_len)
    out.loc[mask] = fill_val
    return out


def clean_lever_30hz(
    trials_df: pd.DataFrame,
    gap_fill_limit: int = GAP_FILL_LIMIT,
    noise_remove_limit: int = NOISE_REMOVE_LIMIT,
) -> pd.DataFrame:
    """Gap-fill then drop short pulls, then mark action onsets."""
    df = trials_df.copy()
    df["t"] = pd.to_numeric(df["t"], errors="coerce")
    df["state_lever"] = pd.to_numeric(df["state_lever"], errors="coerce").fillna(0).astype(int)
    df["state_task"] = pd.to_numeric(df["state_task"], errors="coerce").fillna(0).astype(int)
    df = df.sort_values("t").reset_index(drop=True)

    cleaned = filter_consecutive_runs(df["state_lever"], 0, gap_fill_limit, 1)
    cleaned = filter_consecutive_runs(cleaned, 1, noise_remove_limit, 0)
    df["cleaned_lever"] = cleaned.astype(int)
    df["action"] = (df["cleaned_lever"].diff() == 1).fillna(False).astype(int)
    df["stimulus"] = (df["state_task"] == 1).astype(int)
    return df


def _nwb_trials_dataframe(session) -> pd.DataFrame:
    if session is None:
        return pd.DataFrame()
    try:
        if hasattr(session, "trials") and session.trials is not None:
            if hasattr(session.trials, "to_dataframe"):
                return session.trials.to_dataframe().copy()
            if hasattr(session.trials, "data"):
                return pd.DataFrame(session.trials.data).copy()
    except Exception as exc:
        print(f"NWB trials read error: {exc}")
    return pd.DataFrame()


def official_sound_trials(cleaned_df: pd.DataFrame, session=None) -> pd.DataFrame:
    """One row per sound presentation, from NWB trials or CSV trial_outcome."""
    nwb_trials = _nwb_trials_dataframe(session)
    if not nwb_trials.empty and "trial_outcome" in nwb_trials.columns:
        src = nwb_trials
    else:
        src = cleaned_df[cleaned_df["trial_outcome"].notna()].copy()

    if src.empty:
        return pd.DataFrame(columns=["start_time", "stop_time", "pull_onset", "trial_outcome", "pull_duration_for_success"])

    keep = [c for c in ["start_time", "stop_time", "pull_onset", "trial_outcome", "pull_duration_for_success"] if c in src.columns]
    out = src[keep].copy()
    for col in ["start_time", "stop_time", "pull_onset", "pull_duration_for_success"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.dropna(subset=["start_time", "stop_time"]).sort_values("start_time").reset_index(drop=True)
    return out


def attach_reward_flags(cleaned_df: pd.DataFrame, session=None) -> pd.DataFrame:
    """Mark reward=1 at success onsets via merge_asof (NWB preferred, CSV fallback)."""
    df = cleaned_df.copy()
    df["reward"] = 0

    official = official_sound_trials(df, session)
    if official.empty or "trial_outcome" not in official.columns:
        return df

    success = official[official["trial_outcome"] == "success"].copy()
    if success.empty or "pull_onset" not in success.columns:
        return df
    success = success.dropna(subset=["pull_onset"])
    if success.empty:
        return df

    reward_targets = pd.DataFrame({"reward_t": success["pull_onset"].astype(float), "flag": 1}).sort_values("reward_t")
    merged = pd.merge_asof(
        df.sort_values("t"),
        reward_targets,
        left_on="t",
        right_on="reward_t",
        direction="nearest",
        tolerance=MERGE_TOLERANCE_SEC,
    )
    df["reward"] = merged["flag"].fillna(0).astype(int)
    return df


def _action_end_time(df: pd.DataFrame, t_onset: float) -> float:
    after = df[df["t"] >= t_onset]
    if after.empty:
        return float(t_onset)
    first = after.iloc[0]
    # 公式試行のt_onset（CSV/NWBのpull_onset由来）は、押下がNOISE_REMOVE_LIMITフレーム以下だと
    # cleaned_leverから丸ごと消えていることがある。そのままcleaned_leverを探索すると無関係な
    # どこか先の押下まで暴走するため、onset行でcleaned_lever=0かつ生のstate_lever=1のときは
    # 生信号でこの押下の離脱時刻を測る。No Sound Pull/Second Pullのonsetはcleaned_leverの
    # 立ち上がりから作られる（onset行でcleaned_lever=1）ため、このフォールバックは公式試行
    # （Success/Short Pull）でしか発動しない。
    if int(first["cleaned_lever"]) == 0:
        if int(first["state_lever"]) == 0:
            # 生信号にもこの時刻の押下が無い（t_onsetがどのイベントとも対応しない）。探索を
            # 進めても無関係な押下を拾うだけなので、その場を返して呼び出し側で無効扱いさせる。
            return float(t_onset)
        release = after[after["state_lever"] == 0]
        if release.empty:
            return float(df["t"].iloc[-1])
        return float(release["t"].iloc[0])
    held = after[after["cleaned_lever"] == 1]
    if held.empty:
        return float(t_onset)
    # contiguous hold starting at/after onset
    first_idx = held.index[0]
    run = df.loc[first_idx:]
    release = run[run["cleaned_lever"] == 0]
    if release.empty:
        return float(df["t"].iloc[-1])
    return float(release["t"].iloc[0])


def _state_task_epochs(df: pd.DataFrame) -> pd.DataFrame:
    groups = (df["state_task"] != df["state_task"].shift()).cumsum()
    return df.groupby(groups).agg(
        state=("state_task", "first"),
        t0=("t", "min"),
        t1=("t", "max"),
    ).reset_index(drop=True)


def extract_trials(cleaned_df: pd.DataFrame, session=None) -> pd.DataFrame:
    """Build the Ver.4 trial table from cleaned 30 Hz data + official sound trials."""
    df = cleaned_df
    official = official_sound_trials(df, session)
    epochs = _state_task_epochs(df)
    reward_epochs = epochs[epochs["state"] == 2]

    onset_mask = df["action"] == 1
    onset_times = df.loc[onset_mask, "t"].to_numpy(dtype=float)
    onset_task = df.loc[onset_mask, "state_task"].to_numpy(dtype=int)
    used = np.zeros(len(onset_times), dtype=bool)

    def onsets_in(t0, t1, task=None):
        hit = (onset_times >= t0) & (onset_times <= t1) & (~used)
        if task is not None:
            hit &= onset_task == task
        return np.flatnonzero(hit)

    def nearest_onset(t_ref):
        if not np.isfinite(t_ref) or len(onset_times) == 0:
            return None
        d = np.abs(onset_times - t_ref)
        d[used] = np.inf
        j = int(np.argmin(d))
        if np.isfinite(d[j]) and d[j] <= ONSET_MATCH_TOLERANCE_SEC:
            return j
        return None

    rows = []

    for _, ot in official.iterrows():
        t0 = float(ot["start_time"])
        t1 = float(ot["stop_time"])
        outcome = str(ot.get("trial_outcome", "")).lower()
        pull_onset = ot["pull_onset"] if "pull_onset" in ot.index else np.nan
        if outcome == "success":
            trial_type = "Success"
        elif pd.notna(pull_onset):
            trial_type = "Short Pull"
        else:
            trial_type = "No Reaction"
        reward_threshold = ot["pull_duration_for_success"] if "pull_duration_for_success" in ot.index else np.nan

        if trial_type == "Success":
            # extend window through the following reward phase if present
            following = reward_epochs[(reward_epochs["t0"] >= t0 - 0.05) & (reward_epochs["t0"] <= t1 + 0.05)]
            if not following.empty:
                t1 = float(following["t1"].max())
            y, stim, rew = 1, 1, 1
        elif trial_type == "Short Pull":
            y, stim, rew = 1, 1, 0
            t1 = max(t1, _action_end_time(df, float(pull_onset)))
        else:
            y, stim, rew = 0, 1, 0

        primary_j = nearest_onset(float(pull_onset)) if pd.notna(pull_onset) else None
        if primary_j is None:
            in_sound = onsets_in(t0, t1, task=1)
            if len(in_sound):
                primary_j = int(in_sound[0])

        rows.append({
            "trial_type": trial_type,
            "t_start": t0,
            "t_end": t1,
            "t_onset": float(onset_times[primary_j]) if primary_j is not None else (float(pull_onset) if pd.notna(pull_onset) else np.nan),
            "y": y,
            "x_stim": stim,
            "reward": rew,
            "official_outcome": outcome,
            "pull_duration_for_success": float(reward_threshold) if pd.notna(reward_threshold) else np.nan,
        })

        if primary_j is not None:
            used[primary_j] = True

        extra = onsets_in(t0, t1, task=1)
        for j in extra:
            t_on = float(onset_times[j])
            rows.append({
                "trial_type": "Second Pull",
                "t_start": t_on,
                "t_end": _action_end_time(df, t_on),
                "t_onset": t_on,
                "y": 1,
                "x_stim": 1,
                "reward": 0,
                "official_outcome": outcome,
            })
            used[j] = True

        # Reward-phase onsets belong to the Success window, not extra trials
        if trial_type == "Success":
            for j in onsets_in(t0, t1, task=2):
                used[j] = True

    # Remaining ITI onsets → No Sound Pull
    for j in np.flatnonzero((~used) & (onset_task == 0)):
        t_on = float(onset_times[j])
        rows.append({
            "trial_type": "No Sound Pull",
            "t_start": t_on,
            "t_end": _action_end_time(df, t_on),
            "t_onset": t_on,
            "y": 1,
            "x_stim": 0,
            "reward": 0,
            "official_outcome": "",
        })
        used[j] = True

    trials = pd.DataFrame(rows)
    if trials.empty:
        return trials
    trials = trials.sort_values("t_start").reset_index(drop=True)
    trials["trial_index"] = np.arange(len(trials))
    return trials


def compute_pull_window(trial_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """Actual lever-hold window per trial: `t_onset` to release time (via `_action_end_time`).

    `t_start`/`t_end` cannot be used for this: for Success/Short Pull they span the official
    sound-trial window (plus, for Success, the reward phase), not the pull itself. Returns
    `pull_end`/`pull_duration`, both NaN for trials with no pull (No Reaction), a missing
    `t_onset`, or when no press could be located at `t_onset` in either the cleaned or the
    raw lever signal.
    """
    pull_end = pd.Series(np.nan, index=trial_df.index, dtype=float)
    has_onset = trial_df["t_onset"].notna() & (trial_df["trial_type"] != "No Reaction")
    for i in trial_df.index[has_onset]:
        t_onset = float(trial_df.loc[i, "t_onset"])
        pull_end.loc[i] = _action_end_time(cleaned_df, t_onset)
    duration = pull_end - trial_df["t_onset"]
    # _action_end_time()は押下を特定できないときt_onsetをそのまま返す（duration=0）。
    # これは実測値ではないのでNaNに落とす。
    invalid = duration <= 0
    pull_end[invalid] = np.nan
    duration[invalid] = np.nan
    return pd.DataFrame({"pull_end": pull_end, "pull_duration": duration})


def add_history(
    trial_df: pd.DataFrame,
    alpha_act: float = ALPHA_ACT,
    alpha_rew: float = ALPHA_REW,
) -> pd.DataFrame:
    """h_k = y_{k-1} + a * h_{k-1}, same for reward. No current-trial leakage."""
    out = trial_df.copy()
    y = out["y"].to_numpy(dtype=float)
    r = out["reward"].to_numpy(dtype=float)
    n = len(y)
    hist_act = np.zeros(n, dtype=float)
    hist_rew = np.zeros(n, dtype=float)
    prev_h, prev_r = 0.0, 0.0
    for k in range(1, n):
        hist_act[k] = y[k - 1] + alpha_act * prev_h
        prev_h = hist_act[k]
        hist_rew[k] = r[k - 1] + alpha_rew * prev_r
        prev_r = hist_rew[k]
    out["x_bias"] = 1.0
    out["x_hist"] = hist_act
    out["x_rew"] = hist_rew
    return out


def _col(df: pd.DataFrame, *names: str) -> str | None:
    for name in names:
        if name in df.columns:
            return name
    return None


def extract_video_features(session) -> pd.DataFrame:
    """9 face/body features at video rate: 4 parts × (pos, speed) + pupil."""
    if session is None or not hasattr(session, "entries") or session.entries is None:
        return pd.DataFrame()
    try:
        video_df = pd.DataFrame(session.entries.data).copy()
    except Exception as exc:
        print(f"Video data read error: {exc}")
        return pd.DataFrame()

    if video_df.empty:
        return pd.DataFrame()
    if "t" not in video_df.columns:
        if "time" in video_df.columns:
            video_df = video_df.rename(columns={"time": "t"})
        else:
            video_df = video_df.reset_index()
            if "index" in video_df.columns:
                video_df = video_df.rename(columns={"index": "t"})
    if "t" not in video_df.columns:
        print("Warning: no time column in video data.")
        return pd.DataFrame()

    video_df["t"] = pd.to_numeric(video_df["t"], errors="coerce")
    lp_x = _col(video_df, "face_video_lickport_x", "lickport_x")
    lp_y = _col(video_df, "face_video_lickport_y", "lickport_y")

    feat_map = [
        ("eartip", "x_ear_pos", "x_ear_spd"),
        ("medialcorner", "x_eye_pos", "x_eye_spd"),
        ("nosetip", "x_nose_pos", "x_nose_spd"),
        ("lowerjaw", "x_jaw_pos", "x_jaw_spd"),
    ]
    out = pd.DataFrame({"t": video_df["t"]})
    have_any = False
    for part, pos_name, spd_name in feat_map:
        x_col = _col(video_df, f"{part}_x", f"face_video_{part}_x")
        y_col = _col(video_df, f"{part}_y", f"face_video_{part}_y")
        if x_col is None or y_col is None:
            out[pos_name] = np.nan
            out[spd_name] = np.nan
            continue
        have_any = True
        if lp_x is not None and lp_y is not None:
            out[pos_name] = np.sqrt(
                (video_df[x_col] - video_df[lp_x]) ** 2 + (video_df[y_col] - video_df[lp_y]) ** 2
            )
        else:
            out[pos_name] = np.sqrt(video_df[x_col] ** 2 + video_df[y_col] ** 2)
        out[spd_name] = np.sqrt(video_df[x_col].diff() ** 2 + video_df[y_col].diff() ** 2)

    pupil_col = _col(video_df, "face_video_pupildia", "pupildia")
    if pupil_col is not None:
        have_any = True
        out["x_pupil"] = video_df[pupil_col]
    else:
        out["x_pupil"] = np.nan

    if not have_any:
        return pd.DataFrame()

    feat_cols = [c for c in FACE_COLS if c in out.columns]
    out[feat_cols] = out[feat_cols].interpolate(method="linear").ffill().fillna(0)
    return out.sort_values("t").reset_index(drop=True)


def aggregate_face_window(t0s: np.ndarray, t1s: np.ndarray, video_df: pd.DataFrame, feat_cols: list[str]) -> np.ndarray:
    """Median (pos/pupil) or mean (speed, column name contains "spd") of each face feature
    within `[t0, t1]` per row. Falls back to the single nearest video frame to `t0` when the
    window contains none.
    """
    raw = np.zeros((len(t0s), len(feat_cols)), dtype=float)
    t_vid = video_df["t"].to_numpy()
    vals = video_df[feat_cols].to_numpy(dtype=float)
    for i in range(len(t0s)):
        t0, t1 = t0s[i], t1s[i]
        hit = (t_vid >= t0) & (t_vid <= max(t1, t0))
        if not hit.any():
            j = int(np.argmin(np.abs(t_vid - t0)))
            raw[i] = vals[j]
            continue
        block = vals[hit]
        for c_idx, col in enumerate(feat_cols):
            if "spd" in col:
                raw[i, c_idx] = np.nanmean(block[:, c_idx])
            else:
                raw[i, c_idx] = np.nanmedian(block[:, c_idx])
    return raw


def face_window_bounds(
    trial_df: pd.DataFrame,
    window: str = "trial",
    pre: float = FACE_FIXED_PRE_SEC,
    post: float = FACE_FIXED_POST_SEC,
) -> tuple[np.ndarray, np.ndarray]:
    """Start/end times of the face-aggregation window, one row per trial.

    - ``"trial"``: `t_start`〜`t_end`. 長さが trial_type ごとに大きく違う（Successは報酬フェーズ
      まで含んで約2.4秒、No Reactionは1.0秒、No Sound Pullは中央値0.27秒）。
    - ``"pull"``: `t_onset`〜`pull_end`（実測のレバー保持区間）。pullが無い試行は `"trial"` と同じ。
    - ``"onset_fixed"``: pull onset を基準にした固定長窓 `[t_onset - pre, t_onset + post]`。pullが
      無い試行は cue onset (`t_start`) を基準にする。窓長が定数なので、窓長そのものが集計値に
      効く経路（フレーム数の差）が構造的に閉じる。

    pullの有無は `t_onset` ではなく `pull_end` の有無で判定する。No Reaction 試行でも微小なレバー
    接触で `t_onset` が非NaNになることがあり、それを窓の起点にすると意味のない窓になるため。
    """
    t_start = trial_df["t_start"].to_numpy(dtype=float)
    t_end = trial_df["t_end"].to_numpy(dtype=float)
    if window == "trial":
        return t_start, t_end

    has_pull = trial_df["pull_end"].notna() if "pull_end" in trial_df.columns else pd.Series(False, index=trial_df.index)
    if window == "pull":
        t0 = trial_df["t_onset"].where(has_pull, trial_df["t_start"]).to_numpy(dtype=float)
        t1 = trial_df["pull_end"].where(has_pull, trial_df["t_end"]).to_numpy(dtype=float)
        return t0, t1
    if window == "onset_fixed":
        anchor = trial_df["t_onset"].where(has_pull, trial_df["t_start"]).to_numpy(dtype=float)
        return anchor - pre, anchor + post
    raise ValueError(f"unknown window: {window!r}")


def attach_face_features(
    trial_df: pd.DataFrame, video_df: pd.DataFrame, window: str = "trial"
) -> pd.DataFrame:
    """Median pos/pupil and mean speed in each face window, z-scored, lagged by 1 trial.

    `window` は `face_window_bounds()` の集計窓の選択肢。既定の `"trial"` が Ver.4 の仕様。
    """
    out = trial_df.copy()
    for col in FACE_COLS:
        out[col] = 0.0
    if video_df is None or video_df.empty or out.empty:
        return out

    feat_cols = [c for c in FACE_COLS if c in video_df.columns]
    if not feat_cols:
        return out

    t0s, t1s = face_window_bounds(out, window=window)
    raw = aggregate_face_window(t0s, t1s, video_df, feat_cols)
    raw = np.nan_to_num(raw, nan=0.0)
    z = zscore(raw, axis=0, nan_policy="omit")
    z = np.nan_to_num(z, nan=0.0)
    lagged = np.zeros_like(z)
    lagged[1:] = z[:-1]
    for c_idx, col in enumerate(feat_cols):
        out[col] = lagged[:, c_idx]
    return out


def trials_to_arrays(trial_df: pd.DataFrame, input_cols: list[str]):
    y = trial_df[["y"]].to_numpy(dtype=int)
    x = trial_df[input_cols].to_numpy(dtype=float)
    return y, x


def find_nwb_file(mouse_id: str, task_day: str) -> Path | None:
    root = config.DATA_NWB_ROOT / mouse_id
    if not root.exists():
        return None
    matches = sorted(root.glob(f"{mouse_id}_*_{task_day}.nwb"))
    if matches:
        return matches[0]
    # Fallback pattern must not let e.g. "task-day1" substring-match "task-day15".
    pattern = re.compile(rf"^.*{re.escape(task_day)}(?!\d).*\.nwb$")
    matches = sorted(p for p in root.glob("*.nwb") if pattern.match(p.name))
    return matches[0] if matches else None


def list_task_days(mouse_id: str) -> list[str]:
    mouse_dir = config.DATA_CSV_ROOT / mouse_id
    if not mouse_dir.exists():
        return []
    days = []
    for p in mouse_dir.iterdir():
        if p.is_dir() and (p / "trials_L1L2.csv").exists():
            days.append(p.name)
    def day_key(name: str) -> int:
        m = re.search(r"(\d+)$", name)
        return int(m.group(1)) if m else 0
    return sorted(days, key=day_key)


def process_session(
    mouse_id: str,
    task_day: str,
    nwb_filename: str | None = None,
    alpha_act: float = ALPHA_ACT,
    alpha_rew: float = ALPHA_REW,
    face_window: str = "trial",
) -> dict:
    """Load one session and return trial table plus ssm arrays."""
    csv = dl.load_trials_csv(mouse_id, task_day)
    if csv is None or csv.empty:
        raise FileNotFoundError(f"CSV not found for {mouse_id} {task_day}")

    session = None
    if nwb_filename is None:
        nwb_path = find_nwb_file(mouse_id, task_day)
        nwb_filename = nwb_path.name if nwb_path is not None else None
    if nwb_filename:
        session = dl.load_nwb_session(mouse_id, nwb_filename, nwb_root=config.DATA_NWB_ROOT)

    cleaned = clean_lever_30hz(csv)
    cleaned = attach_reward_flags(cleaned, session)
    trials = extract_trials(cleaned, session)
    trials[["pull_end", "pull_duration"]] = compute_pull_window(trials, cleaned)
    trials = add_history(trials, alpha_act=alpha_act, alpha_rew=alpha_rew)
    video = extract_video_features(session)
    trials = attach_face_features(trials, video, window=face_window)
    trials["mouse_id"] = mouse_id
    trials["task_day"] = task_day

    y, x4 = trials_to_arrays(trials, BEHAVIOR_COLS)
    _, x13 = trials_to_arrays(trials, ALL_INPUT_COLS)
    return {
        "cleaned": cleaned,
        "trials": trials,
        "video": video,
        "y": y,
        "x4": x4,
        "x13": x13,
        "has_face": not video.empty,
        "session": session,
    }


def process_mouse(
    mouse_id: str,
    task_days: list[str] | None = None,
    alpha_act: float = ALPHA_ACT,
    alpha_rew: float = ALPHA_REW,
    face_window: str = "trial",
) -> dict:
    """Each task day becomes one sequence in the ssm list."""
    if task_days is None:
        task_days = list_task_days(mouse_id)
    sessions = []
    trial_tables = []
    ys, xs4, xs13 = [], [], []
    n_face = 0
    for day in task_days:
        try:
            pack = process_session(
                mouse_id, day, alpha_act=alpha_act, alpha_rew=alpha_rew, face_window=face_window
            )
        except FileNotFoundError as exc:
            print(exc)
            continue
        if pack["trials"].empty:
            print(f"Skip {mouse_id} {day}: no trials")
            continue
        sessions.append(pack)
        trial_tables.append(pack["trials"])
        ys.append(pack["y"])
        xs4.append(pack["x4"])
        xs13.append(pack["x13"])
        n_face += int(pack["has_face"])
        print(
            f"{mouse_id} {day}: {len(pack['trials'])} trials, "
            f"face={'yes' if pack['has_face'] else 'no'}"
        )
    all_trials = pd.concat(trial_tables, ignore_index=True) if trial_tables else pd.DataFrame()
    return {
        "sessions": sessions,
        "trials": all_trials,
        "ys": ys,
        "xs4": xs4,
        "xs13": xs13,
        "n_with_face": n_face,
        "task_days": [s["trials"]["task_day"].iloc[0] for s in sessions] if sessions else [],
    }


def train_glmhmm_map(
    train_ys,
    train_xs,
    num_states: int = NUM_STATES,
    prior_sigma: float = PRIOR_SIGMA,
    num_iters: int = 200,
    seeds: list[int] | None = None,
):
    """Bernoulli GLM-HMM with L2 MAP prior. Returns (best_model, lls_of_best, best_ll)."""
    import ssm

    if seeds is None:
        seeds = [0, 1, 2]
    obs_dim = 1
    input_dim = int(train_xs[0].shape[1])
    best_model, best_ll, best_lls = None, -np.inf, None
    print(f"Training GLM-HMM K={num_states} M={input_dim} prior_sigma={prior_sigma}")
    for seed in seeds:
        np.random.seed(seed)
        model = ssm.HMM(
            K=num_states,
            D=obs_dim,
            M=input_dim,
            observations="input_driven_obs",
            observation_kwargs=dict(C=2, prior_mean=0, prior_sigma=prior_sigma),
            transitions="standard",
        )
        try:
            lls = model.fit(
                train_ys,
                inputs=train_xs,
                method="em",
                num_iters=num_iters,
                tolerance=1e-4,
            )
            score = float(lls[-1])
            print(f"  seed {seed}: log_prob={score:.2f}")
            if score > best_ll:
                best_ll, best_model, best_lls = score, model, lls
        except Exception as exc:
            print(f"  seed {seed} failed: {exc}")
    if best_model is None:
        raise RuntimeError("All GLM-HMM seeds failed.")
    print(f"Best log_prob={best_ll:.2f}")
    return best_model, np.asarray(best_lls), best_ll


def decode_states(model, train_ys, train_xs) -> tuple[list[np.ndarray], list[np.ndarray]]:
    z_list, p_list = [], []
    for y, x in zip(train_ys, train_xs):
        z_list.append(model.most_likely_states(y, input=x))
        p_list.append(model.expected_states(data=y, input=x)[0])
    return z_list, p_list


def attach_decoded_states(trial_df: pd.DataFrame, z_list, p_list, day_col: str = "task_day") -> pd.DataFrame:
    out = trial_df.copy()
    if out.empty:
        return out
    chunks = []
    days = list(dict.fromkeys(out[day_col].tolist()))
    for day, z, p in zip(days, z_list, p_list):
        sub = out[out[day_col] == day].copy()
        n = min(len(sub), len(z))
        sub = sub.iloc[:n].copy()
        sub["state"] = z[:n]
        for k in range(p.shape[1]):
            sub[f"p_state_{k}"] = p[:n, k]
        chunks.append(sub)
    return pd.concat(chunks, ignore_index=True)


# ---------------------------------------------------------------------------
# Plots (style aligned with notebooks 10–12)
# ---------------------------------------------------------------------------

def plot_cleaning_validation(df: pd.DataFrame, start_time: float = 100.0, duration: float = 30.0):
    import matplotlib.pyplot as plt

    end_time = start_time + duration
    subset = df[(df["t"] >= start_time) & (df["t"] <= end_time)].copy()
    if subset.empty:
        print(f"No data between {start_time}s and {end_time}s")
        return
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    ax0, ax1, ax2 = axes
    ax0.set_title("1. Stimulus (state_task vs sound window)")
    ax0.plot(subset["t"], subset["state_task"], color="gray", linestyle="--", alpha=0.6, label="state_task")
    ax0.fill_between(subset["t"], 0, 1, where=(subset["stimulus"] == 1), color="skyblue", alpha=0.5, label="stimulus")
    ax0.legend(loc="upper right")
    ax0.set_ylabel("State / Flag")
    ax0.grid(True, alpha=0.3)

    ax1.set_title("2. Lever cleaning and action onset")
    ax1.plot(subset["t"], subset["state_lever"], color="black", linewidth=1, label="raw state_lever")
    ax1.plot(subset["t"], subset["cleaned_lever"], color="tab:blue", linewidth=1.2, alpha=0.8, label="cleaned_lever")
    actions = subset[subset["action"] == 1]
    ax1.scatter(actions["t"], [1] * len(actions), color="red", s=40, zorder=5, label="onset")
    ax1.legend(loc="upper right")
    ax1.set_ylabel("Lever")
    ax1.grid(True, alpha=0.3)

    ax2.set_title("3. Reward flag")
    if "reward" in subset.columns:
        rewards = subset[subset["reward"] == 1]
        if not rewards.empty:
            ax2.vlines(rewards["t"], 0, 1, color="green", linewidth=3, label="reward")
    ax2.plot(subset["t"], (subset["state_task"] == 2).astype(int), color="orange", linestyle=":", label="state_task=2")
    ax2.legend(loc="upper right")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Reward")
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_trial_raster(trial_df: pd.DataFrame, title: str = ""):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(18, 3.5))
    for ttype, color in TRIAL_TYPE_COLORS.items():
        sub = trial_df[trial_df["trial_type"] == ttype]
        if sub.empty:
            continue
        plt.vlines(sub["t_start"], 0, 1, color=color, alpha=0.85, linewidth=1.4, label=f"{ttype} (n={len(sub)})")
    plt.yticks([])
    plt.xlabel("Time (s)")
    plt.title(title or "Trial raster")
    plt.legend(loc="upper right", ncol=5, bbox_to_anchor=(1.0, 1.28), framealpha=1)
    plt.xlim(left=0)
    plt.tight_layout()
    plt.show()


def plot_history(trial_df: pd.DataFrame, n_trials: int = 200):
    import matplotlib.pyplot as plt

    sub = trial_df.iloc[:n_trials]
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    idx = np.arange(len(sub))
    axes[0].set_title("Stimulus and action (trial index)")
    axes[0].fill_between(idx, 0, sub["x_stim"], color="skyblue", alpha=0.4, step="mid", label="x_stim")
    axes[0].vlines(idx[sub["y"] == 1], 0, 1, color="black", linewidth=0.8, label="y=1")
    axes[0].legend(loc="upper right")
    axes[0].set_ylabel("Flag")
    axes[1].plot(idx, sub["x_hist"], color="purple", linewidth=1.5, label="Action History")
    axes[1].set_title("Action History (lagged, trial unit)")
    axes[1].legend(loc="upper right")
    axes[1].grid(True, alpha=0.3)
    axes[2].plot(idx, sub["x_rew"], color="green", linewidth=1.5, label="Reward History")
    jumps = sub["reward"] == 1
    if jumps.any():
        axes[2].scatter(idx[jumps.to_numpy()], sub.loc[jumps, "x_rew"], color="green", s=30, zorder=5)
    axes[2].set_title("Reward History (lagged, trial unit)")
    axes[2].set_xlabel("Trial k")
    axes[2].legend(loc="upper right")
    axes[2].grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_glm_weights(model, feature_names: list[str], title: str = ""):
    import matplotlib.pyplot as plt

    weights = model.observations.params
    colors = plt.cm.tab10(np.linspace(0, 1, model.K))
    plt.figure(figsize=(max(8, 0.7 * len(feature_names)), 5))
    for k in range(model.K):
        w = np.asarray(weights[k][0]).ravel()
        names = feature_names
        if len(w) != len(names):
            names = [f"Feat {i}" for i in range(len(w))]
        plt.plot(range(len(w)), w, marker="o", label=f"State {k + 1}", color=colors[k], linewidth=2)
    plt.axhline(0, color="black", linestyle="--", alpha=0.5)
    plt.xticks(range(len(names)), names, rotation=45, ha="right")
    plt.ylabel("GLM weight")
    plt.title(title or f"GLM weights (K={model.K})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_transition_matrix(model):
    import matplotlib.pyplot as plt

    trans = np.exp(model.transitions.params)[0]
    k = model.K
    plt.figure(figsize=(4.5, 4))
    plt.imshow(trans, vmin=0, vmax=1, cmap="Blues")
    plt.colorbar(label="Probability")
    plt.title("Transition matrix")
    plt.xlabel("State t+1")
    plt.ylabel("State t")
    plt.xticks(range(k), range(1, k + 1))
    plt.yticks(range(k), range(1, k + 1))
    for i in range(k):
        for j in range(k):
            plt.text(j, i, f"{trans[i, j]:.2f}", ha="center", va="center")
    plt.tight_layout()
    plt.show()
    return trans


def plot_state_path(model, y, x, trial_types=None, title: str = ""):
    import matplotlib.pyplot as plt

    z = model.most_likely_states(y, input=x)
    prob = model.expected_states(data=y, input=x)[0]
    t = np.arange(len(y))
    colors = plt.cm.tab10(np.linspace(0, 1, model.K))
    fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True)
    axes[0].fill_between(t, 0, x[:, 1], color="gray", alpha=0.3, step="mid", label="Stimulus")
    axes[0].vlines(t[y.flatten() == 1], 0, 1, color="black", linewidth=0.6, label="Action")
    axes[0].set_title(title or "Behavior")
    axes[0].legend(loc="upper right")
    axes[0].set_ylabel("Event")
    for k in range(model.K):
        axes[1].plot(t, prob[:, k], label=f"State {k + 1}", color=colors[k], alpha=0.85)
    axes[1].set_ylabel("P(state)")
    axes[1].set_title("State posterior")
    axes[1].legend(loc="upper right", ncol=model.K)
    axes[1].set_ylim(-0.05, 1.05)
    axes[2].step(t, z, where="post", color="black", linewidth=1.2)
    if trial_types is not None:
        for ttype, color in TRIAL_TYPE_COLORS.items():
            idx = np.array(trial_types) == ttype
            if idx.any():
                axes[2].scatter(t[idx], z[idx], s=12, color=color, zorder=3, label=ttype)
        axes[2].legend(loc="upper right", ncol=5, fontsize=8)
    axes[2].set_yticks(range(model.K))
    axes[2].set_yticklabels([f"State {k + 1}" for k in range(model.K)])
    axes[2].set_title("Viterbi path")
    axes[2].set_xlabel("Trial k")
    plt.tight_layout()
    plt.show()


def plot_day_panel(model, trial_df: pd.DataFrame, y, x, title: str = ""):
    """One figure, 6 rows sharing a trial-index x-axis: trial type, stimulus, action
    history, reward history, state posterior, Viterbi path.

    Trial type carries the action/outcome distinction (including No Reaction), so the
    stimulus row only shows where `x_stim == 1` and does not repeat an action overlay.
    """
    import matplotlib.pyplot as plt

    z = model.most_likely_states(y, input=x)
    prob = model.expected_states(data=y, input=x)[0]
    t = np.arange(len(y))
    trial_types = trial_df["trial_type"].to_numpy()
    colors = plt.cm.tab10(np.linspace(0, 1, model.K))

    # Trial index has no gaps between trials (unlike note 14's real-time raster, where
    # ITI duration naturally separates events), so a full-width bar per trial fuses a
    # run of the same type into one solid block. Narrower bars (width < 1) leave a
    # sliver of background between neighbors, reproducing note 14's barcode look; this
    # needs more horizontal room per trial than the plain crushed-line fix did, hence
    # the larger per-trial figure width below.
    # Height scales with width at the same 14:15 ratio as the baseline figure: notebook
    # viewers cap displayed image width and scale height down to match, so a wide image
    # with a fixed height renders every row squashed unless height grows with it too.
    fig_width = min(60, max(14, len(t) * 0.06))
    fig_height = fig_width * (15 / 14)
    fig, axes = plt.subplots(6, 1, figsize=(fig_width, fig_height), sharex=True)

    # Fonts/linewidths are in points, which are fixed regardless of fig_width; but
    # notebook viewers scale a wide figure down to a constant display width, so a
    # day with more trials (larger fig_width) renders with proportionally smaller
    # text and thinner lines than a short day. Scale every point-based size by how
    # far fig_width sits above the 14-inch floor so the displayed (post-scaling)
    # size stays constant across days.
    scale = fig_width / 14
    title_fs = 12 * scale
    label_fs = 10 * scale
    tick_fs = 9 * scale
    legend_fs = 8 * scale
    lw_thin = 1.5 * scale
    lw_step = 1.2 * scale
    s_reward = 20 * scale**2
    s_viterbi = 12 * scale**2

    bar_width = 0.6
    for ttype, color in TRIAL_TYPE_COLORS.items():
        idx = trial_types == ttype
        if idx.any():
            axes[0].bar(t[idx], 1, width=bar_width, color=color, linewidth=0, label=f"{ttype} (n={int(idx.sum())})")
    axes[0].set_yticks([])
    axes[0].set_ylabel("Trial type", fontsize=label_fs)
    axes[0].set_title(title or "Day summary", fontsize=title_fs)
    axes[0].legend(loc="upper right", ncol=5, fontsize=legend_fs)

    axes[1].bar(t, x[:, 1], width=bar_width, color="skyblue", linewidth=0)
    axes[1].set_yticks([0, 1])
    axes[1].set_ylabel("Stimulus", fontsize=label_fs)
    axes[1].set_title("Stimulus", fontsize=title_fs)

    axes[2].plot(t, x[:, 2], color="purple", linewidth=lw_thin)
    axes[2].set_ylabel("Act Hist", fontsize=label_fs)
    axes[2].set_title("Action history", fontsize=title_fs)
    axes[2].grid(True, alpha=0.3)

    axes[3].plot(t, x[:, 3], color="green", linewidth=lw_thin)
    if "reward" in trial_df.columns:
        jumps = trial_df["reward"].to_numpy() == 1
        if jumps.any():
            axes[3].scatter(t[jumps], x[jumps, 3], color="green", s=s_reward, zorder=5)
    axes[3].set_ylabel("Rew Hist", fontsize=label_fs)
    axes[3].set_title("Reward history", fontsize=title_fs)
    axes[3].grid(True, alpha=0.3)

    for k in range(model.K):
        axes[4].plot(t, prob[:, k], label=f"State {k + 1}", color=colors[k], alpha=0.85, linewidth=lw_thin)
    axes[4].set_ylabel("P(state)", fontsize=label_fs)
    axes[4].set_title("State posterior", fontsize=title_fs)
    axes[4].set_ylim(-0.05, 1.05)
    axes[4].legend(loc="upper right", ncol=model.K, fontsize=legend_fs)

    axes[5].step(t, z, where="post", color="black", linewidth=lw_step)
    for ttype, color in TRIAL_TYPE_COLORS.items():
        idx = trial_types == ttype
        if idx.any():
            axes[5].scatter(t[idx], z[idx], s=s_viterbi, color=color, zorder=3)
    axes[5].set_yticks(range(model.K))
    axes[5].set_yticklabels([f"State {k + 1}" for k in range(model.K)], fontsize=tick_fs)
    axes[5].set_ylabel("Viterbi", fontsize=label_fs)
    axes[5].set_title("Viterbi path", fontsize=title_fs)
    axes[5].set_xlabel("Trial k", fontsize=label_fs)

    for ax in axes:
        ax.tick_params(axis="both", labelsize=tick_fs)

    plt.tight_layout()
    plt.show()


def plot_state_behavior(model, trial_df: pd.DataFrame, feature_names: list[str]):
    import matplotlib.pyplot as plt

    k = model.K
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    x = np.arange(k)
    width = 0.35
    p0, p1 = [], []
    for s in range(k):
        sub = trial_df[trial_df["state"] == s]
        if sub.empty:
            p0.append(0.0)
            p1.append(0.0)
            continue
        s0 = sub[sub["x_stim"] == 0]
        s1 = sub[sub["x_stim"] == 1]
        p0.append(float(s0["y"].mean()) if len(s0) else 0.0)
        p1.append(float(s1["y"].mean()) if len(s1) else 0.0)
    axes[0].bar(x - width / 2, p0, width, label="Stim=0", color="gray", alpha=0.7)
    axes[0].bar(x + width / 2, p1, width, label="Stim=1", color="tab:red", alpha=0.7)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([f"State {i + 1}" for i in range(k)])
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("P(y=1)")
    axes[0].set_title("Action probability by state")
    axes[0].legend()
    axes[0].grid(axis="y", linestyle="--", alpha=0.3)

    types = list(TRIAL_TYPE_COLORS.keys())
    bottom = np.zeros(k)
    for ttype in types:
        fracs = []
        for s in range(k):
            sub = trial_df[trial_df["state"] == s]
            fracs.append(float((sub["trial_type"] == ttype).mean()) if len(sub) else 0.0)
        axes[1].bar(x, fracs, bottom=bottom, color=TRIAL_TYPE_COLORS[ttype], label=ttype)
        bottom = bottom + np.array(fracs)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([f"State {i + 1}" for i in range(k)])
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title("Trial-type mix by state")
    axes[1].legend(fontsize=8)

    weights = model.observations.params
    colors = plt.cm.tab10(np.linspace(0, 1, k))
    names = feature_names
    for s in range(k):
        w = np.asarray(weights[s][0]).ravel()
        if len(w) != len(names):
            names = [f"Feat {i}" for i in range(len(w))]
        axes[2].plot(names, w, marker="o", label=f"State {s + 1}", color=colors[s])
    axes[2].axhline(0, color="black", linestyle="--", alpha=0.5)
    axes[2].tick_params(axis="x", rotation=45)
    axes[2].set_title("GLM weights")
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    print("--- P(action | stim, state) ---")
    for s in range(k):
        print(f"State {s + 1} | Stim=0: {p0[s]:.2f}  Stim=1: {p1[s]:.2f}")


def plot_learning_curve(lls, title: str = "EM log probability"):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(6, 3.5))
    plt.plot(lls, color="tab:blue")
    plt.xlabel("Iteration")
    plt.ylabel("Log probability")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
