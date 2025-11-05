# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, include
from main_app import views

urlpatterns = [
    path("", include("ture.urls")) 

]
