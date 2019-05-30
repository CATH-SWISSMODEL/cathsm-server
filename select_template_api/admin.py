"""
Organises the admin section of Django
"""

from django.contrib import admin

# Register your models here.
from .models import SelectTemplateTask, SelectTemplateHit, SelectTemplateAlignment

admin.site.register(SelectTemplateTask)
admin.site.register(SelectTemplateHit)
admin.site.register(SelectTemplateAlignment)
