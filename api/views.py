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


def generateOTP(): 
	digits = "0123456789"
	OTP = "" 
	for i in range(4): 
		OTP += digits[math.floor(random.random() * 10)] 

	return OTP



class CustomAuthentication(authentication.BaseAuthentication):


	def authenticate(self, request):
		username = request.data['username']
		password = request.data['password']
		user_type = request.data['user_type']
		if user_type==0:
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
				user = User.objects.get(email=username)
			except User.DoesNotExist:
				raise exceptions.AuthenticationFailed('Invalid social account id.')

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
		elif number_length < 10:
			
			raise exceptions.ParseError("Please enter 10 digit mobile number.")
		elif number_length > 10:
			
			raise exceptions.ParseError("Please enter 10 digit mobile number.")
		else:

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
					code = Profile.objects.filter(id=company_id)
					emptylist = []
				previouswork = []
				for company in code:
					fdict = {}
					previouswork = company.getAllImages()
					if company.profile_pic:
						pictures = company.getSingleImageUrl()
					else:
						pictures = ""
					companyname = company.companyname
					legal = ""
					if company.legalentitytype:
						legal = company.legalentitytype.name
					print(legal)
					legalentitytype = str(legal)
					if int(profile_type) == 1:
						street = company.street
					else:
						state = company.state
					city = company.city
					country = company.country
					postcode = company.postcode
					longitude = company.longitude
					latitude = company.latitude
					phonenumber = ""
					website = ""
					descripiton = ""
					if company.details:
						phonenumber = company.details.phonenumber
						website = company.details.website
						descripiton = company.details.descripiton
					status = company.status
					companyname_status = company.companyname_status
					legalentitytype_status = company.legalentitytype_status
					city_status = company.city_status
					if int(profile_type) == 1:
						street_status = company.street_status
					else:
						state_status = company.state_status
					country_status = company.country_status
					postcode_status = company.postcode_status
					
					fdict['companyname'] = companyname
					fdict['legalentitytype'] = legalentitytype
					fdict['profile_pic'] = pictures
					if int(profile_type) == 1:
						fdict['street'] = street
					else:
						fdict['state'] = state
					fdict['city'] = city
					fdict['country'] = country
					fdict['postcode'] = postcode
					fdict['longitude'] = longitude
					fdict['latitude'] = latitude
					fdict['phonenumber'] = phonenumber
					fdict['website'] = website
					fdict['descripiton'] = descripiton
					fdict['status'] = status
					fdict['companyname_status'] = companyname_status
					fdict['legalentitytype_status'] = legalentitytype_status
					fdict['city_status'] = city_status
					if int(profile_type) == 1:
						fdict['street_status'] = street_status
					else:
						fdict['state_status'] = state_status
					
					fdict['country_status'] = country_status
					fdict['postcode_status'] = postcode_status
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
			print(request.FILES)
			print(request.POST)
	
			companyname = request.data.get("name")
			companyid = request.data.get('companyid')
			profile_pic = request.FILES.get('profile_pic')
			legalentitytype = request.data.get('legalentitytype')
			street = request.data.get('street')
			state = request.data.get("state")
			city = request.data.get('city')
			country = request.data.get('country')
			postalcode = request.data.get('postalcode')
			longitude = request.data.get('longitude')
			latitude = request.data.get('latitude')
			activties = request.data.get('activties')
			phonenumber = request.data.get('phonenumber')
			website = request.data.get('website')
			descripiton = request.data.get('descripiton')
			status = request.data.get('published_status')
			profile_type = request.data.get('profile_type')
			companynames_status = request.data.get('name_status')
			legalentitytype_status = request.data.get('legalentitytype_status')
			city_status = request.data.get('city_status')
			street_status = request.data.get('street_status')
			state_status = request.data.get('state_status')
			country_status = request.data.get('country_status')
			postcode_status = request.data.get('postcode_status') 
			picture_length = request.data.get("picture_length")


			if status=="true":
				status = 1
			else:
				status = 0
			if companynames_status=="true":
				companynames_status = 1
			else:
				companynames_status = 0
			if legalentitytype_status=="true":
				legalentitytype_status = 1
			else:
				legalentitytype_status = 0
			
			if city_status=="true":
				city_status = 1
			else:
				city_status = 0
		
			
			if country_status=="true":
				country_status = 1
			else:
				country_status = 0
			
			if postcode_status=="true":
				postcode_status = 1
			else:
				postcode_status = 0
			legal,created = LegelEntity.objects.get_or_create(name=legalentitytype)
			if int(profile_type) == 1:
				act,created = CompanyActivties.objects.get_or_create(activties=activties)
				det, created = CompanyActivtiesDetail.objects.get_or_create(activties=act)
				det.phonenumber = phonenumber
				det.website = website
				det.descripiton = descripiton
				det.save()
			else:
				act,created = Activties.objects.get_or_create(activties=activties)
				det, created = ActivtiesDetail.objects.get_or_create(activties=act)
				det.phonenumber = phonenumber
				det.website = website
				det.descripiton = descripiton
				det.save()
			if int(profile_type) == 1:
				if companyid:
					code = CompanyProfile.objects.get(id=companyid)
				else:
					code = CompanyProfile.objects.create(owner=request.user)
			else:
				if companyid:
					code = Profile.objects.get(id=companyid)
				else:
					code = Profile.objects.get(users=request.user)

			code.modver_datetime = timezone.now()
			# code.profile_pic = picture
			code.companyname = companyname
			code.legalentitytype = legal
			if int(profile_type) == 1:
				code.street = street
			else:
				code.state = state
			if int(profile_type) == 1:
				if street_status=="true":
					street_status = 1
				else:
					street_status = 0
			else:
				if state_status=="true":
					state_status = 1
				else:
					state_status = 0
			
	
			code.city = city
			code.country = country
			code.postcode = postalcode
			code.companyname_status = companynames_status
			code.legalentitytype_status = legalentitytype_status
			code.city_status = city_status
			code.street_status = street_status
			code.country_status = country_status
			code.postcode_status = postcode_status
			code.created_by_id = request.user.id
			code.longitude = longitude
			code.latitude = latitude
			code.details = det
			code.status = status
			code.profile_pic = profile_pic
			code.types = profile_type
			code.original_id = request.user.id
			code.save()
			for i in range(1,int(picture_length)+1) :
				picture = request.FILES.get('picture%s' % i)
				print(picture)
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
						"id":code.id
					}
					}
			else:
				if companyid:
					content = {
					'status':'success',
					'message':'User profile updates successfully.',
					"data":{
						"id":code.id
					}
					}
				else:
					content = {
					'status':'success',
					'message':'User profile craeted successfully.',
					"data":{
						"id":code.id
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
			obj = CompanyProfile.objects.filter(status="1")
			print(obj)
			emptylist = []
			for company in obj:
				fdict = {}
				companyname = company.companyname
				legalentitytype = company.legalentitytype
				legal = legalentitytype.name
				street = company.street
				city = company.city
				country = company.country
				postcode = company.postcode
				longitude = company.longitude
				latitude = company.latitude
				phonenumber = company.details.phonenumber
				website = company.details.website
				descripiton = company.details.descripiton

				image1 = company.getSingleImageUrl()
				status = company.status
				companyname_status = company.companyname_status
				legalentitytype_status = company.legalentitytype_status
				city_status = company.city_status
				street_status = company.street_status
				country_status = company.country_status
				postcode_status = company.postcode_status
				fdict['companyname'] = companyname
				fdict['legalentitytype'] = legal
				fdict['street'] = street
				fdict['city'] = city
				fdict['country'] = country
				fdict['postcode'] = postcode
				fdict['longitude'] = longitude
				fdict['latitude'] = latitude
				fdict['phonenumber'] = phonenumber
				fdict['website'] = website
				fdict['descripiton'] = descripiton
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
			latitude = float(obj1)
			obj2 = request.data.get('longitude')
			longitude = float(obj2)
			companydistances = CompanyProfile.objects.raw('Select * from (SELECT *,  ( 3959 * acos( cos( radians(%s) ) * cos( radians( latitude ) )* cos( radians( longitude ) - radians(%s) ) + sin( radians(%s) ) * sin(radians(latitude)) ) ) AS distance FROM t_company_profile ) al  where distance < 10 ORDER BY distance; ' % (latitude,longitude,latitude))
			profiledistance = Profile.objects.raw('Select * from (SELECT *,  ( 3959 * acos( cos( radians(%s) ) * cos( radians( latitude ) )* cos( radians( longitude ) - radians(%s) ) + sin( radians(%s) ) * sin(radians(latitude)) ) ) AS distance FROM t_user_profile ) al  where distance < 10 ORDER BY distance ; ' % (latitude,longitude,latitude))
			emptylist = []
			combined = list(companydistances) + list(profiledistance)
			for objs in combined:
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
				emptylist.append(emptydict)

			emptylist.sort(key=lambda k : k['companydistance'])
			content = {
			'status':'success',
			'comapnydata':emptylist
			}
			return Response(content)
		except Exception as e:
			print(str(e))
			raise exceptions.ParseError("Invalid coordinates.")







def distanceCal(lon1, lat1, lon2, lat2):
	"""
	Calculate the great circle distance between two points 
	on the earth (specified in decimal degrees)
	"""
	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])

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

			if not keyword:
				raise exceptions.ParseError("Search keyword cannot be empty.")	

			companysearch = CompanyProfile.objects.filter(Q(companyname__icontains=keyword) | Q(details__descripiton__icontains=keyword) | Q(details__activties__activties__icontains=keyword) )
			profilesearch = Profile.objects.filter((Q(companyname__icontains=keyword)| Q(details__descripiton__icontains=keyword)| Q(details__activties__activties__icontains=keyword)))
			emptylist = []
			if keyword and not longitude and not longitude:

				for company in companysearch:
					emptydict = {}
					emptydict['companyname'] = company.companyname
					emptydict['id'] = company.id
					emptydict['longitude'] = company.longitude
					emptydict['latitude'] = company.latitude
					emptydict['profile_type'] = 1
					emptydict['descripiton'] = company.details.descripiton
					emptydict['profile_image'] = company.getSingleImageUrl()
					emptydict['other_images'] = company.getAllImages()
					emptylist.append(emptydict)
				for indivisual in profilesearch:
					emptydict = {}
					emptydict['companyname'] = indivisual.companyname
					emptydict['id'] = indivisual.id
					emptydict['longitude'] = indivisual.longitude
					emptydict['latitude'] = indivisual.latitude
					emptydict['profile_type'] = 0
					emptydict['descripiton'] = indivisual.details.descripiton
					if indivisual.profile_pic:
						emptydict['profile_image'] = settings.BASE_URL+indivisual.profile_pic.url
					else:
						emptydict['profile_image'] = ""
					emptydict['other_images'] = indivisual.getAllImages()
					emptylist.append(emptydict)
				# print(emptylist)
				if emptylist:
					content = {
					'status':'success',
					'comapnydata': emptylist
					}
					return Response(content)
				else:
					raise exceptions.ParseError("No result found.")
			else:
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
					"""
					 call function distanceCal using request parameters i.e
						longitude
						latitude
						company.longitude
						company.latutude
					compare the return result with request parm return result
					if true then run the inner code otherwise 
					continue to next value in the loop
					(<=)
					company _distance
					company_distanc<=intial_distance
					"""
					company_lontitude = company.longitude
					company_latitude = company.latitude
					company_distance =  distanceCal(longitude,latitude,company_lontitude,company_latitude)
					if company_distance <= intial_distance:
						emptydict = {}
						emptydict['companyname'] = company.companyname
						emptydict['id'] = company.id
						emptydict['longitude'] = company.longitude
						emptydict['latitude'] = company.latitude
						emptydict['profile_type'] = 1
						emptydict['descripiton'] = company.details.descripiton
						emptydict['profile_image'] = company.getSingleImageUrl()
						emptydict['other_images'] = company.getAllImages()
						emptydict['distance'] = company_distance
						emptylist.append(emptydict)
				
				for indivisual in profilesearch:
					indivisual_lontitude = indivisual.longitude
					indivisual_latitude = indivisual.latitude
					indivisual_distance =  distanceCal(longitude,latitude,indivisual_lontitude,indivisual_latitude)
					if indivisual_distance <= intial_distance:
						emptydict = {}
						emptydict['companyname'] = indivisual.companyname
						emptydict['id'] = indivisual.id
						emptydict['longitude'] = indivisual.longitude
						emptydict['latitude'] = indivisual.latitude
						emptydict['profile_type'] = 0
						emptydict['descripiton'] = indivisual.details.descripiton
						if indivisual.profile_pic:
							emptydict['profile_image'] = settings.BASE_URL+indivisual.profile_pic.url
						else:
							emptydict['profile_image'] = ""
						emptydict['other_images'] = indivisual.getAllImages()
						emptydict['distance'] = indivisual_distance
						emptylist.append(emptydict)
				# print(emptylist)
				if emptylist:
					content = {
					'status':'success',
					'comapnydata': emptylist
					}
					return Response(content)
				else:
					raise exceptions.ParseError("No result found.")
		except Exception as e:
			raise e
			raise exceptions.ParseError("Invalid Search.")

		

