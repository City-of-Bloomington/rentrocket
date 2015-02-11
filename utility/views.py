import json, re
from datetime import datetime, timedelta
#from datetime import timedelta

from django.utils import timezone

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

from building.models import Building, Unit, BuildingPerson, find_by_tags, UTILITY_TYPES

from city.models import City, to_tag, all_cities
from utility.models import StatementUpload, Statement, CityServiceProvider, UtilitySummary, ServiceProvider
from rentrocket.helpers import get_client_ip, thankyou_url
        
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



class MetaUtilityForm(forms.Form):
    """
    meta data for a utility form (only needed once)
    """
    #energy_options = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(choices=ENERGY_TYPES), choices=ENERGY_TYPES, required=False)
    utility_options = [ ('', '') ]
    utility_options.extend(UTILITY_TYPES)
    ## UTILITY_TYPES[:]
    ## utility_options.insert( ('', ''), 0)
    utility_type = forms.ChoiceField(choices=utility_options, widget=forms.Select(attrs={'data-bind':"value: utility"}), required=True)

    #will update choices and initial on creation (once we know location)
    utility_provider = forms.ChoiceField(widget=forms.Select(attrs={'data-bind':"value: provider"}), choices=(), required=False)
    company = forms.CharField(widget=forms.TextInput(attrs={'data-bind':'value: other_company_name'}), label="Company name", max_length=200,
                              required=False)

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date', 'data-bind':"value: start_date"}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date', 'data-bind':"value: end_date"}), required=False)

    #this will cause knockout to grab the date from the sent data...
    #but we will need to do other manipulations in javascript,
    #so we can just reset it there
    #start_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date', 'data-bind':"valueWithInit: 'start_date'"}), required=False)
    #end_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date', 'data-bind':"valueWithInit: 'end_date'"}), required=False)

    #should be hidden unless amounts toggled
    #Common units acceptable (gallon, liter, kW, lb, kg, etc)
    #reading_unit = string (required=yes)
    #aka increment
    #not going with "unit" to avoid confusion with a unit in a building
    unit_of_measurement = forms.CharField(widget=forms.TextInput(attrs={'data-bind':'visible: enable_units'}), max_length=50, required=False)

    #widget=forms.CheckboxInput(attrs={'data-bind':"value: enable_units"}), 
    
class UtilityOneRowForm(forms.Form):
    """
    form for sharing utility data manually
    this represents one single row of data (one month's worth)
    """
    #now = timezone.now()
    #years = range(now.year, now.year-30, -1)
    #print years
    
    ## utility_type = forms.ChoiceField(choices=UTILITY_TYPES, widget=forms.Select(attrs={'data-bind':"value: utility"}))
    
    ## alt_type = forms.CharField(max_length=100, required=False)

    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class':'utility-input', 'type':'date', 'readonly':'readonly'}) )

    #Billing cost for utility consumption.
    #reading_cost = currency (required=no)
    #cost = models.FloatField(blank=True)
    cost = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'class':'utility-input'}) )

    #these should be optional fields, only visible if enabled by user:

    #Numerical value of reading (may need to consider other options like (on, off) for acceptable values
    #reading_value = number (required=yes)
    #aka value
    amount = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'class':'utility-input', 'data-bind':'visible: enable_units'}) )

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

