#save paths to the data
schools = "C:/Users/lenja/OneDrive/Desktop/Lenja/Uni_Münster/BGI4S_Python_in_QGIS_and_ArcGIS/GitRepositoryPiQA/Python_Course_ifgi/exercise_4/Muenster/Schools.shp"
muensterDistricts = "C:/Users/lenja/OneDrive/Desktop/Lenja/Uni_Münster/BGI4S_Python_in_QGIS_and_ArcGIS/GitRepositoryPiQA/Python_Course_ifgi/exercise_4/Muenster/Muenster_City_Districts.shp"

#run countpointsinpolygon to get the schools per districts of muenster
schoolsPerDistrict = processing.run("qgis:countpointsinpolygon",{'POLYGONS':muensterDistricts,'POINTS':schools,'WEIGHT':'','OUTPUT':'memory:'})

#iterate through the result and print the names of the districts and the numbersOfSchools per district
for feature in schoolsPerDistrict["OUTPUT"].getFeatures():
    district = feature["Name"]
    numberOfSchools = feature["NUMPOINTS"]
    print(district, ":", numberOfSchools)