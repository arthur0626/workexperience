from django.shortcuts import render

# Create your views here.
def main(request):
    return render(request, 'main.html')

def search(request):
    return render(request, 'search.html')

def login(request):
    return render(request, 'login.html')

