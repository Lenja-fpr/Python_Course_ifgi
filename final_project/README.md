# Flood Risk Analysis - An ArcGIS Toolbox

This ArcGIS Toolbox helps the user to assess the individual flooding risk at a given point within NRW, Germany. 
It returns a PDF report that contains several pieces of information that are relevant for evaluating the flooding risk at the input point:
- Risk of flooding according to the ["Hochwasser-Gefahrenkarte NRW"](https://www.flussgebiete.nrw.de/hochwassergefahrenkarten-und-hochwasserrisikokarten) (high, moderate, low, or none)
- Name and width of and distance to the nearest river
- The nearest water level measuring station with 
  - its current measurement
  - its measurements of the past 30 days including average, if available
  - a water level forecast, if available
- A rain forecast for the next up to 15 days (customizable)

The tool uses two APIs: [PEGELONLINE REST-API](https://pegelonline.wsv.de/webservice/guideRestapi) for all water level data, and [Open-Meteo](https://open-meteo.com/) for the rain forecast. 


## User Guide

### Prerequisites
- ArcGIS Pro installed

### How to use (for Windows):
1. **Clone or download** this repository.


2. Open ArcGIS Pro and create a new **project**, or open an existing one.


3. **Import the toolbox:** Insert -> Toolbox -> New Toolbox -> navigate to the repository folder, open the folder "final_project" and select the file ```FloodRiskAnalysis.atbx```

4. **Data:**
Download the following data and load the specified files into your ArcGIS project:
- from https://www.opengeodata.nrw.de/produkte/umwelt_klima/wasser/hochwasser/hwrm/HQhaeufig-Ueberschwemmungsgrenzen_EPSG25832_Shape.zip :
  ```ueberflutungsgrenzen_hohe_wahrscheinlichkeit.shp```
- from https://www.opengeodata.nrw.de/produkte/umwelt_klima/wasser/hochwasser/hwrm/HQ100-Ueberschwemmungsgrenzen_EPSG25832_Shape.zip :
```ueberflutungsgrenzen_mittlere_wahrscheinlichkeit.shp```
- from https://www.opengeodata.nrw.de/produkte/umwelt_klima/wasser/hochwasser/hwrm/HQextrem-Ueberschwemmungsgrenzen_EPSG25832_Shape.zip :
 ```ueberflutungsgrenzen_niedrige_wahrscheinlichkeit.shp``` 
- from https://www.opengeodata.nrw.de/produkte/umwelt_klima/wasser/oberflaechengewaesser/gsk3e/gsk3e_EPSG25832_Shape.zip :
 ```gsk3e_gewkz_line_breite.shp``` (in the folder "shapefile").


5. **Installations:**
We use the API "Open-Meteo" for our rain forecast and reportlab for creating the PDF report. Therefore, you have to install three packages.

- Open the app "Python Command Prompt" (for ArcGIS Pro)
- Clone your standard environment:
```
conda create -n your_env --clone arcgispro-py3
```
- Activate the new environment:
```
proswap activate your_env
```
If that doesn't work, use
```
activate your_env
```
- Install the following modules:
```
pip install openmeteo-requests
pip install requests-cache retry-requests
conda install reportlab
```
- Go back to ArcGIS and click Project -> Package Manager
- Click on "Active Environment" and select your new environment
- Restart ArcGIS

6. **Use:** In the Geoprocessing window, search for "Flood Risk Analysis" and open the tool. Either use a point layer as input that contains the point whose flooding risk you are interested in, or click the pencil symbol next to the input field and create a point layer. Specify the amount of days you want to get a rain forecast for (up to 15) and the path for the output PDF report file. Make sure to add the ```.pdf``` file ending. When you are done, click "run". You will get a first overview of the results in the Messages window as the tool is running.



## Contributors
- Lenja Fipper - [@Lenja-fpr](https://github.com/Lenja-fpr)
- Kian Jay Lenert - [@kjlenert](https://github.com/kjlenert)
