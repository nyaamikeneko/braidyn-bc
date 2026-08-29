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
import subprocess
from pathlib import Path


class InsufficientSpaceError(RuntimeError):
    """空き容量不足で処理を継続できないことを示す。

    複数個体をまとめて処理するバッチ実行では、個体・day単位の欠損（GIN上に無い等）は
    スキップして続行してよいが、空き容量不足は同じ場所で処理を続ける限り再発し続ける
    システム的な問題のため、呼び出し側（バッチループ）はこの例外だけは握りつぶさず
    全体を停止する運用にする。
    """


def check_free_space(path: Path, required_bytes: int, label: str = "") -> None:
    """path配下の空き容量がrequired_bytes未満なら例外を投げる。

    Cドライブ（Google Drive のミラー先と共有）が枯渇すると、9pマウント越しの
    書き込みが`OSError: [Errno 5] Input/output error`で失敗したり、
    `datalad get`が転送完了後にハングしたりする（実測で確認済み）。
    事前チェックで早期に分かりやすいエラーにする。
    """
    usage = shutil.disk_usage(path)
    if usage.free < required_bytes:
        label_suffix = f"（{label}）" if label else ""
        raise InsufficientSpaceError(
            f"空き容量不足{label_suffix}: {path} の空きは {usage.free / 1e9:.2f}GB "
            f"ですが、{required_bytes / 1e9:.2f}GB必要です。"
        )


def clone_gin_dataset(dest_dir: Path, https_url: str, ssh_url: str, https_timeout_sec: int = 60) -> None:
    """GINデータセットをclone(メタデータのみ)する。

    まずHTTPSを試し、失敗（サーバー側の一時的なダウン・ネットワーク不調等）したら
    SSHにフォールバックする。SSH経由には事前にGINアカウント作成＋SSH公開鍵の登録が
    必要（本ノートブックの依存関係セル参照）。

    注意: SSH URLは`ssh://git@gin.g-node.org/ORG/REPO.git`の形式である必要がある。
    scp風の`git@gin.g-node.org:ORG/REPO.git`形式では
    `GIN: Invalid repository path`エラーになる（実測で確認済み）。
    """
    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        print(f"HTTPSでclone試行中（{https_timeout_sec}秒でタイムアウト）...")
        subprocess.run(
            ["datalad", "clone", https_url, str(dest_dir)],
            check=True, timeout=https_timeout_sec,
        )
        return
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
        print(f"HTTPSでのcloneに失敗しました（{exc}）。SSHにフォールバックします。")
        if dest_dir.exists():
            shutil.rmtree(dest_dir)

    subprocess.run(["datalad", "clone", ssh_url, str(dest_dir)], check=True)


