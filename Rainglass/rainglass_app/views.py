from django.shortcuts import render, redirect
from .models import *
from datetime import date
from .forms import *
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from datetime import datetime
from django.views.generic import View
from django.forms.models import model_to_dict
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from decimal import Decimal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from PIL import Image


def PagenatorPage(List, num, request):
    paginator = Paginator(List, num)
    pages = request.GET.get('page')

    try:
        list = paginator.page(pages)
    except PageNotAnInteger:
        list = paginator.page(1)
    except EmptyPage:
        list = paginator.page(paginator.num_pages)
    return list


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd['username'], password=cd['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    if user.is_staff:
                        return redirect('/manager/')
                    else:
                        return redirect('/')
                else:
                    return HttpResponse("Disabled account")
            else:
                return HttpResponse("Invalid login")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def iOmbor(request):
    maxsulotlar = AsosiyOmbor.objects.all()
    context = {
        'maxsulotlar': maxsulotlar,
    }
    return render(request, 'ishchilar/i-ombor.html', context)


@login_required
def iBuyurtmachi(request):
    try:
        q = request.GET.get("q")
        object_list = Buyurtmachi.objects.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(
            firma__icontains=q) | Q(phone_number__icontains=q) | Q(adress__icontains=q))
    except:
        object_list = Buyurtmachi.objects.all()
    page = request.GET.get('page')
    context = {
        'buyurtmachilar': PagenatorPage(object_list, 10, request),
        'page': page
    }
    return render(request, 'ishchilar/i-buyurtmachi.html', context)


@login_required
def iYakunlangan(request):
    bugun = date.today()
    yakunlangan_yopilmagan = Buyurtma.objects.filter(
        ish_yakunlandi=True, toliq_yopildi=False)
    toliq_yopilgan = Buyurtma.objects.filter(
        ish_yakunlandi=True, toliq_yopildi=True)
    try:
        q = request.GET.get("q")
        yakunlangan_yopilmagan = yakunlangan_yopilmagan.filter(Q(buyurtmachi__first_name__icontains=q) | Q(
            buyurtmachi__last_name__icontains=q) | Q(buyurtmachi__firma__icontains=q) | Q(buyurtma_nomi__icontains=q))
    except:
        pass
    try:
        q = request.GET.get("q2")
        toliq_yopilgan = toliq_yopilgan.filter(Q(buyurtmachi__first_name__icontains=q) | Q(
            buyurtmachi__last_name__icontains=q) | Q(buyurtmachi__firma__icontains=q) | Q(buyurtma_nomi__icontains=q))
    except:
        pass
    toliq_yopilgan = toliq_yopilgan.reverse()
    context = {
        'yakunlangan_yopilmagan': yakunlangan_yopilmagan,
        'toliq_yopilgan': PagenatorPage(toliq_yopilgan, 15, request),
        'bugun': bugun
    }
    return render(request, 'ishchilar/i-yakunlangan.html', context)


@login_required
def iYakunlanmagan(request):
    buyurtmalar = Buyurtma.objects.filter(
        ish_yakunlandi=False, toliq_yopildi=False, ishchi_nazorati=True)
    oz_qolganlar = []
    yaqin_qolganlar = []
    yetarli_qolganlar = []
    muddati_tugaganlar = []
    bugun = date.today()

    for buyurtma in buyurtmalar:
        if (buyurtma.deadline - bugun).days <= 0:
            muddati_tugaganlar.append(buyurtma)
        elif (buyurtma.deadline - bugun).days <= 5:
            oz_qolganlar.append(buyurtma)
        elif (buyurtma.deadline - bugun).days <= 10:
            yaqin_qolganlar.append(buyurtma)
        else:
            yetarli_qolganlar.append(buyurtma)

    nazoratsiz_buyurtmalar = Buyurtma.objects.filter(
        ishchi_nazorati=False, ish_yakunlandi=False, toliq_yopildi=False)

    context = {
        'muddati_tugaganlar': muddati_tugaganlar,
        'oz_qolganlar': oz_qolganlar,
        'yaqin_qolganlar': yaqin_qolganlar,
        'yetarli_qolganlar': yetarli_qolganlar,
        'nazoratsiz_buyurtmalar': nazoratsiz_buyurtmalar,
        'bugun': bugun,
    }

    return render(request, 'ishchilar/i-yakunlanmagan.html', context)


