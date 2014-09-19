from urllib import quote

from google.appengine.ext import blobstore

from django.template import Context, loader
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render

from django.core.urlresolvers import reverse
from django import forms
from django.forms import extras
from django.forms import widgets

from django.shortcuts import render, redirect
from django.forms.util import ErrorList
from django.contrib import messages

#from rentrocket.helpers import address_search
from building.models import search_building
from building.views import validate_building_and_unit, NewBuildingForm

from allauth.account.forms import SignupForm

#from django.shortcuts import render_to_response, get_object_or_404

#render vs render_to_response:
#http://stackoverflow.com/questions/5154358/django-what-is-the-difference-between-render-render-to-response-and-direc
#
# render() automatically includes context_instance (current request) with call

def about(request):
    context = {}
    return render(request, 'about.html', context )

def upload_form(request):
    context = {}
    return render(request, 'upload_form.html', context )


DWELLING_CHOICES = (
    ('rental', 'is'),
    ('owner_occupied', 'is not'),
    )

BEDROOM_CHOICES = (
    ('', ''),
    ('0', '0-studio'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6+'),
    )

class SimpleForm(forms.Form):
    #now = datetime.now()
    #years = range(now.year, now.year-30, -1)
    #print years
    
    property_type = forms.ChoiceField(choices=DWELLING_CHOICES, widget=forms.Select(attrs={'data-bind':"value: property_type"}))
    rent = forms.FloatField(widget=forms.TextInput(attrs={'size': '9'}), required=False)
    
    #bedrooms = forms.ChoiceField(widget=widgets.RadioSelect(choices=BEDROOMS), choices=BEDROOMS, required=False)
    #bedrooms = forms.IntegerField(required=True)
    bedrooms = forms.ChoiceField(choices=BEDROOM_CHOICES, label='# of Bedrooms', required=True)

    electricity = forms.FloatField(widget=forms.TextInput(attrs={'size': '9'}), required=False)

    gas = forms.FloatField(label='Natural Gas', widget=forms.TextInput(attrs={'size': '9'}), required=False)


def simple_data(request):
    """
    this is the controller for the simple form found on the front page
    bare minimum needed for data collection
    """
    results = ''

    #probably OK to show the calculator worksheet either way
    #once we're on the short form destination page
    #show_calculator = True
    show_calculator = False
    
    unitform = None
    bldgform = None
    if request.method == 'POST':
        #make this either way
        simpleform = SimpleForm(request.POST, prefix='simple')

        #make and test the bldgform (and unitform, if necessary)
        (result, bldgform, unitform) = validate_building_and_unit(request)

        if result.errors:
            #we had difficulty finding the corresponding building
            #add errors to the form
            errors = bldgform._errors.setdefault(forms.forms.NON_FIELD_ERRORS, ErrorList())

            #http://stackoverflow.com/questions/188886/inject-errors-into-already-validated-form
            #although once this is on django 1.7:
            #https://docs.djangoproject.com/en/dev/ref/forms/api/#django.forms.Form.add_error
            for error in result.errors:                    
                errors.append(error)

        #should already be errors if not result.building, 
        #so this could just be else, but this is more clear:
        elif result.building and result.unit:

            #TODO
            #consider filling in any empty fields in the form
            #with data we have previously collected about chosen building

            #image button must submit a hybrid value with x and y...
            #discovered by printing POST results:
            #print request.POST
            if 'calculator.x' in request.POST or 'calculator.y' in request.POST:
                show_calculator = True
                print "SHOWING CALCULATOR!!"

            if simpleform.is_valid(): # All validation rules pass

                errors = False

                #now check if rental / rent combo is complete...
                #custome validation check
                if simpleform.cleaned_data['property_type'] == 'rental':
                    result.unit.status = 'rented'
                    if not simpleform.cleaned_data['rent']:
                        simpleform.errors['rent'] = "Please specify the rent."
                        errors = True
                    else:
                        result.unit.rent = simpleform.cleaned_data['rent']
                else:
                    result.unit.status = 'owner-occupied'


                #check if we have electricity
                #or natural gas average bill amounts

                if not errors:
                    #save what ever we have
                    result.unit.bedroom = simpleform.cleaned_data['bedrooms']
                    if not simpleform.cleaned_data['electricity'] is None:
                        result.unit.average_electricity = simpleform.cleaned_data['electricity']
                    if not simpleform.cleaned_data['gas'] is None:
                        result.unit.average_gas = simpleform.cleaned_data['gas']

                    result.unit.save_and_update(request)

                    #redirect to unit details page with an edit message
                    #TODO:
                    #redirect to thank you page instead!
                    
                    messages.add_message(request, messages.INFO, 'Saved changes to unit.')
                    if result.unit.tag:
                        finished_url = reverse('building.views.unit_details', kwargs={'city_tag':result.building.city.tag, 'bldg_tag':result.building.tag, 'unit_tag':result.unit.tag})
                    else:
                        finished_url = reverse('building.views.unit_details', kwargs={'city_tag':result.building.city.tag, 'bldg_tag':result.building.tag})



                    thank_you = "/simple-thankyou?next=%s" % quote(finished_url)
                        
                    #args=(updated.building.tag, city.tag, updated.tag)
                    #return redirect(finished_url)
                    return redirect(thank_you)


                    #in chrome, the original post url stays in the address bar.
                    #finished_url = reverse('utility.views.thank_you')
                    #return redirect(finished_url)

        else:
            errors.append("There was a problem locating the requested building")


    else:
        bldgform = NewBuildingForm(prefix='building')
        simpleform = SimpleForm(prefix='simple')
        
    #view_url = reverse('utility.views.upload_handler')
    view_url = request.path
    #upload_url, upload_data = prepare_upload(request, view_url)
    #upload_url = create_upload_url(view_url)
    upload_data = {}

    action_url = reverse('content.views.simple_data')
    
    #print form['utility_type'].errors
    #print form['utility_type'].label
    #print form['utility_type']
    #print dir(form['energy_options'])
    #print form['energy_options']

    context = { 
        'user': request.user,
        'bldgform': bldgform,
        'unitform': unitform,
        'form': simpleform,
        'show_calculator': show_calculator,
        'action_url': action_url, 
        }

    return render(request, 'simple.html', context )

def simple_thankyou(request):
    """
    this is the controller for the simple form found on the front page
    bare minimum needed for data collection
    """
    results = ''

    dest = request.GET.get('next', '')
    
    form = SignupForm

    context = { 
        'user': request.user,
        'form': form,
        'next': dest,
        #'bldgform': bldgform,
        #'unitform': unitform,
        #'form': simpleform,
        #'show_calculator': show_calculator,
        #'action_url': action_url, 
        }
    
    return render(request, 'simple-thankyou.html', context )

def welcome(request):
    """
    place to start developing a real home page for the project
    """
    #form = SimpleForm()
    bldgform = NewBuildingForm(prefix='building')
    simpleform = SimpleForm(prefix='simple')
        
    #view_url = reverse('utility.views.upload_handler')
    #view_url = request.path
    #upload_url, upload_data = prepare_upload(request, view_url)
    #upload_url = create_upload_url(view_url)
    #action_url = create_upload_url(view_url)
    action_url = reverse('content.views.simple_data')
    
    #print form['utility_type'].errors
    #print form['utility_type'].label
    #print form['utility_type']
    #print dir(form['energy_options'])
    #print form['energy_options']

    context = {
        #'city': city_name,
        #'state': state,
        #'bldg': bldg_tag,
        'form': simpleform,
        'bldgform': bldgform,
        #'results': results,
        'action_url': action_url, 
        }

    return render(request, 'welcome.html', context )

def information(request):
    """
    """
    context = {}
    return render(request, 'information.html', context )

def faq(request):
    """
    """
    context = {}
    return render(request, 'faq.html', context )

def crowdsourcing(request):
    """
    """
    context = {}
    return render(request, 'crowdsourcing.html', context )


#via: http://blog.hudarsono.me/post/2010/11/10/Using-Blobstore-with-Django-
def send_blob(request, blob_key_or_info, content_type=None, save_as=None):
    """Send a blob-response based on a blob_key.

    Sets the correct response header for serving a blob.  If BlobInfo
    is provided and no content_type specified, will set request content type
    to BlobInfo's content type.

    Args:
      blob_key_or_info: BlobKey or BlobInfo record to serve.
      content_type: Content-type to override when known.
      save_as: If True, and BlobInfo record is provided, use BlobInfos
        filename to save-as.  If string is provided, use string as filename.
        If None or False, do not send as attachment.

      Raises:
        ValueError on invalid save_as parameter.
    """

    CONTENT_DISPOSITION_FORMAT = 'attachment; filename="%s"'
    if isinstance(blob_key_or_info, blobstore.BlobInfo):
      blob_key = blob_key_or_info.key()
      blob_info = blob_key_or_info
    else:
      blob_key = blob_key_or_info
      blob_info = None

    #logging.debug(blob_info)
    response = HttpResponse()
    response[blobstore.BLOB_KEY_HEADER] = str(blob_key)

    if content_type:
      if isinstance(content_type, unicode):
        content_type = content_type.encode('utf-8')
      response['Content-Type'] = content_type
    else:
      del response['Content-Type']

    def send_attachment(filename):
      if isinstance(filename, unicode):
        filename = filename.encode('utf-8')
      response['Content-Disposition'] = (CONTENT_DISPOSITION_FORMAT % filename)

    if save_as:
      if isinstance(save_as, basestring):
        send_attachment(save_as)
      elif blob_info and save_as is True:
        send_attachment(blob_info.filename)
      else:
        if not blob_info:
          raise ValueError('Expected BlobInfo value for blob_key_or_info.')
        else:
          raise ValueError('Unexpected value for save_as')

    return response


def blob(request, key):
    return send_blob(request, key)     

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


