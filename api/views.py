from rest_framework import views, mixins, permissions, exceptions
from rest_framework.response import Response
from rest_framework import parsers, renderers
from rest_framework.parsers import FileUploadParser,MultiPartParser,FormParser
from rest_framework.permissions import BasePermission
from .serializers import *
from django.utils.dateformat import format
from django.db.models import Q
from operator import itemgetter
from rest_framework import exceptions
from .models import *
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions
from rest_framework import authentication
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
import jwt
import re
import math, random 
from rest_framework_jwt.utils import jwt_payload_handler
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
from social_django.utils import load_strategy, load_backend
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from requests.exceptions import HTTPError
from django.utils import timezone
from datetime import datetime, timedelta
import datetime
from math import radians, cos, sin, asin, sqrt
from itertools import chain


def generateOTP(): 
	digits = "0123456789"
	OTP = "" 
	for i in range(4): 
		OTP += digits[math.floor(random.random() * 10)] 

	return OTP



class CustomAuthentication(authentication.BaseAuthentication):


	def authenticate(self, request):
		username = request.data['username']
		username = username.lower()
		password = request.data['password']
		user_type = request.data['user_type']
		# name = request.data['name']
		# email = request.data['email']
		print(request.data)
		if int(user_type)==0:
			if not username:
				raise exceptions.AuthenticationFailed('Email not provided.')
			if not password:
				raise exceptions.AuthenticationFailed('Password  not provided.')
			credentials = {
			'username': username,
			'password': password
			}
			user = authenticate(**credentials)
			if user is None:
				raise exceptions.AuthenticationFailed('Invalid username/password.')

			if not user.is_active:
				raise exceptions.AuthenticationFailed('User inactive or deleted.')


			return (user, None)
		else:
			if not username:
				raise exceptions.AuthenticationFailed('Socialid is required.')
			
			try:
				user = User.objects.get(username=username)
			except User.DoesNotExist:
				try:
					user = User.objects.get(email=email)
					print(user.username)
					raise exceptions.AuthenticationFailed('Email already exists.')
				except User.DoesNotExist:
					user = User.objects.create(username=username,email=email,first_name=name)
					Profile.objects.create(users=user)

			if not user.is_active:
				raise exceptions.AuthenticationFailed('User inactive or deleted.')

		return (user, None)
		


class CustomAuthToken(views.APIView):
	authentication_classes = ( SessionAuthentication,CustomAuthentication)
	def post(self, request, *args, **kwargs):
		response = {}
		try:
			# if request.user.is_authenticated:
			payload = jwt_payload_handler(user=request.user)
			token = jwt.encode(payload, settings.SECRET_KEY)
			try:
				profile = Profile.objects.get(users=request.user)
				content = {
					'status':'success',
					'data':{
						'id': request.user.id,
						'name': request.user.first_name,
						'email': request.user.email,
						'phonenumber' : profile.phone,
						'access_token':token,
						'profile_pic':profile.getSingleImageUrl()
					}
				}
				return Response(content)
			except Profile.DoesNotExist:
				response["status"] = "error"
				raise exceptions.ParseError("Unable to login did you register.")
		except Exception as e:
			print(str(e))
			raise exceptions.ParseError("Incorrect username and password.")
			
			

class RegisterationView(views.APIView):

	def post(self, request, *args, **kwargs):
		username = request.data.get("username")
		password = request.data.get("password")
		email = request.data.get('email')
		user_type = int(request.data.get('user_type'))
		phonenumber = request.data.get('phonenumber')
		number_length = len(phonenumber)
		
		if not username:
			if user_type == 0:
				raise exceptions.ParseError("Username cannot be blank.")
			else:
				raise exceptions.ParseError("Please provide social account ID.")	
		elif not password and user_type == 0:
		
			raise exceptions.ParseError("Password cannot be blank.")
		elif not email:
			
			raise exceptions.ParseError("Email cannot be blank.")
		elif not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
			
			raise exceptions.ParseError("Enter valid email address.")
		elif not phonenumber:
			
			raise exceptions.ParseError("Phone Number cannot be blank.")
		elif number_length > 15:
			
			raise exceptions.ParseError("Please enter 10 digit mobile number.")
		elif number_length < 10:
			raise exceptions.ParseError("Please enter 10 digit mobile number.")
		else:
			email = email.lower()
			profile = Profile.objects.filter(phone=phonenumber)
			if profile:
				raise exceptions.ParseError("Phone number already exists.")
			else:
				if user_type == 0: 
					
					user = User.objects.filter(email=email)
					if user:
						raise exceptions.ParseError("Email already exists.")
					else:
						user = User.objects.create_user(
						first_name=username,
						username=email,
						email=email)
						user.set_password(password)
						user.save()
						customer = Profile.objects.create(users=user,
						phone=phonenumber)
						content = {
							'status':'success',
							'message':'You are registered successfully.'
						}
						return Response(content)
				else:
					user = User.objects.filter(username=username)
					if user:
						raise exceptions.ParseError("already exists.")
					else:
						user = User.objects.create_user(
							username=username,
							email=email
						)
						user.save()
						customer = Profile.objects.create(users=user,
						phone=phonenumber)
						customer.save()
						print(customer)
						content = {
							'status':'success',
							'message':'You are registered successfully.'
						}
						return Response(content)
		raise exceptions.ParseError("registration Failed.")

