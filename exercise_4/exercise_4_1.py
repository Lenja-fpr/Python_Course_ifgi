from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWebKitWidgets import QWebView

wv = QWebView(None)
wv.load(QUrl('https://wikipedia.org/wiki/[%name%]'))
wv.show()