@login_required
def iDetail(request, id):
    buyurtma = Buyurtma.objects.get(id=id)
    bugun = date.today()

    return render(request, 'ishchilar/i-detail.html', {
        'buyurtma': buyurtma,
        'bugun': bugun,
    })


@login_required
def detail(request, id):
    buyurtma = Buyurtma.objects.get(id=id)
    yuzasi = buyurtma.boyi * buyurtma.eni
    bugun = date.today()

    return render(request, 'detail.html', {'buyurtma': buyurtma,
                                           'yuzasi': yuzasi,
                                           'bugun': bugun,
                                           })


@login_required
def YangiBuyurtma(request):
    buyurtmachilar = Buyurtmachi.objects.all()
    maxsulotlar = AsosiyOmbor.objects.all()
    if request.method == 'POST':
        picture = request.FILES["rasm"]
        buyurtmach = request.POST.get('buyurtmachi')
        buyurtmachi = Buyurtmachi.objects.get(id=buyurtmach)
        buyurtma_nomi = request.POST.get('buyurtma-nomi')
        boyi = request.POST.get('buyurtma-boyi')
        eni = request.POST.get('buyurtma-eni')
        ochiladi = request.POST.get("ochiladi")
        buyurtma_soni = request.POST.get('buyurtma-soni')
        qabul_qilingan_vaqt = request.POST.get('qabul-sanasi')
        deadline = request.POST.get('deadline')
        sotilish_protsenti = request.POST.get('sotilish-protsenti')
        kvm_uchun_ishchi_tolovi = request.POST.get('ishchi-tolovi')
        montaj_tolovi = request.POST.get('montaj-tolovi')
        izox = request.POST.get('izox')
        ishchi_nazorati = request.POST.get('ishchi-nazorati', False)
        if ishchi_nazorati == "on":
            ishchi_nazorati = True

        ish_yakunlandi = request.POST.get('tayyor', False)
        if ish_yakunlandi == "on":
            ish_yakunlandi = True

        toliq_yopildi = request.POST.get('yopildi', False)
        if toliq_yopildi == "on":
            toliq_yopildi = True

        try:
            new_buyurtma = Buyurtma.objects.create(buyurtmachi=buyurtmachi, buyurtma_nomi=buyurtma_nomi,
                                                   boyi=boyi, eni=eni, ochilishi=ochiladi, buyurtma_soni=buyurtma_soni,
                                                   picture=picture, qabul_qilingan_vaqt=qabul_qilingan_vaqt, deadline=deadline,
                                                   sotilish_protsenti=sotilish_protsenti,
                                                   kvm_uchun_ishchi_tolovi=kvm_uchun_ishchi_tolovi,
                                                   montaj_tolovi=montaj_tolovi, izox=izox, ishchi_nazorati=ishchi_nazorati,
                                                   ish_yakunlandi=ish_yakunlandi, toliq_yopildi=toliq_yopildi)

            new_buyurtma.save()
            image = Image.open(new_buyurtma.picture)
            width, height = image.size
            width = width // 2
            height = height//2
            size = (width, height)
            image = image.resize(size, Image.ANTIALIAS)
            image.save(new_buyurtma.picture.path)
            maxsulotlar = AsosiyOmbor.objects.all()
            for m in maxsulotlar:
                name = m.maxsulot.nomi
                m1_id = request.POST.get(name + "-id")
                if m1_id:
                    m1 = AsosiyOmbor.objects.get(id=m1_id)
                    hajm1 = float(request.POST.get(name + "-hajm"))
                    KerakliMax.objects.create(
                        buyurtma=new_buyurtma, maxsulot=m1, hajm=hajm1)
                    m1.hajm = m1.hajm - \
                        Decimal(request.POST.get(name + "-hajm"))
                    m1.save()
            messages.success(request, "Buyurtma olindi")
            return render(request, 'buyurtma-olish.html', {'buyurtmachilar': buyurtmachilar, 'maxsulotlar': maxsulotlar, })
        except:
            messages.error(request, "Buyurtma olishda xatolik")
            return render(request, 'buyurtma-olish.html', {'buyurtmachilar': buyurtmachilar, 'maxsulotlar': maxsulotlar, })
    else:
        new_client = None
        new_client_id = request.GET.get("new_client_id")
        if new_client_id:
            new_client = Buyurtmachi.objects.get(id=new_client_id)
        context = {
            'buyurtmachilar': buyurtmachilar,
            'maxsulotlar': maxsulotlar,
            'new_client': new_client,
            'status': None,
        }
        return render(request, 'buyurtma-olish.html', context)


