# Import modules
import sys
from qgis.core import QgsApplication, QgsVectorLayer, QgsProject
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon

# Create class MapViewer
class MapViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simple Layer Viewer")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Initialize QGIS application
        self.qgs_app = QgsApplication([], False)
        self.qgs_app.initQgis()

        # Create map canvas
        self.canvas = QgsMapCanvas()
        self.layout.addWidget(self.canvas)

        # Load vector layer
        self.load_vector_layer()

        # Set extent
        self.canvas.setExtent(self.layer.extent())

        # Set up map canvas layer set
        self.bridge = QgsLayerTreeMapCanvasBridge(
            QgsProject.instance().layerTreeRoot(), self.canvas)
        self.bridge.setCanvasLayers()

    def load_vector_layer(self):
        # Change the path to your vector layer
        vector_layer_path = r"C:\Users\Sven Harpering\Desktop\Data Python in QGIS & ArcGIS\Muenster\House_Numbers.shp"
        self.layer = QgsVectorLayer(vector_layer_path, "Layer Name", "ogr")
        if not self.layer.isValid():
            print("Layer failed to load!")
            return
        QgsProject.instance().addMapLayer(self.layer)

    def closeEvent(self, event):
        # Clean up when the application is closed
        self.qgs_app.exitQgis()

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.png"))
    viewer = MapViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()