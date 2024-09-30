from django.shortcuts import render
from .models import Product
from django.http import Http404

# Create your views here.
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_modules/product_list.html',{
        'products': products
    })


def product_detail(request, product_id):
    try:
        return render(request, 'product_modules/product_detail.html', {
            'product': Product.objects.get(id=product_id)
        })
    except:
        raise Http404('Product')
