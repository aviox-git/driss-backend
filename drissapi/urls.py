"""drissapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from .routers import HybridRouter
from django.conf.urls.static import static
from django.conf import settings
from api.views import *
from rest_framework_jwt.views import obtain_jwt_token
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

router = HybridRouter()
router.add_api_view('login',  path('login', CustomAuthToken.as_view(), name=r'login'))
# router.add_api_view('logout',  path('logout', Logout.as_view(), name=r'logout'))
router.add_api_view('forgotpassword',  path('forgot', ForgotView.as_view(), name=r'forgot'))
router.add_api_view('userdetails',  path('userdetails', UserDetailView.as_view(), name=r'userdetails'))
router.add_api_view('companyprofile',  path('companyprofile', CompanyDetailView.as_view(), name=r'companyprofile'))
router.add_api_view('registration', path('registration', RegisterationView.as_view(), name=r"registration"))
router.add_api_view('allcompany', path('allcompany', CompanyList.as_view(), name=r"allcompany"))
router.add_api_view('location', path('location', Location.as_view(), name=r"location"))
router.add_api_view('search', path('search', Search.as_view(), name=r"search"))
router.add_api_view('delete', path('delete', DeleteCompany.as_view(), name=r"delete"))
router.add_api_view('message', path('message', Message.as_view(), name=r"message"))
router.add_api_view('activities', path('activities', Activities.as_view(), name=r"activities"))
router.add_api_view('legalentity', path('legalentity', LegelEntityView.as_view(), name=r"legalentity"))
router.add_api_view('markers', path('markers-images', MarkersImages.as_view(), name=r"markers_images"))
# router.add_api_view('api-auth',path('api-token-auth/', obtain_jwt_token))
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('importdata/', include('homeapp.urls')),
    path('auth/', include('rest_framework_social_oauth2.urls')),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()
