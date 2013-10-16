from django.template import Context, loader
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render


#from django.shortcuts import render_to_response, get_object_or_404

#render vs render_to_response:
#http://stackoverflow.com/questions/5154358/django-what-is-the-difference-between-render-render-to-response-and-direc
#
# render() automatically includes context_instance (current request) with call

def about(request):
    context = {}
    return render(request, 'about.html', context )


def home(request):
    ## t = loader.get_template('index.html')
    ## t = loader.get_template('preferences/index.html')
    ## c = Context({
    ##     'latest_preferences': latest_preferences,
    ## })
    ## return HttpResponse(t.render(c))

    ## form = EventForm()
    
    ## #render_to_response does what above (commented) section does
    ## #return render_to_response('general/index.html', {'user': request.user})
    ## return render(request, 'general/index.html', { 'form': form, } )

    #return HttpResponse("Hello, world. You're at the poll index.")
    context = {}
    return render(request, 'home.html', context )