class ForgotView(views.APIView):
	def get(self, request, *args, **kwargs):
		email = request.GET.get("email")
		confirmotp = generateOTP()

		if not email:
			raise exceptions.ParseError("email cannot be blank.")
		fcode = ForgotCode.objects.filter(code=confirmotp)
		if fcode:
			confirmotp2 = generateOTP()
			user = User.objects.get(email=email)
			start = timezone.now()
			end = start + timedelta(minutes=5)
			email = EmailMessage('Reset Password', confirmotp2 , to=[email])
			email.send()
			code = ForgotCode(
				user=user,
				code=confirmotp2,
				create_datetime= start,
				expiry_datetime=end)
			code.save()
		else:
			try:
				user = User.objects.get(email=email)
				start = timezone.now()
				end = start + timedelta(minutes=5)
				email = EmailMessage('Reset Password', confirmotp , to=[email])
				email.send()
				code = ForgotCode(
					user=user,
					code=confirmotp,
					create_datetime= start,
					expiry_datetime=end)
				code.save()
					
			except User.DoesNotExist:
				raise exceptions.ParseError("Please enter a valid email address.")
			content = {
			'status':'success',
			'message':'OTP is send to your mail. Please use this to reset password.'
			}
			return Response(content)
	def post(self, request, *args, **kwargs):

		OTP = request.data.get("otp")
		new_password = request.data.get('password')
		now =  timezone.now()
		if not OTP:
			raise exceptions.ParseError("OTP cannot be blank.")
		else:
			if not new_password:
				raise exceptions.ParseError("Password cannot be blank.")
			try:
				fcode = ForgotCode.objects.get(code=OTP)
				ends = fcode.expiry_datetime
				if now > ends:
					raise exceptions.ParseError("OTP is expired.")
				else:
					fcode.user.set_password(new_password)
					fcode.user.save()
			except ForgotCode.DoesNotExist:
				raise exceptions.ParseError("Invalid one time password.")
		content = {
		'status':'success',
		'message':'You password is successfully changed.'
		}
		return Response(content)

class UserDetailView(views.APIView):
	authentication_classes = ( SessionAuthentication,JSONWebTokenAuthentication)
	permission_classes = (IsAuthenticated,)
	def get(self, request, *args, **kwargs):
		try:	
			profile = Profile.objects.get(users=request.user)
			user = {}
			user_id =  request.user.id
			profilebyid = Profile.objects.get(id=user_id)

			name = request.user.first_name
			email = request.user.email
			phonenumber = profile.phone
			if profile.profile_pic:
				profile_picture = settings.BASE_URL+profile.profile_pic.url
			else:
				profile_picture = ""
			user['id'] = user_id
			user['name'] = name
			user['email'] = email
			user['phonenumber'] = phonenumber
			user['profile_pic'] = profile_picture
			content = {
			'status':'success',
			'data':user
			}
			return Response(content)
		except Exception as e:
			raise e
			raise exceptions.ParseError("Incorrect access token.")

