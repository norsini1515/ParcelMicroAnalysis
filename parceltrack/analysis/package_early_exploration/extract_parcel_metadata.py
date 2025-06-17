#parceltrack/analysis/extract_parcel_metadata.py

from parceltrack.configs.paths import ProjectPaths

import pandas as pd
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import re
import geopandas as gpd
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


def build_shapefile_tree_with_paths(directory: Path) -> List[Dict[str, str]]:
    def recurse(folder: Path, rel_parts: List[str]) -> List[Dict[str, str]]:
        records = []
        for subfolder in folder.iterdir():
            if subfolder.is_dir():
                shapefiles = [f.name for f in subfolder.glob("*.shp")]
                if shapefiles:
                    full_path = Path(*rel_parts, subfolder.name)
                    for shp in shapefiles:
                        records.append({
                            "Year": infer_year(rel_parts[0]),
                            "FullPath": str(full_path),
                            "Shapefile": shp
                        })
                # Recurse further
                records.extend(recurse(subfolder, rel_parts + [subfolder.name]))
        return records

    all_records = []
    for year_folder in directory.iterdir():
        if year_folder.is_dir():
            all_records.extend(recurse(year_folder, [year_folder.name]))

    return pd.DataFrame(all_records)

def infer_year(folder_name: str) -> int:
    # Case 1: BACIQ198 → 1998
    if folder_name[-2:].startswith('9'):
        yy = folder_name[-2:]
        return int("19" + yy)

    # Case 2: Baci2017 → 2017
    elif match := re.search(r"Baci(\d{4})", folder_name, re.IGNORECASE):
        return int(match.group(1))

    # Case 3: BACIparcels0821 → 2021 (from MMYY)
    elif match := re.search(r"(\d{4})$", folder_name):
        mm_yy = match.group(1)
        mm, yy = int(mm_yy[:2]), int(mm_yy[2:])
        return 2000 + yy if yy < 50 else 1900 + yy  # Cutoff can be adjusted

    raise ValueError(f"Cannot determine year from folder name: {folder_name}")

def generate_flags(shapefile_tree: pd.DataFrame) -> pd.DataFrame:
    """
    Add binary flags indicating the presence of key layer types
    (CAMA, polygons, sales, zoning, census) for each year.

    Parameters:
        shapefile_tree (pd.DataFrame): A long-form DataFrame with columns:
            - 'Year': int
            - 'FullPath': str (path to shapefile folder)
            - 'Shapefile': str (filename of shapefile)

    Returns:
        pd.DataFrame: A summary DataFrame with columns:
            - 'Year': int
            - 'has_cama', 'has_poly', 'has_sales', 'has_zoning', 'has_census': bool
    """
    df = shapefile_tree.copy()
    df["ShapefileLower"] = df["Shapefile"].str.lower()

    df["has_cama"] = df["ShapefileLower"].str.contains(r"cama|baci.*cama|baci.*land|baci.*suba")
    df["has_poly"] = df["ShapefileLower"].str.contains(r"poly")
    df["has_sales"] = df["ShapefileLower"].str.contains(r"sale")
    df["has_zoning"] = df["ShapefileLower"].str.contains(r"zone|zoning|zn")
    df["has_census"] = df["ShapefileLower"].str.contains(r"cenbg|cenct|ct\d{4}|cens")

    summary = df.groupby("Year").agg({
        "has_cama": "any",
        "has_poly": "any",
        "has_sales": "any",
        "has_zoning": "any",
        "has_census": "any"
    }).reset_index()

    return summary

#parsing an individual shapefile
def get_shapefile_metadata(shapefile_tree: pd.DataFrame, base_dir: Path) -> pd.DataFrame:
    """
    For each shapefile listed in the DataFrame, read the file and extract metadata.

    Parameters:
        shapefile_tree (pd.DataFrame): Must contain columns 'FullPath' and 'Shapefile'
        base_dir (Path): Root directory to prepend to 'FullPath'

    Returns:
        pd.DataFrame: Metadata for each shapefile including:
            - FullPath
            - Shapefile
            - Exists (bool)
            - NumFeatures (int or None)
            - Columns (list or None)
            - GeometryType (str or None)
            - CRS (str or None)
    """
    metadata_records = []

    for _, row in shapefile_tree.iterrows():
        rel_path = Path(row["FullPath"]) / row["Shapefile"]
        full_path = base_dir / rel_path
        if row['Year'] < 2021:
            print(row['Year'])
            print('skipping to next row')
            continue
        
        record = {
            "FullPath": str(row["FullPath"]),
            "Shapefile": row["Shapefile"],
            "Exists": full_path.exists()
        }
        # continue
        if full_path.exists():
            try:
                print(f'reading in {full_path}')
                gdf = gpd.read_file(full_path)
                record["NumFeatures"] = len(gdf)
                record["Columns"] = list(gdf.columns)
                record["GeometryType"] = gdf.geometry.geom_type.mode()[0] if not gdf.empty else None
                record["CRS"] = str(gdf.crs) if gdf.crs else None
            except Exception as e:
                record["NumFeatures"] = None

                record["Columns"] = None
                record["GeometryType"] = None
                record["CRS"] = None
                record["Error"] = str(e)
        else:
            record["NumFeatures"] = None
            record["Columns"] = None
            record["GeometryType"] = None
            record["CRS"] = None

        metadata_records.append(record)

    return pd.DataFrame(metadata_records)

if __name__ == '__main__':
    get_inventory = False
    paths = ProjectPaths()

    if get_inventory:
        shapefile_tree = build_shapefile_tree_with_paths(paths.raw)
        shapefile_tree = shapefile_tree.sort_values(by='Year')
        shapefile_tree_flags = generate_flags(shapefile_tree)
        shapefile_tree_flags.to_csv(paths.raw / 'shapefile_invetory_flags.csv', header=True, index=False)
        shapefile_tree.to_csv(paths.raw / 'shapefile_invetory.csv', header=True, index=False)
    else:
        shapefile_tree = pd.read_csv(paths.raw / 'shapefile_invetory.csv')
    
    print(f"{shapefile_tree.shape=}")

    df_meta = get_shapefile_metadata(shapefile_tree, base_dir=paths.raw)
    df_meta.to_csv(paths.raw / 'shapefile_metadata.csv', index=False)
