from django.conf.urls import url
from .views import *

urlpatterns = [

url(r'^$', Homepage.as_view(), name='homepage'),
url(r'^company$', CompanyData.as_view(), name='companyimportdata'),
]
