# -*- coding: utf-8 -*-

from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView, View

class Homepage(TemplateView):
	template_name = 'index.html'
	def get(self, request, *arges, **kwargs):
		return render(request, self.template_name, locals())