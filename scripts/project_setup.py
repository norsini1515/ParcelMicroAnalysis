from parceltrack import ProjectPaths
from pathlib import Path
import zipfile
import os

def extract_all_zips(zip_dir: Path, output_dir: Path):
    for file in zip_dir.glob("*.zip"):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            folder_name = file.stem
            target_folder = output_dir / folder_name
            target_folder.mkdir(exist_ok=True)
            zip_ref.extractall(target_folder)
            print(f"Extracted {file.name} → {target_folder}")

if __name__ == '__main__':
    print('Project structure initialized.')
    project_paths = ProjectPaths()
    extract_all_zips(project_paths.raw)