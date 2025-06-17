from parceltrack.io import (load_files_from_metdata,
                            load_processed_year_files,
                            save_geojson_per_year) 
from parceltrack.configs.paths import ProjectPaths

from pathlib import Path
import geopandas as gpd
from tqdm import tqdm  #progress bar
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import json
import re

import matplotlib.pyplot as plt

def filter_poly_files(shapefile_metadata_df):
    poly_shapes = shapefile_metadata_df[shapefile_metadata_df['Shapefile'].str.lower().str.contains('bacipoly')]
    return poly_shapes
                        
def plot_timeseries_choropleth(
    gdf_dict: dict,
    value_col: str,
    hover_cols: list = ["ACCTID"],
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

    cols = hover_cols + [value_col, 'geometry', 'POLYID']
    for i, (year, gdf) in enumerate(gdf_dict.items()):
        print(year)
        
        used_gdf = gdf[cols].reset_index(drop=True)
        
        if hover_cols:
            gdf["hovertext"] = used_gdf[hover_cols].astype(str).agg("<br>".join, axis=1)
        else:
            gdf["hovertext"] = f"Year: {year}"

        geojson = json.loads(used_gdf.to_json())

        visible = [False] * len(years)
        visible[i] = True

        layers.append(go.Choroplethmap(
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
    output_as_geojsons = False
    
    paths = ProjectPaths()

    if output_as_geojsons:
        shapefile_metadata = pd.read_csv(paths.raw / "shapefile_metadata.csv")
        poly_files = filter_poly_files(shapefile_metadata)
        parcel_files_dict = load_files_from_metdata(poly_files, paths.raw)
        save_geojson_per_year(parcel_files_dict, paths.processed, max_size="25MB")
    
    for year in range(2021, 2025):
        if(year in [2022, 2023, 2024]):
            continue
        parcels_year = load_processed_year_files(directory=paths.processed / 'partitioned_files', year=year)
        save_geojson_per_year({year:parcels_year}, paths.processed)
    
    if False:
        parcel_columns = parcels_2021.columns.tolist()
        columns = ['ACCTID', 'ADDRESS', 'BLOCK', 'ZONING', 'YEARBLT', 'SQFTSTRC', 'NFMLNDVL', 'NFMIMPVL', 'NFMTTLVL', 'geometry']
        parcels_2021_subset = parcels_2021[columns]
        zones = parcels_2021_subset['ZONING'].value_counts(dropna=False)
        
        parcels_2021_subset.plot(
        column="NFMTTLVL",  # or any other column
        cmap="viridis",
        legend=True,
        figsize=(10, 10),
        edgecolor="black",
        linewidth=0.2
        )
        plt.title("Total Parcel Value (2021)")
        plt.show()
