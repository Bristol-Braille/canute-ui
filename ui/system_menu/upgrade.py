import os
from ..config_loader import load

def mounted_paths():
    config = load()
    media_dir = config.get('files', {}).get('media_dir')
    source_dirs = config.get('files', {}).get('library', [])

    for source_dir in source_dirs:
        source_path = os.path.join(media_dir, source_dir.get('path'))
        if source_dir.get('mountpoint', False) and os.path.ismount(source_path):
            yield source_path, source_dir.get('name')

def upgrade_files():
    config = load()
    return config.get('system', {}).get('sysupgrade', [])

available = False
source_paths = mounted_paths()
for source_path, source_name in source_paths:
    for upgrade in upgrade_files():
        upgrade_file = os.path.join(source_path, upgrade)
        if os.path.exists(upgrade_file):
            available = True
            break

def upgrade():
    os.system('sudo systemctl start system-upgrade')