class BuyurtmaniTaxrirlashView(View):

    """
    Editing the order 
    """

    def post(self, request, id):
        buyurtma = Buyurtma.objects.get(id=id)
        picture = request.FILES.get("rasm", False)
        buyurtmachi_id = request.POST.get('buyurtmachi')
        buyurtmachi = Buyurtmachi.objects.get(id=buyurtmachi_id)
        buyurtma_nomi = request.POST.get('buyurtma-nomi')
        boyi = request.POST.get('buyurtma-boyi')
        eni = request.POST.get('buyurtma-eni')
        ochiladi = request.POST.get("ochiladi")
        buyurtma_soni = request.POST.get('buyurtma-soni')
        qabul_qilingan_vaqt = request.POST.get('qabul-sanasi')
        deadline = request.POST.get('deadline')
        sotilish_protsenti = request.POST.get('sotilish-protsenti')
        kvm_uchun_ishchi_tolovi = request.POST.get('ishchi-tolovi')
        montaj_tolovi = request.POST.get('montaj-tolovi')
        izox = request.POST.get('izox')
        ishchi_nazorati = request.POST.get('ishchi-nazorati', False)
        if ishchi_nazorati == "on":
            ishchi_nazorati = True

        ish_yakunlandi = request.POST.get('tayyor', False)
        if ish_yakunlandi == "on":
            ish_yakunlandi = True

        toliq_yopildi = request.POST.get('yopildi', False)
        if toliq_yopildi == "on":
            toliq_yopildi = True

        # Now change the old order and save changes
        buyurtma.buyurtmachi = buyurtmachi
        buyurtma.buyurtma_nomi = buyurtma_nomi
        buyurtma.eni = eni
        buyurtma.boyi = boyi
        buyurtma.ochilishi = ochiladi
        buyurtma.buyurtma_soni = buyurtma_soni
        buyurtma.qabul_qilingan_vaqt = qabul_qilingan_vaqt
        buyurtma.deadline = deadline
        buyurtma.sotilish_protsenti = sotilish_protsenti
        buyurtma.kvm_uchun_ishchi_tolovi = kvm_uchun_ishchi_tolovi
        buyurtma.montaj_tolovi = montaj_tolovi
        buyurtma.izox = izox
        buyurtma.ishchi_nazorati = ishchi_nazorati
        buyurtma.ish_yakunlandi = ish_yakunlandi
        buyurtma.toliq_yopildi = toliq_yopildi
        if picture:
            buyurtma.picture = request.FILES["rasm"]
        buyurtma.save()
        return HttpResponseRedirect("/detail/"+str(buyurtma.id))

    def get(self, request, id):
        buyurtma = Buyurtma.objects.get(id=id)
        buyurtmachilar = Buyurtmachi.objects.all()
        maxsulotlar = AsosiyOmbor.objects.all()
        kerakli_maxsulotlar = buyurtma.kerakli_maxsulotlar.all()
        context = {
            "kerakli_maxsulotlar": kerakli_maxsulotlar,
            "buyurtmachilar": buyurtmachilar,
            "maxsulotlar": maxsulotlar,
            "buyurtma": buyurtma,
        }
        return render(request, "buyurtmani-taxrirlash.html", context)


class KerakliMaxView(View):

    def post(self, request):
        data = json.loads(request.body)
        buyurtma = Buyurtma.objects.get(id=data["buyurtmaId"])
        maxsulot = AsosiyOmbor.objects.get(id=data["id"])
        new_kerakli_max = KerakliMax.objects.create(
            buyurtma=buyurtma, maxsulot=maxsulot, hajm=data["hajm"])
        maxsulot.hajm -= Decimal(data["hajm"])
        maxsulot.save()
        return JsonResponse({"new_kerakli_max": model_to_dict(new_kerakli_max), "max_nomi": new_kerakli_max.maxsulot.maxsulot.nomi, "ombor_max_id": data["id"]}, status=200)


