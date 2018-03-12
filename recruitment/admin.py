from django.contrib import admin
from models import *
# Register your models here.


class HiringAdmin(admin.ModelAdmin):
	list_per_page = 100
	search_fields = ['current_state', ]

admin.site.register(Company)
admin.site.register(Job)
admin.site.register(Candidate)
admin.site.register(Hiring, HiringAdmin)