#@csrf_exempt
def handle_json(request, city_tag=None, bldg_tag=None, unit_tag=None):
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag)

    matches = {}
    if request.is_ajax():
        if request.method == 'POST':
            ## print 'Raw Data: "%s"' % request.body
            ## print dir(request.POST)
            ## print request.POST.get('data')
            data = json.loads(request.body)
            #print data
            #print building.id, unit.id
            if data['utility']:
                end = datetime.strptime(data['end'], '%Y-%m-%d')
                end = timezone.make_aware(end, timezone.UTC())
                start = datetime.strptime(data['start'], '%Y-%m-%d')
                start = timezone.make_aware(start, timezone.UTC())
                #print type(start)
                #print start
                
                #can do lookup once we have the utility type
                #everything else is needed for storing
                main_query = UtilitySummary.objects.filter(building=building, unit=unit, type=data['utility'], start_date__lte=end, start_date__gte=start)
                #main_query = UtilitySummary.objects.filter(building=building, unit=unit, type=data['utility'])
                
                #print "Matches: %s" % len(main_query)
                for option in main_query.all():
                    #print dir(option.start_date)
                    #print type(option.start_date)
                    #print option.start_date
                    #print option.start_date.strftime('%Y-%m-01')
                    date_key = option.start_date.strftime('%Y-%m-01')
                    #date_key = option.start_date.strftime('%m/01/%Y')
                    matches[date_key] = {  }
                    if option.amount:
                        matches[date_key]['amount'] = option.amount
                    else:
                        matches[date_key]['amount'] = ''

                    if option.cost:
                        matches[date_key]['cost'] = option.cost
                    else:
                        matches[date_key]['cost'] = ''

                    #print option
                #filter by dates
                
                #convert all results to json response

    #http://stackoverflow.com/questions/2428092/creating-a-json-response-using-django-and-python
    result = json.dumps(matches)
    #print result
    return HttpResponse(result, content_type="application/json")
    #return HttpResponse("OK")

def save_json(request, city_tag=None, bldg_tag=None, unit_tag=None):
    """
    very similar functionality to edit() POST processing...

    TODO:
    is it possible to combine/abstract any functionality with edit()?
    """
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag)

    if request.is_ajax():
        if request.method == 'POST':
            data = json.loads(request.body)
            #print data
            #print building.id, unit.id
            if data['utility']:
                other_company = None
                provider = None
                if data['company_name'] != "Other":

                    provider_options = ServiceProvider.objects.filter(name=data['company_name'])
                    if len(provider_options):
                        provider = provider_options[0]
                    else:
                        print "error finding utility_provider: %s matches" % len(provider_options)                    
                else:
                    other_company = data['other_company']


                unit_updated = False
                
                for key, value in data['values'].items():
                    query = UtilitySummary.objects.filter(building=building, unit=unit, type=data['utility'], start_date=key)

                    summary = None
                    updated = False

                    if len(query):

                        summary = query[0]
                        
                        if summary.cost != value['cost']:
                            summary.cost = value['cost']
                            updated = True

                        if summary.amount != value['amount']:
                            summary.amount = value['amount']
                            updated = True
                            
                        if provider:
                            if summary.provider != provider:
                                summary.provider = provider
                                updated = True
                        else:
                            if summary.vendor != other_company:
                                summary.vendor = other_company
                                updated = True

                    else:
                        summary = UtilitySummary()
                        summary.building = building
                        summary.unit = unit
                        summary.type = data['utility']

                        #should set one of these
                        if provider:
                            summary.provider = provider
                        else:
                            summary.vendor = other_company
                            
                        summary.start_date = key
                        summary.cost = value['cost']
                        summary.amount = value['amount']
                        updated = True
                        #summary.save()
                        #print "Saving new!!"

                    if updated:
                        #TODO:
                        #consider logging any changes to prevent data loss
                        summary.save()
                        print "Changes saved"
                        unit_updated = True


                if unit_updated:
                    unit.save_and_update(request)
                    ## #only need to update this unit
                    ## unit.update_averages()
                    ## unit.update_energy_score()
                    ## print "updated unit averages"
                    ## #then update the whole building:
                    ## building.update_utility_averages()
                    ## print "updated building averages"
                        

    return HttpResponse("OK")