class KerakliMaxDelete(View):

    def post(self, request):
        data = json.loads(request.body)
        maxsulot = KerakliMax.objects.get(id=data["id"])
        maxsulot.delete()
        ombor_max = AsosiyOmbor.objects.get(id=data["ombor_max_id"])
        ombor_max.hajm += Decimal(data["omHajm"])
        ombor_max.save()
        return JsonResponse({"result": "ok"}, status=200)


@login_required
def yakunlanmagan(request):
    buyurtmalar = Buyurtma.objects.filter(
        ish_yakunlandi=False, toliq_yopildi=False, ishchi_nazorati=True)
    bugun = date.today()
    nazoratsiz_buyurtmalar = Buyurtma.objects.filter(
        ishchi_nazorati=False, ish_yakunlandi=False, toliq_yopildi=False)

    try:
        q = request.GET.get("q")
        nazoratsiz_buyurtmalar = nazoratsiz_buyurtmalar.filter(Q(buyurtmachi__first_name__icontains=q) | Q(
            buyurtmachi__last_name__icontains=q) | Q(buyurtmachi__firma__icontains=q) | Q(buyurtma_nomi__icontains=q))
    except:
        pass

    try:
        q = request.GET.get("q2")
        buyurtmalar = buyurtmalar.filter(Q(buyurtmachi__first_name__icontains=q) | Q(
            buyurtmachi__last_name__icontains=q) | Q(buyurtmachi__firma__icontains=q) | Q(buyurtma_nomi__icontains=q))
        oz_qolganlar = []
        yaqin_qolganlar = []
        yetarli_qolganlar = []
        muddati_tugaganlar = []
        for buyurtma in buyurtmalar:
            if (buyurtma.deadline - bugun).days <= 0:
                muddati_tugaganlar.append(buyurtma)
            elif (buyurtma.deadline - bugun).days <= 5:
                oz_qolganlar.append(buyurtma)
            elif (buyurtma.deadline - bugun).days <= 10:
                yaqin_qolganlar.append(buyurtma)
            else:
                yetarli_qolganlar.append(buyurtma)
    except:
        oz_qolganlar = []
        yaqin_qolganlar = []
        yetarli_qolganlar = []
        muddati_tugaganlar = []
        for buyurtma in buyurtmalar:
            if (buyurtma.deadline - bugun).days <= 0:
                muddati_tugaganlar.append(buyurtma)
            elif (buyurtma.deadline - bugun).days <= 5:
                oz_qolganlar.append(buyurtma)
            elif (buyurtma.deadline - bugun).days <= 10:
                yaqin_qolganlar.append(buyurtma)
            else:
                yetarli_qolganlar.append(buyurtma)

    page = request.GET.get('page')
    context = {
        'muddati_tugaganlar': muddati_tugaganlar,
        'oz_qolganlar': oz_qolganlar,
        'yaqin_qolganlar': yaqin_qolganlar,
        'yetarli_qolganlar': yetarli_qolganlar,
        'nazoratsiz_buyurtmalar': nazoratsiz_buyurtmalar,
        'bugun': bugun,
        'page': page
    }

    return render(request, 'yakunlanmagan.html', context)


@login_required
def yakunlangan(request):
    bugun = date.today()
    yakunlangan_yopilmagan = Buyurtma.objects.filter(
        ish_yakunlandi=True, toliq_yopildi=False)
    toliq_yopilgan = Buyurtma.objects.filter(
        ish_yakunlandi=True, toliq_yopildi=True)
    try:
        q = request.GET.get("q")
        yakunlangan_yopilmagan = yakunlangan_yopilmagan.filter(Q(buyurtmachi__first_name__icontains=q) | Q(
            buyurtmachi__last_name__icontains=q) | Q(buyurtmachi__firma__icontains=q) | Q(buyurtma_nomi__icontains=q))
    except:
        pass
    try:
        q = request.GET.get("q2")
        toliq_yopilgan = toliq_yopilgan.filter(Q(buyurtmachi__first_name__icontains=q) | Q(
            buyurtmachi__last_name__icontains=q) | Q(buyurtmachi__firma__icontains=q) | Q(buyurtma_nomi__icontains=q))
    except:
        pass
    toliq_yopilgan = toliq_yopilgan.reverse()
    page = request.GET.get('page')
    context = {
        'yakunlangan_yopilmagan': yakunlangan_yopilmagan,
        'toliq_yopilgan': PagenatorPage(toliq_yopilgan, 10, request),
        'bugun': bugun,
        'page': page
    }
    return render(request, 'yakunlangan.html', context)


