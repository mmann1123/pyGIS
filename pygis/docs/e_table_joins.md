---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
html_meta:
  "description lang=en": "Learn all about how to join two tables by their attribute values."
  "keywords": "table, attribute, join"
  "property=og:locale": "en_US"
---


----------------
```{admonition} Learning Objectives
* Understand various types of table join relationships
* Recognize different types of table joins
* Understand how table relationships can affect a table join
```
----------------

# Join by Attributes

To join attributes from two tables together, attributes from the first table (join or source table) are appended to the attributes in the second table (target table) based on a matching attribute. [^bolstad] This is also known as a table join.

```{figure} ../_static/img/join_tables.jpg
:name: Joining Two Tables
In a table join, attributes from the first table are appended to the attributes in the second table based on a matching attribute.
```

In assessing matching attributes, a column in the target table (called the *primary key*) is compared to a column in the other table (called the *foreign key*). If a value in one column is found as a value in the other table, the corresponding rows are matched and the attributes of the join table are added to the target table. The resulting table combines the attributes for rows that have been matched.

```{admonition} Definitions
A *primary key* is a column that uniquely distinguishes or identifies each row in a table; this means that each value in the column should not be repeated. A primary key can also be a series of columns (usually two or three), which is referred to as a *concatenated key*. A *foreign key* is a column that uniquely identifies rows in another table. [^bolstad]
```

In assessing matching attributes, a column in the target table (called the “primary key”) is compared to a column in the other table (called the “foreign key”). If a value in one column is found as a value in the other table, the corresponding rows are matched and the attributes of the join table are added to the target table. The resulting table combines the attributes for rows that have been matched.

These are non-spatial joins. The spatial locations of the geometries do not factor into what gets joined (see [chapter for spatial joins](e_spatial_joins.md)).

```{tip}
Most problems arise in creating unique primary and foreign keys that match. If you are having trouble, first make sure your columns are the same data type using `table_name.dtypes`. It is often helpful to append multiple columns of sub-codes together to create one unique key. To help with this you can use `.zfill()` to add leading zeros to code strings to ensure all column elements are of the same length.
```

Table joins can be conducted in Python using `geopandas` or `pandas`.

## Table Join Types

There are many types of table joins, including outer join, inner join, left join, right join, and cross join. These join types determine how and which records from both tables are kept in the resulting output table.

Only the inner, left, and right join types are available in the `geopandas` module and are identical to those in `pandas`. [^gpd_merge]

```{figure} ../_static/img/join_types.jpg
:name: Join Types
Four types of table joins are shown. These Venn diagrams depict which features from both datasets are kept when they are joined together for each join type.
```

### Outer join

All records from both tables are kept, regardless if records from either table have a match. As all attribute fields are combined, records that do not have a match may have null values in the fields that originated from the other table. [^bolstad]

### Inner join

Only records from both tables that have one or more matches are kept in the output table. [^bolstad]

### Left join

All records from the first or left table are kept, regardless if a record in the left table matches with records in the right table. As all attribute fields are combined, records that do not have a match in the right table may have null values in the fields that originated from the right table. [^pd_join]

### Right join

All records from the second or right table are kept, regardless if a record in the right table matches with records in the left table. As all attribute fields are combined, records that do not have a match in the left table may have null values in the fields that originated from the left table. [^pd_join]

```{hint}
A *left join* with Table 1 as the left table and Table 2 as the right table is the same as a *right* join with Table 2 as the left table and Table 1 as the right table.
```

### Cross join

Each record in one table is combined with each record in the second table. The total number of rows in the output table will be the product of the number of rows in each input table. [^bolstad]

```{figure} ../_static/img/join_cross.jpg
:name: Cross Join
In a cross join, all records in one table are combined with all records in the other table.
```

```{admonition} Example
A cross joined can be used if you, for example, have a table listing five products and their prices and a second table of the 50 states and their sales taxes. You could conduct a cross join to calculate the total price (including tax) of each product in each state. [^psu] The total number of rows in the output table will be 250 (5 rows times 50 rows).
```

```{warning}
Different software and programs may not necessarily use the same nomenclature or may perform table joins differently than as specified above. It is important to examine the input tables and the resulting output table to ensure that a join meets your expectations. [^bolstad]
```

## Table Relationships

Table relationships, or cardinality, specify the direction of the join and the relationship between the two tables. There are four types of table relationships: one-to-one, one-to-many, many-to-one, and many-to-many. While these relationships are not specified as a parameter in `geopandas` or `pandas`, it is important to have a general idea of the table relationship between two tables. Generally, a many-to-one join and a many-to-many join should be avoided because it can create ambiguity and unpredictability when analyzing and manipulating the resulting attribute table. [^bolstad], [^esri_cardinality]

### One-to-one relationship

Each record in one table is linked to one (and only one) record in the second table (and vice versa). Each record in both tables will appear only once at most. [^bolstad]

```{figure} ../_static/img/relationship_one_to_one.jpg
:name: One-to-One Relationship
Two joined tables have a one-to-one relationship when each record in one table is linked to one (and only one) record in the second table.
```

### One-to-many relationship or many-to-one relationship

Each record in one table is linked to one or more records in the second table. The output table may see the unique “one” record duplicated across multiple rows to accommodate its multiple linkages in the other table (the “many”). A one-to-many or many-to-one relationship can be dependent on the spatial join type (for example, if a left join results in a one-to-many relationship, then a right join will result in a many-to-one relationship). [^bolstad]

```{warning}
These two table relationships—while similar—are not the same! In a one-to-many relationship, the “many” table is being joined to. Alternatively, in a many-to-one relationship, the “one” table is being joined to. Thus, a many-to-one relationship can result in duplicate “one” records and create uncertainty, which is why a many-to-one join should be avoided. [^bolstad]
```

```{figure} ../_static/img/relationship_one_to_many.jpg
:name: One-to-Many Relationship
Two joined tables have a one-to-many relationship when each record in one table is linked to one or more records in the second table.
```

### Many-to-many relationship

One or more records in one table are linked to one or more records in the second table. The output table may have multiple rows of each target and join record to accommodate the multiple linkages. This can create ambiguity—hence why a many-to-many join should be avoided. [^bolstad]

```{figure} ../_static/img/relationship_many_to_many.jpg
:name: Many-to-Many Relationship
Two joined tables have a many-to-many relationship when one or more records in one table are linked to one or more records in the second table.
```

```{tip}
To avoid a many-to-one join and a many-to-many join, the join should be based on a column that is (or could be) a primary key in the join table (the table that we are joining from). [^bolstad]
```

[^bolstad]: GIS Fundamentals: A First Text on Geographic Information Systems, 5th ed., Paul Bolstad
[^gpd_merge]: [Merging Data, GeoPandas](https://geopandas.org/docs/user_guide/mergingdata.html)
[^pd_join]: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html
[^psu]: https://www.e-education.psu.edu/spatialdb/l1_p4.html
[^esri_cardinality]: https://support.esri.com/en/other-resources/gis-dictionary/term/62dad394-3106-4eb7-a5d7-84fc6a1df79f
