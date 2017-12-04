from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^info/(?P<encoded>.*=?)", views.info, name="info"),
    url(r"^stream/(?P<encoded>.*=?)", views.stream, name="stream"),
    url(r"^nodeinfo", views.nodeinfo, name="nodeinfo"),
    url(r"^abledisk", views.abledisk, name="abledisk"),
    url(r"^progress/(?P<encoded>.*=?)", views.progress, name="progress"),
    url(r"^download/(?P<encoded>.*=?)", views.download, name="download"),
    url(r"^findfile/(?P<encoded>.*=?)", views.findfile, name="findfile"),
    url(r"^removefile/(?P<encoded>.*=?)", views.removefile, name="removefile"),
    url(r"^extractors", views.extractors, name="extractors"),
]
