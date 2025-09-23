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
 
# Introduction to pytidycensus
    
`pytidycensus` is a Python package designed to facilitate the process of acquiring and working with US Census Bureau population data in Python.

This is a port of Kyle Walker's excelent [intro to tidycensus in R](https://walker-data.com/census-r/an-introduction-to-tidycensus.html) - he deserves the credit for this tutorial! I just converted it to Python.

The package has two primary goals: first, to make Census data available to Python users in a pandas-friendly format, helping kickstart the process of generating insights from US Census data. Second, the package streamlines the data wrangling process for spatial Census data analysts. With `pytidycensus`, Python users can request *geometry* along with attributes for their Census data, helping facilitate mapping and spatial analysis.

The US Census Bureau makes a wide range of datasets available through their APIs and other data download resources. `pytidycensus` focuses on a select number of datasets implemented in a series of core functions. These core functions include:

- `get_decennial()`, which requests data from the US Decennial Census APIs for 2000, 2010, and 2020.
- `get_acs()`, which requests data from the 1-year and 5-year American Community Survey samples. Data are available from the 1-year ACS back to 2005 and the 5-year ACS back to 2005-2009.
- `get_estimates()`, an interface to the Population Estimates APIs. These datasets include yearly estimates of population characteristics by state, county, and metropolitan area, along with components of change demographic estimates like births, deaths, and migration rates.

## Getting started with pytidycensus

To get started with `pytidycensus`, users should install the package and load it in their Python environment. They'll also need to set their Census API key. API keys can be obtained at [https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html). After you've signed up for an API key, be sure to activate the key from the email you receive from the Census Bureau so it works correctly.


```python
import pytidycensus as tc

tc.set_census_api_key("YOUR_API_KEY")
```

```{code-cell} ipython3
:tags: ["hide-cell"]
# ignore this, I am just reading in my api key privately
# Read API key from environment variable (for GitHub Actions)
import os
import pytidycensus as tc

# Try to get API key from environment 
api_key = os.environ.get('CENSUS_API_KEY')

# For documentation builds without a key, we'll mock the responses
try:
    tc.set_census_api_key(api_key)
    print("Using Census API key from environment")
except Exception:
    print("Using example API key for documentation")
    # This won't make real API calls during documentation builds
    tc.set_census_api_key("EXAMPLE_API_KEY_FOR_DOCS")
```

### Decennial Census

Once an API key is set, users can obtain decennial Census or ACS data with a single function call. Let's start with `get_decennial()`, which is used to access decennial Census data from the 2000, 2010, and 2020 decennial US Censuses.

To get data from the decennial US Census, users must specify a string representing the requested `geography`; a vector of Census variable IDs, represented by `variables`; or optionally a Census table ID, passed to `table`. The code below gets data on total population by state from the 2010 decennial Census.

```{code-cell} ipython3
import pytidycensus as tc

total_population_10 = tc.get_decennial(
    geography="state",
    variables="P001001",
    year=2010
)

print(total_population_10.head())
```

The function returns a pandas DataFrame with information on total population by state, and assigns it to the object `total_population_10`. Data for 2000 or 2020 can also be obtained by supplying the appropriate year to the `year` parameter.

#### Summary files in the decennial Census

By default, `get_decennial()` uses the argument `sumfile = "sf1"`, which fetches data from the decennial Census Summary File 1. This summary file exists for the 2000 and 2010 decennial US Censuses, and includes core demographic characteristics for Census geographies. 

2020 Decennial Census data are available from the PL 94-171 Redistricting summary file, which is specified with `sumfile = "pl"` and is also available for 2010. The Redistricting summary files include a limited subset of variables from the decennial US Census to be used for legislative redistricting. These variables include total population and housing units; race and ethnicity; voting-age population; and group quarters population. For example, the code below retrieves information on the American Indian & Alaska Native population by state from the 2020 decennial Census.

```{code-cell} ipython3
aian_2020 = tc.get_decennial(
    geography="state",
    variables="P1_005N",
    year=2020,
    sumfile="pl"
)

print(aian_2020.head())
```

