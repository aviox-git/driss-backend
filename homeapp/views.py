# -*- coding: utf-8 -*-

from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView, View
from django.contrib import messages
import csv
from django.contrib.auth.models import User
from api.models import *
import requests,json
from rest_framework import views
from rest_framework.response import Response




class Homepage(TemplateView):
	template_name = 'index.html'
	def get(self, request, *arges, **kwargs):

		return render(request, self.template_name, locals())

	def post(self, request, *arges, **kwargs):

		user_file = request.FILES["userdata"]
		# print(">>>>>>>>>",user_file)
		decode_file = user_file.read().decode('utf-8').splitlines()
		reader = csv.DictReader(decode_file)
		# print(">>>>",reader)
		is_error = False
		for data in reader:
			address = data['address']

			url = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key=AIzaSyDf67nsesrgDWDzIcD8aPYPsRCZ3RuLEvI')
			
			map_api_result = url.json()
			cordinates = {}
			try:
				cordinates = map_api_result["results"][0]["geometry"]["location"]
			except IndexError:
				continue
			
			if not cordinates:
				continue

			try:
				existing_user = User.objects.filter(email=data["email"])
				existing_profile = Profile.objects.filter(phone=data["phone"])
				if existing_user or existing_profile:
					continue
				user = User.objects.create_user(
						first_name=data["name"],
						username=data["email"],
						email=data["email"]
					)
				user.set_password(data["password"])
				user.save()
				

				legelentuty,created = LegelEntity.objects.get_or_create(name=data["name"])

				activity,created = Activties.objects.get_or_create(activties=data["activties"]) 
				
				activities,created = ActivtiesDetail.objects.get_or_create(activties=activity, phonenumber=data["phone"],website=data["website"],descripiton=data["descripiton"])


				customer = Profile.objects.create(
					users=user,
					companyname=data["name"],
					phone=data["phone"],
					city=data["city"],
					state=data["state"],
					country=data["country"],
					postcode=data["postcode"],
					longitude=cordinates["lng"],
					latitude=cordinates["lat"],
					
					legalentitytype=legelentuty,
					details=activities,
					types=1
				)
				print("customer>>>>",customer)
				customer.save()
			except Exception as e:
				# raise e
				is_error=True
				pass


		if is_error:
			messages.success(request, 'Error occured in some data')
		else:
			messages.success(request, 'Data imported.')
		return HttpResponseRedirect("/importdata")

class CompanyData(View):
	def post(self, request, *arges, **kwargs):
		company_file = request.FILES["companydata"]
		decode_file = company_file.read().decode('utf-8').splitlines()
		reader = csv.DictReader(decode_file)
		is_error = False
		for data in reader:

			address = data['address']
			url = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key=AIzaSyDf67nsesrgDWDzIcD8aPYPsRCZ3RuLEvI')
			
			map_api_result = url.json()
			cordinates = {}
			try:
				cordinates = map_api_result["results"][0]["geometry"]["location"]
			except IndexError:
				continue

			if not cordinates:
				continue

			try:
				user = User.objects.filter(email=data["user_email"])
				
				if not user:
					continue
				
				legelentuty,created  = LegelEntity.objects.get_or_create(name=data["name"])
				print("legelentuty>>>>>>..",legelentuty)

				activity,created = CompanyActivties.objects.get_or_create(activties=data["activties"]) 
				print("activity>>>",activity)

				activities,created = CompanyActivtiesDetail.objects.get_or_create(activties=activity,phonenumber=data['phone'],website=data["website"],descripiton=data["descripiton"])
				print(">>>>activities",activities)
				company = CompanyProfile.objects.create(
					owner=user[0],
					companyname=data["name"],
					city=data["city"],
					street=data["street"],
					country=data["country"],
					postcode=data["postcode"],
					longitude=cordinates["lng"], 
					latitude=cordinates["lat"],
					legalentitytype=legelentuty,
					details=activities,
					types=0
				)
				company.save()
			except Exception as e:
				is_error=True
				# raise e
		if is_error:
			messages.success(request, 'Error occured in some data')
		else:
			messages.success(request, 'Data imported.')
		return HttpResponseRedirect("/importdata")