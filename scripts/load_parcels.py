from parceltrack.io import load_geometry
from parceltrack.configs.paths import ProjectPaths

from pathlib import Path
import geopandas as gpd
from tqdm import tqdm  #progress bar
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import json
import math

from typing import Dict, Union

def get_poly_files(shapefile_metadata_df):
    poly_shapes = shapefile_metadata_df[shapefile_metadata_df['Shapefile'].str.lower().str.contains('bacipoly')]
    return poly_shapes

def load_files(filtered_shape_meta_df, in_dir: Path, target_crs=None):
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
                
def plot_timeseries_choropleth(
    gdf_dict: dict,
    value_col: str,
    hover_cols: list = None,
    title: str = "Parcel Value Over Time",
    color_scale: str = "Viridis"
) -> go.Figure:
    """
    Create a timeseries choropleth plot using Plotly with a slider to toggle between years.

    Args:
        gdf_dict (dict): A dictionary of {year: GeoDataFrame}.
        value_col (str): Column to use for color fill.
        hover_cols (list): Columns to show in hover tooltip.
        title (str): Plot title.
        color_scale (str): Color scale for the choropleth.

    Returns:
        plotly.graph_objects.Figure: A choropleth figure with a slider.
    """
    layers = []
    years = sorted(gdf_dict.keys())
    buttons = []

    for i, (year, gdf) in enumerate(gdf_dict.items()):

        if hover_cols:
            gdf["hovertext"] = gdf[hover_cols].astype(str).agg("<br>".join, axis=1)
        else:
            gdf["hovertext"] = f"Year: {year}"

        geojson = json.loads(gdf.to_json())

        visible = [False] * len(years)
        visible[i] = True

        layers.append(go.choroplethmap(
            geojson=geojson,
            locations=gdf.index,
            z=gdf[value_col],
            text=gdf["hovertext"],
            colorscale=color_scale,
            zmin=gdf[value_col].min(),
            zmax=gdf[value_col].max(),
            marker_opacity=0.6,
            marker_line_width=0,
            visible=visible[i],
            name=str(year)
        ))

        buttons.append(dict(
            label=str(year),
            method="update",
            args=[{"visible": [j == i for j in range(len(years))]},
                  {"title": f"{title} ({year})"}]
        ))

    fig = go.Figure(data=layers)
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=10,
        mapbox_center={"lat": 39.29, "lon": -76.61},
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title=title,
        sliders=[{
            "steps": buttons,
            "currentvalue": {"prefix": "Year: "}
        }]
    )

    return fig
        
if __name__ == '__main__':
    output_as_geojsons = True
    
    paths = ProjectPaths()

    shapefile_metadata = pd.read_csv(paths.raw / "shapefile_metadata.csv")
    
    poly_files = get_poly_files(shapefile_metadata)
    print(poly_files.shape)

    parcel_files_dict = load_files(poly_files, paths.raw)

    if output_as_geojsons:
        save_geojson_per_year(parcel_files_dict, paths.processed, max_size="25MB")
    
    # parcels_gdf_2021 = parcel_files_dict[2021].copy()
    
    # combined_gdf = combine_geometries_by_year(parcel_files_gdf)
    # combined_gdf.to_file(paths.data / "joined_polygons_2021_2024.geojson", driver="GeoJSON")
    
    #fig = plot_timeseries_choropleth(parcel_files_dict, "NFMTTLVL")
    #fig.write_html(paths.processed / "choropleth_nfmtlvl.html")

