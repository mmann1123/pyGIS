---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Time Series Analysis with Census Data

This tutorial demonstrates how to conduct time series analysis using US Census data, with a focus on comparing decennial census years and handling changing geographic boundaries over time.


## Getting started with pytidycensus

To get started with `pytidycensus`, users should install the package and load it in their Python environment. They'll also need to set their Census API key. API keys can be obtained at [https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html). After you've signed up for an API key, be sure to activate the key from the email you receive from the Census Bureau so it works correctly.


```{code-cell} ipython3
:tags: [skip-execution]

import pytidycensus as tc

tc.set_census_api_key("YOUR_API_KEY")
```


```{code-cell} ipython3
:tags: ["hide-cell"]
# ignore this, I am just reading in my api key privately
import yaml
import os
import pytidycensus as tc

def get_credentials():
    try:
        with open('credentials.yaml') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

creds = get_credentials()
api_key = creds.get('census_api_key') or os.environ.get('CENSUS_API_KEY')
tc.set_census_api_key(api_key)

```


## Overview

Time series analysis with Census data requires careful attention to:
1. **Data consistency** - comparing like-with-like across survey types
2. **Boundary changes** - census tracts and other geographies change over time
3. **Variable definitions** - ensuring variables measure the same concepts across years

## Survey Types and Temporal Comparability

### Rule 1: Compare Like Survey Types

**IMPORTANT**: Only compare surveys of the same type and duration:

- **ACS 1-year ↔ ACS 1-year**: For large areas (65,000+ population) with high temporal precision
- **ACS 3-year ↔ ACS 3-year**: Legacy surveys (discontinued after 2013)
- **ACS 5-year ↔ ACS 5-year**: For all areas, most stable estimates
- **Decennial ↔ Decennial**: Every 10 years, complete population count

### Why This Matters


``` python
# ❌ WRONG: Don't mix survey types
# This compares a 1-year snapshot to a 5-year average
acs1_2019 = tc.get_acs(geography="state", variables=["B19013_001E"], year=2019, survey="acs1")
acs5_2019 = tc.get_acs(geography="state", variables=["B19013_001E"], year=2019, survey="acs5")

# ✅ CORRECT: Compare same survey types across years
acs5_2015 = tc.get_acs(geography="state", variables=["B19013_001E"], year=2015, survey="acs5")
acs5_2020 = tc.get_acs(geography="state", variables=["B19013_001E"], year=2020, survey="acs5")
```

### Survey Characteristics

| Survey Type | Coverage | Sample Size | Margin of Error | Best For |
|-------------|----------|-------------|-----------------|----------|
| **Decennial** | Complete count | All households | Very low | Decade comparisons, small areas |
| **ACS 5-year** | Sample survey | ~3.5M addresses/year | Lower | Small geographies, stable trends |
| **ACS 1-year** | Sample survey | ~3.5M addresses | Higher | Large areas, recent estimates |

## Case Study: DC Population and Poverty Changes (2010-2020)

Let's analyze how Washington DC's population and poverty patterns changed between the 2010 and 2020 decennial censuses, accounting for tract boundary changes.

### Step 1: Load Required Libraries

```{code-cell} ipython3
import pytidycensus as tc
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Install tobler for area interpolation if not available
try:
    from tobler.area_weighted import area_interpolate
    print("✅ tobler available for area interpolation")
except ImportError:
    print("⚠️ Install tobler for area interpolation: pip install tobler")

# Set your Census API key
# tc.set_census_api_key("YOUR_API_KEY_HERE")
```

