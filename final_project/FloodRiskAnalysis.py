### --- imports ---
import arcpy
import requests
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

### --- input ---
selected_place = arcpy.GetParameterAsText(0)
rain_forecast = arcpy.GetParameterAsText(1)

#test if selected_place contains a feature and throw an error if its true
selected_place_features = int(arcpy.management.GetCount(selected_place)[0])
        
if selected_place_features < 1:
    arcpy.AddError("'Your Place'-Input Layer should contain a Feature")
    
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
    arcpy.AddMessage(f"\nNearest river: {nearestName}")
    arcpy.AddMessage(f"Distance to the nearest river: {distance} m")
    arcpy.AddMessage(f"Witdh of the nearest river: {nearestWidth} m")
    
    
    ### --- Get water level data from the nearest river via an API ---
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
            arcpy.AddMessage(f"\nAPI data available for river {river}")
            # TODO find nearest station for the river in question
            # store its uuid in variable "station_id"
        else:
            arcpy.AddMessage(f"\nNo water levels available for {river} via this API.")
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
    
    ### weather forecast with Open-Meteo API
    
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
    
        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "rain_sum",
            "forecast_days": rain_forecast
        }
        responses = openmeteo.weather_api(url, params = params)
    
        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
    
        # Process daily data. The order of variables needs to be the same as requested.
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
    
        daily_data["rain_sum"] = daily_rain_sum
    
        daily_dataframe = pd.DataFrame(data = daily_data)
        arcpy.AddMessage(daily_dataframe)