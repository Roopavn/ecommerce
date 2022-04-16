from django.shortcuts import render
from matplotlib.style import context
from .models import *

def store(request):
    product = Product.objects.all()
    context = {'products':product}
    return render(request, 'store.html', context)

def cart(request):
    context = {}
    return render(request, 'cart.html', context)

def checkout(request):
    context = {}
    return render(request, 'checkout.html', context)
