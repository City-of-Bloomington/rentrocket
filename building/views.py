import json, re

from django.template import Context, loader
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, extras, widgets
from django import forms

from django.forms.util import ErrorList

from django.contrib import messages
from django.core.urlresolvers import reverse

from models import Building, Unit, Listing, BuildingPerson, ChangeDetails, search_building, RentHistory, find_by_tags

from city.models import City, to_tag, all_cities
from rentrocket.helpers import get_client_ip, address_search

#from django.shortcuts import render_to_response, get_object_or_404

#render vs render_to_response:
#http://stackoverflow.com/questions/5154358/django-what-is-the-difference-between-render-render-to-response-and-direc
#
# render() automatically includes context_instance (current request) with call

def index(request):
    ## t = loader.get_template('index.html')
    ## t = loader.get_template('preferences/index.html')
    ## c = Context({
    ##     'latest_preferences': latest_preferences,
    ## })
    ## return HttpResponse(t.render(c))

    ## form = EventForm()
    
    ## #render_to_response does what above (commented) section does
    ## #return render_to_response('general/index.html', {'user': request.user})

    #buildings = Building.objects.all().order_by('-pub_date')[:5]
    #buildings = Building.objects.all()

    city = City.objects.filter(tag=to_tag("Ann Arbor"))
    
    buildings = Building.objects.filter(city=city)
    context = {'buildings': buildings}

    return render(request, 'index.html', context )

    #return HttpResponse("Hello, world. You're at the building index.")

def map(request, lat=39.166537, lng=-86.531754, zoom=14):
    
    #buildings = Building.objects.filter(city=city)
    context = {'lat': lat,
               'lng': lng,
               'zoom': zoom,
               }

    return render(request, 'map.html', context)

#previously in models.Building.to_dict
def render_as_json(request, building):
    """
    return a simple dictionary representation of the building
    this is used by ajax calls to get a representation of the building
    (via views.lookup)

    This is different than an attempt to convert
    to a full dictionary representation,
    in which case django model_to_dict might be a better solution
    """
    #t = loader.get_template('preferences/index.html')
    #c = Context({
    ##     'latest_preferences': latest_preferences,
    ## })

    t = loader.get_template('building_overlay.html')
    context = Context({ 'building': building,
                })
    #return HttpResponse(t.render(c))
    #profile = render(request, 'building_overlay.html', context)
    profile = t.render(context)

    #old, manual way:
    #profile = '<a href="%s">%s</a>' % (building.url(), building.address)

    result = {'score': building.energy_score, 'address': building.address, 'lat': building.latitude, 'lng': building.longitude, 'profile': profile}
    return result


def lookup(request, lat1, lng1, lat2, lng2, city_tag=None, type="rental", limit=100):
    """
    this is a json request to lookup buildings within a given area
    should return json results that are easy to parse and show on a map

    http://stackoverflow.com/questions/2428092/creating-a-json-response-using-django-and-python
    """
    city = None
    if city_tag:
        city_q = City.objects.filter(tag=city_tag)
        if len(city_q):
            city = city_q[0]

    if city:
        #https://docs.djangoproject.com/en/dev/topics/db/queries/#spanning-multi-valued-relationships
        #rather than multiple filters:
        #(subjectively, this seems slower, or the same)
        #bq = Building.objects.all().filter(city=city).filter(latitude__gte=float(lat1)).filter(longitude__gte=float(lng1)).filter(latitude__lte=float(lat2)).filter(longitude__lte=float(lng2)).order_by('-energy_score')
        
        #it may be better to provide all parameters to on call to filter:
        bq = Building.objects.all().filter(city=city, latitude__gte=float(lat1), longitude__gte=float(lng1), latitude__lte=float(lat2), longitude__lte=float(lng2)).order_by('-energy_score')

    else:
        #bq = Building.objects.all().filter(latitude__gte=float(lat1)).filter(longitude__gte=float(lng1)).filter(latitude__lte=float(lat2)).filter(longitude__lte=float(lng2)).order_by('-energy_score')
        bq = Building.objects.all().filter(latitude__gte=float(lat1), longitude__gte=float(lng1), latitude__lte=float(lat2), longitude__lte=float(lng2)).order_by('-energy_score')
        
    all_bldgs = []
    for building in bq[:limit]:
        #all_bldgs.append(building.to_dict())
        all_bldgs.append(render_as_json(request, building))

    #at this point we need a city to have cutoffs...
    #if we don't have that, just use Bloomington for now:
    if not city:
        city_q = City.objects.filter(tag="bloomington_in")
        if len(city_q):
            city = city_q[0]

    cutoffs = city.cutoffs.split(',')        
        
    bldg_dict = {'buildings': all_bldgs, 'total': len(bq), 'cutoffs': cutoffs}

    #print bldg_dict
    #print cutoffs
    
    return HttpResponse(json.dumps(bldg_dict), content_type="application/json")


