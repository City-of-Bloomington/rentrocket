import json, re
from datetime import datetime

from google.appengine.ext import blobstore

from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render, redirect

from django.core.urlresolvers import reverse
from django import forms
from django.forms import extras
from django.forms import widgets
from django.forms.formsets import formset_factory

from building.models import Building, Unit, BuildingPerson, find_by_tags

from city.models import City, to_tag, all_cities
from utility.models import UTILITY_TYPES, StatementUpload
from rentrocket.helpers import get_client_ip
        
#from filetransfers.api import prepare_upload
from google.appengine.ext.blobstore import create_upload_url


ENERGY_TYPES = (
    ('electricity', 'Electricity'),
    ('gas', 'Natural Gas'),
    ('other', 'Other'),
    #('oil', 'Heating Oil'),
    )

BEDROOMS = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6 or More'),
    )



STATES = (
    ("", ""),
    ("AL","AL"),
    ("AK", "AK"),
    ("AZ", "AZ"),
    ("AR", "AR"),
    ("CA", "CA"),
    ("CO", "CO"),
    ("CT", "CT"),
    ("DE", "DE"),
    ("FL", "FL"),
    ("GA", "GA"),
    ("HI", "HI"),
    ("ID", "ID"),
    ("IL", "IL"),
    ("IN", "IN"),
    ("IA", "IA"),
    ("KS", "KS"),
    ("KY", "KY"),
    ("LA", "LA"),
    ("ME", "ME"),
    ("MD", "MD"),
    ("MA", "MA"),
    ("MI", "MI"),
    ("MN", "MN"),
    ("MS", "MS"),
    ("MO", "MO"),
    ("MT", "MT"),
    ("NE", "NE"),
    ("NV", "NV"),
    ("NH", "NH"),
    ("NJ", "NJ"),
    ("NM", "NM"),
    ("NY", "NY"),
    ("NC", "NC"),
    ("ND", "ND"),
    ("OH", "OH"),
    ("OK", "OK"),
    ("OR", "OR"),
    ("PA", "PA"),
    ("RI", "RI"),
    ("SC", "SC"),
    ("SD", "SD"),
    ("TN", "TN"),
    ("TX", "TX"),
    ("UT", "UT"),
    ("VT", "VT"),
    ("VA", "VA"),
    ("WA", "WA"),
    ("WV", "WV"),
    ("WI", "WI"),
)

class ExtendedCitySelectForm(forms.Form):
    """
    based on the CitySelectForm from: rentrocket/city/views.py

    in this case we do not want the form to automatically submit
    plus we want the user to be able to specify a different city, if needed. 
    """
    options = [ ('', "Choose location...") ]

    keys = all_cities.keys()
    keys.sort()
    for key in keys:
        options.append( (key, "%s, %s" % (all_cities[key]['name'], all_cities[key]['state'])) )

    options.append( ('other', "Other") )
    
    #http://stackoverflow.com/questions/2902008/django-how-do-i-add-arbitrary-html-attributes-to-input-fields-on-a-form
    #https://docs.djangoproject.com/en/dev/ref/forms/widgets/#select
    city = forms.ChoiceField(options, widget=forms.Select(attrs={'data-bind':"value: city"}))

    alt_city = forms.CharField(max_length=100, required=False)
    alt_state = forms.ChoiceField(STATES, widget=forms.Select(attrs={}), required=False)



class UtilityForm(forms.Form):
    #energy_options = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(choices=ENERGY_TYPES), choices=ENERGY_TYPES, required=False)
    utility_options = [ ('', '') ]
    utility_options.extend(UTILITY_TYPES)
    ## UTILITY_TYPES[:]
    ## utility_options.insert( ('', ''), 0)
    utility_type = forms.ChoiceField(choices=utility_options, widget=forms.Select(attrs={'data-bind':"value: utility"}), required=True)
    
    company = forms.CharField(max_length=200, required=False)

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date', 'data-bind':"value: utility"}), required=False)
    end_date = forms.DateField(required=False)

    #should be hidden unless amounts toggled
    #Common units acceptable (gallon, liter, kW, lb, kg, etc)
    #reading_unit = string (required=yes)
    #aka increment
    #not going with "unit" to avoid confusion with a unit in a building
    unit_of_measurement = forms.CharField(max_length=50, required=False)


    
