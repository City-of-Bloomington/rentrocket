from django.db import models

from building.models import Building, Parcel, Unit

class Inspection(models.Model):
    """
    Modeled after House Facts Data Standard

    Details of an inspection performed on a given unit
    """
    AGENCY_CHOICES = (
        ('hlth', 'Health'),
        ('envr', 'Environment'),
        ('bldg', 'Building'),
        ('hous', 'Housing'),
        ('plan', 'Planning'),
        ('fire', 'Fire'),
        ('code', 'Code Enforcement'),
        #('', ''),
        )

    JURISDICTION_CHOICES = (
        ('ci', 'City'),
        ('cn', 'County'),
        ('st', 'State'),
        ('fe', 'Federal'),
        #('', ''),
        )

    TYPE_CHOICES = (
        ('pe', 'Permit'),
        ('ro', 'Routine'),
        ('co', 'Complaint'),
        ('fo', 'Follow-up'),
        #('', ''),
        )


    # should just get this as needed by way of Building
    #parcel = models.ForeignKey(Parcel)

    unit = models.ForeignKey(Unit)

    #this will provide easier lookups for city, state, address
    building = models.ForeignKey(Building)

    #String representing the inspecting agency.
    #Must be one of the following types:
    #Health, Environment, Building, Housing, Planning, Fire, Code Enforcement.
    agency = models.CharField(max_length=4, choices=AGENCY_CHOICES, default="hlth")

    #Must be one of the following: city, county, state, federal.
    agency_jurisdiction = models.CharField(max_length=2, choices=JURISDICTION_CHOICES, default="ci")

    #String representing the type of inspection. Must be one of the following:
    #types: permit, routine, complaint, follow-up.
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default="pe")

    #Date of the inspection 
    date = models.DateTimeField()

    #Summary inspection rating or result associated with the inspection
    #(e.g. pass/ fail, satisfactory/ not-satisfactory, etc)
    rating = models.CharField(max_length=20)

    #any additional notes about the inspection
    notes = models.TextField()

    #Optional. Numerical score associated with the inspection if one exists
    score = models.IntegerField(null=True, blank=True)

    #TODO:
    #incorporate a feed_info field for:
    #inspections
    #buildings
    #parcels

    #source 

    added = models.DateTimeField('date published')
    updated = models.DateTimeField('date updated')

class Violation(models.Model):
    """
    Modeled after House Facts Data Standard

    Details of a specific violation
    """

    CATEGORY_CHOICES = (
        #('', ''),
        #Cockroaches; rats; mice; bedbugs; racoons
        ('anima', 'Animals and Pests'),
        #Overgrown vegetation, landslide
        ('veget', 'Vegetation'),
        #Refuse accumulation; dumping; spoiled food
        ('refus', 'Refuse'),
        #Unsanitary floors or walls; non-functioning sewage system
        ('sanit', 'Sanitation'),
        #Radon
        ('radia', 'Radiation Hazard'),
        #Nuisance odors; smoking in common areas
        ('airpo', 'Air Pollutants and Odors'),
        #Medical waste; Contaminated Needles, mold/mildew
        ('biolo', 'Bioological Hazard'),
        #Lead hazard; asbestos hazard
        ('chemi', 'Chemical Hazards'),
        #Interior noise violation; exterior noise violation
        ('noise', 'Noise'),
        #Inadequate heat or ventilation
        ('indoo', 'Indoor Climate'),
        #No running water; inoperable toilet
        ('plumb', 'Plumbing '),
        #Exposed electrical hazards; excess electrical loads
        ('elect', 'Electrical'),
        #Non-functioning smoke detector; heat source near combustible material
        ('fireh', 'Fire Hazards and Prevention'),
        #Inadequate exterior lighting
        ('secur', 'Building Security'),
        #Water or moisture intrusion; structural hazard; 
        ('struc', 'Building Structure'),
        #Unpermitted use; violations of conditions of use
        ('plann', 'Planning or Zoning'),
        #Abandoned Building; Blighted Building; Dilapidated Housing 
        ('aband', 'Abandon, Boarded or Substandard Building'),
        #No permit for electrical, gas, construction, plumbing ect
        ('noper', 'No Permit'),
        #Storm Water; Water Leak; Sewer Leak
        ('water', 'Water Hazard'),
        #Gas Leak, Illegal Gas Appliance
        ('gasha', 'Gas Hazard'),
        #Other
        ('other', 'Other'),
        )

    inspection = models.ForeignKey(Inspection)

    #these fields are all available from inspection object directly...
    #no need to duplicate here (DRY)
    #inspection_agency, violation_address, unit_number, violation_city,
    #violation_state

    date = models.DateTimeField()

    date_closed = models.DateTimeField()

    category = models.CharField(max_length=4, choices=CATEGORY_CHOICES, default="other")

    #Locally defined violation type (bedbugs, mold, etc)
    #aka violation_type
    description = models.CharField(max_length=50)

    #Must be one of the following three(?) categories:
    #high (imminently harmful to health and requires rapid correction)
    #and low (nuisance with correction over a reasonable period of time) 
    severity = models.CharField(max_length=12, blank=True)

    legal_authority = models.CharField(max_length=12, blank=True)


