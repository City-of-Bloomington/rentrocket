from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
#from django.forms import extras, widgets
from models import Listing

from building.models import find_by_tags

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['rent', 'deposit', 'available_start', 'lease_term', 'lease_type']


def index(request):

    #city = City.objects.filter(tag=to_tag("Ann Arbor"))
    #buildings = Building.objects.filter(city=city)
    #context = {'buildings': buildings}
    
    context = {}

    return render(request, 'index.html', context )

def new_temp(request):
    context = {}
    return render(request, 'new.html', context )


@login_required
def new(request, city_tag, bldg_tag, unit_tag=None):
    (city, building, unit) = find_by_tags(city_tag, bldg_tag, unit_tag=unit_tag)

    #TODO:
    #find any active listing for current unit

    if request.method == 'POST':
        listingform = ListingForm(request.POST, instance=building,
                                    prefix='listing')

        if listingform.is_valid(): # All validation rules pass
            #https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method
            #by passing commit=False, we get a copy of the model before it
            #has been saved. This allows diff to work below
            updated = listingform.save(commit=False)

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
                #redirect to listing details with an edit message
                messages.add_message(request, messages.INFO, 'Saved changes to listing.')
                finished_url = reverse('listing.views.details', args=(updated.tag, updated.city.tag))
                
                return redirect(finished_url)

    else:
        #listingform = ListingForm(instance=listing, prefix='listing')
        listingform = ListingForm(prefix='listing')
        #listingform.fields['name'].label = "Building Name"
        #if building.units.count() == 1:
        #    unitform = UnitForm(instance=unit, prefix='unit')

    context = { 'building': building,
                'user': request.user,
                'listingform': listingform,
                }
    return render(request, 'listing-edit.html', context)


