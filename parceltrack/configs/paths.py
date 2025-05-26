"""
parceltrack/configs/paths.py

ProjectPaths utility

Centralized directory manager for the ParcelMicroAnalysis project. 
Resolves all key folders (data, notebooks, scripts, etc.) relative to the project root.

Example:
    from parceltrack.configs.paths import ProjectPaths
    paths = ProjectPaths()
    print(paths.raw)  # -> /absolute/path/to/data/raw
"""

from pathlib import Path

class ProjectPaths:
    def __init__(self, root: Path = None):
        self.root = root or Path(__file__).resolve().parents[2]  # <- Now inside parceltrack/configs

        # Top-level project directories
        self.data = self.root / "data"
        self.raw = self.data / "raw"
        self.processed = self.data / "processed"
        self.notebooks = self.root / "notebooks"
        self.reports = self.root / "reports"
        self.scripts = self.root / "scripts"
        self.tests = self.root / "tests"

        # Internal package structure
        self.package = self.root / "parceltrack"
        self.analysis = self.package / "analysis"
        self.configs = self.package / "configs"
        self.visuals = self.package / "visualization"
        self.io = self.package / 'io'

        # Automatically create dirs
        self.ensure_dirs()

    def __repr__(self):
        return f"<ProjectPaths root={self.root}>"

    def ensure_dirs(self):
        for attr in self.__dict__.values():
            if isinstance(attr, Path):
                attr.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    paths = ProjectPaths()
    print(paths.root)
