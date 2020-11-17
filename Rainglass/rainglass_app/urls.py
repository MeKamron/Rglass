from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

app_name = 'rainglass_app'

urlpatterns = [
    path('login/', user_login, name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', iYakunlanmagan, name='i-yakunlanmagan'),
    path('i-yakunlangan/', iYakunlangan, name='i-yakunlangan'),
    path('i-ombor/', iOmbor, name='i-ombor'),
    path('i-buyurtmachi/', iBuyurtmachi, name='i-buyurtmachi'),
    path('i-detail/<int:id>/', iDetail, name='i-detail'),
    path('manager/', yakunlanmagan, name='yakunlanmagan'),
    path('detail/<int:id>/', detail, name='detail'),
    path('yakunlangan/', yakunlangan, name='yakunlangan'),
    path('yangibuyurtma/', YangiBuyurtma, name='yangibuyurtma'),
    path("buyurtmani-taxrirlash/<int:id>/", login_required(BuyurtmaniTaxrirlashView.as_view()), name="buyurtmani-taxrirlash"),
    path('ombor/', ombor, name='ombor'),
    path('ombor-tarix/', omborTarix, name='ombor-tarix'),
    path('omborga-qoshish/', omborgaQoshish, name='omborga-qoshish'),
    path('turga-qoshish/', turga_qoshish, name="turga-qoshish"),
    path('mavjud-maxsulotga-qoshish/', mavjudMaxsulotgaQoshish, name='mavjud-maxsulotga-qoshish'),
    path('maxsulot-taxrirlash/<int:id>/', maxsulot_taxrirlash, name='maxsulot-taxrirlash'),
    path('buyurtmachi/', buyurtmachi, name='buyurtmachi'),
    path('yangi-buyurtmachi/', yangiBuyurtmachi, name='yangi-buyurtmachi'),
    path('buyurtmachini-taxrirlash/<int:id>/', buyurtmachi_taxrirlash, name="buyurtmachini-taxrirlash"),
    path('kerakli-max/', login_required(KerakliMaxView.as_view()), name="kerakli-max"),
    path("kerakli-max-delete/", login_required(KerakliMaxDelete.as_view()), name="kerakli-max-delete"),
    path("ishchilar/", ishchilar, name="ishchilar"),
    path("ishchi-detail/<int:id>/", ishchi_detail, name="ishchi-detail"),
    path("ishchi-taxrirlash/<int:id>/", ishchi_taxrirlash, name="ishchi-taxrirlash"),
    path("davomad/", davomad, name="davomad"),
]