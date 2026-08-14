### --- imports ---
import arcpy
import requests
import os


### --- input ---
selected_place = arcpy.GetParameterAsText(0)


### --- Compare the selected place to the Floodrisk Map of NRW ---

# is the point inside an area with a high risk?
# check by using select by location
arcpy.management.SelectLayerByLocation(
    in_layer="ueberflutungsgrenzen_hohe_wahrscheinlichkeit",
    overlap_type="INTERSECT",
    select_features=selected_place,
    selection_type="NEW_SELECTION",
    invert_spatial_relationship="NOT_INVERT"
)
# check if a feature is selected
if int(arcpy.management.GetCount("ueberflutungsgrenzen_hohe_wahrscheinlichkeit")[0]) != 0:
    arcpy.AddMessage("The given place is located in an area with a high risk of flooding")

    # clear the selection
    arcpy.SelectLayerByAttribute_management("ueberflutungsgrenzen_hohe_wahrscheinlichkeit","CLEAR_SELECTION")

else:
    # is the point in an area with a middle risk?
    # check by using select by location
    arcpy.management.SelectLayerByLocation(
        in_layer="ueberflutungsgrenzen_mittlere_wahrscheinlichkeit",
        overlap_type="INTERSECT",
        select_features=selected_place,
        selection_type="NEW_SELECTION",
        invert_spatial_relationship="NOT_INVERT"
    )
    #check if a feature is selected
    if int(arcpy.management.GetCount("ueberflutungsgrenzen_mittlere_wahrscheinlichkeit")[0]) != 0:
        arcpy.AddMessage("The given place is located in an area with a moderate risk of flooding")
    
        #clear the selection
        arcpy.SelectLayerByAttribute_management("ueberflutungsgrenzen_mittlere_wahrscheinlichkeit","CLEAR_SELECTION")

    else:
        # is the point in an area with a low risk?
        #check by using select by location
        arcpy.management.SelectLayerByLocation(
            in_layer="ueberflutungsgrenzen_niedrige Wahrscheinlichkeit",
            overlap_type="INTERSECT",
            select_features=selected_place,
            selection_type="NEW_SELECTION",
            invert_spatial_relationship="NOT_INVERT"
        )
        #check if a feature is selected
        if int(arcpy.management.GetCount("ueberflutungsgrenzen_niedrige Wahrscheinlichkeit")[0]) != 0:
            arcpy.AddMessage("The given place is located in an area with a low risk of flooding")
            
            #clear the selection
            arcpy.SelectLayerByAttribute_management("ueberflutungsgrenzen_niedrige Wahrscheinlichkeit","CLEAR_SELECTION")

        else:
            # the point is in an area without a risk
            arcpy.AddMessage("The given place is located in an area without a risk of flooding (compared to the 'Hochwasser-Gefahrenkarte NRW')")


### --- find the nearest river ---
# get nearest river
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

# get datails of the nearest river
with arcpy.da.SearchCursor(selected_place, ["NEAR_DIST", "NEAR_FID"]) as cur:
    for row in cur:
        distance = row[0] # distance to the closest river
        near_fid = row[1] # ObjectID of the closest river
        
where = f"FID = {near_fid}"

with arcpy.da.SearchCursor("gsk3e_gewkz_line_breite", ["FID", "GEWHNAME", "ST_BREITE"], where) as cur:
    for row in cur:
        nearestName = row[1]
        nearestWidth = row[2]

# output
arcpy.AddMessage(f"Nearest river: {nearestName}")
arcpy.AddMessage(f"Distance to the nearest river: {distance}")
arcpy.AddMessage(f"Witdh of the nearest river: {nearestWidth}m")


# -------- Get water level data from the nearest river via an API ---------------

river = nearestName.upper()

# handle Umlaute in the river name for the API request
if "Ä" in river:
    river = river.replace("Ä", "%C3%84")
if "Ö" in river:
    river = river.replace("Ö", "%C3%96")
if "Ü" in river:
    river = river.replace("Ü", "%C3%9C")
    
# hande spaces:
if " " in river:
    river = river.replace(" ", "%20")


