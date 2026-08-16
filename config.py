import os
from pathlib import Path

# このプロジェクトのルートディレクトリ（config.pyがある場所）
PROJECT_ROOT = Path(__file__).parent.resolve()


def _first_existing(paths):
    """Return the first path that exists; otherwise the first candidate."""
    for path in paths:
        if path.exists():
            return path
    return paths[0]


# OSや環境（Colabかどうか）を判定してデータルートを設定
if 'COLAB_GPU' in os.environ:
    print("環境: Colab")
    GDRIVE_ROOT = Path('/content/drive/MyDrive')
    DATA_NWB_ROOT = GDRIVE_ROOT / 'braidyn-bc/data'
    DATA_CSV_BACKUP_ROOT = GDRIVE_ROOT / 'braidyn-bc-backup/hackathon_data'
    DATA_CSV_ROOT = _first_existing(
        [GDRIVE_ROOT / 'hackathon_data', DATA_CSV_BACKUP_ROOT],
    )

elif 'WSL_DISTRO_NAME' in os.environ:
    print("環境: ローカル (WSL)")
    GDRIVE_ROOT = Path('/mnt/g') / 'マイドライブ'
    DATA_NWB_ROOT = _first_existing(
        [
            GDRIVE_ROOT / 'nwb_manual',
            Path('/mnt/g/.shortcut-targets-by-id/1DtufNi90fhQp6kIcuS0MxtTz-Uk5LSS9/braidyn-bc/data'),
        ],
    )
    DATA_CSV_BACKUP_ROOT = GDRIVE_ROOT / 'braidyn-bc-backup' / 'hackathon_data'
    DATA_CSV_ROOT = _first_existing(
        [
            Path('/mnt/g/.shortcut-targets-by-id/1fI6PWRHgihU6asA4OyW-_rN-JII33Fkj/hackathon_data'),
            DATA_CSV_BACKUP_ROOT,
        ],
    )

    if not DATA_NWB_ROOT.exists():
        print(f"警告: NWBデータパスが見つかりません: {DATA_NWB_ROOT}")
    if not DATA_CSV_ROOT.exists():
        print(f"警告: CSVデータパスが見つかりません: {DATA_CSV_ROOT}")

else:
    print("環境: ローカル (Windows)")
    GDRIVE_ROOT = Path('G:/') / 'マイドライブ'
    DATA_NWB_ROOT = _first_existing(
        [
            GDRIVE_ROOT / 'nwb_manual',
            Path(r'G:\.shortcut-targets-by-id\1DtufNi90fhQp6kIcuS0MxtTz-Uk5LSS9\braidyn-bc\data'),
        ],
    )
    DATA_CSV_BACKUP_ROOT = GDRIVE_ROOT / 'braidyn-bc-backup' / 'hackathon_data'
    DATA_CSV_ROOT = _first_existing(
        [
            Path(r'G:\.shortcut-targets-by-id\1fI6PWRHgihU6asA4OyW-_rN-JII33Fkj\hackathon_data'),
            DATA_CSV_BACKUP_ROOT,
        ],
    )

    if not DATA_NWB_ROOT.exists():
        print(f"警告: NWBデータパスが見つかりません: {DATA_NWB_ROOT}")
    if not DATA_CSV_ROOT.exists():
        print(f"警告: CSVデータパスが見つかりません: {DATA_CSV_ROOT}")

print(f"DATA_CSV_ROOT: {DATA_CSV_ROOT}")
print(f"DATA_CSV_BACKUP_ROOT: {DATA_CSV_BACKUP_ROOT}")