class Message(views.APIView):
	authentication_classes = ( SessionAuthentication,JSONWebTokenAuthentication)
	permission_classes = (IsAuthenticated,)
	def post(self, request, *args, **kwargs):
		try:
			email = request.data.get("email")
			
			message = request.data.get("message")
			if not email:
				raise exceptions.ParseError("email cannot be blank.")
			elif not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
				raise exceptions.ParseError("enter valid email address.")
			elif not message:
				raise exceptions.ParseError("message cannot be blank .")
			try:
				user = User.objects.get(email=email)
				if user is not None:
					email = EmailMessage('Message', message , to=[email])
					email.send()
			except User.DoesNotExist:
				raise exceptions.ParseError("email not registered .")
			content = {
			'status':'success',
			'message':'message sent .'
			}
			return Response(content)
		except Exception as e:
			raise e
			raise exceptions.ParseError("Incorrect access token.")


class Activities(views.APIView):
	authentication_classes = ( SessionAuthentication,JSONWebTokenAuthentication)
	permission_classes = (IsAuthenticated,)
	def get(self, request, *args, **kwargs):
		activities = Activties.objects.all()
		activities_list = []
		for activity in activities:
			activities_list.append({"id":activity.id,"name":activity.activties})
		response = {
			"status":'success',
			"data":activities_list
		}
		return Response(response)