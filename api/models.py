from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from django.conf import settings

Status_Choices = (
	('1','Published'),
	('0','Unpublished'),
	)

Type_Choices = (
	("1",'Profile'),
	("0",'CompanyProfile'),
	)


class CustomerImages(models.Model):
	user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
	phone = models.BigIntegerField(blank=False, null=True, verbose_name='Phone Number')
	create_datetime  = models.DateTimeField(default=timezone.now,null=True,blank=True)
	modver_datetime = models.CharField(default='9999-12-31 00:00:00',max_length=100,null=True,blank=True)
	original_id = models.CharField(max_length=100,null=True,blank=True)
	created_by_id = models.CharField(max_length=100,null=True,blank=True)

	class Meta:
		db_table = "t_customer_image"

	def __str__(self):
		return self.user.first_name

class Activties(models.Model):
	activties = models.CharField(max_length=200,null=True, blank=True)
	create_datetime  = models.DateTimeField(default=timezone.now,null=True,blank=True)
	modver_datetime = models.CharField(default='9999-12-31 00:00:00',max_length=100,null=True,blank=True)
	original_id = models.CharField(max_length=100,null=True,blank=True)
	created_by_id = models.CharField(max_length=100,null=True,blank=True)

	class Meta:
		db_table = "t_activity"

class LegelEntity(models.Model):
	name = models.CharField(max_length=200,null=True, blank=True)
	create_datetime  = models.DateTimeField(default=timezone.now,null=True,blank=True)
	modver_datetime = models.CharField(default='9999-12-31 00:00:00',max_length=100,null=True,blank=True)
	original_id = models.CharField(max_length=100,null=True,blank=True)
	created_by_id = models.CharField(max_length=100,null=True,blank=True)

	class Meta:
		db_table = "t_legelentity"


class ActivtiesDetail(models.Model):
	activties = models.ForeignKey(Activties,on_delete=models.DO_NOTHING,null=True, blank=True)
	phonenumber = models.BigIntegerField(null=True, blank=True)
	phonenumber_status = models.BooleanField(null=True,blank=True,default=False)
	website = models.CharField(max_length=300,null=True, blank=True)
	website_status = models.BooleanField(null=True,blank=True)
	descripiton = models.TextField(null=True, blank=True)
	create_datetime  = models.DateTimeField(default=timezone.now,null=True,blank=True)
	modver_datetime = models.CharField(default='9999-12-31 00:00:00',max_length=100,null=True,blank=True)
	original_id = models.CharField(max_length=100,null=True,blank=True)
	created_by_id = models.CharField(max_length=100,null=True,blank=True)

	class Meta:
		db_table = "t_activity_detail"


class ForgotCode(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True)
	code = models.CharField(max_length=4)
	create_datetime = models.DateTimeField(default=timezone.now,null=True,blank=True)
	expiry_datetime = models.DateTimeField(null=True,blank=True)
	
	class Meta:
		db_table = "t_forgot_code"

	def __unicode__(self):
		return self.user

class Profile(models.Model):
	users = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
	phone = models.CharField(max_length=100,blank=False, null=True, verbose_name='Phone Number')
	profile_pic = models.ImageField(upload_to='profiles_pic/',null=True,blank=True)
	companyname = models.CharField(max_length=100,null=True,blank=True)
	companyname_status = models.BooleanField(null=True,blank=True,default=False)
	legalentitytype = models.ForeignKey(LegelEntity,on_delete=models.DO_NOTHING,null=True,blank=True)
	legalentitytype_status = models.BooleanField(null=True,blank=True,default=False)
	city = models.CharField(max_length=100,null=True,blank=True)
	city_status = models.BooleanField(null=True,blank=True,default=False)
	state = models.CharField(max_length=100,null=True,blank=True)
	state_status = models.BooleanField(null=True,blank=True,default=False)
	country = models.CharField(max_length=100,null=True,blank=True)
	country_status = models.BooleanField(null=True,blank=True,default=False)
	postcode = models.CharField(max_length=10,null=True,blank=True)
	postcode_status = models.BooleanField(null=True,blank=True,default=False)
	longitude = models.FloatField(null=True,blank=True)
	latitude  = models.FloatField(null=True,blank=True)
	details = models.ForeignKey(ActivtiesDetail,on_delete=models.DO_NOTHING,null=True,blank=True)
	status = models.CharField(max_length=100,choices=Status_Choices,null=True,blank=True)
	types = models.CharField(max_length=100,choices=Type_Choices,null=True,blank=True)
	create_datetime  = models.DateTimeField(default=timezone.now,null=True,blank=True)
	modver_datetime = models.CharField(default='9999-12-31 00:00:00',max_length=100,null=True,blank=True)
	original_id = models.CharField(max_length=100,null=True,blank=True)
	created_by_id = models.CharField(max_length=100,null=True,blank=True)

	class Meta:
		db_table = "t_user_profile"
	
	def __str__(self):
		return self.users.username

	def getAllImages(self):
		allimages = UserPic.objects.filter(profile=self)
		images_list = []
		for image in allimages:
			try:
				images_list.append(settings.BASE_URL+image.images.url)
			except:
				pass

		return images_list


	def getSingleImageUrl(self):
		if self.profile_pic:
			return settings.BASE_URL+self.profile_pic.url
		else:
			allimages = UserPic.objects.filter(profile=self)
			single_image = ""
			for image in allimages:
				try:
					single_image = settings.BASE_URL+image.images.url
					break
				except:
					pass
			return single_image

