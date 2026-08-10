# Calculate the distance from a given point to the next water body, return the distance and the name of the water
#imports
import arcpy

# input
selected_place = arcpy.GetParameterAsText(0)

# analysis
# get nearest water
arcpy.analysis.Near(
    in_features= selected_place,
    near_features="gsk3e_gewkz_line_breite",
    search_radius="1 Kilometers",
    location="LOCATION",
    angle="NO_ANGLE",
    method="PLANAR",
    field_names="NEAR_FID NEAR_FID;NEAR_DIST NEAR_DIST;NEAR_X NEAR_X;NEAR_Y NEAR_Y",
    distance_unit="Meters"
)

# get datails of the nearest water
with arcpy.da.SearchCursor(selected_place, ["NEAR_DIST", "NEAR_FID"]) as cur:
    for row in cur:
        distance = row[0] # distance to the closest water
        near_fid = row[1] # ObjectID of the closest water
        
where = f"FID = {near_fid}"

with arcpy.da.SearchCursor("gsk3e_gewkz_line_breite", ["FID", "GEWHNAME", "ST_BREITE"], where) as cur:
    for row in cur:
        nearestName = row[1]
        nearestWidth = row[2]

# output
arcpy.AddMessage(f"Nearest water: {nearestName}")
arcpy.AddMessage(f"Distance to the nearest Water: {distance}")
arcpy.AddMessage(f"Witdh of the nearest Water: {nearestWidth}m")