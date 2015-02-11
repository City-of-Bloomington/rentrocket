from django.shortcuts import render

def index(request):

    #city = City.objects.filter(tag=to_tag("Ann Arbor"))
    #buildings = Building.objects.filter(city=city)
    #context = {'buildings': buildings}
    
    context = {}

    return render(request, 'index.html', context )

def new(request):
    context = {}

    return render(request, 'new.html', context )