def datalad_get_with_recovery(gin_root: Path, rel_path: Path, timeout_sec: int = 3600) -> None:
    """`datalad get`を実行する。

    実測で、ダウンロード自体は完了している（ファイルサイズが期待値に達している）のに
    プロセスが後処理でハングし続ける現象を確認した（原因はCドライブの空き容量枯渇と
    見られる。`check_free_space`で事前チェックしてもなお発生しうるため、ここでも
    タイムアウト後にサイズ照合で救済する）。タイムアウトした場合、`git annex find`で
    取得した期待サイズとローカルファイルの実サイズが一致していれば成功とみなす。
    """
    expected_raw = subprocess.run(
        ["git", "annex", "find", "--format=${bytesize}", str(rel_path)],
        cwd=str(gin_root), check=True, capture_output=True, text=True,
    ).stdout.strip()
    expected_bytes = int(expected_raw) if expected_raw else None

    proc = subprocess.Popen(["datalad", "get", str(rel_path)], cwd=str(gin_root))
    try:
        proc.wait(timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        actual_path = gin_root / rel_path
        actual_bytes = actual_path.stat().st_size if actual_path.exists() else -1
        if expected_bytes is not None and actual_bytes == expected_bytes:
            print(
                "datalad getがタイムアウトしましたが、ファイルサイズが期待値と一致しているため"
                "成功とみなします（ダウンロード完了後のハング）。"
            )
            return
        raise RuntimeError(
            f"datalad get がタイムアウトし、ファイルサイズも不一致です"
            f"(期待={expected_bytes}, 実際={actual_bytes})。ディスク空き容量を確認してください。"
        )
    else:
        if proc.returncode != 0:
            raise RuntimeError(f"datalad get failed with code {proc.returncode}")


def _annex_object_path(gin_root: Path, target: Path) -> Path | None:
    """targetの実体が置かれている `.git/annex/objects/` 配下のパスを返す（無ければNone）。

    ワークツリー側の見え方はannexのモードで異なる:
    - ロック済み: `.git/annex/objects/...` へのシンボリックリンク → リンクを辿る。
    - unlocked（このGINデータセットが使っている形式。`datalad clone`直後は
      64バイト程度のポインタファイル）: `datalad get`後は実体へのハードリンク
      またはコピー → inode一致で探し、駄目ならサイズ一致で1件に絞れる場合のみ採用。

    誤削除を防ぐため、当該リポジトリの `.git/annex/objects/` 配下のファイルしか返さない。
    """
    annex_objects = gin_root / ".git" / "annex" / "objects"
    if not annex_objects.exists():
        return None
    if target.is_symlink():
        obj_path = target.resolve()
        if obj_path.is_file() and annex_objects.resolve() in obj_path.parents:
            return obj_path
        return None
    if not target.is_file():
        return None

    target_stat = target.stat()
    same_size = []
    for obj_path in annex_objects.rglob("*"):
        if not obj_path.is_file():
            continue
        obj_stat = obj_path.stat()
        if obj_stat.st_dev == target_stat.st_dev and obj_stat.st_ino == target_stat.st_ino:
            return obj_path
        if obj_stat.st_size == target_stat.st_size:
            same_size.append(obj_path)
    return same_size[0] if len(same_size) == 1 else None


def _remove_annex_object(gin_root: Path, target: Path) -> None:
    """targetの実体（`.git/annex/objects/`配下）を削除する。

    ワークツリー側のファイルを消してもannexの実体が残っていれば1.7GBは解放されない。
    `git annex unused` → `git annex dropunused` を使う手もあるが、これはdropが
    ハングした後のフォールバックなので、annexのサブプロセスをさらに走らせるのは
    本末転倒。ファイルシステム操作だけで完結させる。

    実体のあるディレクトリはgit-annexが読み取り専用にしているのでchmodしてから消す。
    """
    obj_path = _annex_object_path(gin_root, target)
    if obj_path is None:
        return
    size = obj_path.stat().st_size
    obj_path.parent.chmod(0o755)
    obj_path.unlink()
    print(f"annexの実体も削除しました: {obj_path} ({size / 1e9:.2f}GB)")


def _restore_pointer_file(gin_root: Path, rel_path: Path, timeout_sec: int = 60) -> None:
    """ワークツリーから消したファイルをgitのポインタファイルとして復元する。

    実体を消した後に`git checkout`すると、annexは内容が手元に無いことを検知して
    ポインタファイル（数十バイト）を書き戻す。これをやらないとワークツリーが
    「削除済み」状態のままになり、`find_gin_nwb_path`が次回そのdayを見つけられなくなる
    （実測: day1のポインタファイルがこれで消えていた）。失敗しても致命的ではないので
    警告だけ出して続行する。
    """
    proc = subprocess.Popen(
        ["git", "checkout", "--", str(rel_path)],
        cwd=str(gin_root),
    )
    try:
        proc.wait(timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    if (gin_root / rel_path).exists():
        print(f"ポインタファイルを復元しました: {rel_path}")
    else:
        print(f"警告: ポインタファイルを復元できませんでした（`git checkout -- {rel_path}`を手動実行してください）")


def datalad_drop_with_recovery(gin_root: Path, rel_path: Path, timeout_sec: int = 120) -> None:
    """`datalad drop`を実行する。タイムアウトした場合は作業コピーを直接削除する。

    dropもgetと同様の理由でハングすることがある。使い捨てのGINキャッシュなので、
    annexのブックキーピングが多少不整合になっても実害はなく、確実にディスクから
    消えることを優先する。ワークツリー側のファイルを消すだけでは容量が解放されない
    （実体は`.git/annex/objects/`にある）ため`_remove_annex_object`で実体も消し、
    ワークツリーは`_restore_pointer_file`でポインタファイルに戻す。
    """
    proc = subprocess.Popen(["datalad", "drop", str(rel_path)], cwd=str(gin_root))
    try:
        proc.wait(timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        target = gin_root / rel_path
        if target.is_symlink() or target.exists():
            _remove_annex_object(gin_root, target)
            target.unlink()
            print(f"datalad dropがタイムアウトしたため、作業コピーを直接削除しました: {target}")
            _restore_pointer_file(gin_root, rel_path)


def cleanup_work_dir(work_dir: Path) -> int:
    """work_dir直下のNWB（変換途中・変換済みの一時ファイル）を削除し、解放バイト数を返す。

    本体ループは`finally`で一時ファイルを消すが、カーネルごと落ちる・実行を中断する等で
    残骸が残ることがある（実測: ハング修正前の中断runで186MBのday1が残っていた）。
    1ファイル約195MBがWSLのext4.vhdxを膨らませ続けるため、ループの前後で掃除する。
    """
    if not work_dir.exists():
        print(f"作業ディレクトリはまだありません: {work_dir}")
        return 0
    freed = 0
    for path in sorted(work_dir.glob("*.nwb")):
        size = path.stat().st_size
        path.unlink()
        freed += size
        print(f"一時ファイルを削除: {path.name} ({size / 1e6:.1f} MB)")
    if freed == 0:
        print(f"削除対象の一時ファイルはありません: {work_dir}")
    else:
        print(f"合計 {freed / 1e6:.1f} MB 解放しました: {work_dir}")
    return freed


def copy_to_drive(src_path: Path, dst_path: Path) -> None:
    """Google Drive（9pマウント）へファイルをコピーする。

    `shutil.copy2`等が内部で使う`sendfile()`は9pマウント越しだと
    `OSError: [Errno 5] Input/output error`になることがある（実測で確認済み。
    Cドライブ枯渇時に発生し、通常のread/writeループでも空き容量不足なら
    同様に失敗するが、その場合は`check_free_space`で事前に弾く）。
    通常のread/writeでコピーし、失敗時は中途半端なdstを残さない。
    """
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(src_path, "rb") as fsrc, open(dst_path, "wb") as fdst:
            while True:
                chunk = fsrc.read(4 * 1024 * 1024)
                if not chunk:
                    break
                fdst.write(chunk)
    except Exception:
        if dst_path.exists():
            dst_path.unlink()
        raise


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
    new_pathをtarget_pathへコピーする。呼び出し側で置き換え後の検証
    （`verify_processing_only`等）が成功したら、退避ファイルは
    `finalize_swap`で削除する。失敗した場合は退避ファイルを
    `target_path`へ戻して元に戻す。

    new_path（WSLローカル）とtarget_path（Drive）は別ファイルシステムのため、
    `shutil.move`が内部でコピー+削除にフォールバックし`copy_to_drive`と同じ
    `sendfile()`のI/Oエラーを踏むことがある。そのため明示的に`copy_to_drive`を使う。
    """
    backup_path = target_path.with_suffix(target_path.suffix + backup_suffix)
    if target_path.exists():
        if backup_path.exists():
            backup_path.unlink()
        target_path.rename(backup_path)
    try:
        copy_to_drive(new_path, target_path)
        new_path.unlink()
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
