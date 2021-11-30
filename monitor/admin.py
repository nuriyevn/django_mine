from django.contrib import admin
from .models import Instance
from .models import Entry
# Register your models here.


admin.site.register(Entry)
admin.site.register(Instance)

