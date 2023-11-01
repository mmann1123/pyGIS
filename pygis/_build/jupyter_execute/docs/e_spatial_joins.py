#!/usr/bin/env python
# coding: utf-8

# ----------------
# ```{admonition} Learning Objectives
# * Understand various types of spatial join relationships
# * Recognize different types of spatial joins
# * Understand how table relationships can affect a spatial join
# ```
# ----------------
# 
# # Spatial Joins
# 
# To spatially join one dataset to another, attributes from the first dataset (join feature) are appended to the attributes in the second dataset (target feature) based on the relative spatial relationship between the two datasets’ geometries. [^esri_join], [^gpd_merge]
# 
# ```{note}
# Unlike table joins by attributes, we’re not really concerned with the tables having a primary key (a column, or columns, that uniquely identifies each record in a table) to conduct a join. Instead, the relative spatial location between the features in two datasets will determine what gets joined.
# ```
# 
# This chapter will cover spatial join relationships, spatial join types, and attribute table relationships.
# 
# ## Spatial Join Relationships
# 
# There are multiple spatial join relationships that we can specify. Only the features that meet the specified spatial relationship criteria will be joined together. [^esri_join], [^gpd_merge] The spatial arrangement necessary to satisfy a specified spatial relationship depends on the vector types (i.e., point, line, polygon) of the join feature and the target feature. Note that some spatial relationships are not possible for certain combinations of vector types.
# 
# Below is a description of the spatial relationships available in the `geopandas` module (this list is not necessarily exhaustive). [^gpd_meerge] We also provide diagrams visualizing the spatial arrangement needed for various combinations of vector types to satisfy the spatial relationship criteria and allow for a join.
# 
# ### Contains
# 
# One feature contains another if the geometry’s points are not to the exterior of the other’s geometry and the geometry’s interior contains at least one point of the other geometry’s interior.
# 
# ```{figure} ../_static/img/overlay_contains.jpg
# :name: Contains
# Spatial arrangements for *contains* for different combinations of vector types.
# ```
# 
# ### Crosses
# 
# The geometry’s interior *crosses* that of the other geometry, provided that the geometry does not contain the other and the dimension of the intersection is less than the dimension of either geometry.
# 
# ```{figure} ../_static/img/overlay_crosses.jpg
# :name: Crosses
# Spatial arrangements for *crosses* for different combinations of vector types.
# ```
# 
# ### Intersects
# 
# A feature *intersects* another if the geometry’s boundary or interior has any part in common with the other geometry.
# 
# ```{figure} ../_static/img/overlay_intersects.jpg
# :name: Intersects
# Spatial arrangements for *intersects* for different combinations of vector types.
# ```
# 
# ### Overlaps
# 
# A feature *overlaps* another if the geometry shares at least one point, but not all points, with the other geometry, provided that the geometries and the intersection of their interiors all have the same dimensions.
# 
# ```{figure} ../_static/img/overlay_overlaps.jpg
# :name: Overlaps
# Spatial arrangements for *overlaps* for different combinations of vector types.
# ```
# 
# ### Touches
# 
# A feature *touches* another if the geometry shares at least one point with the other geometry, provided that no part of the geometry’s interior intersects with the other geometry.
# 
# ```{figure} ../_static/img/overlay_touches.jpg
# :name: Touches
# Spatial arrangements for *touches* for different combinations of vector types.
# ```
# 
# ### Within
# 
# A feature is *within* another if the geometry is enclosed in the other geometry (geometry’s boundary and interior intersects with the other geometry’s interior only).
# 
# ```{figure} ../_static/img/overlay_within.jpg
# :name: Within
# Spatial arrangements for *within* for different combinations of vector types.
# ```
# 
# ## Spatial Join Types
# 
# There are four types of spatial joins: outer join, inner join, left join, and right join. These spatial join types determine which features from both datasets are kept in the resulting output dataset.
# 
# ```{figure} ../_static/img/join_types.jpg
# :name: Join Types
# There are four types of spatial joins. These Venn diagrams depict which features from both datasets are kept when they are joined together for each join type.
# ```
# 
# Only the inner, left, and right join types are available in the `geopandas` module and are identical to those in `pandas`. [^gpd_merge]
# 
# ### Outer join
# 
# All features from both datasets are kept, regardless if the features meet the specified spatial relationship criteria for a join. As all attribute fields are combined, rows that do not have a match may have null values in the fields that originated from the other dataset. [^bolstad]
# 
# ### Inner join
# 
# Only features from both datasets that meet the spatial relationship for the joined are kept. The geometries from the first or left dataset are used for the join. [^bolstad]
# 
# ### Left join
# 
# All features from the first or left dataset are kept, regardless if the features meet the specified spatial relationship criteria for a join. As all attribute fields are combined, rows that do not have a match with the right dataset may have null values in the fields that originated from the right dataset.
# 
# ### Right join
# 
# All features from the second or right dataset are kept, regardless if the features meet the specified spatial relationship criteria for a join. As all attribute fields are combined, rows that do not have a match with the left dataset may have null values in the fields that originated from the left dataset.
# 
# For more details on join types, see the [chapter on joining by attributes](e_table_joins).
# 
# ## Table Relationships
# 
# Table relationships, or cardinality, specify the direction of the join and the relationship between the two datasets. There are four types of table relationships: one-to-one, one-to-many, many-to-one, and many-to-many. While these relationships are not specified as a parameter in the `geopandas` module when conducting a spatial join, it is important to have a general idea of the table relationship between the two datasets. Generally, a many-to-one join and a many-to-many join should be avoided because it can create ambiguity and unpredictability when analyzing and manipulating the resulting attribute table. [^bolstad]
# 
# ### One-to-one relationship
# 
# Each feature in one geometry is linked to one (and only one) feature in the second geometry (and vice versa). Each feature in both datasets will appear only once at most. [^bolstad]
# 
# ```{figure} ../_static/img/relationship_one_to_one.jpg
# :name: One-to-One Relationship
# Two joined tables have a one-to-one relationship when each feature in one geometry is linked to one (and only one) feature in the second geometry.
# ```
# 
# ### One-to-many relationship or many-to-one relationship
# 
# Each feature in one geometry is linked to one or more features in the second geometry. The output geometry may see the “one” feature duplicated across multiple rows to accommodate its multiple linkages in the other dataset (the “many”). A one-to-many or many-to-one relationship can be dependent on the spatial join type (for example, if a left join results in a one-to-many relationship, then a right join will result in a many-to-one relationship). [^bolstad]
# 
# ```{warning}
# These two table relationships—while similar—are not the same! In a one-to-many relationship, the “many” geometry is the dataset that is being joined to. Alternatively, in a many-to-one relationship, the “one” geometry is the dataset being joined to. Thus, the many-to-one relationship can result in duplicate “one” geometries and create uncertainty, which is why a many-to-one join should be avoided. [^bolstad]
# ```
# 
# ```{figure} ../_static/img/relationship_one_to_many.jpg
# :name: One-to-Many Relationship
# Two joined tables have a one-to-many relationship when each feature in one geometry is linked to one or more features in the second geometry.
# ```
# 
# ### Many-to-many relationship
# 
# One or more features in one geometry are linked to one or more features in the second geometry. The output geometry may have multiple rows of each target and join feature to accommodate the multiple linkages, which can create ambiguity—hence why a many-to-many join should be avoided. [^bolstad]
# 
# ```{figure} ../_static/img/relationship_many_to_many.jpg
# :name: Many-to-Many Relationship
# Two joined tables have a many-to-many relationship when one or more features in one geometry are linked to one or more features in the second geometry.
# ```
# 
# ```{tip}
# To ensure you’re doing a one-to-one or one-to-many join, it may be helpful to envision your spatial join before performing a spatial join. Think about what geometries you will be joining to (the target feature) and what geometry or geometries from the join feature might be joined to one geometry in the target feature.
# ```
# 
# 
# [^bolstad]: GIS Fundamentals: A First Text on Geographic Information Systems, 5th ed., Paul Bolstad
# [^gpd_merge]: [Merging Data, GeoPandas](https://geopandas.org/docs/user_guide/mergingdata.html)
# [^esri_join]: [Spatial Join (Analysis), Esri](https://pro.arcgis.com/en/pro-app/latest/tool-reference/analysis/spatial-join.htm)
