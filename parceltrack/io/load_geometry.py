# parceltrack/io/parcel_loader.py

from pathlib import Path
from typing import Union
import geopandas as gpd

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