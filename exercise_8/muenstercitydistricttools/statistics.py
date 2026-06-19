import time
import os
from qgis.utils import iface
from qgis.core import (
    QgsProject,
    QgsFeatureRequest,
    QgsDistanceArea,
)

# Creates a dictionary with all values for the createPDF function
def createStatistics(cityDistrictName):
    
    # Load all needed layers by name from TOC
    districts = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]
    houseNums = QgsProject.instance().mapLayersByName("House_Numbers")[0]
    parcels = QgsProject.instance().mapLayersByName("Muenster_Parcels")[0]
    schools = QgsProject.instance().mapLayersByName("Schools")[0]
    pools = QgsProject.instance().mapLayersByName("public_swimming_pools")[0]
        
    # Filter the districts layer to find just the one the user chose
    request = QgsFeatureRequest()
    request.setFilterExpression(f'"NAME" = \'{cityDistrictName}\'')
    for district in districts.getFeatures(request):
        district_geom = district.geometry()
        parent_district = district["P_District"]
        district_id = district.id()
        district_name = district["NAME"]
        
    # Use QgsDistanceArea with the correct ellipsoid for accurate real-world measurements
    da = QgsDistanceArea()
    da.setEllipsoid('ETRS89')
    
    # measureArea() returns square metres — divide twice by 1000 to get km²
    area_km2 = round(da.measureArea(district_geom) / 1000 / 1000, 2)
    
    # Count features within the selected district:
    # House numbers
    count_houses = sum(1 for h in houseNums.getFeatures() if h.geometry().within(district_geom))
    # Count schools
    count_schools = sum(1 for f in schools.getFeatures() if f.geometry().within(district_geom))
    # Count public swimming pools
    count_pools = sum(1 for f in pools.getFeatures() if f.geometry().within(district_geom))
    # Parcels
    count_parcels = sum(1 for p in parcels.getFeatures() if p.geometry().intersects(district_geom))
    
    # Set the districts layer to active for zooming
    iface.setActiveLayer(districts)
    # Select the district and zoom to it
    districts.select(district_id)
    iface.mapCanvas().zoomToSelected(districts)
    # Refresh and wait
    iface.mapCanvas().refresh()
    time.sleep(5)
    # Save the screenshot to the QGIS project folder
    image_path = os.path.join(QgsProject.instance().homePath(), "temp_map.png")
    iface.mapCanvas().saveAsImage(image_path)
    # Clear selection
    districts.deselect(district_id)
    
    # Return dictionary
    return {
        "district_name": district_name,
        "parent_district": parent_district,
        "area_km2": area_km2,
        "count_houses": count_houses,
        "count_parcels": count_parcels,
        "count_schools": count_schools,
        "count_pools": count_pools
    }