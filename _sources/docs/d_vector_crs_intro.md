---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

(d_vector_crs_intro)=

# Vector CRS 
 
<!--
https://geocompr.robinlovelace.net/geometric-operations.html
 In this section we will learn how to reproject vector data:


 Affine transformation is any transformation that preserves lines and parallelism. However, angles or length are not necessarily preserved. Affine transformations include, among others, shifting (translation), scaling and rotation. Additionally, it is possible to use any combination of these. Affine transformations are an essential part of geocomputation. For example, shifting is needed for labels placement, scaling is used in non-contiguous area cartograms (see Section 8.6), and many affine transformations are applied when reprojecting or improving the geometry that was created based on a distorted or wrongly projected map. The sf package implements affine transformation for objects of classes sfg and sfc.

nz_sfc = st_geometry(nz)

Shifting moves every point by the same distance in map units. It could be done by adding a numerical vector to a vector object. For example, the code below shifts all y-coordinates by 100,000 meters to the north, but leaves the x-coordinates untouched (left panel of Figure 5.5).

nz_shift = nz_sfc + c(0, 100000)

Scaling enlarges or shrinks objects by a factor. It can be applied either globally or locally. Global scaling increases or decreases all coordinates values in relation to the origin coordinates, while keeping all geometries topological relations intact. It can be done by subtraction or multiplication of asfg or sfc object.

Local scaling treats geometries independently and requires points around which geometries are going to be scaled, e.g., centroids. In the example below, each geometry is shrunk by a factor of two around the centroids (middle panel in Figure 5.5). To achieve that, each object is firstly shifted in a way that its center has coordinates of 0, 0 ((nz_sfc - nz_centroid_sfc)). Next, the sizes of the geometries are reduced by half (* 0.5). Finally, each object’s centroid is moved back to the input data coordinates (+ nz_centroid_sfc).

nz_centroid_sfc = st_centroid(nz_sfc)
nz_scale = (nz_sfc - nz_centroid_sfc) * 0.5 + nz_centroid_sfc

Rotation of two-dimensional coordinates requires a rotation matrix:

R=[cosθ−sinθsinθcosθ]

It rotates points in a clockwise direction. The rotation matrix can be implemented in R as:

rotation = function(a){
  r = a * pi / 180 #degrees to radians
  matrix(c(cos(r), sin(r), -sin(r), cos(r)), nrow = 2, ncol = 2)
} 

The rotation function accepts one argument a - a rotation angle in degrees. Rotation could be done around selected points, such as centroids (right panel of Figure 5.5). See vignette("sf3") for more examples.

nz_rotate = (nz_sfc - nz_centroid_sfc) * rotation(30) + nz_centroid_sfc

Illustrations of affine transformations: shift, scale and rotate.

FIGURE 5.5: Illustrations of affine transformations: shift, scale and rotate.

Finally, the newly created geometries can replace the old ones with the st_set_geometry() function:

nz_scale_sf = st_set_geometry(nz, nz_scale) -->