class CompanyDetailView(views.APIView):
	parser_classes = (MultiPartParser,FormParser,)
	authentication_classes = ( SessionAuthentication,JSONWebTokenAuthentication)
	permission_classes = (IsAuthenticated,)
	def get(self,request):
		try:
			company_id = request.GET.get("companyid")
			print(company_id)
			profile_type = request.GET.get("profile_type")
			if not company_id:
				raise exceptions.ParseError("companyid is required.")
			elif not profile_type:
				raise exceptions.ParseError("profile_type is not selected.")
			else:
				if int(profile_type) == 1:
					code = CompanyProfile.objects.filter(id=company_id)
					# pictures = CompanyImages.objects.filter(profile__id=company_id)
					picture_list = []
					if code:
						picture_list = code[0].getAllImages()
				else:
					user = User.objects.get(id=company_id)
					code = Profile.objects.filter(users=user)
					emptylist = []
				previouswork = []
				for company in code:
					fdict = {}
					previouswork = company.getAllImages()
					phonenumber = ""
					pictures = company.getSingleImageUrl()
					companyname = company.companyname
					if int(profile_type) == 0:
						if not companyname:
							user = User.objects.get(id=company_id)
							companyname = user.first_name
					
					legalentitytype = 1
					if company.legalentitytype:
						legalentitytype = company.legalentitytype.id
					street = ""
					if int(profile_type) == 1:
						street = company.street
					else:
						street = company.state
					city = company.city
					country = company.country
					postcode = company.postcode
					longitude = company.longitude
					latitude = company.latitude
					
					website = ""
					descripiton = ""
					activity = ""
					phonenumber_status = False
					website_status = False
					if company.details:
						phonenumber = company.details.phonenumber
						phonenumber_status  = company.details.phonenumber_status
						website = company.details.website
						website_status = company.details.website_status
						descripiton = company.details.descripiton
						activity = company.details.activties.id
					else:
						if company.phone and int(profile_type) == 0:
							phonenumber = company.phone
					activity_status = company.activity_status
					status = company.status
					companyname_status = company.companyname_status
					legalentitytype_status = company.legalentitytype_status
					city_status = company.city_status
					street_status = False
					if int(profile_type) == 0:
						street_status = company.state_status
					else:
						street_status = company.street_status
					country_status = company.country_status
					postcode_status = company.postcode_status
					
					fdict['companyname'] = companyname
					fdict['legalentitytype'] = legalentitytype
					fdict['profile_pic'] = pictures
					fdict['street'] = street
					fdict['city'] = city
					fdict['country'] = country
					fdict['postcode'] = postcode
					fdict['longitude'] = longitude
					fdict['latitude'] = latitude
					fdict['phonenumber'] = phonenumber
					fdict['phonenumber_status'] = phonenumber_status
					fdict['website'] = website
					fdict['website_status'] = website_status
					fdict['description'] = descripiton
					fdict['status'] = status
					fdict['companyname_status'] = companyname_status
					fdict['legalentitytype_status'] = legalentitytype_status
					fdict['city_status'] = city_status
					fdict['street_status'] = street_status
					fdict['country_status'] = country_status
					fdict['postcode_status'] = postcode_status
					fdict['activity'] = activity
					fdict['activity_status'] = activity_status
					if int(profile_type) == 1:
						fdict["images"]=picture_list
					else:
						fdict["images"]=previouswork
					content = {
						'status':'success',
						'data': fdict
					}
					return Response(content)
				if not code:
					return Response({
						'status':'error',
						'message': "No profile found."
					})
		except Exception as e:
			return Response({
						'status':'error',
						'message': str(e)
					})

	def post(self, request, format=None, *args, **kwargs):
		try:
			companyname = request.data.get("name")
			companyid = request.data.get('companyid')
			profile_pic = request.FILES.get('profile_pic')
			legalentitytype = request.data.get('legalentitytype')
			street = request.data.get('street')
			city = request.data.get('city')
			country = request.data.get('country')
			postalcode = request.data.get('postalcode')
			longitude = request.data.get('longitude')
			latitude = request.data.get('latitude')
			activties = request.data.get('activity')
			activity_status = request.data.get('activity_status')
			phonenumber = request.data.get('phonenumber')
			phonenumber_status = request.data.get("phonenumber_status")
			website = request.data.get('website')
			website_status = request.data.get("website_status")
			descripiton = request.data.get('descripiton')
			status = request.data.get('published_status')
			profile_type = request.data.get('profile_type')
			companynames_status = request.data.get('name_status')
			legalentitytype_status = request.data.get('legalentitytype_status')
			city_status = request.data.get('city_status')
			street_status = request.data.get('street_status')
			country_status = request.data.get('country_status')
			postcode_status = request.data.get('postcode_status') 
			picture_length = request.data.get("picture_length")
			if status=="true":
				status = 1
			else:
				status = 0

			if phonenumber_status=="true":
				phonenumber_status = 1
			else:
				phonenumber_status = 0

			if activity_status=="true":
				activity_status = 1
			else:
				activity_status = 0

			if website_status=="true":
				website_status = 1
			else:
				website_status = 0
			
			
			
			legalentity = LegelEntity.objects.get(id=int(legalentitytype))
			user = None

			if int(profile_type) == 1:
				if companyid:
					code = CompanyProfile.objects.get(id=companyid)
				else:
					user = User.objects.get(id=request.user.id)
					user.first_name = companyname
					user.save()
					code = CompanyProfile.objects.create(owner=request.user)
			else:

				code = Profile.objects.get(users=request.user)
				user = User.objects.get(id=request.user.id)
				user.first_name = companyname
				user.save()

			act_obj = None
			if int(profile_type) == 1:
				act_obj = CompanyActivties.objects.get(id=int(activties))
			else:
				act_obj = Activties.objects.get(id=int(activties))
			if code.details:
				code.details.activties = act_obj
				code.details.phonenumber = phonenumber
				code.details.phonenumber_status = phonenumber_status
				code.details.website = website
				code.details.website_status = website_status
				code.details.descripiton = descripiton
				code.details.save()
			else:
				if int(profile_type) == 1:
					act_detail_obj = CompanyActivtiesDetail.objects.create(activties=act_obj)
				else:
					act_detail_obj = ActivtiesDetail.objects.create(activties=act_obj)
				act_detail_obj.activties = act_obj
				act_detail_obj.phonenumber = phonenumber
				act_detail_obj.phonenumber_status = phonenumber_status
				act_detail_obj.website = website
				act_detail_obj.website_status = website_status
				act_detail_obj.descripiton = descripiton
				act_detail_obj.save()
				code.details = act_detail_obj


			code.modver_datetime = timezone.now()
			if profile_pic:
				code.profile_pic = profile_pic
			code.companyname = companyname
			code.activity_status = activity_status
			code.legalentitytype = legalentity
			if int(profile_type) == 1:
				code.street = street
			else:
				code.state = street
			
	
			code.city = city
			code.country = country
			code.postcode = postalcode
			if companynames_status=="true":
				companynames_status = 1
			else:
				companynames_status = 0
			code.companyname_status = companynames_status
			if legalentitytype_status=="true":
				legalentitytype_status = 1
			else:
				legalentitytype_status = 0
			code.legalentitytype_status = legalentitytype_status
			if city_status=="true":
				city_status = 1
			else:
				city_status = 0
			code.city_status = city_status
			if street_status=="true":
				street_status = 1
			else:
				street_status = 0
			if int(profile_type) == 1:
				code.street_status = street_status
			else:
				code.state_status = street_status
			if country_status=="true":
				country_status = 1
			else:
				country_status = 0
			code.country_status = country_status
			if postcode_status=="true":
				postcode_status = 1
			else:
				postcode_status = 0
			code.postcode_status = postcode_status
			code.created_by_id = request.user.id
			code.longitude = longitude
			code.latitude = latitude
			code.status = status
			code.profile_pic = profile_pic
			code.types = profile_type
			code.original_id = request.user.id
			code.save()
			for i in range(1,int(picture_length)+1) :
				picture = request.FILES.get('picture%s' % i)
				if int(profile_type) == 1:
					data=CompanyImages(profile=code,images=picture)
					data.save()
				else:
					data=UserPic(profile=code,images=picture)
					data.save()			
			if int(profile_type) == 1:
				if companyid:
					content = {
					'status':'success',
					'message':'Company profile updates successfully.',
					"data":{
						"id":code.id
					}
					}
				else:
					content = {
					'status':'success',
					'message':'Company profile created successfully.',
					"data":{
						"id":user.id
					}
					}
			else:
				if companyid:
					content = {
						'status':'success',
						'message':'User profile updates successfully.',
						"data":{
							"id":user.id,
							"name":user.first_name,
							"email":user.email,
							"phonenumber":code.phone,
							"profile_pic":code.getSingleImageUrl()
						}
					}
				else:
					content = {
						'status':'success',
						'message':'User profile craeted successfully.',
						"data":{
							"id":user.id,
							"name":user.first_name,
							"email":user.email,
							"phonenumber":code.phone,
							"profile_pic":code.getSingleImageUrl()
						}
					}
			return Response(content)
		except Exception as e:
			raise e
			raise exceptions.ParseError("Incorrect access token.")


