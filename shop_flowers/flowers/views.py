from django.shortcuts import render
from .models import Bouquet

# Create your views here.
def bouquet(request):
    bouquets = Bouquet.objects.all()
    return render(request, 'flowers/bouquet.html', {'bouquets': bouquets})