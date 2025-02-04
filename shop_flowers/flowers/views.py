from django.shortcuts import render
from .models import Bouquet
from django.shortcuts import get_object_or_404

def bouquet(request):
    bouquets = Bouquet.objects.all()
    return render(request, 'flowers/bouquet.html', {'bouquets': bouquets})

def bouquet_detail(request, pk):
    bouquet = get_object_or_404(Bouquet, pk=pk)
    return render(request, 'flowers/bouquet_detail.html', {'bouquet': bouquet})