class CompanyList(views.APIView):
	authentication_classes = ( SessionAuthentication,JSONWebTokenAuthentication)
	permission_classes = (IsAuthenticated,)
	def get(self,request):
		try:
			obj = CompanyProfile.objects.filter(owner=request.user)
			emptylist = []
			for company in obj:
				fdict = {}
				companyname = company.companyname
				legalentitytype = company.legalentitytype
				legal = ""
				if legalentitytype:
					legal = legalentitytype.name
					legalentitytypeid = legalentitytype.id
				street = company.street
				city = company.city
				country = company.country
				postcode = company.postcode
				longitude = company.longitude
				latitude = company.latitude
				phonenumber_status = False
				website = ""
				website_status = False
				descripiton = ""
				phonenumber = ""
				if company.details:
					phonenumber = company.details.phonenumber
					phonenumber_status = company.details.phonenumber_status
					website = company.details.website
					website_status = company.details.website_status
					descripiton = company.details.descripiton

				image1 = company.getSingleImageUrl()
				status = company.status
				companyname_status = company.companyname_status
				legalentitytype_status = company.legalentitytype_status
				city_status = company.city_status
				street_status = company.street_status
				country_status = company.country_status
				postcode_status = company.postcode_status
				fdict['id'] = company.id
				fdict['companyname'] = companyname
				fdict['legalentitytypeid'] = legalentitytypeid
				fdict['legalentitytype'] = legal
				fdict['street'] = street
				fdict['city'] = city
				fdict['country'] = country
				fdict['postcode'] = postcode
				fdict['longitude'] = longitude
				fdict['latitude'] = latitude
				fdict['phonenumber'] = phonenumber
				fdict['phonenumber_status'] = phonenumber_status
				fdict['website'] = website
				fdict['website_status'] = website_status
				fdict['description'] = descripiton
				fdict['image'] = image1
				fdict['status'] = status
				fdict['companyname_status'] = companyname_status
				fdict['legalentitytype_status'] = legalentitytype_status
				fdict['city_status'] = city_status
				fdict['street_status'] = street_status
				fdict['country_status'] = country_status
				fdict['postcode_status'] = postcode_status
				emptylist.append(fdict)
			content = {
			'status':'success',
			'comapnydata': emptylist
			}
			return Response(content)
		except Exception as e:
			raise e
			raise exceptions.ParseError("Incorrect access token.")