class UserPic(models.Model):
	profile = models.ForeignKey(Profile,on_delete=models.CASCADE,null=True,blank=True)
	images = models.FileField(upload_to='images/',null=True,blank=True)
	create_datetime  = models.DateTimeField(default=timezone.now,null=True,blank=True)
	modver_datetime = models.CharField(default='9999-12-31 00:00:00',max_length=100,null=True,blank=True)
	original_id = models.CharField(max_length=100,null=True,blank=True)
	created_by_id = models.CharField(max_length=100,null=True,blank=True)
	class Meta:
		db_table = "t_user_image"

	# def __str__(self):
	# 	return self.profile.companyname
		

class CompanyActivties(models.Model):
	activties = models.CharField(max_length=200,null=True, blank=True)
	create_datetime  = models.DateTimeField(default=timezone.now,null=True,blank=True)
	modver_datetime = models.CharField(default='9999-12-31 00:00:00',max_length=100,null=True,blank=True)
	original_id = models.CharField(max_length=100,null=True,blank=True)
	created_by_id = models.CharField(max_length=100,null=True,blank=True)

	class Meta:
		db_table = "t_comapany_activity"
		
	
class CompanyActivtiesDetail(models.Model):
	activties = models.ForeignKey(CompanyActivties,on_delete=models.DO_NOTHING,null=True, blank=True)
	phonenumber = models.BigIntegerField(null=True, blank=True)
	phonenumber_status = models.BooleanField(null=True,blank=True)
	website = models.CharField(max_length=300,null=True, blank=True)
	website_status = models.BooleanField(null=True,blank=True)
	descripiton = models.TextField(null=True, blank=True)
	create_datetime  = models.DateTimeField(default=timezone.now,null=True,blank=True)
	modver_datetime = models.CharField(default='9999-12-31 00:00:00',max_length=100,null=True,blank=True)
	original_id = models.CharField(max_length=100,null=True,blank=True)
	created_by_id = models.CharField(max_length=100,null=True,blank=True)

	class Meta:
		db_table = "t_company_activity_detail"
		

class CompanyProfile(models.Model):
	owner = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
	profile_pic = models.ImageField(upload_to='profiles_pic/',null=True,blank=True)
	companyname = models.CharField(max_length=100,null=True,blank=True)
	companyname_status = models.BooleanField(null=True,blank=True,default=False)
	legalentitytype = models.ForeignKey(LegelEntity,on_delete=models.DO_NOTHING,null=True,blank=True)
	legalentitytype_status = models.BooleanField(null=True,blank=True,default=False)
	city = models.CharField(max_length=100,null=True,blank=True)
	city_status = models.BooleanField(null=True,blank=True,default=False)
	street = models.CharField(max_length=100,null=True,blank=True)
	street_status = models.BooleanField(null=True,blank=True,default=False)
	country = models.CharField(max_length=100,null=True,blank=True)
	country_status = models.BooleanField(null=True,blank=True,default=False)
	postcode = models.CharField(max_length=10,null=True,blank=True)
	postcode_status = models.BooleanField(null=True,blank=True,default=False)
	longitude = models.FloatField(null=True,blank=True)
	latitude  = models.FloatField(null=True,blank=True)
	details = models.ForeignKey(CompanyActivtiesDetail,on_delete=models.CASCADE,null=True,blank=True)
	status = models.CharField(max_length=100,choices=Status_Choices,null=True,blank=True)
	types = models.CharField(max_length=100,choices=Type_Choices,null=True,blank=True)
	create_datetime  = models.DateTimeField(default=timezone.now,null=True,blank=True)
	modver_datetime = models.CharField(default='9999-12-31 00:00:00',max_length=100,null=True,blank=True)
	original_id = models.CharField(max_length=100,null=True,blank=True)
	created_by_id = models.CharField(max_length=100,null=True,blank=True)

	class Meta:
		db_table = "t_company_profile"

	def __str__(self):
		return self.companyname

	def getSingleImageUrl(self):
		if self.profile_pic:
			return settings.BASE_URL+self.profile_pic.url
		else:
			allimages = CompanyImages.objects.filter(profile=self)
			single_image = ""
			for image in allimages:
				try:
					single_image = settings.BASE_URL+image.images.url
					break
				except:
					pass
			return single_image

	def getAllImages(self):
		allimages = CompanyImages.objects.filter(profile=self)
		images_list = []
		for image in allimages:
			try:
				images_list.append(settings.BASE_URL+image.images.url)
			except:
				pass

		return images_list

class CompanyImages(models.Model):
	profile = models.ForeignKey(CompanyProfile,on_delete=models.CASCADE,null=True,blank=True)
	images = models.ImageField(upload_to='images/',null=True,blank=True)
	create_datetime  = models.DateTimeField(default=timezone.now,null=True,blank=True)
	modver_datetime = models.CharField(default='9999-12-31 00:00:00',max_length=100,null=True,blank=True)
	original_id = models.CharField(max_length=100,null=True,blank=True)
	created_by_id = models.CharField(max_length=100,null=True,blank=True)


	class Meta:
		db_table = "t_comapny_image"

	def __str__(self):
		return self.profile.companyname