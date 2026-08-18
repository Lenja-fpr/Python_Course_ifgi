### --- imports ---
import arcpy
import requests
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus.flowables import KeepTogether
from datetime import datetime
import matplotlib.pyplot as plt


### --- input ---
selected_place = arcpy.GetParameterAsText(0)
rain_forecast = arcpy.GetParameterAsText(1)

#test if selected_place contains a feature and throw an error if its true
selected_place_features = int(arcpy.management.GetCount(selected_place)[0])
        
if selected_place_features < 1:
    arcpy.AddError("'Your Place'-Input Layer should contain a Feature")
    

### --- Compare the selected place to the flood risk map of NRW ---

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
    risk_text = "The given place is located in an area with a high risk of flooding (compared to the 'Hochwasser-Gefahrenkarte NRW')."

    # clear the selection
    arcpy.SelectLayerByAttribute_management("ueberflutungsgrenzen_hohe_wahrscheinlichkeit","CLEAR_SELECTION")

else:

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
    #check if a feature is selected
    if int(arcpy.management.GetCount("ueberflutungsgrenzen_mittlere_wahrscheinlichkeit")[0]) != 0:
        risk_text = "The given place is located in an area with a moderate risk of flooding (compared to the 'Hochwasser-Gefahrenkarte NRW')."

        #clear the selection
        arcpy.SelectLayerByAttribute_management("ueberflutungsgrenzen_mittlere_wahrscheinlichkeit","CLEAR_SELECTION")

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
            risk_text = "The given place is located in an area with a moderate risk of flooding"
        
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
                risk_text = "The given place is located in an area with a low risk of flooding (compared to the 'Hochwasser-Gefahrenkarte NRW')."
                
                #clear the selection
                arcpy.SelectLayerByAttribute_management("ueberflutungsgrenzen_niedrige Wahrscheinlichkeit","CLEAR_SELECTION")
    
            else:
                # the point is in an area without a risk
                risk_text = f"The given place is located in an area without risk of flooding (compared to the 'Hochwasser-Gefahrenkarte NRW')."
    
# show the risk_text
arcpy.AddMessage(risk_text)


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
with arcpy.da.SearchCursor(selected_place, ["NEAR_DIST", "NEAR_FID", "SHAPE@"]) as cur:
    for row in cur:
        distance = round(row[0],2) # distance to the closest river (rounded to 2 decimal places)
        near_fid = row[1] # ObjectID of the closest river
        point = row[2] # get the location of the selected place

        #get the location as lat or long
        point_wgs84 = point.projectAs(
            arcpy.SpatialReference(4326)
        )
        longitude = point_wgs84.firstPoint.X
        latitude = point_wgs84.firstPoint.Y   

where = f"FID = {near_fid}"

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
with arcpy.da.SearchCursor(selected_place, ["NEAR_DIST", "NEAR_FID", "SHAPE@"]) as cur:
    for row in cur:
        distance = round(row[0],2) # distance to the closest river (rounded to 2 decimal places)
        near_fid = row[1] # ObjectID of the closest river
        point = row[2] # get the location of the selected place

        #get the location as lat or long
        point_wgs84 = point.projectAs(
            arcpy.SpatialReference(4326)
        )
        longitude = point_wgs84.firstPoint.X
        latitude = point_wgs84.firstPoint.Y   

where = f"FID = {near_fid}"

with arcpy.da.SearchCursor("gsk3e_gewkz_line_breite", ["FID", "GEWHNAME", "ST_BREITE"], where) as cur:
    for row in cur:
        nearestName = row[1]
        nearestWidth = row[2]

# output
arcpy.AddMessage(f"Nearest river: {nearestName}")
arcpy.AddMessage(f"Distance to the nearest river: {distance}m")
arcpy.AddMessage(f"Width of the nearest river: {nearestWidth}m")


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
    arcpy.AddMessage(f"Station name: {station_name}")
    station_id = uuid
    return distance, station_id

# check if the API responds
response = requests.get(f"https://pegelonline.wsv.de/webservices/rest-api/v2/stations.json")
json_data = response.json() if response and response.status_code == 200 else None
water_level_msg = ""
if json_data:
    # check if threre is data available for the nearest river
    response = requests.get(f"https://pegelonline.wsv.de/webservices/rest-api/v2/stations.json?waters={river}")
    json_river_data = response.json() if response and response.status_code == 200 else None
    if not json_river_data:
        water_level_msg=f"No water levels available for the river {nearestName} via pegelonline API. The following water level data was measured at the nearest measuring station of any river: <br/>"
        # find the nearest measuring station of any river and store its uuid in variable "station_id"
        distance, station_id = findNearestStation(json_data)
    else:
        # find the nearest station for the river in question store its uuid in variable "station_id"
        distance, station_id = findNearestStation(json_river_data)

    # check if measurements are available for this station
    response = requests.get(f"https://pegelonline.wsv.de/webservices/rest-api/v2/stations/{station_id}.json?includeTimeseries=true&includeCurrentMeasurement=true")
    json_data = response.json() if response and response.status_code == 200 else None
    water_level_msg = ""
    if json_data:
        # build water level info text
        water_level_msg = water_level_msg +(f"""Water level for the river {json_data['water']['longname']} 
            in {json_data['longname']} 
            at {json_data['timeseries'][0]['currentMeasurement']['timestamp']}:
            <b> {json_data['timeseries'][0]['currentMeasurement']['value']}{json_data['timeseries'][0]['unit']}</b>. <br/>
            <b> Distance to measuring station: </b> {distance}m""")
        if(('stateMnwMhw' in json_data['timeseries'][0]['currentMeasurement']) and (json_data['timeseries'][0]['currentMeasurement']['stateMnwMhw'] != "unknown")):
            water_level_msg = water_level_msg + (f"<br/> The current water level is <b> {json_data['timeseries'][0]['currentMeasurement']['stateMnwMhw']} </b> for this river.")
        # print water level info
        arcpy.AddMessage(water_level_msg)

        # get time series image of the past 30 days water levels
        response = requests.get(f"https://pegelonline.wsv.de/webservices/rest-api/v2/stations/{station_id}/W/measurements.png?start=P30D&width=900&height=400")
        if response.status_code == 200:
            chart30d = response   
        else:
            arcpy.AddMessage("No water level history available for this station right now.")
            chart30d = None

        # add forecast if it is available
        url = f"https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/{station_id}/WV/measurements.csv?contentType=text/plain"
        response = requests.get(url)
        if response and response.status_code == 200:
            csv = url
        else: 
            csv = None
            arcpy.AddMessage("No water level forecast available for this station.")

    else: water_level_msg = water_level_msg + ("No water level data available for this station right now.")

