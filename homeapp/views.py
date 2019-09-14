# -*- coding: utf-8 -*-

from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView, View
from django.contrib import messages
import csv
from django.contrib.auth.models import User
from api.models import *





class Homepage(TemplateView):
	template_name = 'index.html'
	def get(self, request, *arges, **kwargs):

		return render(request, self.template_name, locals())

	def post(self, request, *arges, **kwargs):
		user_file = request.FILES["userdata"]
		decode_file = user_file.read().decode('utf-8').splitlines()
		reader = csv.DictReader(decode_file)
		is_error = False
		for data in reader:
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
				legelentuty = LegelEntity.objects.all()[0]
				activities = ActivtiesDetail.objects.all()[0]

				customer = Profile.objects.create(
					users=user,
					companyname=data["name"],
					phone=data["phone"],
					city=data["city"],
					state=data["state"],
					country=data["country"],
					postcode=data["postcode"],
					longitude=data["longitude"],
					latitude=data["latitude"],
					legalentitytype=legelentuty,
					details=activities,
					types=1,
				)
				customer.save()
			except Exception as e:
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
			try:
				user = User.objects.filter(email=data["user_email"])
				existing_profile = Profile.objects.filter(companyname=data["name"],phone=data["phone"])
				if not user or existing_profile:
					continue
				legelentuty = LegelEntity.objects.all()[0]
				activities = CompanyActivtiesDetail.objects.all()[0]

				company = CompanyProfile.objects.create(
					users=user,
					companyname=data["name"],
					phone=data["phone"],
					city=data["city"],
					street=data["street"],
					country=data["country"],
					postcode=data["postcode"],
					longitude=data["longitude"],
					latitude=data["latitude"],
					legalentitytype=legelentuty,
					details=activities,
					types=1,
				)
				company.save()
			except Exception as e:
				is_error=True
				raise e
		if is_error:
			messages.success(request, 'Error occured in some data')
		else:
			messages.success(request, 'Data imported.')
		return HttpResponseRedirect("/importdata")