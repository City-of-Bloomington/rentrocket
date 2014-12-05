"""
*2014.12.04 07:43:18
similar to update_energy_scores.py

go through every city
and go through every building in that city
this time keep track of the high and low values for building averages

after that, for each city,
split high and low into 4 equal ranges (or how ever many colors are on the map)

might be nice to also count how many properties fall into these ranges
this will require another scan of all options though.

this script assumes all values are up to date and equivalent
if not, use update_energy_scores.py
"""
import os, sys, re
from datetime import datetime
import codecs


sys.path.append(os.path.dirname(os.getcwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

from building.models import Building, Parcel, BuildingPerson, Unit
from city.models import City
from rentrocket.helpers import to_tag

#change output name based on production vs dev...
#don't want to accidentally overwrite one with the other
if os.getenv('SETTINGS_MODE') == 'prod':
    summary_csv = codecs.open('energy_score_summary.csv', 'a', encoding='utf-8')
else:
    summary_csv = codecs.open('energy_score_summary-temp.csv', 'a', encoding='utf-8')

# Only set this to true when generating a new csv file:
add_header = False
#add_header = True

now = datetime.now()

city_options = City.objects.all()
print "Number of cities available: %s" % len(city_options)
if not len(city_options):
    raise ValueError, "CITY NOT FOUND! run make_cities.py first"

total_count = 0
for city in city_options:
    print "Looking at city: %s" % (city.name)

    high = 0
    low = 90000000
    buildings = Building.objects.filter(city=city)
    print len(buildings)
    print buildings.count()
    count = 0

    scored_count = 0
    incomplete_count = 0
    
    for building in buildings:

        if building.energy_score:
            if building.energy_score != .0001:
                scored_count += 1
                if building.energy_score > high:
                    print "new high value: %s (previous: %s)" % (building.energy_score, high)
                    print "%04d: %s" % (count, building.address)
                    print
                    high = building.energy_score

                if building.energy_score < low:
                    print "new low value: %s (previous: %s)" % (building.energy_score, high)
                    print "%04d: %s" % (count, building.address)
                    print
                    low = building.energy_score

            else:
                incomplete_count += 1
                
        count += 1
        total_count += 1
        
    scope = high - low
    increment = scope / 4.0

    ## cutoffs = [ str(low + increment), str(low + increment*2),
    ##             str(low + increment*3), str(high) ]
    ## cutoff_str = ','.join(cutoffs)

    cutoffs = [ low + increment, low + increment*2, low + increment*3, high ]

    cutoffs2 = []
    for co in cutoffs:
        cutoffs2.append(str(co))
    cutoff_str = ','.join(cutoffs2)

    #assign this to city for use in javascript marker display
    print cutoff_str
    city.cutoffs = cutoff_str
    city.save()

    #now generate statistics for current city (re-run loop)
    
    low = 0
    med_low = 0
    med_high = 0
    high = 0

    counts = [ 0, 0, 0, 0 ]

    for building in buildings:

        if building.energy_score and building.energy_score != .0001:
            #print "Placing: %s in %s" % (building.energy_score, cutoffs)
            placed = False
            cutoffs_index = 0
            while not placed:
                cur_cutoff = cutoffs[cutoffs_index]
                #print "Checking: %s" % cur_cutoff
                if building.energy_score <= cur_cutoff:
                    counts[cutoffs_index] += 1
                    placed = True
                    
                cutoffs_index += 1

    titles = [ "Date", "City", "State", "Total Buildings", "Buildings w/ Incomplete Data", "Scored Buildings (Complete Data)", "Low Scoring", "Med-Low Scoring", "Med-High Scoring", "High Scoring", "Low Cutoff", "Med-Low Cutoff", "Med-High Cutoff", "High Cutoff", "Score Based On"]

    if add_header:
        summary_csv.write(','.join(titles) + '\n')
        add_header = False

    [ low, med_low, med_high, high ] = counts
    row = [ now, city.name, city.state, count, incomplete_count, scored_count, low, med_low, med_high, high, ]
    row.extend(cutoffs)
    row.append('bedrooms')
    
    row_str = []
    for item in row:
        row_str.append(str(item))

    summary_csv.write(','.join(row_str) + '\n')

#for keeping next run separate:
summary_csv.write('\n')
summary_csv.close()