def match_existing(request, query=None, city_tag=None, limit=100):
    """
    similar to lookup, but filter results by query instead of geo-coords
    """
    if not query:
        query = request.GET.get('query', '')
        

    all_bldgs = []
    if not query:
        print "Empty query... skipping"
        
    else:
        city = None
        if city_tag:
            city_q = City.objects.filter(tag=city_tag)
            if len(city_q):
                city = city_q[0]

        if city:
            bq = Building.objects.all().filter(city=city).filter(address__icontains=query).order_by('-energy_score')
        else:
            bq = Building.objects.all().filter(address__icontains=query).order_by('-energy_score')

        all_bldgs = []
        for building in bq[:limit]:
            #all_bldgs.append(building.to_dict())
            #all_bldgs.append(render_as_json(request, building))
            all_bldgs.append( { 'value': building.address, 'data': { 'building_tag': building.tag, 'city_tag': building.city.tag } } )

    print all_bldgs
    #this is the format required by jquery.autocomplete (devbridge) plugin:
    bldg_dict = {'suggestions': all_bldgs}
        
    return HttpResponse(json.dumps(bldg_dict), content_type="application/json")

def search_geo(request, query=None, limit=100):
    """
    use a geocoder to look up options that match...
    this is the first phase of adding a new building,
    and it would be nice to start providing relevant results instantly
    """
    all_options = []
    if not query:
        query = request.GET.get('query', '')
        
    if not query:
        #print "Empty query... skipping"
        pass
        
    else:
        #print "QUERY: %s" % query
        #(search_options, error, unit) = address_search(query)
        results = address_search(query)

        for option in results.matches[:limit]:
            if option.has_key('place_total'):
                all_options.append( { 'value': option['place_total'], 'data': option['place_total'] } )

    print all_options
    #this is the format required by jquery.autocomplete (devbridge) plugin:
    options_dict = {'suggestions': all_options}
        
    return HttpResponse(json.dumps(options_dict), content_type="application/json")






## def send_json(request, bldg_tag, city_tag):
##     pass

#not sure that this is necessary... edit suffices
## def update(request, bldg_tag, city_tag):
##     pass

class ChooseUnitForm(forms.Form):
    unit_text = forms.CharField(max_length=15, label='New Unit', required=False, widget=forms.TextInput(attrs={ 'placeholder': 'Apt #', 'size': '10' }))

    def __init__(self, *args, **kwargs):
        #extra = kwargs.pop('extra')
        choices = kwargs.pop('choices')
        super(ChooseUnitForm, self).__init__(*args, **kwargs)
        
        self.fields['unit_select'] = forms.ChoiceField(choices, label='Available Units', required=False, widget=forms.Select(attrs={'onchange':"this.form.submit()"}))
        

class NewBuildingForm(forms.Form):
    #address = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={ 'placeholder': 'Street + Apt#, City, State, Zip', 'class': 'typeahead', 'size': '40' }))
    address = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={ 'placeholder': 'Street + Apt#, City, State, Zip', 'class': 'typeahead form-control', 'type':'address'}))

    #these are handled by autocomplete now
    #search_options_visible = False
    #search_options = False

    unit_select_visible = False

    #moving this logic into the controller
    #it would be nice to have access to the search result for later checks
    ## def clean(self):
    ##     print "cleaning called!"
    ##     cleaned_data = super(NewBuildingForm, self).clean()

    ##     result = search_building(cleaned_data.get("address"))
    ##     #result = search_building(cleaned_data.get("address"))
    ##     #print result

    ##     if result.errors:
    ##         for error in result.errors:
    ##             raise forms.ValidationError(error)

    ##     # wait on creating... handle this in view:
    ##     ## elif not result.building:
    ##     ##     #we don't have something that matches an existing building
    ##     ##     #should be ok to make a new one!
    ##     ##     result = search_building(cleaned_data.get("address"), make=True)
    ##     ##     if result.errors:
    ##     ##         for error in result.errors:
    ##     ##             raise forms.ValidationError(error)

    ##     elif (not result.unit) and (result.building.units.count() > 1):
    ##         #what about one unit, but unit.number != ''?
    ##         #also want to add then
    ##         self.unit_select_visible = True

    ##         #self.__init__()
    ##         #print dir(self.fields['unit_select'])
    ##         #self.fields['unit_select'].choices = choices
    ##         #self.unit_options = False
    ##         #print "UNIT TEXT: ", self.unit_text

    ##         raise forms.ValidationError("Please specify a unit or apartment number")

    ##     #http://stackoverflow.com/questions/15946979/django-form-cleaned-data-is-none
    ##     #must return cleaned_data!!
    ##     return cleaned_data