class Location(views.APIView):

	def post(self,request):
		try:
			obj1 = request.data.get('latitude')
			if not obj1:
				obj1 = request.POST.get('latitude')
			obj2 = request.data.get('longitude')
			if not obj2:
				obj2 = request.POST.get('latitude')
			latitude = float(obj1)
			if not obj1 or not obj2:
				content = {
				'status':'error',
				'message':"Cordinates must be provided."
				}
				return Response(content)
			longitude = float(obj2)
			companydistances = CompanyProfile.objects.raw('Select * from (SELECT *,  ( 3959 * acos( cos( radians(%s) ) * cos( radians( latitude ) )* cos( radians( longitude ) - radians(%s) ) + sin( radians(%s) ) * sin(radians(latitude)) ) ) AS distance FROM t_company_profile ) al  where distance < 10 ORDER BY distance; ' % (latitude,longitude,latitude))
			profiledistance = Profile.objects.raw('Select * from (SELECT *,  ( 3959 * acos( cos( radians(%s) ) * cos( radians( latitude ) )* cos( radians( longitude ) - radians(%s) ) + sin( radians(%s) ) * sin(radians(latitude)) ) ) AS distance FROM t_user_profile ) al  where distance < 10 ORDER BY distance ; ' % (latitude,longitude,latitude))
			emptylist = []
			for objs in companydistances:
				if objs.status:
					emptydict = {}
					companyname = objs.companyname
					companyid = objs.id
					companydistance = objs.distance
					companylongitude = objs.longitude
					companylatitude = objs.latitude
					emptydict['companyname'] = companyname
					emptydict['companyid'] = companyid
					emptydict['companylongitude'] = companylongitude
					emptydict['companylatitude'] = companylatitude
					emptydict['companydistance'] = companydistance
					emptydict['profile_type'] = 1
					emptydict['profile_image'] = objs.getSingleImageUrl()
					emptydict['other_images'] = objs.getAllImages()
					emptydict['location'] = objs.city
					emptydict['location_status'] = objs.city_status
					emptydict['legalentitytypeid'] = objs.legalentitytype.id
					emptydict['legalentitytype'] = objs.legalentitytype.name
					emptydict['street'] = objs.street
					emptydict['city'] = objs.city
					emptydict['country'] = objs.country
					emptydict['postcode'] = objs.postcode
					emptydict['status'] = objs.status
					emptydict['companyname_status'] = objs.companyname_status
					emptydict['legalentitytype_status'] = objs.legalentitytype_status
					emptydict['city_status'] = objs.city_status
					emptydict['street_status'] = objs.street_status
					emptydict['country_status'] = objs.country_status
					emptydict['postcode_status'] = objs.postcode_status
					emptydict['distance_status'] = True
					emptydict['activity'] = ""
					emptydict['activity_status']= objs.activity_status
					if objs.details:
						emptydict['description'] = objs.details.descripiton
						emptydict['phonenumber'] = objs.details.phonenumber
						emptydict['phonenumber_status'] = objs.details.phonenumber_status
						emptydict['website'] = objs.details.website
						emptydict['website_status'] = objs.details.website_status
						emptydict['activity'] = objs.details.activties.activties
					emptylist.append(emptydict)
			for objs in profiledistance:
				if objs.status:
					emptydict = {}
					companyname = objs.companyname
					companyid = objs.id
					companydistance = objs.distance
					companylongitude = objs.longitude
					companylatitude = objs.latitude
					emptydict['companyname'] = companyname
					emptydict['companyid'] = companyid
					emptydict['companylongitude'] = companylongitude
					emptydict['companylatitude'] = companylatitude
					emptydict['companydistance'] = companydistance
					emptydict['profile_type'] = 0
					emptydict['profile_image'] = objs.getSingleImageUrl()
					emptydict['other_images'] = objs.getAllImages()
					emptydict['location'] = objs.city
					emptydict['location_status'] = objs.city_status
					emptydict['legalentitytypeid'] = objs.legalentitytype.id
					emptydict['legalentitytype'] = objs.legalentitytype.name
					emptydict['street'] = objs.state
					emptydict['city'] = objs.city
					emptydict['country'] = objs.country
					emptydict['postcode'] = objs.postcode
					emptydict['status'] = objs.status
					emptydict['companyname_status'] = objs.companyname_status
					emptydict['legalentitytype_status'] = objs.legalentitytype_status
					emptydict['city_status'] = objs.city_status
					emptydict['street_status'] = objs.state_status
					emptydict['country_status'] = objs.country_status
					emptydict['postcode_status'] = objs.postcode_status
					emptydict['distance_status'] = True
					emptydict['activity'] = ""
					emptydict['activity_status']= objs.activity_status
					if objs.details:
						emptydict['description'] = objs.details.descripiton
						emptydict['phonenumber'] = objs.details.phonenumber
						emptydict['phonenumber_status'] = objs.details.phonenumber_status
						emptydict['website'] = objs.details.website
						emptydict['website_status'] = objs.details.website_status
						emptydict['activity'] = objs.details.activties.activties
					emptylist.append(emptydict)
				emptylist.sort(key=lambda k : k['companydistance'])
			content = {
			'status':'success',
			'data':emptylist
			}
			return Response(content)
		except Exception as e:
			print(str(e))
			raise exceptions.ParseError(str(e))







