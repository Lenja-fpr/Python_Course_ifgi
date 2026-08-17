# Flood Risk Analysis - An ArcGIS toolbox
## Documentation


### Draft


- clone or download this repository (insert more detailed explanation)
- import the atbx file into an ArcGIS project (insert more detailed explanation)
- Download the zip file from ```https://www.opengeodata.nrw.de/produkte/umwelt_klima/wasser/oberflaechengewaesser/gsk3e/``` and import the shapefiles ```gsk3e_gewkz_line_breite.shp``` and/or ```gsk3e_gewkz_point_stat.shp``` into your ArcGIS project
- Create a point layer with your point
- to be continued

API used: https://pegelonline.wsv.de/webservice/guideRestapi

### Data
Download the following data and load it into your ArcGIS project

- https://www.opengeodata.nrw.de/produkte/umwelt_klima/wasser/hochwasser/hwrm/HQhaeufig-Ueberschwemmungsgrenzen_EPSG25832_Shape.zip

  load the file ```ueberflutungsgrenzen_hohe_wahrscheinlichkeit``` into your ArcGIS project

- https://www.opengeodata.nrw.de/produkte/umwelt_klima/wasser/hochwasser/hwrm/HQ100-Ueberschwemmungsgrenzen_EPSG25832_Shape.zip

  load the file ```ueberflutungsgrenzen_mittlere_wahrscheinlichkeit``` into your ArcGIS project

- https://www.opengeodata.nrw.de/produkte/umwelt_klima/wasser/hochwasser/hwrm/HQextrem-Ueberschwemmungsgrenzen_EPSG25832_Shape.zip

  load the file ```ueberflutungsgrenzen_niedrige Wahrscheinlichkeit``` into your ArcGIS project

- https://www.opengeodata.nrw.de/produkte/umwelt_klima/wasser/oberflaechengewaesser/gsk3e/gsk3e_EPSG25832_Shape.zip

  load the file ```gsk3e_gewkz_line_breite``` into your ArcGIS project

### Installation
We use "Openmeteo" for our rain forecast and reportlab for creating the PDF report. Therefore, you have to install three packages.

! The following instructions only work for Windows !

- open the "Python Command Prompt" (for ArcGIS Pro)
- clone your standard environment
```
conda create -n your_env --clone arcgispro-py3
```
- activate the new environment
```
proswap activate your_env
```
if that doesn't work, use
```
activate your_env
```
- install the following modules:
```
pip install openmeteo-requests
pip install requests-cache retry-requests numpy pandas
conda install reportlab
```
- open your ArcGIS Project
- go to "Project" -> "Package Manager"
- click on "Active Environment" and choose your new environment
- restart ArcGIS