def validate_building_and_unit(request):
    """
    common process for showing and validating the multipart form
    to create a new building, plus a new unit if needed.
    
    should only be called after a request has been posted!
    """
    unitform = None
    bldgform = NewBuildingForm(request.POST, prefix='building')

    #want to keep this around for all checks:
    result = None

    if bldgform.is_valid(): # All validation rules pass

        result = search_building(bldgform.cleaned_data.get("address"))

        ## #in case we need to add errors to the form
        ## errors = bldgform._errors.setdefault(forms.forms.NON_FIELD_ERRORS, ErrorList())
        ## if result.errors:
        ##     #http://stackoverflow.com/questions/188886/inject-errors-into-already-validated-form
        ##     #although once this is on django 1.7:
        ##     #https://docs.djangoproject.com/en/dev/ref/forms/api/#django.forms.Form.add_error
        ##     for error in result.errors:                    
        ##         errors.append(error)

        ##     #no need to go any further... handle those errors first

        ## else:
        if not result.errors:
            if (result.building) and (not result.unit) and (result.building.units.count() > 1):
                #what about one unit, but unit.number != ''?
                #also want to add then
                bldgform.unit_select_visible = True
                result.errors.append("Please specify a unit or apartment number")
                
            elif (not result.building):
                #need to make a new building here!
                result = search_building(bldgform.cleaned_data.get("address"), make=True)
            else:
                #must have a building, and don't need to make anything:
                #result will get sent back
                pass

            if bldgform.unit_select_visible:
                #we've discovered that there are units available
                #ask for clarification

                choices = [ ('', '') ]
                for unit in result.building.units.all():
                    choices.append( (unit.number, unit.number) )

                unitform = ChooseUnitForm(request.POST, prefix='unit', choices=choices)
                #maybe the form has the clarification we need
                #this is always true, since neither field is required
                #but it should handle the processing of the form
                if unitform.is_valid():
                    unit = ''
                    if unitform.cleaned_data['unit_text'] and unitform.cleaned_data['unit_select']:
                        #clear out the old ones
                        #del errors[:]
                        result.errors.append("Please choose an existing unit, or specify an new one; not both")
                    elif unitform.cleaned_data['unit_text']:
                        unit = unitform.cleaned_data['unit_text']
                    elif unitform.cleaned_data['unit_select']:
                        unit = unitform.cleaned_data['unit_select']

                    if not unit:
                        if not "Please specify a unit or apartment number" in result.errors:
                            result.errors.append("Please specify a unit or apartment number")
                    else:
                        #should have everything we need

                        #check if the building has the specified unit
                        #if not, make it..
                        #we don't have something that matches an existing building
                        #should be ok to make a new one!
                        #result = search_building(cleaned_data.get("address"), make=True)
                        result = search_building(bldgform.cleaned_data.get("address"), unit=unit, make=True)
                        #if result.errors:
                        #    for error in result.errors:                    
                        #        errors.append(error)

                        ## else:
                        ##     #redirect to new building page
                        ##     #print "MADE BUILDING! %s" % result.matches
                        ##     #print result

    return (result, bldgform, unitform)