@login_required
def ombor(request):
    maxsulotlar = AsosiyOmbor.objects.all()
    context = {'maxsulotlar': maxsulotlar,
               }
    return render(request, 'ombor.html', context)


@login_required
def omborTarix(request):
    try:
        q = request.GET.get("q")
        object_list = OmborTarix.objects.filter(maxsulot__nomi__icontains=q)
    except:
        object_list = OmborTarix.objects.all()
    page = request.GET.get('page')
    context = {
        'maxsulotlar': PagenatorPage(object_list, 10, request),
        'page': page
    }
    return render(request, 'ombor-tarix.html', context)


@login_required
def omborgaQoshish(request):
    maxsulotlar = Maxsulot.objects.all()
    turlar = MaxsulotTuri.objects.all()
    if request.method == 'POST':
        nomi = request.POST.get('nomi')
        turi_id = request.POST.get('turi')
        turi = MaxsulotTuri.objects.get(id=turi_id)
        narxi = request.POST.get('narxi')
        hajm = request.POST.get('hajmi')
        qabul_sanasi = request.POST.get('sanasi')
        for maxsulot in maxsulotlar:
            if nomi == maxsulot.nomi and turi == maxsulot.turi:
                messages.error(
                    request, "Bu maxsulot mavjud! Mavjud maxsulotga qo'shish bo'limiga o'ting.")
                return render(request, 'omborga-qoshish.html')
        new_maxsulot = Maxsulot.objects.create(nomi=nomi, turi=turi)
        new_maxsulot.save()
        try:
            OmborTarix.objects.create(maxsulot=new_maxsulot, narxi=float(
                narxi), hajm=float(hajm), qabul_sanasi=qabul_sanasi)
            messages.success(
                request, "Yangi maxsulot muvaffaqqiyatli qo'shildi!")
            return render(request, 'omborga-qoshish.html')
        except:
            messages.error(request, "Xatolik!")
            return render(request, 'omborga-qoshish.html')
    else:
        try:
            tur_id = request.GET.get("tur")
            yangi_tur = MaxsulotTuri.objects.get(nomi=tur_id)
            context = {
                'maxsulotlar': maxsulotlar,
                'turlar': turlar,
                'yangi_tur': yangi_tur,
            }

            return render(request, 'omborga-qoshish.html', context)
        except:
            pass
        context = {
            'maxsulotlar': maxsulotlar,
            'turlar': turlar,
        }
        return render(request, 'omborga-qoshish.html', context)


@login_required
def mavjudMaxsulotgaQoshish(request):
    if request.method == 'POST':
        maxsulot_id = request.POST.get('mavjud-maxsulot')
        maxsulot = Maxsulot.objects.get(id=maxsulot_id)
        narxi = request.POST.get("narxi")
        hajm = request.POST.get('hajmi')
        qabul_sanasi = request.POST.get('sanasi')
        qabul_sanasi = datetime.strptime(qabul_sanasi, '%Y-%m-%d').date()
        # try:

        OmborTarix.objects.create(maxsulot=maxsulot, narxi=float(
            narxi), hajm=float(hajm), qabul_sanasi=qabul_sanasi)
        messages.success(
            request, "Mavjud maxsulotga muvaffaqqiyatli qo'shildi!")
        return render(request, 'mavjud-maxsulotga-qoshish.html')
        # except:
        #     messages.error(request, "Maxsulotga qo'shishda xatolik!")
        #     return render(request, 'mavjud-maxsulotga-qoshish.html')
    else:
        maxsulotlar = AsosiyOmbor.objects.all()
        context = {
            'maxsulotlar': maxsulotlar,
        }
        return render(request, 'mavjud-maxsulotga-qoshish.html', context)


