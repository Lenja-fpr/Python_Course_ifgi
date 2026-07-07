import arcpy
import sys
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'C:\Users\Admin\Documents\Uni\PythonQGISArcGIS\Arcpy_Intro\Arcpy_Intro.gdb'
aprx = arcpy.mp.ArcGISProject("CURRENT")

# get the needed point layer
pointLayer = arcpy.GetParameterAsText(0)

# check if points have been selected
if int(arcpy.GetCount_management(pointLayer)[0]) == 0:
    arcpy.AddError("No points selected. Please select at least one point.")
    sys.exit()

# check for invalid geometries
geom_check = arcpy.management.CheckGeometry(pointLayer, r"in_memory\geom_check")
if int(arcpy.management.GetCount(geom_check)[0]) > 0:
    arcpy.AddError("The input point layer contains invalid geometries.")
    sys.exit()

# check if the projection is already correct, else change the projection to meters-based projection
target_sr = arcpy.SpatialReference(25832)

desc = arcpy.Describe(pointLayer)
sr = desc.spatialReference

if sr is None:
    arcpy.AddError("The input layer has no spatial reference.")
    sys.exit()

if sr.factoryCode != target_sr.factoryCode:
    arcpy.AddMessage("Reprojecting input points to EPSG:25832")
    points_projected = arcpy.management.Project(
        pointLayer,
        "pointLayer_projected",
        target_sr
    )[0]
else:
    arcpy.AddMessage("Input points already have the target projection")
    points_projected = arcpy.management.CopyFeatures(
        pointLayer,
        "pointLayer_projected"
    )[0]

# 
arcpy.management.Project(
    in_dataset = "stops_ms_mitte",
    out_dataset = "busstops_projected",
    out_coor_system = arcpy.SpatialReference(25832))

arcpy.management.Project(
    in_dataset = pointLayer,
    out_dataset = "pointLayer_projected",
    out_coor_system = arcpy.SpatialReference(25832))

# additional parameters (feature class to evaluate against, name field, name value) 
in_fc = arcpy.GetParameterAsText(0) # the clicked point (Feature Set)
near_fc = arcpy.GetParameterAsText(1) # feature class to evaluate against
name_field = arcpy.GetParameterAsText(2) # chosen field, e.g. "name"
name_value = arcpy.GetParameterAsText(3) # chosen value, e.g. "Wilhelmstraße"

# build a layer from the feature class to evaluate against with the field name and field value
sql = f"{name_field} = '{name_value}'" 
arcpy.management.MakeFeatureLayer(near_fc, "near_lyr", sql)

# find the nearest bus stop for every point of the input feature class
arcpy.analysis.Near(points_projected, "near_lyr", distance_unit="Meters")

# get distance and ID of the identified stops
with arcpy.da.SearchCursor(points_projected, ["NEAR_DIST", "NEAR_FID"]) as cur:
    for row in cur:
        distance = row[0] # distance to the closest bus stop
        near_fid = row[1] # ObjectID of said bus stop
        
# get the name of the bus stops via the ObjectID
where = f"OBJECTID = {near_fid}"
with arcpy.da.SearchCursor("busstops_projected", ["OBJECTID", "name"], where) as cur:
    for row in cur:
        stop_name = row[1]

# print results to the geoprocessing window
arcpy.AddMessage(f"Distance: {round(distance, 0)} Meters")
arcpy.AddMessage(f"Nearest stop: {stop_name}")