def distanceCal(lon1, lat1, lon2, lat2):
	"""
	Calculate the great circle distance between two points 
	on the earth (specified in decimal degrees)
	"""
	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
	print(lon1)
	print(lon1)
	# haversine formula 
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	r = 6371 # Radius of earth in kilometers. Use 3956 for miles
	return c * r


class Search(views.APIView):
	def post(self,request):
		try:
			keyword = request.data.get('Keyword')
			longitude = request.data.get('longitude')
			latitude = request.data.get('latitude')
			NElongitude = request.data.get("NElongitude")
			NElatitude = request.data.get("NElatitude")
			clongitude = request.data.get("current_long")
			clatitude = request.data.get("current_lat")
			long_list = []
			lat_list = []
			if str(longitude) == "0":
				longitude = None
			if str(latitude) == "0":
				latitude = None
			if not keyword:
				raise exceptions.ParseError("Search keyword cannot be empty.")	

			companysearch = CompanyProfile.objects.filter(Q(companyname__icontains=keyword) | Q(details__descripiton__icontains=keyword) | Q(details__activties__activties__icontains=keyword) )
			profilesearch = Profile.objects.filter((Q(companyname__icontains=keyword)| Q(details__descripiton__icontains=keyword)| Q(details__activties__activties__icontains=keyword)))

			emptylist = []

			"""
			 call function distanceCal using request parameters i.e
				longitude
				latitude
				NElongitude
				NElatitude
			then save return result in a variable
			intial_distance
			"""
			intial_distance = 10
			if NElongitude and NElatitude:
				intial_distance = distanceCal(float(longitude),float(latitude),float(NElongitude),float(NElatitude))		
			# companydistances = CompanyProfile.objects.raw('Select * from (SELECT *,  ( 3959 * acos( cos( radians(%s) ) * cos( radians( latitude ) )* cos( radians( longitude ) - radians(%s) ) + sin( radians(%s) ) * sin(radians(latitude)) ) ) AS distance FROM t_company_profile) al where distance < 10 ORDER BY distance; ' % (latitude,longitude,latitude))
			# print(dir(companydistances))
			# profiledistance = Profile.objects.raw('Select * from (SELECT *,  ( 3959 * acos( cos( radians(%s) ) * cos( radians( latitude ) )* cos( radians( longitude ) - radians(%s) ) + sin( radians(%s) ) * sin(radians(latitude)) ) ) AS distance FROM t_user_profile ) al where distance < 10 ORDER BY distance; ' % (latitude,longitude,latitude))

			for company in companysearch:
				if company.status:
					company_lontitude = company.longitude
					company_latitude = company.latitude
					company_distance =  distanceCal(longitude,latitude,company_lontitude,company_latitude)
					if company_distance <= intial_distance:
						emptydict = {}
						long_list.append(company.longitude)
						lat_list.append(company.latitude)
						emptydict['companyname'] = company.companyname
						emptydict['id'] = company.id
						emptydict['longitude'] = company.longitude
						emptydict['latitude'] = company.latitude
						emptydict['profile_type'] = 1

						emptydict['profile_image'] = company.getSingleImageUrl()
						emptydict['other_images'] = company.getAllImages()
						if clongitude and clatitude:
							emptydict['companydistance'] = distanceCal(clongitude,clatitude,company_lontitude,company_latitude)
						else:
							emptydict['companydistance'] = company_distance
						emptydict['location'] = company.street
						emptydict['legalentitytype'] = company.legalentitytype.name
						emptydict['legalentityid'] = company.legalentitytype.id
						emptydict['street'] = company.street
						emptydict['city'] = company.city
						emptydict['country'] = company.country
						emptydict['postcode'] = company.postcode
						emptydict['description'] = ""
						emptydict['phonenumber'] = ""
						emptydict['phonenumber_status'] = False
						emptydict['website'] = ""
						emptydict['website_status'] = False
						emptydict['activity'] = ""
						emptydict['activity_status']= company.activity_status
						if company.details:
							emptydict['description'] = company.details.descripiton
							emptydict['phonenumber'] = company.details.phonenumber
							emptydict['phonenumber_status'] = company.details.phonenumber_status
							emptydict['website'] = company.details.website
							emptydict['website_status'] = company.details.website_status
							emptydict['activity'] = company.details.activties.activties
						emptydict['status'] = company.status
						emptydict['companyname_status'] = company.companyname_status
						emptydict['legalentitytype_status'] = company.legalentitytype_status
						emptydict['city_status'] = company.city_status
						emptydict['street_status'] = company.street_status
						emptydict['country_status'] = company.country_status
						emptydict['postcode_status'] = company.postcode_status
						emptydict['distance_status'] = True
						emptylist.append(emptydict)
			
			for indivisual in profilesearch:
				if indivisual.status:
					indivisual_lontitude = indivisual.longitude
					indivisual_latitude = indivisual.latitude
					indivisual_distance =  distanceCal(longitude,latitude,indivisual_lontitude,indivisual_latitude)
					if indivisual_distance <= intial_distance:
						emptydict = {}
						long_list.append(indivisual.longitude)
						lat_list.append(indivisual.latitude)
						emptydict['companyname'] = indivisual.companyname
						emptydict['id'] = indivisual.id
						emptydict['longitude'] = indivisual.longitude
						emptydict['latitude'] = indivisual.latitude
						emptydict['profile_type'] = 0
						emptydict['description'] = indivisual.details.descripiton
						emptydict['location'] = indivisual.state
						emptydict['legalentitytype'] = indivisual.legalentitytype.name
						emptydict['legalentityid'] = indivisual.legalentitytype.id
						emptydict['street'] = indivisual.state
						emptydict['city'] = indivisual.city
						emptydict['country'] = indivisual.country
						emptydict['postcode'] = indivisual.postcode
						emptydict['description'] = ""
						emptydict['phonenumber'] = ""
						emptydict['phonenumber_status'] = False
						emptydict['website'] = ""
						emptydict['website_status'] = False
						emptydict['activity'] = ""
						emptydict['activity_status']= indivisual.activity_status
						if indivisual.details:
							emptydict['description'] = indivisual.details.descripiton
							emptydict['phonenumber'] = indivisual.details.phonenumber
							emptydict['phonenumber_status'] = indivisual.details.phonenumber_status
							emptydict['website'] = indivisual.details.website
							emptydict['website_status'] = indivisual.details.website_status
							emptydict['activity'] = indivisual.details.activties.activties
						emptydict['status'] = indivisual.status
						emptydict['companyname_status'] = indivisual.companyname_status
						emptydict['legalentitytype_status'] = indivisual.legalentitytype_status
						emptydict['city_status'] = indivisual.city_status
						emptydict['street_status'] = indivisual.state_status
						emptydict['country_status'] = indivisual.country_status
						emptydict['postcode_status'] = indivisual.postcode_status
						emptydict['profile_image'] = indivisual.getSingleImageUrl()
						emptydict['other_images'] = indivisual.getAllImages()
						if clongitude and clatitude:
							emptydict['companydistance'] = distanceCal(clongitude,clatitude,indivisual_lontitude,indivisual_latitude)
						else:
							emptydict['companydistance'] = indivisual_distance
						emptydict['distance_status'] = True
						emptylist.append(emptydict)
			# print(emptylist)
			if emptylist:
				if len(lat_list) == 1:
					centred_lat = lat_list[0]
					centred_long = long_list[0]
				else:
					centred_lat = sum(lat_list)/len(lat_list)
					centred_long = sum(long_list)/len(long_list)
				content = {
				'status':'success',
				'comapnydata': emptylist,
				'centred_cordinates':{"lat":centred_lat,"long":centred_long}
				}
				return Response(content)
			else:
				raise exceptions.ParseError("No result found.")
		except Exception as e:
			raise e
			raise exceptions.ParseError("Invalid Search.")

		

