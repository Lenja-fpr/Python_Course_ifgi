# Import modules
from qgis.core import QgsVectorLayer, QgsProject
from qgis.core import *
import os

# Supply path to qgis install location
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.40.5", True)

# Path to data and QGIS-project
data_path = r"C:\Users\lenja\OneDrive\Desktop\Lenja\Uni_Münster\BGI4S_Python_in_QGIS_and_ArcGIS\GitRepositoryPiQA\Python_Course_ifgi\exercise_4\Muenster"
project_path = r"C:\Users\lenja\OneDrive\Desktop\Lenja\Uni_Münster\BGI4S_Python_in_QGIS_and_ArcGIS\GitRepositoryPiQA\Python_Course_ifgi\exercise_4\myFirstProject.qgz"  # for QGIS version 3+

# save the data as a list
listOfFiles = os.listdir(data_path)

# Create QGIS instance and "open" the project
project = QgsProject.instance()
project.read(project_path)

# go through the list
for file in listOfFiles:

    # check if the file is a shapefile
    if file[-3:] == "shp":

        # get the path of the file
        filePath = data_path + "\\" + file

        # get layer name
        layerName = os.path.splitext(os.path.basename(file))[0]

        # Create layer
        layer = QgsVectorLayer(filePath, layerName, "ogr")

        # Check if layer is valid
        if not layer.isValid():
            print("Error loading the layer!")

        else:
            # Add layer to project
            project.addMapLayer(layer)

            print("Added layer " + file + " to the project")

# Save project
project.write()

print("Project saved successfully!")