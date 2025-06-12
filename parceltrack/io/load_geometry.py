# parceltrack/io/load_geometry.py

from pathlib import Path
from typing import Dict, Union
import geopandas as gpd
import pandas as pd
import tqdm
import math
import re

def parse_size(size_str: str) -> int:
    """Convert size string like '25MB' to bytes."""
    size_str = size_str.upper().strip()
    if size_str.endswith("MB"):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith("KB"):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith("B"):
        return int(size_str[:-1])
    else:
        raise ValueError(f"Unsupported size format: {size_str}")
    
def load_geometry(
    filepath: Union[str, Path],
    validate_geometry: bool = True,
    target_crs: Union[str, int, None] = None
) -> gpd.GeoDataFrame:
    """
    Load any geospatial file into a GeoDataFrame (Shapefile, GeoJSON, GeoPackage, etc.).

    Args:
        filepath (str | Path): Input path to a spatial file.
        validate_geometry (bool): Drop invalid/missing geometries.
        target_crs (str | int | None): Reproject CRS (e.g., 'EPSG:6487').

    Returns:
        gpd.GeoDataFrame: Cleaned and optionally reprojected geometries.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        gdf = gpd.read_file(path)
    except Exception as e:
        raise RuntimeError(f"Failed to load geospatial file: {e}")

    if validate_geometry:
        gdf = gdf[gdf.geometry.notnull() & gdf.is_valid]

    if target_crs:
        try:
            gdf = gdf.to_crs(target_crs)
        except Exception as e:
            raise ValueError(f"CRS transformation failed: {e}")

    return gdf

def load_files_from_metdata(filtered_shape_meta_df, in_dir: Path, target_crs=None):
    """
    Load shapefiles listed in a metadata DataFrame into GeoDataFrames.

    Args:
        filtered_shape_meta_df (pd.DataFrame): Contains 'Year', 'FullPath', and 'Shapefile' columns.
        in_dir (Path): Base directory to prepend to 'FullPath'.
        target_crs (str | int | None): Optional CRS to reproject geometries.

    Returns:
        Dict[int, Dict[str, gpd.GeoDataFrame]]: Nested dict by year and shapefile name.
    """

    print(f'Loading {filtered_shape_meta_df.shape[0]} shapefiles...')
    geoms = {}
    
    for _, row in tqdm(filtered_shape_meta_df.iterrows(), total=filtered_shape_meta_df.shape[0]):
    # for _, row in filtered_shape_meta_df.iterrows():
        year = row["Year"]
        print('loading', year)
        rel_path = Path(row["FullPath"]) / row["Shapefile"]
        full_path = in_dir / rel_path

        try:
            gdf = load_geometry(full_path, target_crs=target_crs)
            if year not in geoms:
                geoms[year] = None
            geoms[year] = gdf.copy()
            print(f"[SUCCESS] Loaded {year} {row['Shapefile']}, {len(gdf)} features.")
        except Exception as e:
            print(f"[FAILURE] {year} {row['Shapefile']}: {e}")

    return geoms
   
def save_geojson_per_year(
    geoms: Dict[int, gpd.GeoDataFrame],
    output_dir: Path,
    max_size: Union[str, None] = None
):
    """
    Save each year's GeoDataFrame to individual GeoJSON files. If max_size is set,
    split each file into multiple parts to stay under the size limit.

    Args:
        geoms (dict): {year: GeoDataFrame}
        output_dir (Path): Directory to save output files
        max_size (str | None): Optional max file size (e.g., '25MB'). If None, save as single file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    max_bytes = parse_size(max_size) if max_size else None

    for year, gdf in geoms.items():
        print(f"Saving {year}...")

        # Save full file temporarily to measure size
        temp_path = output_dir / f"__temp_parcels_{year}.geojson"
        gdf.to_file(temp_path, driver="GeoJSON")
        size = temp_path.stat().st_size

        if max_bytes is None or size <= max_bytes:
            volume_max = 1
            chunks = [(1, gdf)]
        else:
            volume_max = math.ceil(size / max_bytes)
            chunk_size = math.ceil(len(gdf) / volume_max)
            chunks = [
                (i + 1, gdf.iloc[start:start + chunk_size])
                for i, start in enumerate(range(0, len(gdf), chunk_size))
            ]

        for i, chunk in chunks:
            out_path = output_dir / f"parcels_{year}_part{i}_{volume_max}.geojson"
            chunk.to_file(out_path, driver="GeoJSON")
            print(f"Saved part {i}/{volume_max}: {out_path} ({chunk.shape[0]} rows)")

        if temp_path.exists():
            temp_path.unlink()

def load_processed_year_files(directory, year, target_crs=None):
    """
    Loads and concatenates all GeoJSON partition files for a given year using `load_geometry`.

    Parameters:
    - directory (str or Path): Folder containing partitioned GeoJSON files.
    - year (int or str): Year of interest (e.g., 2021).
    - target_crs (str or CRS, optional): CRS to reproject all GeoDataFrames into.

    Returns:
    - GeoDataFrame: Combined GeoDataFrame with unified CRS.
    """
    directory = Path(directory)
    pattern = re.compile(rf'^parcels_{year}_part\d+_\d+\.geojson$')
    matching_files = sorted([f for f in directory.iterdir() if pattern.match(f.name)])

    if not matching_files:
        raise FileNotFoundError(f"No matching files found for year {year} in {directory}")

    print(f"[INFO] Loading {len(matching_files)} GeoJSON files for year {year}...")

    gdfs = [load_geometry(f, target_crs=target_crs) for f in matching_files]
    combined = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)

    print(f"[SUCCESS] Combined {len(gdfs)} files into {len(combined)} features.")
    return combined






