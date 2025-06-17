📘 Summary: Parcel Spillovers & Urban Reactivity
🔍 Theoretical Foundations
Spillover Effects
Parcels are spatially interdependent. A change at one (e.g., development or vacancy) may ripple outward, altering the character or value of neighbors. This reflects spatial externalities, foundational in urban economics and land use modeling (Irwin & Bockstael, 2002; Glaeser et al., 2005).

Reactivity & Elasticity
Reactivity refers to the magnitude and speed of a parcel’s response to a neighbor’s change. Elasticity adds an economic framing—how sensitive value or use is to those triggers.
These concepts also reflect the spatial lag principle (from Lecture 1): nearby phenomena influence each other more strongly than distant onesLecture 1 Statisitcal A….

Equity & Spatial Inequality
Not all neighborhoods are equally reactive. Historic disinvestment or exclusionary zoning may cause under-response or hypersensitivity. Modeling these disparities helps uncover latent spatial injustice and informs more equitable planning.

🧭 Conceptual Model
Inputs:

Parcel-level shapefiles: geometry, use class, owner type, assessed value

Event labels: Redevelopment, sale, vacancy, rezoning

Process:

Detect “events” in focal parcels (T)

Track outcomes in neighboring parcels (T+1)

Quantify % or magnitude of changes over space and time

Outputs:

Parcel or neighborhood-level reactivity scores

Heatmaps of elasticity

Overlay equity variables: redlining maps, zoning, census demographics

🗂 Data Foundations
Baltimore Parcels (MDP)

2021–2024: Clean structure with ACCTID joins

1996–2019: Older datasets requiring harmonization

Augmented Layers

SDAT attributes: land use, tax values, sale history

Census overlays: race, income, age, education

Historic planning layers: redlining, zoning

Built environment: permits, demolitions, footprint change

🧪 Methodologies
Change Detection

Detect differences in parcel shape, use class, value across years

Normalize value shifts to real dollars for temporal comparability

Spatial Joins / Buffers

Identify “neighbors” based on contiguity or distance thresholds

Represent relationships via spatial weights matrix (W)

Event Study Logic

Model outcomes before/after events in surrounding parcels

Ideal for inferring spatial causality and timing lags

Modeling Approaches

Panel Regression: Track parcels over time; include fixed effects

Spatial Lag Models: Value change depends on neighbors' change

ML Models (RF, XGBoost): Capture nonlinear spillovers

Splines / Kernel Methods: Model gradient effects by distance

Regularization (Lasso/Ridge): Combat overfitting with high-D spatial features

Clustering / Mapping

Use DBSCAN or GWR to detect reactivity zones

Classify areas as high/low elasticity zones for planning insight

Equity Lens

Examine if reactivity correlates with race, income, zoning history

Use statistical overlays and crosstabs to quantify disparities




📚 Parcel Spillover & Reactivity Analysis: Full Technical and Conceptual Blueprint
1. 🔍 Theoretical Foundations
1.1 Spatial Interdependence & Externalities
Urban parcels are not independent units. Each parcel's trajectory—its land use, value, or structural form—is shaped by changes in its spatial vicinity.
This reflects Waldo Tobler’s First Law of Geography:

“Everything is related to everything else, but near things are more related than distant things.”

1.2 Reactivity & Elasticity
Reactivity: Magnitude and speed of nearby parcels’ change in response to a focal event.
Elasticity: Percentage change in outcome relative to percentage change in a neighbor’s attribute. Econometrically:
This framing supports log-log modeling

Where 
𝛽
β captures the elasticity of parcel value change to redevelopment in neighbors.

1.3 Equity and Spatial Injustice
Spatial reactivity is stratified by wealth, zoning, and race—this is critical for identifying where ripple effects fail or disproportionately harm.

Using overlays like:

Historic redlining (HOLC maps)

Current zoning codes

Census tract-level ACS variables (race, income, education)
You can cross-tabulate reactivity patterns with systemic inequality.

2. 🧭 Conceptual Model (with Formal Structure)
Step 1: Identify Events
Define event labels:

Ownership turnover

Land use reclassification

Vacancy / demolition

New construction


Step 2: Construct Neighborhood Context
For each focal parcel define spatial weights


Step 3: Quantify Change in Neighbors
Neighbord change sum of weights * price changes of neighbor


Step 4: Model Formulation
Panel Regression with Lag Structure:
Fixed effects, time dummys

Spatial Lag Model:

Step 4: Model Formulation

Panel Regression with Lag Structure:
Spatial Lag Model:
Machine Learning Alternative
With nonlinear estimators:
Random Forests
Gradient Boosting Machines, Forests, 
Spatially structured neural nets (e.g., GCNs, CNNs over raster-like features)