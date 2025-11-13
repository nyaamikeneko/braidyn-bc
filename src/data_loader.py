import pandas as pd
from pathlib import Path
import sys

# nwbxなどのライブラリをインポート
import bdbc_nwb_explorer as nwbx

# config.py をインポートするためにプロジェクトルートをsys.pathに追加
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.append(str(PROJECT_ROOT))

try:
    # config.py から定義したパスをインポート
    from config import DATA_NWB_ROOT, DATA_CSV_ROOT
except ImportError:
    print("エラー: config.py がインポートできません。")
    # フォールバック（インポート失敗時）
    DATA_NWB_ROOT = Path('.') 
    DATA_CSV_ROOT = Path('.')

def load_nwb_session(session_id: str, nwb_filename: str):
    """
    指定されたセッションIDとファイル名からNWBデータを読み込む
    
    例: 
    session_id = "VG1GC-105"
    nwb_filename = "VG1GC-105_2024-02-02_task-day8.nwb"
    """
    filepath = DATA_NWB_ROOT / session_id / nwb_filename
    
    if not filepath.exists():
        print(f"NWBファイルが見つかりません: {filepath}")
        return None
    
    print(f"NWB読み込み中: {filepath}")
    session = nwbx.read_nwb(filepath)
    return session

def load_trials_csv(session_id: str, task_day_dir: str, csv_name: str = "trials_L1L2.csv"):
    """
    指定されたセッションIDとタスク日からCSVデータを読み込む
    
    例:
    session_id = "VG1GC-105"
    task_day_dir = "task-day8"
    """
    filepath = DATA_CSV_ROOT / session_id / task_day_dir / csv_name
    
    if not filepath.exists():
        print(f"CSVファイルが見つかりません: {filepath}")
        return None
        
    print(f"CSV読み込み中: {filepath}")
    trials = pd.read_csv(filepath)
    print(f"全試行数: {len(trials)}")
    return trials