def make_provider_names(city):
    """
    helper to generate a list of tuples for provider_names
    for use in MetaUtilityForm
    """
    city_provider_options = CityServiceProvider.objects.filter(city=city)
    #send in a dictionary of providers for this city, grouped by utility type
    #utility_providers = { '': ['Other'] }
    utility_providers = { }
    provider_names = [('', '')]
    for cpo in city_provider_options:
        for utility in cpo.provider.utilities.all():
            if utility.type in utility_providers.keys():
                utility_providers[utility.type].append(cpo.provider.name)
            else:
                utility_providers[utility.type] = [cpo.provider.name]
        if not (cpo.provider.name, cpo.provider.name) in provider_names:
            provider_names.append( (cpo.provider.name, cpo.provider.name) )

    for ut in UTILITY_TYPES:
        #print ut
        if not ut[0] in utility_providers.keys():
            utility_providers[ut[0]] = [ "Other" ]

    provider_names.append( ('Other', 'Other') )

    return (provider_names, utility_providers)

def parse_form_providers(form):
    #look up vendor / provider
    #set those accordingly to assist with saving Summaries

    #utility_provider = forms.ChoiceField(widget=forms.Select(attrs={'data-bind':"value: provider"}), choices=(), required=False)
    #company = forms.CharField(label="Company name", max_length=200,

    provider = None

    #aka 'other field' aka 'company' (in form) aka 'vendor' in model
    company_name = None
    if form.cleaned_data['utility_provider'] != "Other":

        #this works, but seems like a roundabout way to get there
        ## subset = city_provider_options.filter(provider__name=form.cleaned_data['utility_provider'])
        ## if len(subset):
        ##     city_provider = subset[0]
        ##     provider = city_provider.provider
        ## else:
        ##     print "error finding utility_provider: %s matches" % len(subset)
        provider_options = ServiceProvider.objects.filter(name=form.cleaned_data['utility_provider'])
        if len(provider_options):
            provider = provider_options[0]
        else:
            print "error finding utility_provider: %s matches" % len(provider_options)                    
    else:
        company_name = form.cleaned_data['company']

    ## print form.cleaned_data['utility_provider']
    ## print "COMPANY NAME: ", company_name

    return (provider, company_name)

