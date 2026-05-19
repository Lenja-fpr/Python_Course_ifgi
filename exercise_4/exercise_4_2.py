from qgis.core import QgsProject

# prepare the csv file
csv_file = open(r"C:\temp\SchoolReport.csv", "w")
# header
lines = ["SchoolName;X;Y"]
# get layer
schools = QgsProject.instance().mapLayersByName("Schools")[0]

# iterate over selected schools and collect their names and 
#   coordinates in a list
for feature in schools.getSelectedFeatures():
    name = feature["Name"]
    point = feature.geometry().asPoint()
    x = point.x()
    y = point.y()
    line = f"{name};{x};{y}"
    lines.append(line)

# write the list into the csv file
csv_file.write("\n".join(lines))
csv_file.close()