@login_required
def turga_qoshish(request):
    if request.method == "POST":
        nomi = request.POST.get("tur-nomi")
        for tur in MaxsulotTuri.objects.all():
            if tur.nomi == nomi:
                messages.error(request, "Bu maxsulot turi mavjud!")
                return render(request, 'turga-qoshish.html')
        try:
            yangi_tur = MaxsulotTuri.objects.create(nomi=nomi)
            yangi_tur.save()
            messages.success(
                request, "Maxsulot turi muvaffaqqiyatli qo'shildi!")
            return render(request, 'turga-qoshish.html', {'yangi_tur': yangi_tur})
        except:
            messages.error(request, "Turga qo'shishda xatolik!")
            return render(request, "turga-qoshish.html")
    return render(request, 'turga-qoshish.html')


@login_required
def maxsulot_taxrirlash(request, id):
    maxsulot = OmborTarix.objects.get(id=id)
    if request.method == "POST":
        narxi = request.POST.get('narxi')
        hajm = request.POST.get('hajmi')
        qabul_sanasi = request.POST.get('sanasi')
        try:
            maxsulot.narxi = narxi
            maxsulot.hajm = hajm
            maxsulot.qabul_sanasi = qabul_sanasi
            maxsulot.save()
            messages.success(request, "Maxsulot muvaffaqqiyatli taxrirlandi!")
        except:
            messages.error(request, "Taxrirlashda xatolik!")
    return render(request, 'maxsulot_taxrirlash.html', {'maxsulot': maxsulot})


@login_required
def buyurtmachi(request):
    try:
        q = request.GET.get("q")
        object_list = Buyurtmachi.objects.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(
            firma__icontains=q) | Q(phone_number__icontains=q) | Q(adress__icontains=q))
    except:
        object_list = Buyurtmachi.objects.all()
    page = request.GET.get('page')
    context = {
        'buyurtmachilar': PagenatorPage(object_list, 10, request),
        "page": page
    }
    return render(request, 'buyurtmachi.html', context)


@login_required
def yangiBuyurtmachi(request):
    if request.method == "POST":
        ism = request.POST.get('ism')
        familya = request.POST.get('familya')
        firma = request.POST.get('firma')
        telfon = request.POST.get('telfon')
        adress = request.POST.get('adress')
        try:
            yangi_buyurtmachi = Buyurtmachi.objects.create(first_name=ism,
                                                           last_name=familya,
                                                           firma=firma,
                                                           phone_number=telfon,
                                                           adress=adress)
            yangi_buyurtmachi.save()
            messages.success(request, "Buyurtmachi muvaffaqqiyatli qo'shildi!")
            return render(request, 'yangi-buyurtmachi.html', {"new_client": yangi_buyurtmachi})
        except:
            messages.error(request, "Buyurtmachi qo'shishda xatolik!")
    return render(request, 'yangi-buyurtmachi.html')


@login_required
def buyurtmachi_taxrirlash(request, id):
    buyurtmachi = Buyurtmachi.objects.get(id=id)
    if request.method == "POST":
        ism = request.POST.get("ism")
        familya = request.POST.get("familiya")
        firma = request.POST.get("firma")
        telfon = request.POST.get("telfon")
        adress = request.POST.get("adress")

        try:
            buyurtmachi.first_name = ism
            buyurtmachi.last_name = familya
            buyurtmachi.firma = firma
            buyurtmachi.phone_number = telfon
            buyurtmachi.adress = adress
            buyurtmachi.save()
            messages.success(
                request, "Buyurtmachi muvaffaqqiyatli taxrirlandi!")
        except:
            messages.error(request, "Taxrirlashda xatolik!")
    return render(request, "buyurtmachini-taxrirlash.html", {'buyurtmachi': buyurtmachi})


