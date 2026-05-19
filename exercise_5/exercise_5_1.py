### Where is my next school 

## get the city districts layer
districts_path = "C:/Users/lenja/OneDrive/Desktop/Lenja/Uni_Münster/BGI4S_Python_in_QGIS_and_ArcGIS/GitRepositoryPiQA/Python_Course_ifgi/exercise_4/Muenster/Muenster_City_Districts.shp"
districts = qgis.core.QgsVectorLayer(districts_path, "Muenster_City_Districts", "ogr")
## get the schools layer
schools_path = "C:/Users/lenja/OneDrive/Desktop/Lenja/Uni_Münster/BGI4S_Python_in_QGIS_and_ArcGIS/GitRepositoryPiQA/Python_Course_ifgi/exercise_4/Muenster/Schools.shp"
schools = qgis.core.QgsVectorLayer(schools_path, "Schools", "ogr")

## create a request object for the districts
requestD = QgsFeatureRequest()
## create a clause
clauseD = QgsFeatureRequest.OrderByClause("Name", ascending=True)
## pass the clause to the request object
orderD =  QgsFeatureRequest.OrderBy([clauseD])
requestD.setOrderBy(orderD)

## create a request object for the schools
requestS = QgsFeatureRequest()
## create a clause
clauseS = QgsFeatureRequest.OrderByClause("NAME", ascending=True)
## pass the clause to the request object
orderS =  QgsFeatureRequest.OrderBy([clauseS])
requestS.setOrderBy(orderS)

## create a list to store the district names
districts_names = []

## save the names in alphabetical order
for district in districts.getFeatures(requestD):
    districts_names.append(district["Name"])

## show an input dialog window
parent = iface.mainWindow()
sDistrict, bOk = QInputDialog.getItem(parent, "District Names", "Select District: ", districts_names)

## run the following code, if the user clicked "OK"
if bOk:
    
    ##initialize a variable to store the geometry of the choosen district
    choosen_district = None
    
    ##get the geometry of the choosen district
    for district in districts.getFeatures():
        if district["Name"] == sDistrict:
            choosen_district = district.geometry()

    ## check if a district is choosen
    if choosen_district == None:
        QMessageBox.warning(parent, "Schools", "there must be a choosen district")
        exit()
        
    ## get the centroid of the district
    centroid = choosen_district.centroid()
    
    ##resolve any selection in the school layer
    schools.removeSelection()
    
    ## select the schools that are are located in the choosen district
    for school in schools.getFeatures(requestS):
        if school.geometry().within(choosen_district):
            ## select the school
            schools.select(school.id())
    
    ##save the selected schools in a list
    schools_in_district = []
    for school in schools.selectedFeatures():
        ##get the distance
        distance = round(QgsDistanceArea().measureLine(centroid.asPoint(), school.geometry().asPoint()) / 1000, 2)
        ##save the informations about the school in the list
        schools_in_district.append(
            f"{school['NAME']}, {school['SchoolType']}, \ndistance to district centrum {distance} km \n"
        )
    
    ## zoom to the selection
    iface.mapCanvas().zoomToSelected()
    
    ## if there are no schools in the districts:
    if schools_in_district == []:
        QMessageBox.information(parent, f"Schools in {sDistrict}", f"There are no schools in {sDistrict}")
    ##if there are schools in the district
    else:
        QMessageBox.information(parent, f"Schools in {sDistrict}", "\n".join(schools_in_district))

##if the user canceled:
else:
    QMessageBox.warning(parent, "Schools", "User cancelled")