class Message(views.APIView):
	def post(self, request, *args, **kwargs):
		print(request.data)
		try:
			user_id = request.data.get("id")
			if not user_id:
				user_id = request.POST.get("id")
			email = request.data.get("email")
			if not email:
				email = request.POST.get("email")
			name = request.data.get("name")
			if not email:
				name = request.POST.get("name")
			message = request.data.get("message")
			if not message:
				message = request.POST.get("message")
			profile_types = request.data.get("profile_type")
			profile_type = str(profile_types)
			if not profile_type:
				profile_type = request.POST.get("profile_type")
			full_message = """You have got new message from """
			full_message += "\n"+name+"\n"
			full_message += "\n"+email+"\n"

			full_message += message
			if not email:
				raise exceptions.ParseError("email cannot be blank.")
			elif not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
				raise exceptions.ParseError("enter valid email address.")
			elif not message:
				raise exceptions.ParseError("message cannot be blank .")

			user_mail = None
			if int(profile_type)==1:
				user=CompanyProfile.objects.get(id=user_id)
				user_mail = user.owner.email
			else:
				user=Profile.objects.get(id=user_id)
				user_mail = user.users.email
				# user = User.objects.get(id=user_id)
				# user_mail = user.email

			if user_mail:
				email = EmailMessage('Message', full_message , to=[user_mail])
				email.send()
				content = {
					'status':'success',
					'message':'message sent .'
				}
			else:
				content = {
					'status':'error',
					'message':'message sent failed.'
				}
		
			return Response(content)
		except Exception as e:
			raise e
			raise exceptions.ParseError("Incorrect access token.")


