import arcpy
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'C:\Users\Admin\Documents\Uni\PythonQGISArcGIS\Arcpy_Intro\Arcpy_Intro.gdb'

# find the nearest bus stop for every point of the input feature class
arcpy.analysis.Near("input10_fc", "stops_ms_mitte_2", distance_unit = "Meters")

# get distance and ID of the identified stops
with arcpy.da.SearchCursor("input10_fc", ["NEAR_DIST", "NEAR_FID"]) as cur:
    for row in cur:
        distance = row[0] # distance to the closest bus stop
        near_fid = row[1] # ObjectID of said bus stop
        
# get the name of the bus stops via the ObjectID
where = f"OBJECTID = {near_fid}"
with arcpy.da.SearchCursor("stops_ms_mitte_2", ["OBJECTID", "name"], where) as cur:
    for row in cur:
        stop_name = row[1]

# print results to the geoprocessing window
arcpy.AddMessage(f"Distance: {round(distance, 0)} Meters")
arcpy.AddMessage(f"Nearest stop: {stop_name}")