from django.db import models
from django.urls import reverse
import datetime
from django.contrib.auth.models import User


class MaxsulotTuri(models.Model):

    """
    The categories that a product can belong to
    """

    nomi = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "MaxsulotTuri"
        ordering = ('-id',)

    def __str__(self):
        return self.nomi


class Maxsulot(models.Model):
    """
    The exact product coming to the store
    """
    nomi = models.CharField(max_length=200)
    turi = models.ForeignKey(
        MaxsulotTuri, on_delete=models.CASCADE, related_name='maxsulotlar')

    class Meta:
        verbose_name_plural = "Maxsulot"
        ordering = ('-id',)

    def __str__(self):
        return self.nomi


class OmborTarix(models.Model):
    """
    History of products that come to store
    Does not change even if the product is edited
    """
    maxsulot = models.ForeignKey(Maxsulot, on_delete=models.CASCADE)
    narxi = models.PositiveIntegerField(default=0)
    hajm = models.DecimalField(max_digits=20, decimal_places=1, default=0)
    qabul_sanasi = models.DateField()

    class Meta:
        verbose_name_plural = "OmborTarix"
        ordering = ('-id',)

    def __str__(self):
        return self.maxsulot.nomi

    def save(self, *args, **kwargs):
        if self.id is None: # if method is post
            result = AsosiyOmbor.objects.filter(maxsulot=self.maxsulot).first()
            if result is None:
                AsosiyOmbor.objects.create(maxsulot=self.maxsulot, hajm=self.hajm, narxi=self.narxi)
            else:
                result.hajm = float(result.hajm) + float(self.hajm)
                result.narxi = float(self.narxi)
                result.save()
        else:
            obj = OmborTarix.objects.get(id=self.id)
            h_farq = float(self.hajm) - float(obj.hajm)
            obj.hajm = float(obj.hajm) + h_farq
            n_farq = float(self.narxi) - float(obj.narxi)
            obj.narxi = obj.narxi + n_farq
            obj2 = AsosiyOmbor.objects.filter(maxsulot=self.maxsulot).first()
            obj2.hajm = float(obj2.hajm) + h_farq
            obj2.narxi = obj.narxi + n_farq
            obj2.save()
        super(OmborTarix, self).save(*args, **kwargs)


class AsosiyOmbor(models.Model):
    """
    The store just to show how much a product there is
    Changes if the product is edited
    """
    maxsulot = models.ForeignKey(Maxsulot, on_delete=models.CASCADE)
    narxi = models.PositiveIntegerField(default=0)
    hajm = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "AsosiyOmbor"
        ordering = ('-id',)

    def __str__(self):
        return self.maxsulot.nomi


class Buyurtmachi(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    firma = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=13)
    adress = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Buyurtmachi"
        ordering = ("-id",)

    def __str__(self):
        if self.firma:
            return self.firma
        else:
            return self.first_name

 
class Buyurtma(models.Model):
    buyurtmachi = models.ForeignKey(
        Buyurtmachi, on_delete=models.CASCADE, related_name='buyurtmalar')
    buyurtma_nomi = models.CharField(max_length=200)
    boyi = models.FloatField()
    eni = models.FloatField()
    ochilishi = models.CharField(max_length=200, blank=True)
    buyurtma_soni = models.IntegerField(default=1)
    picture = models.ImageField(upload_to='media/')
    qabul_qilingan_vaqt = models.DateField()
    deadline = models.DateField()
    sotilish_protsenti = models.PositiveIntegerField()
    kvm_uchun_ishchi_tolovi = models.FloatField()
    montaj_tolovi = models.FloatField(default=0)
    izox = models.TextField(blank=True) 
    ishchi_nazorati = models.BooleanField(default=False)
    ish_yakunlandi = models.BooleanField(default=False)
    toliq_yopildi = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Buyurtma"
        ordering = ("deadline",)

    def __str__(self):
        if self.buyurtmachi.firma:
            return self.buyurtmachi.firma + " - " +self.buyurtma_nomi
        else:
            return self.buyurtmachi.first_name + " " + buyurtmachi.last_name +" - "+ self.buyurtma_nomi

    def get_absolute_url(self):
        return reverse('rainglass:detail', args=[self.id])

    def get_absolute_url_ishchi(self):
        return reverse('rainglass:i-detail', args=[self.id])

    
class KerakliMax(models.Model):
    buyurtma = models.ForeignKey(Buyurtma, on_delete=models.CASCADE, related_name="kerakli_maxsulotlar")
    maxsulot = models.ForeignKey(AsosiyOmbor, on_delete=models.CASCADE)
    hajm = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return self.maxsulot.maxsulot.nomi



############################################
#            Ishchilar bo'limi             #
############################################

class Ishchi(models.Model):
    ism = models.CharField(max_length=200)
    familya = models.CharField(max_length=200)
    telfon = models.CharField(max_length=200)

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.ism

    def get_absolute_url(self):
        return reverse("rainglass:ishchi-detail", args=[self.id])


class Davomad(models.Model):
    ishchi = models.ForeignKey(Ishchi, on_delete=models.CASCADE, related_name="davomadlar")
    sana = models.DateField(default=datetime.date.today())
    keldi = models.BooleanField(default=False)
    ish_miqdori = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return str(self.sana)

    class Meta:
        ordering = ("-sana",)
        


############################################
#              Login bo'limi               # 
############################################

class Staff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.PositiveIntegerField()

    def __str__(self):
        return self.user.username
    