# Ishchilar bo'limi
@login_required
def ishchilar(request):
    ishchilar = Ishchi.objects.all()
    if request.method == "POST":
        ism = request.POST.get("ism")
        familya = request.POST.get("familya")
        telfon = request.POST.get("telfon")
        try:
            Ishchi.objects.create(ism=ism, familya=familya, telfon=telfon)
            messages.success(request, "Yangi ishchi qo'shildi")
        except:
            messages.error(request, "Xatolik, tekshirib qaytadan urinib ko'ring")
    else:
        try:
            q = request.GET.get("q")
            ishchilar = ishchilar.filter(Q(ism__icontains=q) | Q(familya__icontains=q) | Q(telfon__icontains=q))
        except:
            pass
    context = {
            "ishchilar": PagenatorPage(ishchilar, 15, request)
        }
    return render(request, "ishchilar.html", context)


@login_required
def ishchi_detail(request, id):
    ishchi = Ishchi.objects.get(id=id)
    davomadlar = ishchi.davomadlar.all()
    today = datetime.today()
    context = {
        "ishchi": ishchi,
        "davomadlar": davomadlar,
        "today": today
        }
    if request.method == "POST":
        sana = request.POST.get("sana")
        keldi = request.POST.get("keldi")
        if keldi == "on":
            keldi = True
        else:
            keldi = False
        ish_miqdori = request.POST.get("ish-miqdori")
        try:
            Davomad.objects.create(
                ishchi=ishchi, sana=sana, keldi=keldi, ish_miqdori=ish_miqdori)
            messages.success(request, "Davomad olindi")
        except:
            messages.error(
                request, "Davomad olishda xatolik, avval tekshirib qayta urinib ko'ring")
    return render(request, "ishchi-detail.html", context)


@login_required
def ishchi_taxrirlash(request, id):
    ishchi = Ishchi.objects.get(id=id)
    if request.method == "POST":
        ism = request.POST.get("ism")
        familya = request.POST.get("familya")
        telfon = request.POST.get("telfon")

        try:
            ishchi.ism = ism
            ishchi.familya = familya
            ishchi.telfon = telfon
            ishchi.save()
            messages.success(request, "Muvaffaqqiyatli taxrirlandi")
        except:
            messages.error(
                request, "Xatolik, tekshirib qaytadan urinib ko'ring")
    return render(request, "ishchi-taxrirlash.html", {"ishchi": ishchi})


@login_required
def davomad(request):
    mavjud_davomad = None
    today = datetime.today()
    ishchilar = Ishchi.objects.all()
    if request.method == "POST":
        ishchi_id = request.POST.get("ishchi")
        ishchi = Ishchi.objects.get(id=ishchi_id)
        sana = request.POST.get("sana")
        keldi = request.POST.get("keldi")
        if keldi == "on":
            keldi = True
        else:
            keldi = False
        ish_miqdori = request.POST.get("ish-miqdori")
        d_id = request.POST.get("d_id")

        if d_id:
            m_davomad = Davomad.objects.get(id=d_id)
            try:
                m_davomad.ishchi = ishchi
                m_davomad.sana = sana
                m_davomad.keldi = keldi
                m_davomad.ish_miqdori = ish_miqdori
                m_davomad.save()
                messages.success(request, "Davomad taxrirlandi")
                mavjud_davomad = m_davomad
            except:
                mavjud_davomad = m_davomad
                messages.error(
                    request, "Taxrirlashda xatolik, avval tekshirib qayta urinib ko'ring")
        else:
            # check if the date is already avaiolable
            davomadlar = ishchi.davomadlar.all()
            d_olingan = False
            for davomad in davomadlar:
                if davomad.sana == datetime.strptime(sana,"%Y-%m-%d").date():
                    messages.error(request, "Bu sana uchun davomad olingan!")
                    d_olingan = True
                
                if d_olingan == False:
                    #if it is a new date, save the data
                    try:
                        Davomad.objects.create(
                            ishchi=ishchi, sana=sana, keldi=keldi, ish_miqdori=ish_miqdori)
                        messages.success(request, "Davomad olindi")
                    except:
                        messages.error(
                            request, "Davomad olishda xatolik, avval tekshirib qayta urinib ko'ring")
    else:
        d_id = request.GET.get("d_id")
        if d_id:
            mavjud_davomad = Davomad.objects.get(id=d_id)
    return render(request, "davomad.html", {"ishchilar": ishchilar, "today": today, "mavjud_davomad": mavjud_davomad})