The argument `sumfile = "pl"` is assumed (and in turn not required) when users request data for 2020 until more detailed files are released.

> **Note**: When users request data from the 2020 decennial Census, `get_decennial()` prints out a message alerting users that 2020 decennial Census data use *differential privacy* as a method to preserve confidentiality of individuals who responded to the Census. This can lead to inaccuracies in small area analyses using 2020 Census data and also can make comparisons of small counts across years difficult.

### American Community Survey

Similarly, `get_acs()` retrieves data from the American Community Survey. The ACS includes a wide variety of variables detailing characteristics of the US population not found in the decennial Census. The example below fetches data on the number of residents born in Mexico by state.

```{code-cell} ipython3
born_in_mexico = tc.get_acs(
    geography="state",
    variables="B05006_150",
    year=2020
)

print(born_in_mexico.head())
```

If the year is not specified, `get_acs()` defaults to the most recent five-year ACS sample. The data returned is similar in structure to that returned by `get_decennial()`, but includes an `estimate` column (for the ACS estimate) and `moe` column (for the margin of error around that estimate) instead of a `value` column. Different years and different surveys are available by adjusting the `year` and `survey` parameters. `survey` defaults to the 5-year ACS; however this can be changed to the 1-year ACS by using the argument `survey = "acs1"`. For example, the following code will fetch data from the 1-year ACS for 2019:

```{code-cell} ipython3
born_in_mexico_1yr = tc.get_acs(
    geography="state",
    variables="B05006_150",
    survey="acs1",
    year=2019
)

print(born_in_mexico_1yr.head())
```

Note the differences between the 5-year ACS estimates and the 1-year ACS estimates. For states with larger Mexican-born populations like Arizona, California, and Colorado, the 1-year ACS data will represent the most up-to-date estimates, albeit characterized by larger margins of error relative to their estimates. For states with smaller Mexican-born populations, the estimate might return `NaN`, Python's notation representing missing data. If you encounter this in your data's `estimate` column, it will generally mean that the estimate is too small for a given geography to be deemed reliable by the Census Bureau. In this case, only the states with the largest Mexican-born populations have data available for that variable in the 1-year ACS, meaning that the 5-year ACS should be used to make full state-wise comparisons if desired.