class UtilityOneForm(forms.Form):
    """
    form for sharing utility data manually
    """
    #now = datetime.now()
    #years = range(now.year, now.year-30, -1)
    #print years
    
    ## utility_type = forms.ChoiceField(choices=UTILITY_TYPES, widget=forms.Select(attrs={'data-bind':"value: utility"}))
    
    ## alt_type = forms.CharField(max_length=100, required=False)


    start_date = forms.DateField(required=False)

    #Billing cost for utility consumption.
    #reading_cost = currency (required=no)
    #cost = models.FloatField(blank=True)
    cost = forms.DecimalField(required=False)

    #these should be optional fields, only visible if enabled by user:

    #Numerical value of reading (may need to consider other options like (on, off) for acceptable values
    #reading_value = number (required=yes)
    #aka value
    amount = forms.DecimalField(required=False)



    #Last day of the utility service billing period in YYYY-MM-DD format
    #to simplify data entry, will only require a start date...
    #can infer end date
    #reading_period_end_date = date (required=no)
    #end_date = models.DateTimeField(blank=True)

    #this should be handled in parent form (or based on context)
    #One of the following categories (water, sewer, storm water, gas, electricity, trash, recycling, compost, data, video, phone, data+video, video+phone, data+phone, data+video+phone, wifi). It would be nice to keep the nomenclature common across cities for analytical purposes.
    #reading_type = string (required=yes)
    #type = models.CharField(max_length=12, choices=UTILITY_TYPES, default="electricity")

    #again, this should be handled in parent form (or based on context)
    #Vendor for utility service. Examples: City of Bloomington Utilities, Comcast, AT&T, Duke Energy, etc)
    #vendor = string (required=no)
    #vendor = models.CharField(max_length=200, blank=True)



def edit(request, city_tag=None, bldg_tag=None, unit_tag=None):
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag)

    results = ''
    UtilityFormSet = formset_factory(UtilityOneForm, extra=12)
    
    if request.method == 'POST':
        meta = UtilityForm(request.POST, prefix='meta')
        utility_set = UtilityFormSet(request.POST, prefix='months')
        #form = ShareForm(request.POST)

        if form.is_valid(): # All validation rules pass
            #need to do a specialized validation here..
            #alt_city and alt_state only required if city == other

            errors = False

            if request.FILES.has_key("file"):
                #blob_key = request.FILES["blobkey"].blobstore_info._BlobInfo__key

                blob_key = request.FILES['file'].blobstore_info.key()

                #print "BLOBKEY: ", blob_key
                #obj.blobstore_key = blob_key
                statement = StatementUpload()
                statement.blob_key = blob_key
                
                statement.city_tag = to_tag(city_name + " " + state)

                if bldg_tag:
                    statement.building_address = bldg_tag
                else:
                    #if form.cleaned_data.has_key('email'):
                    statement.building_address = form.cleaned_data['address']
                statement.unit_number = unit_tag

                statement.ip_address = get_client_ip(request)
                #if form.cleaned_data.has_key('email'):
                statement.person_email = form.cleaned_data['email']

                #print request.user
                #print dir(request.user)
                if request.user and not request.user.is_anonymous():
                    statement.user = request.user
                
                #if form.cleaned_data.has_key('vendor'):
                statement.vendor = form.cleaned_data['vendor']

                #if form.cleaned_data.has_key('utility_type'):
                if form.cleaned_data['utility_type'] == 'other':
                    #if form.cleaned_data.has_key('alt_type'):
                    statement.type = form.cleaned_data['alt_type']
                else:
                    statement.type = form.cleaned_data['utility_type']

                #if form.cleaned_data.has_key('move_in'):
                statement.move_in = form.cleaned_data['move_in']

                #if form.cleaned_data.has_key('energy_options'):
                #statement.energy_options = form.cleaned_data['energy_options']
                options = form.cleaned_data['energy_options']
                if 'other' in options:
                    options.remove('other')
                    if form.cleaned_data['alt_energy']:
                        options.append(form.cleaned_data['alt_energy'])
                
                statement.energy_sources = options

                statement.unit_details = { 'bedrooms': form.cleaned_data['bedrooms'], 'sqft': form.cleaned_data['sqft'], }
                                
                statement.save()
                #print statement
                #form.save()
                #return HttpResponseRedirect(view_url)
                #return redirect(view_url, permanent=True)
                #in chrome, the original post url stays in the address bar...
                finished_url = reverse('utility.views.thank_you')
                return redirect(finished_url)

            ## else:
            ##     print "NO BLOBKEY!!!", str(request)
            ##     print dir(request)
            ##     print request.FILES
            ##     if request.FILES.has_key('file'):
            ##         print request.FILES['file']
            ##         print dir(request.FILES['file'])
            ##         print request.FILES['file'].blobstore_info.key()
            ##     print 

    else:
        #form = ShareForm()
        meta = UtilityForm(prefix='meta')
        utility_set = UtilityFormSet(prefix='months')
        
    #view_url = reverse('utility.views.upload_handler')
    view_url = request.path

    print unit
    context = {
        'city': city.name,
        #'state': state,
        'bldg': building,
        'unit': unit,
        'meta': meta,
        'utility': utility_set,
        'results': results,
        #'upload_url': upload_url, 
        }

    return render(request, 'utility_generic.html', context )


