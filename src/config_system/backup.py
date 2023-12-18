import json
from datetime import datetime
from pathlib import Path

def create_backup(storage, backup_dir: Path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"config_backup_{timestamp}.json"
    
    with backup_file.open('w') as f:
        json.dump(storage.dump_all(), f)
