**Slide Deck: Ripple Effects - Modeling Parcel-Level Change and Its Impacts in Baltimore**

---

**Slide 1: Title Slide**
**Ripple Effects:** Modeling Parcel-Level Change and Its Impacts in Baltimore
Nick Orsini | Geospatial Statistics | Johns Hopkins University

---

**Slide 2: Project Overview**
**Core Idea:**
Model how changes to individual parcels (redevelopment, vacancy, etc.) influence surrounding parcels over time.
Focus: Baltimore City parcels, 2015-2023 (pending MDP data).

**Goal:** Quantify and visualize spatial & temporal spillover effects.

---

**Slide 3: Alignment with Course**
Applies full spatial statistics workflow:

* Wrangle multi-year parcel data
* Perform spatial EDA and clustering
* Build spatial and temporal models (e.g., lags, panel)
* Visualize findings via Story Map

**Bonus:** Potential to evolve into real-world tool for planning & policy.

---

**Slide 4: Personal Motivation**
Builds on undergrad thesis at Salisbury University:

* OLS model of land value in Wicomico County
* Struggled with autocorrelation, lacked ML, panel techniques

**Now equipped with:**

* Spatial regression, regularization, cross-validation
* Panel data methods and advanced modeling

---

**Slide 5: Data Sources**
**Parcel-Level:**

* MDP historical shapefiles
* SDAT attributes: land use, value, ownership, vacancy

**Spatial Context:**

* Census blocks / neighborhoods
* Distance to CBD, amenities

**Outcomes:**

* Parcel value change
* Inferred or scraped rent prices
* Condition (violations, vacancies)

---

**Slide 6: Analytical Techniques**

* Spatial Lag Models
* Panel Regression (parcel-by-time)
* Machine Learning (Random Forests, XGBoost)
* Regularization (Ridge, Lasso)
* Spline or kernel methods for nonlinear spatial effects

---

**Slide 7: Visualization & Storytelling**

* ArcGIS Story Map: Maps + narrative
* Time series maps of change propagation
* Hotspot analysis and cluster dynamics
* Simulation of future ripple scenarios

---

**Slide 8: Future Vision: Dashboard Tool**
**Interactive Simulation Interface**

* Input: Choose parcel + change type
* Output: Predict spillover effects (value, rent, condition)
* Temporal sliders and aggregation controls

**Use Cases:**

* Planning intervention targeting
* Displacement risk detection
* Public policy modeling

---

**Slide 9: Challenges & Mitigations**
**Data Challenges:** Parcel ID consistency, rent data scarcity
**Tech Solutions:** Matching heuristics, Craigslist scraping, proxy indicators

**Modeling Challenges:** Spatial autocorrelation, interpretability
**Mitigations:** Use spatial diagnostics, blend ML and interpretable models

---

**Slide 10: Next Steps**

* Await response from MDP
* Begin spatial EDA + rent data scraping
* Define parcel "change" events + metrics
* Start drafting Story Map content

---

**Slide 11: Conclusion**
This project:

* Bridges theory and practice
* Builds on personal academic growth
* Has impact potential beyond class

**From static land values to dynamic ripple modeling.**
**From a class project to a planning tool.**