class Activities(views.APIView):
	
	def get(self, request, *args, **kwargs):
		user_type = request.data.get("user_type")
		if not user_type:
				user_type = request.GET.get("user_type")
		activities = []
		if int(user_type) == 1:
			activities = CompanyActivties.objects.all()
		else:
			activities = Activties.objects.all()
		activities_list = []
		for activity in activities:
			activities_list.append({"id":activity.id,"name":activity.activties})
		response = {
			"status":'success',
			"data":activities_list
		}
		return Response(response)


class LegelEntityView(views.APIView):

	def get(self, request):
		legalentitytype = LegelEntity.objects.all()
		legalentitytype_list = []
		for legalentitytypes in legalentitytype:
			legalentitytype_list.append({"id":legalentitytypes.id,"name":legalentitytypes.name})
		response = {
			"status":'success',
			"data":legalentitytype_list
		}
		return Response(response)


class MarkersImages(views.APIView):
	def get(self, request, *args, **kwargs):
		response = {
			"status":'success',
			"data":{
			"comapny_marker":settings.BASE_URL+"/media/images/individual.png",
			"current_marker":settings.BASE_URL+"/media/images/current_location.png",
			"individual_marker":settings.BASE_URL+"/media/images/company.png"
			}
		}
		return Response(response)



class DeleteCompany(views.APIView):
	authentication_classes = ( SessionAuthentication,JSONWebTokenAuthentication)
	permission_classes = (IsAuthenticated,)
	def post(self, request, *args, **kwargs):
		company_id = request.data.get("id")
		if not company_id:
			company_id = request.POST.get("id")
		CompanyProfile.objects.filter(id=int(company_id)).delete()
		return Response({
			"status":'success',
			"message":"Company is deleted successfully."
			})


class SearchLocation(views.APIView):
	def get(self,request,):
		try:
			company_list=[]
			

			keyword=request.data.get('keyword','')
			
			if not keyword:
				keyword = request.GET.get('keyword','')
			print(">>>>>",keyword)
			company_name = CompanyProfile.objects.filter(companyname__icontains=keyword).values('companyname')
		
			profile_company = Profile.objects.filter(companyname__icontains=keyword).values('companyname')
			
			Q = list(chain(company_name , profile_company))
			#Combined_Q = company_name | profile_company
			# company_list.append(company_name)
			# profile_list.append(profile_company)
			# profile_list.extend(company_list)
			response = {
			"status":'success',
			"data": Q
			}
			return Response(response)

		except Exception as e:
			raise e
			raise exceptions.ParseError("Invalid Search.")


