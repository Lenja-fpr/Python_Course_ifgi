from PyQt5.QtWidgets import QInputDialog, QMessageBox
from qgis.utils import iface
from qgis.core import QgsPointXY, QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry

# input dialog
parent = iface.mainWindow()
sCoords, bOK = QInputDialog.getText(
    parent,
    "Coordinates",
    "Enter coordinates as latitude, longitude",
    text = "51.96066,7.62476"
)

# coordinate reference system transformation:
# Get the city districts layer
city_districts = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]
# source crs from user input
crs_from = QgsCoordinateReferenceSystem(4326)
# target crs from Münster city districs layer
crs_to = city_districts.crs()
# transformation object
transform = QgsCoordinateTransform(crs_from, crs_to, QgsProject.instance())

# convert input string to numerical coordinates
if bOK:
    parts = sCoords.split(",") # ["51.96066", "7.62476"]
    lat = float(parts[0]) # north-south
    lon = float(parts[1]) # east-west
    point_wgs84 = QgsPointXY(lon, lat)
    # Transform to the layer's CRS
    point_projected = transform.transform(point_wgs84)
    # Wrap in a QgsGeometry so .within() can be used
    point_geom = QgsGeometry.fromPointXY(point_projected)

# check if the coordinates are inside of Münster 
found = False
for district in city_districts.getFeatures(): # loop through districts
    district_geom = district.geometry()
    if point_geom.within(district_geom):
        district_name = district["Name"]
        QMessageBox.information(
            parent,
            "Point inside Münster",
            f"Yay! Your point lies within Münster's city district {district_name}."
        )
        found = True
        break
if not found:
    QMessageBox.information(
    parent,
    "No match",
    f"Your point does not lie within Münster :("
    )