**Note on Data Availability**: Some older Tiger/Line shapefiles may have broken download links. If you encounter 404 errors for 2010 geometries, you can:
1. Use ACS data instead (more reliable geometry downloads)
2. Download geometries manually from [Census Tiger/Line files](https://www2.census.gov/geo/tiger/)
3. Focus on geographic levels that haven't changed (counties, states)

### Step 2: Understand Variable Changes Between Census Years

Census variables change between decennial years. Let's identify comparable variables:

```{code-cell} ipython3
# Search for population variables in both years
pop_2010_vars = tc.search_variables(pattern="total population", year=2010, dataset="decennial")
pop_2020_vars = tc.search_variables(pattern="total population", year=2020, dataset="decennial")

print("2010 Population Variables:")
print(pop_2010_vars[['name', 'label']].head())
print("\n2020 Population Variables:")
print(pop_2020_vars[['name', 'label']].head())
```

```{code-cell} ipython3
# For this analysis, we'll use:
# 2010: P001001 (Total population)
# 2020: P1_001N (Total population)
#
# Note: Poverty data is not available in decennial census
# We'll focus on population change and use ACS for poverty comparison
```

### Step 3: Get 2010 and 2020 Decennial Data with Geometry

```{code-cell} ipython3
# Get 2010 decennial data for DC tracts
dc_2010 = tc.get_decennial(
    geography="tract",
    variables={"total_pop": "P001001"},
    state="DC",
    year=2010,
    geometry=True,
    output="wide"
)

print(f"2010 DC Tracts: {len(dc_2010)} tracts")
print(f"2010 Total Population: {dc_2010['total_pop'].sum():,}")
print(dc_2010.head())
```

```{code-cell} ipython3
# Get 2020 decennial data for DC tracts
dc_2020 = tc.get_decennial(
    geography="tract",
    variables={"total_pop": "P1_001N"},
    state="DC",
    year=2020,
    geometry=True,
    output="wide"
)

print(f"2020 DC Tracts: {len(dc_2020)} tracts")
print(f"2020 Total Population: {dc_2020['total_pop'].sum():,}")
print(dc_2020.head())
```

### Step 4: Visualize Boundary Changes

```{code-cell} ipython3
# Create side-by-side maps to show boundary changes
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# 2010 tracts
dc_2010.plot(
    column='total_pop',
    cmap='viridis',
    legend=True,
    ax=ax1,
    edgecolor='white',
    linewidth=0.5
)
ax1.set_title('DC Census Tracts 2010\nTotal Population', fontsize=14)
ax1.axis('off')

# 2020 tracts
dc_2020.plot(
    column='total_pop',
    cmap='viridis',
    legend=True,
    ax=ax2,
    edgecolor='white',
    linewidth=0.5
)
ax2.set_title('DC Census Tracts 2020\nTotal Population', fontsize=14)
ax2.axis('off')

plt.tight_layout()
plt.show()

# Show tract count differences
print(f"Tract count change: {len(dc_2020)} - {len(dc_2010)} = {len(dc_2020) - len(dc_2010)} tracts")
```

### Step 5: Area Interpolation for Boundary Changes

Since tract boundaries changed between 2010 and 2020, we need to interpolate data to enable direct comparison.

```{code-cell} ipython3
# Prepare data for interpolation
# Area interpolation requires consistent projections
dc_2010_proj = dc_2010.to_crs('EPSG:3857')  # Web Mercator for area calculations
dc_2020_proj = dc_2020.to_crs('EPSG:3857')

print("Coordinate Reference Systems:")
print(f"2010: {dc_2010_proj.crs}")
print(f"2020: {dc_2020_proj.crs}")
```

```{code-cell} ipython3
# Define intensive vs extensive variables
# Intensive: rates, densities, percentages (area-weighted average)
# Extensive: counts, totals (area-weighted sum)

extensive_variables = ['total_pop']  # Population counts
intensive_variables = []  # We don't have rates in this decennial example

# Interpolate 2010 data to 2020 tract boundaries
dc_2010_interpolated = area_interpolate(
    source_df=dc_2010_proj,
    target_df=dc_2020_proj,
    intensive_variables=intensive_variables,
    extensive_variables=extensive_variables
)

print(f"Original 2010 population: {dc_2010['total_pop'].sum():,}")
print(f"Interpolated 2010 population: {dc_2010_interpolated['total_pop'].sum():,.0f}")
print(f"Difference: {abs(dc_2010['total_pop'].sum() - dc_2010_interpolated['total_pop'].sum()):,.0f}")
```

### Step 6: Calculate Population Change

```{code-cell} ipython3
# Merge interpolated 2010 data with 2020 geometries
dc_change = dc_2020_proj.copy()
dc_change['pop_2010_interpolated'] = dc_2010_interpolated['total_pop']
dc_change['pop_2020'] = dc_2020_proj['total_pop']

# Calculate change metrics
dc_change['pop_change_abs'] = dc_change['pop_2020'] - dc_change['pop_2010_interpolated']
dc_change['pop_change_pct'] = ((dc_change['pop_2020'] - dc_change['pop_2010_interpolated']) /
                               dc_change['pop_2010_interpolated'] * 100)

# Handle division by zero
dc_change['pop_change_pct'] = dc_change['pop_change_pct'].replace([np.inf, -np.inf], np.nan)

print("Population Change Summary:")
print(f"Total 2010 (interpolated): {dc_change['pop_2010_interpolated'].sum():,.0f}")
print(f"Total 2020: {dc_change['pop_2020'].sum():,.0f}")
print(f"Net change: {dc_change['pop_change_abs'].sum():,.0f}")
print(f"Percent change: {(dc_change['pop_change_abs'].sum() / dc_change['pop_2010_interpolated'].sum() * 100):.1f}%")
```

### Step 7: Visualize Population Change

```{code-cell} ipython3
# Create change visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))

# 2010 population (interpolated to 2020 boundaries)
dc_change.to_crs('EPSG:4326').plot(
    column='pop_2010_interpolated',
    cmap='Blues',
    legend=True,
    ax=ax1,
    edgecolor='white',
    linewidth=0.3
)
ax1.set_title('2010 Population\n(Interpolated to 2020 Boundaries)', fontsize=12)
ax1.axis('off')

# 2020 population
dc_change.to_crs('EPSG:4326').plot(
    column='pop_2020',
    cmap='Blues',
    legend=True,
    ax=ax2,
    edgecolor='white',
    linewidth=0.3
)
ax2.set_title('2020 Population', fontsize=12)
ax2.axis('off')

# Absolute change
dc_change.to_crs('EPSG:4326').plot(
    column='pop_change_abs',
    cmap='RdBu_r',
    legend=True,
    ax=ax3,
    edgecolor='white',
    linewidth=0.3,
    vmin=-2000,
    vmax=2000
)
ax3.set_title('Population Change (Absolute)\n2010-2020', fontsize=12)
ax3.axis('off')

# Percent change
dc_change_clean = dc_change.dropna(subset=['pop_change_pct'])
dc_change_clean.to_crs('EPSG:4326').plot(
    column='pop_change_pct',
    cmap='RdBu_r',
    legend=True,
    ax=ax4,
    edgecolor='white',
    linewidth=0.3,
    vmin=-50,
    vmax=50
)
ax4.set_title('Population Change (Percent)\n2010-2020', fontsize=12)
ax4.axis('off')

plt.tight_layout()
plt.show()
```

### Step 8: Add Poverty Analysis Using ACS Data

Since poverty data isn't available in the decennial census, let's use ACS 5-year data for a complementary analysis:

```{code-cell} ipython3
# Get ACS poverty data for comparison years
# Use 2010-2014 ACS vs 2016-2020 ACS for temporal separation

dc_poverty_2012 = tc.get_acs(
    geography="tract",
    variables={
        "poverty_count": "B17001_002E",
        "poverty_total": "B17001_001E"
    },
    state="DC",
    year=2012,  # 2008-2012 ACS 5-year
    survey="acs5",
    geometry=True,
    output="wide"
)

dc_poverty_2020 = tc.get_acs(
    geography="tract",
    variables={
        "poverty_count": "B17001_002E",
        "poverty_total": "B17001_001E"
    },
    state="DC",
    year=2020,  # 2016-2020 ACS 5-year
    survey="acs5",
    geometry=True,
    output="wide"
)

# Calculate poverty rates
dc_poverty_2012['poverty_rate'] = (dc_poverty_2012['poverty_count'] /
                                   dc_poverty_2012['poverty_total'] * 100)
dc_poverty_2020['poverty_rate'] = (dc_poverty_2020['poverty_count'] /
                                   dc_poverty_2020['poverty_total'] * 100)

print("Poverty Data Summary:")
print(f"2012 ACS - Tracts: {len(dc_poverty_2012)}, Avg Poverty Rate: {dc_poverty_2012['poverty_rate'].mean():.1f}%")
print(f"2020 ACS - Tracts: {len(dc_poverty_2020)}, Avg Poverty Rate: {dc_poverty_2020['poverty_rate'].mean():.1f}%")
```

```{code-cell} ipython3
# Interpolate 2012 poverty data to 2020 boundaries
dc_poverty_2012_proj = dc_poverty_2012.to_crs('EPSG:3857')
dc_poverty_2020_proj = dc_poverty_2020.to_crs('EPSG:3857')

# For poverty analysis:
# poverty_count, poverty_total are extensive (counts)
# poverty_rate is intensive (rate)
extensive_vars_poverty = ['poverty_count', 'poverty_total']
intensive_vars_poverty = ['poverty_rate']

dc_poverty_2012_interpolated = area_interpolate(
    source_df=dc_poverty_2012_proj,
    target_df=dc_poverty_2020_proj,
    intensive_variables=intensive_vars_poverty,
    extensive_variables=extensive_vars_poverty
)

print("Interpolation Check:")
print(f"Original 2012 poverty count: {dc_poverty_2012['poverty_count'].sum():,.0f}")
print(f"Interpolated 2012 poverty count: {dc_poverty_2012_interpolated['poverty_count'].sum():,.0f}")
```

```{code-cell} ipython3
# Calculate poverty change
dc_poverty_change = dc_poverty_2020_proj.copy()
dc_poverty_change['poverty_rate_2012'] = dc_poverty_2012_interpolated['poverty_rate']
dc_poverty_change['poverty_rate_2020'] = dc_poverty_2020_proj['poverty_rate']
dc_poverty_change['poverty_change'] = (dc_poverty_change['poverty_rate_2020'] -
                                       dc_poverty_change['poverty_rate_2012'])

# Create poverty change visualization
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 8))

# 2012 poverty rates
dc_poverty_change.to_crs('EPSG:4326').plot(
    column='poverty_rate_2012',
    cmap='Reds',
    legend=True,
    ax=ax1,
    edgecolor='white',
    linewidth=0.3,
    vmin=0,
    vmax=40
)
ax1.set_title('Poverty Rate 2012\n(2008-2012 ACS 5-year)', fontsize=12)
ax1.axis('off')

# 2020 poverty rates
dc_poverty_change.to_crs('EPSG:4326').plot(
    column='poverty_rate_2020',
    cmap='Reds',
    legend=True,
    ax=ax2,
    edgecolor='white',
    linewidth=0.3,
    vmin=0,
    vmax=40
)
ax2.set_title('Poverty Rate 2020\n(2016-2020 ACS 5-year)', fontsize=12)
ax2.axis('off')

# Poverty change
dc_poverty_change.to_crs('EPSG:4326').plot(
    column='poverty_change',
    cmap='RdBu_r',
    legend=True,
    ax=ax3,
    edgecolor='white',
    linewidth=0.3,
    vmin=-15,
    vmax=15
)
ax3.set_title('Poverty Rate Change\n2012 to 2020 (percentage points)', fontsize=12)
ax3.axis('off')

plt.tight_layout()
plt.show()

print(f"Average poverty rate change: {dc_poverty_change['poverty_change'].mean():.1f} percentage points")
print(f"Tracts with decreasing poverty: {(dc_poverty_change['poverty_change'] < 0).sum()}")
print(f"Tracts with increasing poverty: {(dc_poverty_change['poverty_change'] > 0).sum()}")
```

## Key Insights and Best Practices

### 1. Area Interpolation Results
- **Population Conservation**: Interpolation preserves total population counts across boundary changes
- **Spatial Accuracy**: Provides more accurate comparisons than ignoring boundary changes
- **Variable Types**: Properly handles extensive (counts) vs intensive (rates) variables

### 2. Temporal Analysis Guidelines

```{code-cell} ipython3
# Summary statistics for our analysis
print("=== DECENNIAL POPULATION CHANGE (2010-2020) ===")
print(f"Total population change: {dc_change['pop_change_abs'].sum():,.0f}")
print(f"Percent population change: {(dc_change['pop_change_abs'].sum() / dc_change['pop_2010_interpolated'].sum() * 100):.1f}%")
print(f"Tracts with population growth: {(dc_change['pop_change_abs'] > 0).sum()}")
print(f"Tracts with population decline: {(dc_change['pop_change_abs'] < 0).sum()}")

print(f"\n=== ACS POVERTY RATE CHANGE (2012-2020) ===")
print(f"Average poverty rate change: {dc_poverty_change['poverty_change'].mean():.1f} percentage points")
print(f"Tracts with poverty reduction: {(dc_poverty_change['poverty_change'] < 0).sum()}")
print(f"Tracts with poverty increase: {(dc_poverty_change['poverty_change'] > 0).sum()}")
```

### 3. Technical Considerations

**Coordinate Reference Systems:**
- Use projected CRS (like EPSG:3857) for accurate area calculations
- Transform back to geographic CRS (EPSG:4326) for mapping

**Variable Classification:**
- **Extensive variables**: Counts, totals (population, households) - use area-weighted sums
- **Intensive variables**: Rates, densities, percentages - use area-weighted averages

**Data Quality:**
- Always check interpolation results for conservation of totals
- Handle edge cases (zero population, missing data)
- Document assumptions and limitations

### 4. Alternative Approaches

#### Simple County-Level Analysis (No Boundary Changes)

```{code-cell} ipython3
# For researchers who prefer simpler approaches or encounter data issues:

# Option 1: Use consistent geography (e.g., counties that don't change)
print("=== Simple County-Level Analysis ===")
dc_county_2010 = tc.get_decennial(
    geography="county",
    variables={"total_pop": "P001001"},
    state="DC",
    year=2010
)

dc_county_2020 = tc.get_decennial(
    geography="county",
    variables={"total_pop": "P1_001N"},
    state="DC",
    year=2020
)

print("County-level comparison (no interpolation needed):")
print(f"2010: {dc_county_2010.iloc[0]['total_pop']:,}")
print(f"2020: {dc_county_2020.iloc[0]['total_pop']:,}")
print(f"Change: {dc_county_2020.iloc[0]['total_pop'] - dc_county_2010.iloc[0]['total_pop']:,}")
print(f"Percent change: {((dc_county_2020.iloc[0]['total_pop'] - dc_county_2010.iloc[0]['total_pop']) / dc_county_2010.iloc[0]['total_pop'] * 100):.1f}%")
```

#### Multi-State Analysis for Pattern Detection

```{code-cell} ipython3
# Option 2: Compare multiple states to identify broader patterns
states = ["DC", "MD", "VA"]  # DC Metro area
state_changes = []

for state in states:
    try:
        pop_2010 = tc.get_decennial(
            geography="state",
            variables={"total_pop": "P001001"},
            state=state,
            year=2010
        )

        pop_2020 = tc.get_decennial(
            geography="state",
            variables={"total_pop": "P1_001N"},
            state=state,
            year=2020
        )

        change = pop_2020.iloc[0]['total_pop'] - pop_2010.iloc[0]['total_pop']
        pct_change = (change / pop_2010.iloc[0]['total_pop']) * 100

        state_changes.append({
            'State': pop_2010.iloc[0]['NAME'],
            'Pop_2010': pop_2010.iloc[0]['total_pop'],
            'Pop_2020': pop_2020.iloc[0]['total_pop'],
            'Change': change,
            'Pct_Change': pct_change
        })

    except Exception as e:
        print(f"Error processing {state}: {e}")

# Display results
if state_changes:
    df_changes = pd.DataFrame(state_changes)
    print("\nDC Metro Area Population Changes (2010-2020):")
    print(df_changes.to_string(index=False, formatters={
        'Pop_2010': '{:,}'.format,
        'Pop_2020': '{:,}'.format,
        'Change': '{:,}'.format,
        'Pct_Change': '{:.1f}%'.format
    }))
```

#### Using Census Relationship Files

```{code-cell} ipython3
# Option 3: Use crosswalk files (for advanced users)
print("Advanced Alternative: Census Bureau provides relationship files that map")
print("geographic changes between years:")
print("https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html")
print()
print("These files provide precise allocation ratios for:")
print("- Block to block relationships")
print("- Tract to tract relationships")
print("- County subdivision changes")
print()
print("Benefits:")
print("- Official Census Bureau methodology")
print("- Precise allocation weights")
print("- No need for geometric calculations")
```

## Conclusion

Time series analysis with Census data requires careful attention to:

1. **Survey Consistency**: Only compare like survey types (ACS5↔ACS5, Decennial↔Decennial)
2. **Boundary Changes**: Use area interpolation to handle changing geographies
3. **Variable Definitions**: Ensure variables measure the same concepts across years
4. **Methodological Documentation**: Clearly document interpolation assumptions

The `area_interpolate` function from the `tobler` package provides a robust solution for handling boundary changes, enabling accurate temporal comparisons of demographic trends.

### Next Steps

- Explore additional variables (housing, education, employment)
- Apply similar methods to other geographic areas
- Consider uncertainty and margins of error in trend analysis
- Validate results against known demographic trends

For more advanced spatial analysis techniques, see the [tobler documentation](https://pysal.org/tobler/) and [PySAL ecosystem](https://pysal.org/).