def details(request, city_tag, bldg_tag, unit_tag=''):
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag='')

    #print unit.full_address()
    context = { 'building': building,
                'units': [unit],
                'unit': unit,
                'user': request.user,
                #'redirect_field': REDIRECT_FIELD_NAME,
                }
    return render(request, 'unit_details.html', context)




## class UtilityForm(forms.Form):
##     utility_type = forms.ChoiceField(choices=UTILITY_TYPES)


class UploadForm(forms.Form):
    now = datetime.now()
    years = range(now.year, now.year-30, -1)
    #print years
    
    utility_type = forms.ChoiceField(choices=UTILITY_TYPES, widget=forms.Select(attrs={'data-bind':"value: utility"}))
    alt_type = forms.CharField(max_length=100, required=False)
    
    file = forms.FileField()
    address = forms.CharField(max_length=100, required=False)
    vendor = forms.CharField(max_length=200, required=False)
    move_in = forms.DateField(widget=extras.SelectDateWidget(years=years), required=False)
    energy_options = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(choices=ENERGY_TYPES), choices=ENERGY_TYPES, required=False)
    alt_energy = forms.CharField(max_length=100, required=False)
    bedrooms = forms.ChoiceField(widget=widgets.RadioSelect(choices=BEDROOMS), choices=BEDROOMS, required=False)
    sqft = forms.CharField(max_length=5, required=False)
    email = forms.EmailField(required=False)


def upload(request, state=None, city_name=None, bldg_tag=None, unit_tag=None):
    results = ''
    
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid(): # All validation rules pass
            #need to do a specialized validation here..
            #alt_city and alt_state only required if city == other

            errors = False

            if request.FILES.has_key("file"):
                #blob_key = request.FILES["blobkey"].blobstore_info._BlobInfo__key

                blob_key = request.FILES['file'].blobstore_info.key()

                #print "BLOBKEY: ", blob_key
                #obj.blobstore_key = blob_key
                statement = StatementUpload()
                statement.blob_key = blob_key
                
                statement.city_tag = to_tag(city_name + " " + state)

                if bldg_tag:
                    statement.building_address = bldg_tag
                else:
                    #if form.cleaned_data.has_key('email'):
                    statement.building_address = form.cleaned_data['address']
                statement.unit_number = unit_tag

                statement.ip_address = get_client_ip(request)
                #if form.cleaned_data.has_key('email'):
                statement.person_email = form.cleaned_data['email']

                #print request.user
                #print dir(request.user)
                if request.user and not request.user.is_anonymous():
                    statement.user = request.user
                
                #if form.cleaned_data.has_key('vendor'):
                statement.vendor = form.cleaned_data['vendor']

                #if form.cleaned_data.has_key('utility_type'):
                if form.cleaned_data['utility_type'] == 'other':
                    #if form.cleaned_data.has_key('alt_type'):
                    statement.type = form.cleaned_data['alt_type']
                else:
                    statement.type = form.cleaned_data['utility_type']

                #if form.cleaned_data.has_key('move_in'):
                statement.move_in = form.cleaned_data['move_in']

                #if form.cleaned_data.has_key('energy_options'):
                #statement.energy_options = form.cleaned_data['energy_options']
                options = form.cleaned_data['energy_options']
                if 'other' in options:
                    options.remove('other')
                    if form.cleaned_data['alt_energy']:
                        options.append(form.cleaned_data['alt_energy'])
                
                statement.energy_sources = options

                statement.unit_details = { 'bedrooms': form.cleaned_data['bedrooms'], 'sqft': form.cleaned_data['sqft'], }
                                
                statement.save()
                #print statement
                #form.save()
                #return HttpResponseRedirect(view_url)
                #return redirect(view_url, permanent=True)
                #in chrome, the original post url stays in the address bar...
                finished_url = reverse('utility.views.thank_you')
                return redirect(finished_url)

            ## else:
            ##     print "NO BLOBKEY!!!", str(request)
            ##     print dir(request)
            ##     print request.FILES
            ##     if request.FILES.has_key('file'):
            ##         print request.FILES['file']
            ##         print dir(request.FILES['file'])
            ##         print request.FILES['file'].blobstore_info.key()
            ##     print 

    else:
        form = UploadForm()
        
    #view_url = reverse('utility.views.upload_handler')
    view_url = request.path
    #upload_url, upload_data = prepare_upload(request, view_url)
    upload_url = create_upload_url(view_url)
    upload_data = {}
    
    #print form['utility_type'].errors
    #print form['utility_type'].label
    #print form['utility_type']
    #print dir(form['energy_options'])
    #print form['energy_options']

    context = {
        'city': city_name,
        'state': state,
        'bldg': bldg_tag,
        'form': form,
        'results': results,
        'upload_url': upload_url, 
        }

    return render(request, 'upload_generic.html', context )




