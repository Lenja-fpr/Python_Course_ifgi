## imports
import csv

## create a map canvas
mc = iface.mapCanvas()

## create a layer with the fields, set the coordinate System
uri = "multipolygon?crs=EPSG:4326&field=standard_land_value:float&field=type:string&field=district:string&index=yes"
memoryLayer = QgsVectorLayer(uri, "Standard_Land_Value", "memory")
memoryLayer.setCrs(QgsCoordinateReferenceSystem("EPSG:25832"))

## parse over the csv file
with open(r"C:\Users\lenja\OneDrive\Desktop\Lenja\Uni_Münster\BGI4S_Python_in_QGIS_and_ArcGIS\GitRepositoryPiQA\Python_Course_ifgi\exercise_6\Data for Session 6\Data for Session 6\standard_land_value_muenster.csv", mode="r", encoding="utf-8") as file:
    
    ## parse over the lines of the csv file
    for line in file:
        ## ignore the first line
        if line != "standard_land_value;type;district;geometry\n":
            
            ## split the line (at the ;)
            line = line.split(";")
            
            ## create a new feature
            feature = QgsFeature(memoryLayer.fields())
            
            ## set the attributes from the csv file
            feature.setAttribute("standard_land_value",float(line[0].replace(",", ".")))
            feature.setAttribute("type", line[1])
            feature.setAttribute("district", line[2])
            
            ## remove the \n from the geometry entry in the lines if nessesary
            if line[3][-2:] == "\n":
                line[3] = line[3][:-2]
            ## set the geometry from the csv file
            feature.setGeometry(QgsGeometry.fromWkt(line[3]))
            
            
            ## add the new feature to the memory layer
            memoryLayer.dataProvider().addFeatures([feature]) 

## add the new layer to the map
QgsProject.instance().addMapLayer(memoryLayer)