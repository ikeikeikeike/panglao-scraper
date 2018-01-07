from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^alives", views.alives, name="alives"),
    url(r"^busies", views.busies, name="busies"),
]
