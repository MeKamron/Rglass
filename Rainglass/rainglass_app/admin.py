from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

admin.site.unregister(Group)
admin.site.register(MaxsulotTuri)
admin.site.register(Staff)

@admin.register(KerakliMax)
class KerakliMaxAdmin(admin.ModelAdmin):
    list_display = ("id", "maxsulot", "hajm")


@admin.register(OmborTarix)
class OmborTarixAdmin(admin.ModelAdmin):
    list_display = ("id", 'maxsulot','narxi', "hajm", "qabul_sanasi")


@admin.register(AsosiyOmbor)
class AsosiyOmborAdmin(admin.ModelAdmin):
    list_display = ("id", "maxsulot", "narxi", "hajm") 


@admin.register(Maxsulot)
class MaxsulotAdmin(admin.ModelAdmin):
    list_display = ("id", "nomi", "turi")


@admin.register(Buyurtma)
class BuyurtmaAdmin(admin.ModelAdmin):
    list_display = ('buyurtmachi', 'buyurtma_nomi', 'buyurtma_soni',)


@admin.register(Buyurtmachi)
class BuyurtmachiAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'firma', 'phone_number', 'adress')


@admin.register(Ishchi)
class IshchiAdmin(admin.ModelAdmin):
    list_display = ('ism', 'familya', 'telfon')


@admin.register(Davomad)
class DavomadAdmin(admin.ModelAdmin):
    list_display = ('sana', 'ishchi',  'keldi', 'ish_miqdori')



