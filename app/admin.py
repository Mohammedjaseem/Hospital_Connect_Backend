from django.contrib import admin
from .models import Domain,Client,Organizations

# Register your models here.

admin.site.register(Domain)
admin.site.register(Client)
admin.site.register(Organizations)
