from parceltrack.io import load_geometry
from parceltrack.configs.paths import ProjectPaths

from pathlib import Path
import geopandas as gpd
from tqdm import tqdm  # optional progress bar
import pandas as pd
import plotly.express as px

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

def combine_geometries_by_year(geoms: dict) -> gpd.GeoDataFrame:
    """
    Combine a dictionary of GeoDataFrames by year into a single GeoDataFrame.

    Args:
        geoms (Dict[int, gpd.GeoDataFrame]): Dictionary where keys are years and
                                             values are GeoDataFrames.

    Returns:
        gpd.GeoDataFrame: Combined GeoDataFrame with a new 'Year' column.
    """
    frames = []
    for year, gdf in geoms.items():
        gdf = gdf.copy()
        gdf["Year"] = year
        frames.append(gdf)

    return gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=frames[0].crs if frames else None)

def plot_timeseries_choropleth(
    gdf: gpd.GeoDataFrame,
    variable: str,
    year_col: str = "Year",
    hover_cols: list = None,
    title: str = None,
    cmap: str = "Viridis"
):
    """
    Create a choropleth time series map with Plotly for a given variable.

    Args:
        gdf (GeoDataFrame): DataFrame with geometry and variable to plot.
        variable (str): Column to visualize as color.
        year_col (str): Column representing the time axis (default: 'Year').
        hover_cols (list): Optional columns to include in the hover tooltip.
        title (str): Optional plot title.
        cmap (str): Color scale name (e.g. 'Viridis', 'Inferno').

    Returns:
        plotly.graph_objects.Figure: Plotly choropleth map figure.
    """
    if variable not in gdf.columns:
        raise ValueError(f"{variable} not found in dataframe.")

    if year_col not in gdf.columns:
        raise ValueError(f"{year_col} not found in dataframe.")

    if hover_cols is None:
        hover_cols = [variable]

    gdf = gdf.to_crs(epsg=4326)

    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color=variable,
        animation_frame=year_col,
        hover_data=hover_cols,
        mapbox_style="carto-positron",
        color_continuous_scale=cmap,
        zoom=10,
        center={"lat": gdf.geometry.centroid.y.mean(), "lon": gdf.geometry.centroid.x.mean()},
        title=title or f"{variable} over time"
    )

    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    return fig


if __name__ == '__main__':
    paths = ProjectPaths()
    # extract_all_zips(paths.raw, paths.raw)

    shapefile_metadata = pd.read_csv(paths.raw / "shapefile_metadata.csv")
    
    poly_files = get_poly_files(shapefile_metadata)
    print(poly_files.shape)

    parcel_files_dict = load_files(poly_files, paths.raw)
    parcels_gdf_2021 = parcel_files_dict[2021].copy()
    
    
    # combined_gdf = combine_geometries_by_year(parcel_files_gdf)
    # combined_gdf.to_file(paths.data / "joined_polygons_2021_2024.geojson", driver="GeoJSON")
    
    # fig = plot_timeseries_choropleth(combined_gdf, "NFMTTLVL")
    # fig.write_html(paths.processed / "choropleth_nfmtlvl.html")