#@login_required
def new(request, query=None):
    unitform = None
    bldgform = None
    if request.method == 'POST':
        (result, bldgform, unitform) = validate_building_and_unit(request)

        if result.errors:
            #in case we need to add errors to the form
            errors = bldgform._errors.setdefault(forms.forms.NON_FIELD_ERRORS, ErrorList())

            #http://stackoverflow.com/questions/188886/inject-errors-into-already-validated-form
            #although once this is on django 1.7:
            #https://docs.djangoproject.com/en/dev/ref/forms/api/#django.forms.Form.add_error
            for error in result.errors:                    
                errors.append(error)

        elif result.building:
            if not result.city:
                result.city = result.building.city

            print result
            if (not result.unit) or (not result.unit.tag):
                #redirect to building details with an edit message
                if result.created:
                    messages.add_message(request, messages.INFO, 'Created building')
                else:
                    messages.add_message(request, messages.INFO, 'Located existing building')
                    
                finished_url = reverse('building.views.details', args=(result.building.tag, result.city.tag))
                
            else:
                if result.created:
                    messages.add_message(request, messages.INFO, 'Created new unit')
                else:
                    messages.add_message(request, messages.INFO, 'Located existing unit')

                print "UNIT TAG: %s" % result.unit.tag
                finished_url = reverse('building.views.unit_details', args=(result.city.tag, result.building.tag, result.unit.tag))

            return redirect(finished_url)
        
    else:
        bldgform = NewBuildingForm(prefix='building')
        
    context = { 
        'user': request.user,
        'bldgform': bldgform,
        'unitform': unitform,
        }
    return render(request, 'building-new.html', context)



class BuildingForm(ModelForm):
    class Meta:
        model = Building
        #fields = ['pub_date', 'headline', 'content', 'reporter']
        fields = [ 'name', 'website', 'type',

                   #will collect this at the unit level...
                   #building level can be added via scripts
                   #when assessor databases are available with this info
                   #'sqft',
                   #'number_of_units', 'built_year', 'value',
                   
                   'who_pays_electricity', 'who_pays_gas', 'who_pays_water', 'who_pays_trash', 'who_pays_internet', 'who_pays_cable',


                   #TODO:
                   #even this should be calculated from the unit details
                   #'average_electricity', 'average_gas', 'average_water', 'average_trash',


                   #TODO:
                   #these can be calculated
                   #'total_average',
                   #only gas and electric included here:
                   #(use this / sqft for energy score)
                   #'energy_average',

                   #this is a temporary field until score is
                   #calculated automatically
                   
                   #regardless of who pays utilities, 
                   #once we have energy data,
                   #we will want to summarize the results here
                   #so that we can use this to color code appropriately
                   #'energy_score',

                   #these will usually happen on a building level

                   'heat_source_details',
                   'heat_source_other',

                   #'energy_saving_features',
                   'energy_saving_details',
                   'energy_saving_other',

                   #'renewable_energy',
                   'renewable_energy_details',
                   'renewable_energy_other',


                   #smart living
                   #make a separate field
                   'composting',
                   'recycling',

                   #'garden',
                   'garden_details',
                   'garden_other',

                   #'bike_friendly',
                   'bike_friendly_details',
                   'bike_friendly_other',

                   #'walk_friendly',
                   'walk_friendly_details',
                   'walk_friendly_other',

                   'transit_friendly_details',
                   'transit_friendly_other',

                   'smart_living',

                                      
                   #amenities
                   'air_conditioning',

                   'laundry',

                   'parking_options',

                   #generally, are pets allowed?
                   #details for this should go in lease
                   #pets = models.BooleanField(default=False)
                   #'pets',

                   #switching to string to allow description:
                   'pets_options',
                   'pets_other',

                   'gym',
                   'pool',
                   'game_room',
                   #for everything else...
                   #anything here will not be available as a filter...
                   #if there is a common addition that should be part of filter,
                   #make a separate field
                   'amenities'

                   ]
        YES_OR_NO = (
            (True, 'Yes'),
            (False, 'No')
            )
        
        widgets = {
            'renewable_energy': forms.RadioSelect(choices=YES_OR_NO, attrs={'class': 'yesno'}),
            'composting': forms.RadioSelect(choices=YES_OR_NO),
            'recycling': forms.RadioSelect(choices=YES_OR_NO),
            'garden': forms.RadioSelect(choices=YES_OR_NO),
            'bike_friendly': forms.RadioSelect(choices=YES_OR_NO),
            'walk_friendly': forms.RadioSelect(choices=YES_OR_NO),
            'transit_friendly': forms.RadioSelect(choices=YES_OR_NO),
            'air_conditioning': forms.RadioSelect(choices=YES_OR_NO),
            'gym': forms.RadioSelect(choices=YES_OR_NO),
            'pool': forms.RadioSelect(choices=YES_OR_NO),
            'game_room': forms.RadioSelect(choices=YES_OR_NO),
            
        }
                   