# function to find the nearest measuring station to a given point from a json list of stations 
def findNearestStation(json):
    # collect the uuids, names and coordinates of all stations in a list
    stations_list = []
    for station in json:
        if 'longitude' in station:
            uuid = station['uuid']
            name = station['longname']
            lon = station['longitude']
            lat = station['latitude']
            stations_list.append([uuid, name, (lon, lat)])
        
    # add the measuring stations to a feature class and add it to the map:
    # get the currently active geodatabase
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    map_obj = aprx.activeMap
    gdb = aprx.defaultGeodatabase
    fc_path = os.path.join(gdb, "measuring_stations")
    # create a new featureclass (overwrite if it already exists)
    for layer in map_obj.listLayers():
        if layer.name == "measuring_stations":
            if layer.isFeatureLayer:
                layer_path = layer.dataSource
            if os.path.normcase(layer_path) == os.path.normcase(fc_path):
                map_obj.removeLayer(layer)
                #del layer
    if arcpy.Exists(fc_path):
        arcpy.management.Delete(fc_path)
    arcpy.management.CreateFeatureclass(gdb, "measuring_stations", "POINT", spatial_reference=arcpy.SpatialReference(4326))
    # add fields to the featureclass
    arcpy.management.AddField("measuring_stations", "uuid", "TEXT")
    arcpy.management.AddField("measuring_stations", "name", "TEXT")
    
    # fill the featureclass with the data from the table
    with arcpy.da.InsertCursor(fc_path, ["uuid", "name", "SHAPE@XY"]) as cursor:
        for uuid, name, coordinates in stations_list:
            cursor.insertRow([uuid, name, coordinates])
    
    # find nearest station
    arcpy.analysis.Near(
        in_features=selected_place,
        near_features="measuring_stations",
        location="LOCATION",
        angle="NO_ANGLE",
        method="PLANAR",
        field_names="NEAR_FID NEAR_FID;NEAR_DIST NEAR_DIST;NEAR_X NEAR_X;NEAR_Y NEAR_Y",
        distance_unit="Meters"
    )

    # get details of the nearest station
    with arcpy.da.SearchCursor(
        selected_place,
        ["NEAR_DIST", "NEAR_FID"]
    ) as cur:

        for row in cur:
            distance = row[0]
            near_fid = row[1]

    # get the actual ObjectID field name of measuring_stations
    oid_field = arcpy.Describe("measuring_stations").OIDFieldName

    # find the station with the corresponding ObjectID
    where = f"{arcpy.AddFieldDelimiters('measuring_stations', oid_field)} = {near_fid}"

    with arcpy.da.SearchCursor(
        "measuring_stations",
        [oid_field, "uuid", "name"],
        where
    ) as cur:

        for row in cur:
            uuid = row[1]
            station_name = row[2]
 
    # output
    arcpy.AddMessage(f"Distance to station: {distance} m")
    arcpy.AddMessage(f"Station name: {station_name}")
    station_id = uuid
    return station_id



# check if the API responds
response = requests.get(f"https://pegelonline.wsv.de/webservices/rest-api/v2/stations.json")
json_data = response.json() if response and response.status_code == 200 else None
if json_data:
    # check if threre is data available for the nearest river
    response = requests.get(f"https://pegelonline.wsv.de/webservices/rest-api/v2/stations.json?waters={river}")
    json_river_data = response.json() if response and response.status_code == 200 else None
    if not json_river_data:
        arcpy.AddMessage(f"No water levels available for the river {nearestName} via pegelonline API. The following water level data was measured at the nearest measuring station of any river:")
        # find the nearest measuring station of any river and store its uuid in variable "station_id"
        station_id = findNearestStation(json_data)
    else:
        # find the nearest station for the river in question store its uuid in variable "station_id"
        station_id = findNearestStation(json_river_data)

    # check if measurements are available for this station
    response = requests.get(f"https://pegelonline.wsv.de/webservices/rest-api/v2/stations/{station_id}.json?includeTimeseries=true&includeCurrentMeasurement=true")
    json_data = response.json() if response and response.status_code == 200 else None
    if json_data:
        # print water level info
        arcpy.AddMessage(f"""Water levels for the river {json_data['water']['longname']} 
            in {json_data['longname']} 
            at {json_data['timeseries'][0]['currentMeasurement']['timestamp']}: 
            {json_data['timeseries'][0]['currentMeasurement']['value']}{json_data['timeseries'][0]['unit']}.""")
        if(('stateMnwMhw' in json_data['timeseries'][0]['currentMeasurement']) and (json_data['timeseries'][0]['currentMeasurement']['stateMnwMhw'] != "unknown")):
            arcpy.AddMessage(f"The current water level is {json_data['timeseries'][0]['currentMeasurement']['stateMnwMhw']} for this river.")
            # TODO add average
            # TODO add time series image of the past 15 days water levels
            # TODO add forecast
    else: arcpy.AddMessage("No water level data available for this station right now.") 

else: arcpy.AddMessage("No water levels API response.")
