from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


class Registration(serializers.Serializer):
	User_Name = serializers.CharField(label="Username")
	email = serializers.EmailField(label=("Email"))
	Password = serializers.CharField(label="Password", style={'input_type': 'password'})
	New_Password = serializers.CharField(label="New Password", style={'input_type': 'password'})
	Phone_Number = serializers.CharField(label="Phone Number")
	code = serializers.IntegerField()

	
	def validate(self, attrs):
		print("----------------------------------------------")
		
		email = attrs.get('email').lower()
		password = attrs.get('Password')
		newpassword = attrs.get('New_Password')
		username = attrs.get('User_Name')
		phone = attrs.get('Phone_Number')
		if password and username:
			user = User.objects.filter(username=User_Name)
			if user:
				attrs['msg'] = "Username already exists"
			else:
				attrs['msg'] = "Registration successful"
		else:
			attrs['msg'] = "All fields required."
		return attrs

class SocialSerializer(serializers.Serializer):
	provider = serializers.CharField(max_length=255, required=True)
	access_token = serializers.CharField(max_length=4096, required=True, trim_whitespace=True)

class CompanyProfileSerializer(serializers.Serializer):
	class Meta:
		model = CompanyProfile
		fields = "__all__"

class HomepageSerializer(serializers.Serializer):
	companyname = models.CharField()
	companyid = models.CharField()
	companydistance = models.FloatField()

