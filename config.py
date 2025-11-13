import os
from pathlib import Path

# このプロジェクトのルートディレクトリ（config.pyがある場所）
PROJECT_ROOT = Path(__file__).parent.resolve()

# OSや環境（Colabかどうか）を判定してデータルートを設定
if 'COLAB_GPU' in os.environ:
    # Colab環境の場合
    print("環境: Colab")
    GDRIVE_ROOT = Path('/content/drive/MyDrive')
    
    # Colab用のパス定義
    DATA_NWB_ROOT = GDRIVE_ROOT / 'braidyn-bc/data'
    DATA_CSV_ROOT = GDRIVE_ROOT / 'hackathon_data'

else:
    # Windows (ローカル) 環境を想定
    print("環境: ローカル (Windows)")
    
    # 提示されたローカルの絶対パスを直接指定
    # (r'...' は Windows のパス区切り文字 \ を正しく扱うための記法)
    DATA_NWB_ROOT = Path(r'G:\.shortcut-targets-by-id\1DtufNi90fhQp6kIcuS0MxtTz-Uk5LSS9\braidyn-bc\data')
    
    # 提示されたパスからCSVルートを設定 (末尾の特定セッション部分を除外)
    DATA_CSV_ROOT = Path(r'G:\.shortcut-targets-by-id\1fI6PWRHgihU6asA4OyW-_rN-JII33Fkj\hackathon_data')

    # パスの存在確認
    if not DATA_NWB_ROOT.exists():
        print(f"警告: NWBデータパスが見つかりません: {DATA_NWB_ROOT}")
    if not DATA_CSV_ROOT.exists():
        print(f"警告: CSVデータパスが見つかりません: {DATA_CSV_ROOT}")


# これ以降、DATA_NWB_ROOT や DATA_CSV_ROOT を直接使用できます