import arcpy
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'C:\Users\Admin\Documents\Uni\PythonQGISArcGIS\Arcpy_Intro\Arcpy_Intro.gdb'
aprx = arcpy.mp.ArcGISProject("CURRENT")

##get the needed point layer
pointLayer = arcpy.GetParameterAsText(0)

## change the projection to meters-based projection
arcpy.management.Project(
    in_dataset = "stops_ms_mitte",
    out_dataset = "busstops_projected",
    out_coor_system = arcpy.SpatialReference(25832))

arcpy.management.Project(
    in_dataset = pointLayer,
    out_dataset = "pointLayer_projected",
    out_coor_system = arcpy.SpatialReference(25832))

# find the nearest bus stop for every point of the input feature class
arcpy.analysis.Near("pointLayer_projected", "busstops_projected", distance_unit = "Meters")

# get distance and ID of the identified stops
with arcpy.da.SearchCursor("pointLayer_projected", ["NEAR_DIST", "NEAR_FID"]) as cur:
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