def edit(request, city_tag=None, bldg_tag=None, unit_tag=None):
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag)

    results = ''
    #UtilityFormSet = formset_factory(UtilityOneRowForm, extra=12)
    UtilityFormSet = formset_factory(UtilityOneRowForm, extra=0)

    (provider_names, utility_providers) = make_provider_names(city)
    
    if request.method == 'POST':
        meta = MetaUtilityForm(request.POST, prefix='meta')
        #http://stackoverflow.com/questions/657607/setting-the-selected-value-on-a-django-forms-choicefield
        meta.fields['utility_provider'].choices = provider_names
        utility_set = UtilityFormSet(request.POST, prefix='months')

        if meta.is_valid() and utility_set.is_valid(): 
            # All validation rules pass
            errors = False

            (provider, company_name) = parse_form_providers(meta)
            
            #keep query around for all rows
            main_query = None

            unit_updated = False

            #go through each item in utility_set
            for form in utility_set:
                #see if there is data
                if form.cleaned_data['cost'] or form.cleaned_data['amount']:
                    #if we haven't done the initial lookup yet, do it now
                    if not main_query:
                        main_query = UtilitySummary.objects.filter(building=building, unit=unit, type=meta.cleaned_data['utility_type'])
                        
                    #look up the corresponding UtilitySummary model object
                    subset = main_query.filter(start_date=form.cleaned_data['start_date'])
                    updated = False
                    #if len(subset):
                    if subset.count():
                        #already have something in the database...
                        #look at that and update accordingly
                        #print "Updating existing entry:"

                        #following equivalent?
                        summary = subset[0]
                        #summary = subset.first()

                        #if different, apply and save changes
                        if summary.cost != form.cleaned_data['cost']:
                            summary.cost = form.cleaned_data['cost']
                            updated = True

                        if summary.amount != form.cleaned_data['amount']:
                            summary.amount = form.cleaned_data['amount']
                            updated = True
                            
                        if provider:
                            if summary.provider != provider:
                                summary.provider = provider
                                updated = True
                        else:
                            if summary.vendor != company_name:
                                summary.vendor = company_name
                                updated = True

                    else:
                        summary = UtilitySummary()
                        summary.building = building
                        summary.unit = unit
                        summary.type = meta.cleaned_data['utility_type']

                        #should set one of these
                        if provider:
                            summary.provider = provider
                        else:
                            summary.vendor = company_name
                            
                        summary.start_date = form.cleaned_data['start_date']
                        summary.cost = form.cleaned_data['cost']
                        summary.amount = form.cleaned_data['amount']
                        #summary.save()
                        #print "Saving new!!"
                        updated = True

                    if updated:
                        #TODO:
                        #consider logging any changes to prevent data loss
                        summary.save()
                        #print "Changes saved"
                        unit_updated = True

            if unit_updated:
                #this takes care of updating corresponding averages and scores
                unit.save_and_update(request)

                                                                    
            #TODO:
            #would be better to redirect back to the building detail page
            #and show a thank you message
            #that message should include options to share, tweet, etc
            
            #in chrome, the original post url stays in the address bar...
            #finished_url = reverse('utility.views.thank_you')
            finished_url = thankyou_url(unit)

            return redirect(finished_url)

    else:
        #form = ShareForm()        
        now = timezone.now()
        months = previous_months()
        months.reverse()
        #for i in range(1,13):
        #    print i
        initial = []
        for month in months:
            initial.append( {'start_date': month} )
        utility_set = UtilityFormSet(initial=initial, prefix='months')

        meta = MetaUtilityForm(initial={'start_date':months[-1], 'end_date':months[0]}, prefix='meta')
        meta.fields['utility_provider'].choices = provider_names
        #meta.start_date = months[-1]
        #meta.end_date = months[0]
        
    #view_url = reverse('utility.views.upload_handler')
    view_url = request.path

    print unit
    context = {
        'city': city.name,
        #'state': state,
        'bldg': building,
        'unit': unit,
        #forms:
        'meta': meta,
        'utility': utility_set,

        'providers': json.dumps(utility_providers),
        'results': results,
        #'upload_url': upload_url, 
        }

    return render(request, 'utility_generic.html', context)

def previous_months(total=12):
    """
    return a list of datetimes that span the total number of previous months
    """
    #cur_month = datetime.utcnow().replace(day=1)
    cur_month = timezone.now().replace(day=1)
    months = [ cur_month ]
    #subtract one since we already added the cur_month above:
    for i in range(total-1):
        prev_month = cur_month - timedelta(days=1)
        prev_month = prev_month.replace(day=1)
        months.append(prev_month)
        cur_month = prev_month

    return months

    

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





class UploadForm(forms.Form):
    now = timezone.now()
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


class UploadShortForm(forms.Form):
    #these are taken from MetaUtilityForm,
    #but it seems simpler to make this custom
    utility_options = [ ('', '') ]
    utility_options.extend(UTILITY_TYPES)
    utility_type = forms.ChoiceField(choices=utility_options, widget=forms.Select(attrs={'data-bind':"value: utility"}), required=True)

    #will update choices and initial on creation (once we know location)
    utility_provider = forms.ChoiceField(widget=forms.Select(attrs={'data-bind':"value: provider"}), choices=(), required=False)

    #vendor = forms.CharField(max_length=200, required=False)
    company = forms.CharField(widget=forms.TextInput(attrs={'data-bind':'value: other_company_name'}), label="Company name", max_length=200, required=False)

    ## utility_type = forms.ChoiceField(choices=UTILITY_TYPES, widget=forms.Select(attrs={'data-bind':"value: utility"}))
    ## alt_type = forms.CharField(max_length=100, required=False)
    
    file = forms.FileField()


