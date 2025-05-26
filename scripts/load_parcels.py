from parceltrack.io import load_geometry
from parceltrack.configs.paths import ProjectPaths

from pathlib import Path
import zipfile
import os

def get_raw_files(paths):
    print(os.listdir(paths.raw))

def extract_all_zips(zip_dir: Path, output_dir: Path):
    for file in zip_dir.glob("*.zip"):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            folder_name = file.stem
            target_folder = output_dir / folder_name
            target_folder.mkdir(exist_ok=True)
            zip_ref.extractall(target_folder)
            print(f"Extracted {file.name} → {target_folder}")

if __name__ == '__main__':
    paths = ProjectPaths()
    extract_all_zips(paths.raw, paths.raw)