@login_required
def edit(request, bldg_tag, city_tag):
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag='')

    #unless we figure out it should be set, keep it None
    unitform = None
    
    if request.method == 'POST':
        buildingform = BuildingForm(request.POST, instance=building,
                                    prefix='building')

        if buildingform.is_valid(): # All validation rules pass
            #https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method
            #by passing commit=False, we get a copy of the model before it
            #has been saved. This allows diff to work below
            updated = buildingform.save(commit=False)

            updated.set_booleans()
            #print json.dumps(updated.diff)
            
            #print updated.diff
            changes = ChangeDetails()
            changes.ip_address = get_client_ip(request)
            changes.user = request.user
            changes.diffs = json.dumps(updated.diff)
            changes.building = updated
            #not required
            #changes.unit =
            changes.save()
            
            #now it's ok to save the building details:
            updated.save()

            unit_ok = False
            if building.units.count() == 1:
                unitform = UnitForm(request.POST, instance=unit, prefix='unit')
                if unitform.is_valid(): # All validation rules pass
                    updated_unit = unitform.save(commit=False)
                    updated_unit.save_and_update(request)
                    unit_ok = True
            else:
                unit_ok = True

            if unit_ok:
                #redirect to building details with an edit message
                messages.add_message(request, messages.INFO, 'Saved changes to building.')
                finished_url = reverse('building.views.details', args=(updated.tag, updated.city.tag))
                
                return redirect(finished_url)

    else:
        buildingform = BuildingForm(instance=building, prefix='building')
        buildingform.fields['name'].label = "Building Name"
        if building.units.count() == 1:
            unitform = UnitForm(instance=unit, prefix='unit')

    context = { 'building': building,
                'user': request.user,
                'buildingform': buildingform,
                'unitform': unitform,
                }
    return render(request, 'building-edit.html', context)


def details(request, bldg_tag, city_tag):
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag='')

    #print building.units.all()[0].tag
    #unit_url = reverse('unit_details', kwargs={'city_tag':building.city.tag, 'bldg_tag':building.tag, 'unit_tag':building.units.all()[0].tag})
    #print unit_url

        
    context = { 'building': building,
                'units': building.units.all(),
                'user': request.user,
                'redirect_field': REDIRECT_FIELD_NAME,
                }
    return render(request, 'details.html', context)







def unit_json(request, city_tag, bldg_tag, unit_tag):
    pass

class UnitForm(ModelForm):
    class Meta:
        model = Unit
        fields = [ 'bedrooms', 'bathrooms', 'sqft', 'floor', 'max_occupants', 'rent', 'status',
                   #'average_electricity', 'average_gas', 'average_water', 'average_trash',
                   ]

@login_required
def unit_edit(request, city_tag, bldg_tag, unit_tag=''):
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag=unit_tag)

    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)

        if form.is_valid(): # All validation rules pass
            updated = form.save(commit=False)

            updated.save_and_update(request)

            #redirect to unit details page with an edit message
            messages.add_message(request, messages.INFO, 'Saved changes to unit.')
            if updated.tag:
                finished_url = reverse('building.views.unit_details', kwargs={'city_tag':city.tag, 'bldg_tag':building.tag, 'unit_tag':updated.tag})
            else:
                finished_url = reverse('building.views.unit_details', kwargs={'city_tag':city.tag, 'bldg_tag':building.tag})
                
            #args=(updated.building.tag, city.tag, updated.tag)
            return redirect(finished_url)
    else:
        print unit
        form = UnitForm(instance=unit)
        
    context = { 'building': building,
                'unit': unit,
                'user': request.user,
                'form': form,
                }
    return render(request, 'unit_edit.html', context)

def unit_details(request, city_tag, bldg_tag, unit_tag=''):
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag=unit_tag)

    print unit.full_address()
    context = { 'building': building,
                'units': [unit],
                'unit': unit,
                'user': request.user,
                'redirect_field': REDIRECT_FIELD_NAME,
                }
    return render(request, 'unit_details.html', context)

