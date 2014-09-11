from google.appengine.ext import blobstore

from django.template import Context, loader
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render

from django.core.urlresolvers import reverse
from django import forms
from django.forms import extras
from django.forms import widgets

#from rentrocket.helpers import address_search
from building.models import search_building

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
    ('owned', 'is not'),
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
    
    address = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': 'Street, City, State, Zip'}))

    #zip_code = forms.CharField(max_length=10, required=True)

    property_type = forms.ChoiceField(choices=DWELLING_CHOICES, widget=forms.Select(attrs={'data-bind':"value: property_type"}))
    rent = forms.FloatField(widget=forms.TextInput(attrs={'size': '9'}), required=False)
    
    #bedrooms = forms.ChoiceField(widget=widgets.RadioSelect(choices=BEDROOMS), choices=BEDROOMS, required=False)
    #bedrooms = forms.IntegerField(required=True)
    bedrooms = forms.ChoiceField(choices=BEDROOM_CHOICES, label='# of Bedrooms', required=True)

    electricity = forms.FloatField(widget=forms.TextInput(attrs={'size': '9'}), required=False)

    gas = forms.FloatField(label='Natural Gas', widget=forms.TextInput(attrs={'size': '9'}), required=False)

    #city = forms.ChoiceField(options, widget=forms.Select(attrs={'data-bind':"value: city"}))    
    ## alt_type = forms.CharField(max_length=100, required=False)    
    ## file = forms.FileField()
    ## vendor = forms.CharField(max_length=200, required=False)
    ## move_in = forms.DateField(widget=extras.SelectDateWidget(years=years), required=False)
    ## energy_options = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(choices=ENERGY_TYPES), choices=ENERGY_TYPES, required=False)
    ## alt_energy = forms.CharField(max_length=100, required=False)
    ## sqft = forms.CharField(max_length=5, required=False)
    ## email = forms.EmailField(required=False)

def simple_data(request):
    """
    this is the controller for the simple form found on the front page
    bare minimum needed for data collection
    """
    results = ''

    #probably OK to show the calculator worksheet either way
    show_calculator = True

    
    if request.method == 'POST':
        #form = SimpleForm(request.POST, request.FILES)
        form = SimpleForm(request.POST)

        #image button must submit a hybrid value with x and y...
        #discovered by printing POST
        #print request.POST
        if 'calculator.x' in request.POST or 'calculator.y' in request.POST:
            show_calculator = True
            print "SHOWING CALCULATOR!!"

        if form.is_valid(): # All validation rules pass

            errors = False

            #results = address_search(form.cleaned_data['address'])
            results = search_building(form.cleaned_data['address'])
            print "OPTIONS!:"
            print results

            if not form.cleaned_data['alt_city']:
                form.errors['alt_city'] = "Please specify the city."
                errors = True

            #if options == 1:
            #see if we have the city specified in selected option
            #if not, create it

            #then see if we have a matching building

            #if so, and if unit or apartment
            #ask if this is a unit that is part of the building

            #if not, create building + unit
            #add supplied details to building


            #if we have details for utility usage
            #process (and save) those here





            #need to do a specialized validation here..
            #alt_city and alt_state only required if city == other
            
            ## if bldg_tag:
            ##     statement.building_address = bldg_tag
            ## else:
            ##     #if form.cleaned_data.has_key('email'):
            ##     statement.building_address = form.cleaned_data['address']
            ## statement.unit_number = unit_tag

            ## statement.ip_address = get_client_ip(request)
            ## #if form.cleaned_data.has_key('email'):
            ## statement.person_email = form.cleaned_data['email']

            ## #print request.user
            ## #print dir(request.user)
            ## if request.user and not request.user.is_anonymous():
            ##     statement.user = request.user

            ## #if form.cleaned_data.has_key('vendor'):
            ## statement.vendor = form.cleaned_data['vendor']

            ## #if form.cleaned_data.has_key('utility_type'):
            ## if form.cleaned_data['utility_type'] == 'other':
            ##     #if form.cleaned_data.has_key('alt_type'):
            ##     statement.type = form.cleaned_data['alt_type']
            ## else:
            ##     statement.type = form.cleaned_data['utility_type']

            ## #if form.cleaned_data.has_key('move_in'):
            ## statement.move_in = form.cleaned_data['move_in']

            ## #if form.cleaned_data.has_key('energy_options'):
            ## #statement.energy_options = form.cleaned_data['energy_options']
            ## options = form.cleaned_data['energy_options']
            ## if 'other' in options:
            ##     options.remove('other')
            ##     if form.cleaned_data['alt_energy']:
            ##         options.append(form.cleaned_data['alt_energy'])

            ## statement.energy_sources = options

            ## statement.unit_details = { 'bedrooms': form.cleaned_data['bedrooms'], 'sqft': form.cleaned_data['sqft'], }

            ## statement.save()
            ## #print statement
            ## #form.save()
            ## #return HttpResponseRedirect(view_url)
            ## #return redirect(view_url, permanent=True)
            ## #in chrome, the original post url stays in the address bar...
            ## finished_url = reverse('utility.views.thank_you')
            ## return redirect(finished_url)

    else:
        form = SimpleForm()
        
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
        #'city': city_name,
        #'state': state,
        #'bldg': bldg_tag,
        'form': form,
        'show_calculator': show_calculator,
        'action_url': action_url, 
        }

    return render(request, 'simple.html', context )


def welcome(request):
    """
    place to start developing a real home page for the project
    """
    form = SimpleForm()
        
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
        'form': form,
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


