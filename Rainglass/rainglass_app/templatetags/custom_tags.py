from django import template


register = template.Library()


@register.filter(name='sub')
def sub(a1, a2):
    return a1 - a2


@register.filter(name='ad')
def ad(a1, a2):
    return a1 + a2


@register.filter(name="multiply")
def multiply(a1, a2, *args, **kwargs):
    return int(a1) * int(a2)


@register.filter(name="divide")
def divide(a1, a2, *args, **kwargs):
    return int(a1) / int(a2)


@register.filter(name='exclude')
def exclude(a1, a2, *args, **kwargs):
    return a1.exclude(id=a2.id)


@register.filter(name='tan_narx')
def tan_narx(a1, *args, **kwargs):
    tannarx = 0
    kerakli_maxsulotlar = a1.kerakli_maxsulotlar.all()
    for maxsulot in kerakli_maxsulotlar:
        tannarx += maxsulot.maxsulot.narxi * float(maxsulot.hajm)
    return tannarx


@register.filter(name='yuzasi')
def yuzasi(a1, *args, **kwargs):
    yuza = a1.boyi * a1.eni
    return yuza


@register.filter(name='n_format')
def n_format(a1, *args, **kwargs):
    return f'{a1:,}'