else: water_level_msg = "No water levels available; the API does not respond."


# ---------- Weather forecast ------------------

# weather forecast with Open-Meteo API
    
# only check the Open-Meteo API if needed
if int(rain_forecast) >= 1:

    #the api can give forecasts up to 15 days, check if the requested number of days is higher
    if int(rain_forecast) > 15:
        arcpy.AddMessage(f"\nRain forecast is not possible for {rain_forecast} days,\nwe can show you the predicted amount of rain in mm for the next 15 days at your selected place instead:")
        rain_forecast = 15
    else:
        arcpy.AddMessage(f"\nHere you can see the predicted amount of rain in mm for the next {rain_forecast} days at your selected place:")
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    #set the parameters
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "rain_sum",
        "forecast_days": rain_forecast
    }

    #get the response
    responses = openmeteo.weather_api(url, params = params)

    # Process location.
    response = responses[0]

    # Process daily data.
    daily = response.Daily()
    daily_rain_sum = daily.Variables(0).ValuesAsNumpy()

    daily_data = {
        "date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True).tz_localize(None),
            end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True).tz_localize(None),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )
    }

    # create output
    daily_data["rain_sum"] = daily_rain_sum
    daily_dataframe = pd.DataFrame(data = daily_data)
    arcpy.AddMessage(daily_dataframe)


# ----------- Build output PDF ------------------

# initialize file
pdf_path = arcpy.GetParameterAsText(1)
pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
styles = getSampleStyleSheet()
content = []

# heading:
content.append(Paragraph("Flood Risk Analysis Report", styles["Title"]))
content.append(Spacer(1, 12))

# subheading:
# get coordinates of input point
with arcpy.da.SearchCursor(selected_place, ["SHAPE@XY"]) as cursor:
    for row in cursor:
        x, y = row[0]
        coords = f"{x}, {y}"
# get current time and date
now = datetime.now()
subheading = f"""
This report contains data to enable the reader to evaluate the flooding risk of the point {coords}. <br/>
Report created at {now}.
"""
content.append(Paragraph(subheading, styles["Normal"]))
content.append(Spacer(1, 20))

# text
body = f"""
{risk_text} <br/> <br/>
<b> Nearest river: </b> {nearestName} <br/>
<b> Distance to the nearest river: </b> {distance}m <br/>
<b> Width of the nearest river: </b> {nearestWidth}m <br/> <br/>
{water_level_msg} <br/> <br/>
<b>Water level history for the past 30 days:</b> 
"""
content.append(Paragraph(body, styles["Normal"]))
content.append(Spacer(1, 12))

# water level history chart image as a reportlab flowable if it is available
if chart30d:
    chart = Image(BytesIO(chart30d.content), width=500, height=300)
    #chart.hAlign = "CENTER"
    content.append(chart) 
else:
    content.append(Paragraph("No water level history available for this station right now.", styles["Normal"]))
content.append(Spacer(1, 12))

# rain forecast
rain_forecast = f"""
<b> Rain forecast </b> in mm for the next week at your selected place: <br/>
"""
content.append(Paragraph(rain_forecast, styles["Normal"]))
table = Table(
      [[Paragraph(col) for col in daily_dataframe.columns]] + daily_dataframe.values.tolist(), 
      style=[
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('LINEBELOW',(0,0), (-1,0), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.lightgrey, colors.white])],
      hAlign = 'LEFT')
content.append(KeepTogether(table))
content.append(Spacer(1, 12))

# water level forecast
if csv: 
    # ceate chart
    data = pd.read_csv(csv, sep=";")
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    df = pd.DataFrame(data)
    X = data['timestamp']
    Y = data['value']
    plt.figure(figsize=(10, 5))
    plt.bar(X, Y, color="b")
    plt.xlabel("Date")
    plt.ylabel("Predicted water level")
    plt.xticks(rotation=45)
    plt.tight_layout()

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format="PNG", dpi=150)
    plt.close()

    img_buffer.seek(0)

    chart_forecast = Image(
        img_buffer,
        width=500,
        height=250
    )

    water_forecast = f"""
    <b>Water level forecast</b>:  <br/>
    """
else: 
    chart_forecast = None
    water_forecast = "No water level forecast available for this station."

content.append(Paragraph(water_forecast, styles["Normal"]))
if chart_forecast:
    content.append(chart_forecast)
content.append(Spacer(1, 30))

# credit
credit = "This report was created using the Flood Risk Analysis toolbox for ArcGIS by Lenja Fipper and Kian Jay Lenert, created in 2026."
content.append(Paragraph(credit, styles["Normal"]))

# build PDF
pdf.build(content)

arcpy.SetParameterAsText(1, pdf_path)

arcpy.AddMessage("PDF successfully created.")