> **Note**: The regular 1-year ACS was not released in 2020 due to low response rates during the COVID-19 pandemic. The Census Bureau released a set of experimental estimates for the 2020 1-year ACS that are not available in pytidycensus. These estimates can be downloaded at [https://www.census.gov/programs-surveys/acs/data/experimental-data/1-year.html](https://www.census.gov/programs-surveys/acs/data/experimental-data/1-year.html).
 
Variables from the ACS detailed tables, data profiles, summary tables, comparison profile, and supplemental estimates are available through `pytidycensus`'s `get_acs()` function; the function will auto-detect from which dataset to look for variables based on their names. Alternatively, users can supply a table name to the `table` parameter in `get_acs()`; this will return data for every variable in that table. For example, to get all variables associated with table B01001, which covers sex broken down by age, from the 2016-2020 5-year ACS:

```{code-cell} ipython3
age_table = tc.get_acs(
    geography="state",
    table="B01001",
    year=2020
)

print(age_table.head())
```  

To find all of the variables associated with a given ACS table, `pytidycensus` downloads a dataset of variables from the Census Bureau website and looks up the variable codes for download. If the `cache_table` parameter is set to `True`, the function instructs `pytidycensus` to cache this dataset on the user's computer for faster future access. This only needs to be done once per ACS or Census dataset if the user would like to specify this option.

## Geography and variables in pytidycensus

The `geography` parameter in `get_acs()` and `get_decennial()` allows users to request data aggregated to common Census enumeration units. `pytidycensus` accepts enumeration units nested within states and/or counties, when applicable. Census blocks are available in `get_decennial()` but not in `get_acs()` as block-level data are not available from the American Community Survey. To request data within states and/or counties, state and county names can be supplied to the `state` and `county` parameters, respectively.

Here's a table of commonly used geographies:

| Geography | Definition | Available by | Available in |
|-----------|------------|--------------|--------------|
| `"us"` | United States | | `get_acs()`, `get_decennial()`, `get_estimates()` |
| `"region"` | Census region | | `get_acs()`, `get_decennial()`, `get_estimates()` |
| `"division"` | Census division | | `get_acs()`, `get_decennial()`, `get_estimates()` |
| `"state"` | State or equivalent | state | `get_acs()`, `get_decennial()`, `get_estimates()` |
| `"county"` | County or equivalent | state, county | `get_acs()`, `get_decennial()`, `get_estimates()` |
| `"county subdivision"` | County subdivision | **state**, county | `get_acs()`, `get_decennial()`, `get_estimates()` |
| `"tract"` | Census tract | **state**, county | `get_acs()`, `get_decennial()` |
| `"block group"` | Census block group | **state**, county | `get_acs()` (2013-), `get_decennial()` |
| `"block"` | Census block | **state**, **county** | `get_decennial()` |
| `"place"` | Census-designated place | state | `get_acs()`, `get_decennial()`, `get_estimates()` |
| `"metropolitan statistical area/micropolitan statistical area"` OR `"cbsa"` | Core-based statistical area | state | `get_acs()`, `get_decennial()`, `get_estimates()` |
| `"zip code tabulation area"` OR `"zcta"` | Zip code tabulation area | state | `get_acs()`, `get_decennial()` |

The geography parameter must be typed exactly as specified in the table above to request data correctly from the Census API. For core-based statistical areas and zip code tabulation areas, two heavily-requested geographies, the aliases `"cbsa"` and `"zcta"` can be used, respectively, to fetch data for those geographies.

```{code-cell} ipython3
cbsa_population = tc.get_acs(
    geography="cbsa",
    variables="B01003_001",
    year=2020
)

print(cbsa_population.head())
```

### Geographic subsets

For many geographies, `pytidycensus` supports more granular requests that are subsetted by state or even by county, if supported by the API. If a geographic subset is in bold in the table above, it is required; if not, it is optional.

For example, an analyst might be interested in studying variations in household income in the state of Wisconsin. Although the analyst *can* request all counties in the United States, this is not necessary for this specific task. In turn, they can use the `state` parameter to subset the request for a specific state.

```{code-cell} ipython3
wi_income = tc.get_acs(
    geography="county",
    variables="B19013_001",
    state="WI",
    year=2020
)

print(wi_income.head())
```

`pytidycensus` accepts state names (e.g. `"Wisconsin"`), state postal codes (e.g. `"WI"`), and state FIPS codes (e.g. `"55"`), so an analyst can use what they are most comfortable with.

Smaller geographies like Census tracts can also be subsetted by county. Given that Census tracts nest neatly within counties (and do not cross county boundaries), we can request all Census tracts for a given county by using the optional `county` parameter. Dane County, home to Wisconsin's capital city of Madison, is shown below. Note that the name of the county can be supplied as well as the FIPS code.

```{code-cell} ipython3
dane_income = tc.get_acs(
    geography="tract",
    variables="B19013_001",
    state="WI",
    county="Dane",
    year=2020
)

print(dane_income.head())
```

With respect to geography and the American Community Survey, users should be aware that whereas the 5-year ACS covers geographies down to the block group, the 1-year ACS only returns data for geographies of population 65,000 and greater. This means that some geographies (e.g. Census tracts) will never be available in the 1-year ACS, and that other geographies such as counties are only partially available. To illustrate this, we can check the number of rows in the object `wi_income`:

```{code-cell} ipython3
print(len(wi_income))
```

There are 72 rows in this dataset, one for each county in Wisconsin. However, if the same data were requested from the 2019 1-year ACS:

```{code-cell} ipython3
wi_income_1yr = tc.get_acs(
    geography="county",
    variables="B19013_001",
    state="WI",
    year=2019,
    survey="acs1"
)

print(len(wi_income_1yr))
```

There are fewer rows in this dataset, representing only the counties that meet the "total population of 65,000 or greater" threshold required to be included in the 1-year ACS data.

## Searching for variables in pytidycensus

One additional challenge when searching for Census variables is understanding variable IDs, which are required to fetch data from the Census and ACS APIs. There are thousands of variables available across the different datasets and summary files. To make searching easier for Python users, `pytidycensus` offers the `load_variables()` function. This function obtains a dataset of variables from the Census Bureau website and formats it for fast searching.

The function takes two required arguments: `year`, which takes the year or endyear of the Census dataset or ACS sample, and `dataset`, which references the dataset name. For the 2000 or 2010 Decennial Census, use `"sf1"` or `"sf2"` as the dataset name to access variables from Summary Files 1 and 2, respectively. For 2020, the only dataset supported at the time of this writing is `"pl"` for the PL-94171 Redistricting dataset.

For variables from the American Community Survey, users should specify the dataset as `"acs"` and survey as `"acs1"` for the 1-year ACS or `"acs5"` for the 5-year ACS. An example request would look like `load_variables(year=2020, dataset="acs", survey="acs5")` for variables from the 2020 5-year ACS Detailed Tables.

As this function requires processing thousands of variables from the Census Bureau which may take a few moments depending on the user's internet connection, the user can specify `cache=True` in the function call to store the data in the user's cache directory for future access.

An example of how `load_variables()` works is as follows:

```{code-cell} ipython3
v20 = tc.load_variables(2020, "acs", "acs5", cache=True)
print(v20.head())
```

The returned DataFrame has columns including: `name`, which refers to the Census variable ID; `label`, which is a descriptive data label for the variable; and `concept`, which refers to the topic of the data and often corresponds to a table of Census data.

`pytidycensus` also provides a convenient `search_variables()` function to help find specific variables:

```{code-cell} ipython3
# Search for income-related variables
income_vars = tc.search_variables("income", 2020, "acs", "acs5")
print(income_vars.head())
```

By browsing the table in this way, users can identify the appropriate variable IDs (found in the `name` column) that can be passed to the `variables` parameter in `get_acs()` or `get_decennial()`. Additionally, if users desire an entire table of related variables from the ACS, they can use the `get_table_variables()` function or pass the table prefix to the `table` parameter in the main functions.

## Data structure in pytidycensus

By default, `pytidycensus` returns a pandas DataFrame of ACS or decennial Census data. For decennial Census data, this will include columns:

- `GEOID`, representing the Census ID code that uniquely identifies the geographic unit;
- `NAME`, which represents a descriptive name of the unit;
- `variable`, which contains information on the Census variable name corresponding to that row;
- `value`, which contains the data values for each unit-variable combination. 

For ACS data, instead of a `value` column, there will be two columns: `estimate`, which represents the ACS estimate, and `moe`, representing the margin of error around that estimate.

By default, data is returned in a "tidy" format where each row represents a unique geography-variable combination. This is ideal for data analysis with pandas. Here's an example with income groups by state for the ACS:

```{code-cell} ipython3
hhinc = tc.get_acs(
    geography="state",
    table="B19001",
    survey="acs1",
    year=2019
)

print(hhinc.head())
```

In this example, each row represents state-characteristic combinations. Alternatively, if a user desires the variables spread across the columns of the dataset, the setting `output="wide"` will enable this. For ACS data, estimates and margins of error for each ACS variable will be found in their own columns. For example:

```{code-cell} ipython3
hhinc_wide = tc.get_acs(
    geography="state",
    table="B19001",
    survey="acs1",
    year=2019,
    output="wide"
)

print(hhinc_wide.head())
```

The wide-form dataset includes `GEOID` and `NAME` columns, as in the tidy dataset, but is also characterized by estimate/margin of error pairs across the columns for each Census variable in the table.

### Understanding GEOIDs

The `GEOID` column returned by default in `pytidycensus` can be used to uniquely identify geographic units in a given dataset. For geographies within the core Census hierarchy (Census block through state), GEOIDs can be used to uniquely identify specific units as well as units' parent geographies. Let's take the example of households by Census block from the 2020 Census in Cimarron County, Oklahoma.

```{code-cell} ipython3
cimarron_blocks = tc.get_decennial(
    geography="block",
    variables="H1_001N",
    state="OK",
    county="Cimarron",
    year=2020,
    sumfile="pl"
)

print(cimarron_blocks.head())
```

The mapping between the `GEOID` and `NAME` columns in the returned 2020 Census block data offers some insight into how GEOIDs work for geographies within the core Census hierarchy. Take the first block in the table, which might have a GEOID like **400259503001110**. The GEOID value breaks down as follows:

- The first two digits, **40**, correspond to the [Federal Information Processing Series (FIPS) code](https://www.census.gov/library/reference/code-lists/ansi.html) for the state of Oklahoma.
- Digits 3 through 5, **025**, are representative of Cimarron County.
- The next six digits, **950300**, represent the block's Census tract.
- The twelfth digit, **1**, represents the parent block group of the Census block.
- The last three digits, **110**, represent the individual Census block.

For geographies outside the core Census hierarchy, GEOIDs will uniquely identify geographic units but will only include IDs of parent geographies to the degree to which they nest within them.

### Renaming variable IDs

Census variables IDs can be cumbersome to type and remember. As such, `pytidycensus` has built-in tools to automatically rename the variable IDs if requested by a user. For example, let's say that a user is requesting data on median household income (variable ID `B19013_001`) and median age (variable ID `B01002_001`). By passing a *dictionary* to the `variables` parameter in `get_acs()` or `get_decennial()`, the functions will return the desired names rather than the Census variable IDs.

```{code-cell} ipython3
ga = tc.get_acs(
    geography="county",
    state="Georgia",
    variables={"medinc": "B19013_001", "medage": "B01002_001"},
    year=2020
)

print(ga.head())
```

ACS variable IDs, which would be found in the `variable` column, are replaced by `medage` and `medinc`, as requested. When a wide-form dataset is requested, `pytidycensus` will still append suffixes to the specified column names:

```{code-cell} ipython3
ga_wide = tc.get_acs(
    geography="county",
    state="Georgia",
    variables={"medinc": "B19013_001", "medage": "B01002_001"},
    output="wide",
    year=2020
)

print(ga_wide.head())
```

## Spatial data with pytidycensus

One of the most powerful features of `pytidycensus` is its ability to return geometry along with Census data, facilitating mapping and spatial analysis. To get geometry with your data, simply set the `geometry=True` parameter:

```{code-cell} ipython3
wi_income_geo = tc.get_acs(
    geography="county",
    variables="B19013_001",
    state="WI",
    year=2020,
    geometry=True
)

print(type(wi_income_geo))  # This will be a GeoDataFrame
wi_income_geo.head()
```

The returned object will be a GeoPandas GeoDataFrame, which can be used for mapping and spatial analysis. For example, you could create a simple choropleth map:

```{code-cell} ipython3
import matplotlib.pyplot as plt

# Plot the data (if using a Jupyter notebook, you might want to use %matplotlib inline)
fig, ax = plt.subplots(1, figsize=(10, 6))
wi_income_geo.plot(column='B19013_001E', cmap='viridis', legend=True, ax=ax)
ax.set_title('Median Household Income by County in Wisconsin')
plt.axis('off')
plt.show()
```

## Debugging pytidycensus errors

At times, you may think that you've formatted your use of a `pytidycensus` function correctly but the Census API doesn't return the data you expected. Whenever possible, `pytidycensus` carries through the error message from the Census API or translates common errors for the user.

To assist with debugging errors, or more generally to help users understand how `pytidycensus` functions are being translated to Census API calls, `pytidycensus` offers a parameter `show_call` that when set to `True` prints out the actual API call that `pytidycensus` is making to the Census API.

```{code-cell} ipython3
cbsa_bachelors = tc.get_acs(
    geography="cbsa",
    variables="DP02_0068P",
    year=2019,
    show_call=True
)
```

The printed URL can be copy-pasted into a web browser where users can see the raw JSON returned by the Census API and inspect the results.

## Conclusion

This introduction to `pytidycensus` has covered the basics of retrieving and working with Census data in Python. The package provides a convenient interface to access data from the US Census Bureau's APIs, with built-in support for spatial data analysis. For more information and examples, please refer to the examples directory and the package documentation.