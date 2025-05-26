🚀 Core Development Options
📥 1. Data Loading
Write load_parcels(path: Union[str, Path]) -> GeoDataFrame

Optional caching

Add auto-detection of .shp vs .geojson

🧼 2. Preprocessing Utilities
Standardize CRS (e.g., convert to EPSG:6487 or 26985 for Baltimore)

Drop invalid/missing geometries

Geometry validation and simplification

📈 3. Temporal Comparison
Track changes across years (e.g., merge 1996 vs 2023)

Flag new/removed parcels, changed shapes

🧪 4. Exploratory Spatial Analysis
Cluster density mapping

Parcel size distribution over time

Join with other attributes (e.g., zoning, ownership)

📊 5. Notebook Starter
EDA for one year of parcel data (basic visuals, distributions, shape integrity)

🔍 6. Visualization
Plot parcels with matplotlib or GeoPandas.plot()

Style by change flags or shape metrics