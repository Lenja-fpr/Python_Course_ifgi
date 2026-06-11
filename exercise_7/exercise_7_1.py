import time
import os
from typing import Any, Optional
from qgis import processing
from qgis.utils import iface
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProject,
    QgsFeatureRequest,
    QgsDistanceArea,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFileDestination,
)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt



class CreateCityDistrictProfile(QgsProcessingAlgorithm):

    # Constants
    city_districts = "CITY_DISTRICTS"
    choice_layer = "CHOICE_LAYER"
    pdf_output = "PDF_OUTPUT"
    
    # Identity methods
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
    
    def createInstance(self):
        return CreateCityDistrictProfile()
    
    def name(self):
        return 'createcitydistrictprofile'

    def displayName(self):
        return self.tr('Create City District Profile')

    def group(self):
        return self.tr('City District Tools')

    def groupId(self):
        return 'citydistricttools' 

    def shortHelpString(self):
        return self.tr("Creates a PDF profile for a selected Münster city district.")

    # Returns city district names from city districts layer in alphabetical order
    def getCityDistrictsList(self):
        districts = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]
        names = []
        if districts.isValid():
            request = QgsFeatureRequest()
            clause = QgsFeatureRequest.OrderByClause("NAME")
            request.setOrderBy(QgsFeatureRequest.OrderBy([clause]))
            for district in districts.getFeatures(request):
                names.append(district["NAME"])
        return names

    # Definition of GUI parameters
    def initAlgorithm(self, config: Optional[dict[str, Any]] = None):
        
        # Add a dropdown for selecting a city district
        self.addParameter(
            QgsProcessingParameterEnum(
                "CITY_DISTRICTS",
                "Choose a city district",
                options = self.getCityDistrictsList(),
                usesStaticStrings = True
            )
        )
        
        # Add a dropdown for picking if statistics for schools or pools
        # should be included in the result
        self.addParameter(
            QgsProcessingParameterEnum(
                "CHOICE_LAYER",
                "Include statistics for:",
                options = ["Schools", "Pools"],
                usesStaticStrings = True
            )
        )
        
        # Add element for selecting where to save the resulting PDF 
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'PDF_Output',
                self.tr('Output PDF file'),
                fileFilter='PDF files (*.pdf)'
            )
        )
    
    # Create a statistics chart
    def createStatisticalChart(self, pointLayer, district_geom):
        # Choose the right column name based on the chosen layer (schools or pools)
        type_col = "SchoolType" if pointLayer.name() == "Schools" else "Type"
        counts = {}
        for feature in pointLayer.getFeatures():
            if district_geom.intersects(feature.geometry()):
                val = feature[type_col]
                counts[val] = counts.get(val, 0) + 1
        if not counts:
                return "", False # no features —> no chart
        # Build and save the bar chart
        plt.bar(list(counts.keys()), list(counts.values()))
        plt.title(f"Distribution by type")
        plt.ylabel("Count")
        chart_path = os.path.join(QgsProject.instance().homePath(), "temp_chart.png")
        plt.savefig(chart_path, dpi=150, bbox_inches="tight")
        plt.clf() # clear figure
        plt.close()
        return chart_path, True
    
    
    
    # Creates a dictionary with all values for the createPDF function
    def createStatistics(self, cityDistrictName, chosenLayer):
        
        # Load all needed layers by name from TOC
        districts = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]
        houseNums = QgsProject.instance().mapLayersByName("House_Numbers")[0]
        parcels = QgsProject.instance().mapLayersByName("Muenster_Parcels")[0]
        if chosenLayer == "Schools":
            pointLayer = QgsProject.instance().mapLayersByName("Schools")[0]
        else:
            pointLayer = QgsProject.instance().mapLayersByName("public_swimming_pools")[0]
            
        # Filter the districts layer to find just the one the user chose
        request = QgsFeatureRequest()
        request.setFilterExpression(f'"NAME" = \'{cityDistrictName}\'')
        for district in districts.getFeatures(request):
            district_geom = district.geometry()
            parent_district = district["P_District"]
            district_id = district.id()
            
        # Use QgsDistanceArea with the correct ellipsoid for accurate real-world measurements
        da = QgsDistanceArea()
        da.setEllipsoid('ETRS89')
        
        # measureArea() returns square metres — divide twice by 1000 to get km²
        area_km2 = round(da.measureArea(district_geom) / 1000 / 1000, 2)
        
        # Count features within the selected district:
        # House numbers
        count_houses = sum(1 for h in houseNums.getFeatures() if h.geometry().within(district_geom))
        # Schools or pools
        count_choice = sum(1 for f in pointLayer.getFeatures() if f.geometry().within(district_geom))
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
        
        # Include statistics plot
        chart = self.createStatisticalChart(pointLayer, district_geom)
        chart_path = chart[0]
        chart_status = chart[1]
        
        # Return dictionary
        return {
            "parent_district": parent_district,
            "area_km2": area_km2,
            "count_houses": count_houses,
            "count_parcels": count_parcels,
            "chosen_layer": chosenLayer,
            "count_choice": count_choice,
            "image_path": image_path,
            "chart_path": chart_path,
            "chart_status": chart_status
        }

    # Create a PDF including all results
    def createPDF(self, cityDistrict, layerChoice, pdf_output):
        
        # Get all needed data
        data = self.createStatistics(cityDistrict, layerChoice)
        
        # Set up the PDF document and styles
        pdf = SimpleDocTemplate(pdf_output)
        styles = getSampleStyleSheet()
        page_width, _ = letter
        content = []
        
        # Title
        content.append(Paragraph(f"City District Profile: {cityDistrict}", styles["Title"]))
        content.append(Spacer(1, 12))
        
        # Map image
        map_img = Image(data["image_path"], width=page_width * 0.6,
        height=page_width * 0.3)
        content.append(map_img)
        content.append(Spacer(1, 12))
        
        # Text with all statistics
        no_feature_msg = f"No {data['chosen_layer'].lower()} in this district."
        feature_msg = f"{data['count_choice']} {data['chosen_layer'].lower()} are located in this district."
        body = f"""
        {cityDistrict} is part of the parent district {data['parent_district']}.
        Its area size is {data['area_km2']} km² and it contains {data['count_parcels']} parcels
        with a total of {data['count_houses']} households.
        """ + (f"{feature_msg}" if data["count_choice"] > 0 else no_feature_msg)
        content.append(Paragraph(body, styles["Normal"]))
        content.append(Spacer(1, 12))
        
        # Add the statistics chart if one has been created
        if data["chart_status"]:
            stats_img = Image(data["chart_path"], width=page_width * 0.6,
            height=page_width * 0.3)
            content.append(stats_img)
            content.append(Spacer(1, 12))
        
        # Build and save the PDF
        pdf.build(content)
        
        # Remove the temporary map
        os.remove(data["image_path"])
        # Remove the temporary statistics image if it was created
        if data["chart_status"]:
            os.remove(data["chart_path"])

    def processAlgorithm(self, parameters, context, feedback):
        # Read each GUI value using the matching parameterAs…() method
        city_district = self.parameterAsString(parameters, "CITY_DISTRICTS", context)
        layer_choice = self.parameterAsString(parameters, "CHOICE_LAYER", context)
        pdf_path = self.parameterAsFileOutput(parameters, "PDF_OUTPUT", context)
        # Run the whole pipeline
        self.createPDF(city_district, layer_choice, pdf_path)
        # Return a dict matching the output parameter keys
        return {"PDF_OUTPUT": pdf_path}

