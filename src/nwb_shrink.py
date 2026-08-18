"""GINのNWBから processing/downsampled と processing/ophys だけを残した軽量版を作るユーティリティ.

GINのNWB（1ファイル約1.7GB）の内訳（docs/data.md「NWBファイルの内部構造とサイズ内訳」実測）:
`acquisition`（5kHz生波形16ch、約2.3GB論理サイズ、82%）、`processing`（499MB、18%）。
さらに `processing` は `behavior`（動画ネイティブレート、約302MB）・`downsampled`（30Hz、約130MB）・
`ophys`（30Hz、約65MB）に分かれる。

`bdbc_nwb_explorer.read_nwb()` はデフォルト(downsampled=True)では
`processing['downsampled']` と `processing['ophys']` しか読まず、`acquisition` と
`processing['behavior']`（ネイティブレートのキーポイント）は一切参照しない
（`bdbc_nwb_explorer/view.py` の `read_acquisition()` / `read_video_tracking()` / `read_trials()` /
`read_roi_dFF()` で確認済み）。そのためこの2つを除去した版（約195MB）を作っても
既存パイプライン（src/glmhmm_ver4.py）は無改造で動く。
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path


def strip_to_downsampled_and_ophys(src_path: Path, dst_path: Path) -> None:
    """acquisitionとprocessing/behaviorを除去したNWBをdst_pathに書き出す。

    processing/downsampledとprocessing/ophysだけが残る（約195MB）。
    既に両方とも除去済み（=既に最小版）でも安全に動く（べき等）。
    """
    from pynwb import NWBHDF5IO

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with NWBHDF5IO(str(src_path), mode="r") as src_io:
        nwbfile = src_io.read()
        for name in list(nwbfile.acquisition.keys()):
            del nwbfile.acquisition[name]
        if "behavior" in nwbfile.processing:
            del nwbfile.processing["behavior"]
        with NWBHDF5IO(str(dst_path), mode="w") as dst_io:
            dst_io.export(src_io=src_io, nwbfile=nwbfile)


def find_gin_nwb_path(gin_root: Path, mouse_id: str, task_day: str) -> Path | None:
    """GINデータセットのクローン内から該当NWBを探す。

    GIN内部の実際の命名規則（`VG1GC-66_..._task-dayN.nwb` のようにローカルの
    nwb_manualと同じ命名か、BIDS風`sub-XX/ses-XX`かなど）は事前に分からないため、
    mouse_id・task_dayを含むファイル名を再帰的に探す。
    `src/glmhmm_ver4.find_nwb_file` と同様、day番号直後に数字が続く誤爆
    （"task-day1" が "task-day15" にヒットする等）を避けるため、task_dayの直後に
    数字が続かないことを正規表現で保証する。

    `datalad clone`（メタデータのみ）の直後でも、git-annexはファイル名を含む
    シンボリックリンクを配置するため、このrglobは`datalad get`前でも機能する。
    """
    day_pattern = re.compile(rf".*{re.escape(task_day)}(?!\d).*", re.IGNORECASE)

    candidates = [
        p for p in gin_root.rglob("*.nwb")
        if mouse_id.lower() in str(p).lower() and day_pattern.match(str(p))
    ]
    return sorted(candidates)[0] if candidates else None


def matches_nwb_manual_glob(path: Path, mouse_id: str, task_day: str) -> bool:
    """`src/glmhmm_ver4.find_nwb_file`が拾える命名（`{mouse_id}_*_{task_day}.nwb`）か判定する。"""
    pattern = re.compile(rf"^{re.escape(mouse_id)}_.*_{re.escape(task_day)}(?!\d)\.nwb$")
    return pattern.match(path.name) is not None


def normalized_dest_filename(src_filename: str, mouse_id: str, task_day: str) -> str:
    """`find_nwb_file`が拾える形式のファイル名を返す。

    GIN由来のファイル名が既に`{mouse_id}_*_{task_day}.nwb`形式ならそのまま使い、
    そうでない場合（BIDS風命名等）は`find_nwb_file`のglobパターンに合わせて
    正規化した名前を作る。
    """
    dummy = Path(src_filename)
    if matches_nwb_manual_glob(dummy, mouse_id, task_day):
        return src_filename
    return f"{mouse_id}_gin_{task_day}.nwb"


def verify_processing_only(path: Path) -> None:
    """processing-onlyのNWBが読めて、trials/imagingが空でないことを確認する。

    読み込みに失敗した場合や中身が空の場合はAssertionError/例外を投げる
    (呼び出し側でtry/exceptして扱う想定)。
    """
    import bdbc_nwb_explorer as nwbx

    session = nwbx.read_nwb(path)
    trials = session.data.trials
    imaging = session.data.imaging
    assert trials is not None and len(trials) > 0, f"trialsが空です: {path}"
    assert imaging is not None and len(imaging) > 0, f"imagingが空です: {path}"


def swap_in_place(new_path: Path, target_path: Path, backup_suffix: str = ".full.bak") -> None:
    """target_pathの中身をnew_pathの内容で安全に置き換える。

    target_pathが既に存在する場合は先に`backup_suffix`付きへ退避してから
    new_pathをtarget_pathへ移動する。呼び出し側で置き換え後の検証
    （`verify_processing_only`等）が成功したら、退避ファイルは
    `finalize_swap`で削除する。失敗した場合は退避ファイルを
    `target_path`へ戻して元に戻す。
    """
    backup_path = target_path.with_suffix(target_path.suffix + backup_suffix)
    if target_path.exists():
        if backup_path.exists():
            backup_path.unlink()
        target_path.rename(backup_path)
    try:
        shutil.move(str(new_path), str(target_path))
    except Exception:
        if backup_path.exists():
            if target_path.exists():
                target_path.unlink()
            backup_path.rename(target_path)
        raise


def finalize_swap(target_path: Path, backup_suffix: str = ".full.bak") -> None:
    """swap_in_placeが成功したことを確認した後、退避ファイルを削除する。"""
    backup_path = target_path.with_suffix(target_path.suffix + backup_suffix)
    if backup_path.exists():
        backup_path.unlink()
