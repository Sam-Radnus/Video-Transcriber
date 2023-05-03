from django.urls import path,include
from . import views

urlpatterns=[
    path('',views.home_page,name="home_page"),
    path('convert',views.download_video,name="transcribe video"),
    path('result',views.show_result,name="show result")
]