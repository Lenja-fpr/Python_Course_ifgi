# Calculate the distance from a given point to the next water body, return the distance and the name of the water
#imports
import arcpy
import requests

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

# Get water level data from the nearest river via an API
#river = nearestName.upper()
river = "RHEIN" # delete this later when the API stuff below is fully implemented

# check if the API responds
response = requests.get(f"https://pegelonline.wsv.de/webservices/rest-api/v2/stations.json")
json_data = response.json() if response and response.status_code == 200 else None
if json_data:
    # check if threre is data available for the nearest river
    response = requests.get(f"https://pegelonline.wsv.de/webservices/rest-api/v2/stations.json?waters={river}")
    json_data = response.json() if response and response.status_code == 200 else None
    if json_data:
        arcpy.AddMessage(f"API data available for river {river}")
        # TODO find nearest station for the river in question
        # store its uuid in variable "station_id"
    else:
        arcpy.AddMessage(f"No water levels available for {river} via this API.")
        # TODO find nearest measuring station of any river
        # store its uuid in variable "station_id"
        # print(f"The nearest measuring station is {station}, measuring the water levels of {its river}.")

    station_id = "b475386c-30cc-453a-b3b7-1d17ace13595" # static id for now

    # check if measurements are available for this station
    response = requests.get(f"https://pegelonline.wsv.de/webservices/rest-api/v2/stations/{station_id}.json?includeTimeseries=true&includeCurrentMeasurement=true")
    json_data = response.json() if response and response.status_code == 200 else None
    if json_data:
        # print water level info
        arcpy.AddMessage(f"""Water level of the river {json_data['water']['longname']} 
            in {json_data['longname']} 
            at {json_data['timeseries'][0]['currentMeasurement']['timestamp']}: 
            {json_data['timeseries'][0]['currentMeasurement']['value']}{json_data['timeseries'][0]['unit']},
            which is {json_data['timeseries'][0]['currentMeasurement']['stateMnwMhw']} for this river.""")
            # TODO add average
            # TODO add time series image of the past 15 days water levels
            # TODO add forecast
    else: arcpy.AddMessage("No water level data available for this station right now.")

else: arcpy.AddMessage("No water levels API response.")