def upload_simple(request, city_tag=None, bldg_tag=None, unit_tag=None):
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag)

    (provider_names, utility_providers) = make_provider_names(city)
    
    if request.method == 'POST':
        print "form posted"
        form = UploadShortForm(request.POST, request.FILES)
        form.fields['utility_provider'].choices = provider_names

        #print form.fields['file'].data
        #print form.fields['file'].cleaned_data
        #print form.fields['file'].cleaned_data

        #if meta.is_valid() and form.is_valid(): 
        if form.is_valid(): 

            errors = False

            if request.FILES.has_key("file"):
                #blob_key = request.FILES["blobkey"].blobstore_info._BlobInfo__key
                blob_key = request.FILES['file'].blobstore_info.key()

                #print "BLOBKEY: ", blob_key
                #obj.blobstore_key = blob_key
                statement = Statement()
                statement.blob_key = blob_key

                statement.original_filename = request.FILES['file'].name
                
                statement.unit = unit

                statement.ip_address = get_client_ip(request)

                #print request.user
                #print dir(request.user)
                if request.user and not request.user.is_anonymous():
                    statement.user = request.user
                
                (provider, company_name) = parse_form_providers(form)
                #if form.cleaned_data.has_key('vendor'):
                #statement.vendor = form.cleaned_data['vendor']

                #should set one of these
                if provider:
                    statement.provider = provider
                else:
                    statement.vendor = company_name

                #if form.cleaned_data.has_key('utility_type'):
                #if meta.cleaned_data['utility_type'] == 'other':
                #if form.cleaned_data['utility_type'] == 'other':
                    #if form.cleaned_data.has_key('alt_type'):
                    #statement.type = form.cleaned_data['alt_type']
                #else:
                statement.type = form.cleaned_data['utility_type']
                                
                statement.save()
                #print statement
                #form.save()
                #return HttpResponseRedirect(view_url)
                #return redirect(view_url, permanent=True)
                #in chrome, the original post url stays in the address bar...
                finished_url = reverse('utility.views.thank_you')
                return redirect(finished_url)

            else:
                print "NO BLOBKEY!!!", str(request)
                print dir(request)
                print request.FILES
                if request.FILES.has_key('file'):
                    print request.FILES['file']
                    print dir(request.FILES['file'])
                    print request.FILES['file'].blobstore_info.key()
                print 

        else:
            print dir(form)
            print form.errors
            print "form did not validate"

    else:
        #form = UploadShortForm()
        #meta = MetaUtilityForm(prefix='meta')

        form = UploadShortForm()
        form.fields['utility_provider'].choices = provider_names
        
    #view_url = reverse('utility.views.upload_handler')
    view_url = request.path
    #upload_url, upload_data = prepare_upload(request, view_url)
    upload_url = create_upload_url(view_url)
    upload_data = {}
    
    context = {
        'city': city.name,
        'bldg': building,
        'unit': unit,
        #'form': form,
        'meta': form,
        'upload_url': upload_url,
        'providers': json.dumps(utility_providers),        
        }

    return render(request, 'upload_simple.html', context )


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

def secret2(request):
    if request.user.is_staff:
        upload_q = Statement.objects.all()    
        return render(request, 'secret2.html', {"upload_q":upload_q})
    else:
        raise Http404
        #return render(request, '404.html', {})



## def upload(request, state=None, city_name=None, bldg_tag=None):
    
##     results = ''

##     if request.method == 'POST': # If the form has been submitted...
##         form = MetaUtilityForm(request.POST) # A form bound to the POST data
##         if form.is_valid(): # All validation rules pass
##             # Process the data in form.cleaned_data
##             # ...
##             results += "THANK YOU!<br> "
##             results += str(form.cleaned_data)
##             #return HttpResponseRedirect('/thanks/') # Redirect after POST
##     else:
##         form = MetaUtilityForm() # An unbound form

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

