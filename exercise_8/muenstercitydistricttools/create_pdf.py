from PyQt5 import QtCore, QtGui, QtWidgets
from qgis.PyQt.QtWidgets import QDialog 
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject
from .MuensterCityDistrictTools_profile import Ui_Dialog
from .MuensterCityDistrictTools_export import Ui_Dialog as Ui_ExportDialog
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from .statistics import createStatistics

def createPDF(self, cityDistrict, pdf_output):
        ## get the layer and the selected Features
        layer = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]
        features = layer.selectedFeatures()

        # Get all needed data
        data = createStatistics(features[0]["NAME"])
        
        # Set up the PDF document and styles
        pdf = SimpleDocTemplate(pdf_output)
        styles = getSampleStyleSheet()
        page_width, _ = letter
        content = []
        
        # Title
        content.append(Paragraph(f"City District Profile: {cityDistrict}", styles["Title"]))
        content.append(Spacer(1, 12))
        
        # Text with all statistics
        body = f"""
        {cityDistrict} is part of the parent district {data['parent_district']}.
        Its area size is {data['area_km2']} km² and it contains {data['count_parcels']} parcels
        with a total of {data['count_houses']} households. {data['count_schools']} schools and 
        {data['count_pools']} pools are located in this district.
        """
        content.append(Paragraph(body, styles["Normal"]))
        content.append(Spacer(1, 12))
        
        # Build and save the PDF
        pdf.build(content)