BLOOMINGTON_UTILITY_CHOICES = (
    ('vectren', 'Vectren'),
    ('duke', 'Duke'),
    )

class BloomingtonUtilityForm(forms.Form):
    utility_name = forms.ChoiceField(widget=widgets.RadioSelect(), choices=BLOOMINGTON_UTILITY_CHOICES)

    ## name = forms.CharField(max_length=100)
    ## title = forms.CharField(max_length=3,
    ##             widget=forms.Select(choices=TITLE_CHOICES))
    ## birth_date = forms.DateField(required=False)


## Who supplies your energy?  </p>
##  Only Duke 
##  Only Vectren 
##  Both Duke and Vectren 

## Number of months you have lived at this address:  </p>
##  1-4 
##  5-8 
##  9-12 
##  More than 12 

## How many bedrooms does your residence have?  </p>
##  1 bedroom/studio 
##  2 bedrooms 
##  3 bedrooms 
##  More than 4 bedrooms 


def upload_bloomington(request, bldg_tag=None):
    
    results = ''

    state = "IN"
    city_name = "Bloomington"
    
    if request.method == 'POST': # If the form has been submitted...
        form = UtilityForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            results += "THANK YOU!<br> "
            results += str(form.cleaned_data)
            #return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = UtilityForm() # An unbound form

    context = {
        'form': form,
        'results': results,
        }

    return render(request, 'upload_generic.html', context )




def thank_you(request):
    return render(request, 'thank_you.html', {})


def secret(request):
    #check that user is authenticated
    #check that user is admin

    #if not:
    #404
    #else:
    #show all uploads:
    if request.user.is_staff:
        upload_q = StatementUpload.objects.all()    
        return render(request, 'secret.html', {"upload_q":upload_q})
    else:
        raise Http404
        #return render(request, '404.html', {})



## def upload(request, state=None, city_name=None, bldg_tag=None):
    
##     results = ''

##     if request.method == 'POST': # If the form has been submitted...
##         form = UtilityForm(request.POST) # A form bound to the POST data
##         if form.is_valid(): # All validation rules pass
##             # Process the data in form.cleaned_data
##             # ...
##             results += "THANK YOU!<br> "
##             results += str(form.cleaned_data)
##             #return HttpResponseRedirect('/thanks/') # Redirect after POST
##     else:
##         form = UtilityForm() # An unbound form

##     context = {
##         'form': form,
##         'results': results,
##         }

##     return render(request, 'upload_generic.html', context )



def submit(request):

    context = {}
    return render(request, 'upload_submit.html', context )

def index(request):
    results = ''


    if request.method == 'POST': # If the form has been submitted...
        # A form bound to the POST data
        form = ExtendedCitySelectForm(request.POST) 
        if form.is_valid(): # All validation rules pass
            #need to do a specialized validation here..
            #alt_city and alt_state only required if city == other

            errors = False
            if form.cleaned_data['city'] == "other":
                if not form.cleaned_data['alt_city']:
                    form.errors['alt_city'] = "Please specify the city."
                    errors = True
                    
                if not form.cleaned_data['alt_state']:
                    form.errors['alt_state'] = "Please specify the state."
                    errors = True

                if not errors:
                    #ok...
                    #must be ok now...
                    
                    results += "THANK YOU!<br> "
                    results += str(form.cleaned_data)
                    # Redirect after POST
                    #return HttpResponseRedirect('/thanks/') 
                    #print "HELLO!?!"
                    #print dir(form)
                    #results += str(dir(form))
                    url = '/utility/upload/' + form.cleaned_data['alt_state'] + "/" + form.cleaned_data['alt_city'] + "/"
                    return HttpResponseRedirect(url)
            else:
                dbcity = all_cities.get(form.cleaned_data['city'], None)
                print dbcity

                #result = ""
                if dbcity:
                    #result += "Found match: %s" % city[0].name
                    #result += "Found match: %s" % city['name']

                    #update the city in our session for future reference:
                    #request.session['city'] = dbcity
                    #assert city['tag'] == city_tag
                    url = '/utility/upload/' + dbcity['state'] + "/" + dbcity['name'] + "/"
                    return HttpResponseRedirect(url)
                else:
                    #shouldn't get here:
                    form.errors['city'] = "Unknown city selected."
                    errors = True
                

    else:
        form = ExtendedCitySelectForm() # An unbound form


    context = {
        'form': form,
        'results': results,
        }

    return render(request, 'utility_index.html', context )

