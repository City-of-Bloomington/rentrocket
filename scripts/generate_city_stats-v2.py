"""
*2015.01.29 11:12:57
rather than splitting into 4 equal ranges,
sort buildings by energy scores
then split the number of buildings with scores into 4 equal groups
use the scores at the boundaries of those groups as the cutoffs
(may not be equal increments, value wise)

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
    count = buildings.count()
    
    #incomplete_count = 0
    incomplete_q = Building.objects.all().filter(city=city, energy_score=float(.0001) )
    print "Incomplete: ", incomplete_q.count()
    incomplete_count = incomplete_q.count()


    scored_q = Building.objects.all().filter(city=city, energy_score__gt=float(.0001), ).order_by('-energy_score')


    scored_count = scored_q.count()
    print "Scored: ", scored_q.count()

    increment = scored_count / 4
    print "Increment: ", increment

    counts = [ ]
    cutoffs = [ ]
    for i in range(1, 5):
        cur_index = increment*i
        print "looking at index: %s (out of %s)" % ( cur_index, scored_count )
        counts.append( increment )
        if scored_count:
            if i != 4:
                cutoffs.append( scored_q[cur_index].energy_score )
            else:
                cutoffs.append( scored_q[scored_count-1].energy_score )
        else:
            cutoffs.append( 0 )
        
    print "Counts: ", counts
    print "Cutoffs: ", cutoffs

    #this is the way they were in previous version:
    cutoffs.reverse()
    
    titles = [ "Date", "City", "State", "Total Buildings", "Buildings w/ Incomplete Data", "Scored Buildings (Complete Data)", "Low Scoring", "Med-Low Scoring", "Med-High Scoring", "High Scoring", "Low Cutoff", "Med-Low Cutoff", "Med-High Cutoff", "High Cutoff", "Score Based On"]

    if add_header:
        summary_csv.write(','.join(titles) + '\n')
        add_header = False

    cutoffs2 = []
    for co in cutoffs:
        cutoffs2.append(str(co))
    cutoff_str = ','.join(cutoffs2)

    #assign this to city for use in javascript marker display
    print cutoff_str
    city.cutoffs = cutoff_str
    city.save()

    #low in this case refers to the energy score value...
    #lower values represent higher utility usage, so it's confusing here
    #[ low, med_low, med_high, high ] = counts

    #this doesn't matter if they're all equal:
    [ high, med_high, med_low, low, ] = counts
    
    row = [ now, city.name, city.state, count, incomplete_count, scored_count, low, med_low, med_high, high, ]
    row.extend(cutoffs)

    #use this to keep track of what method is currently in use
    #for generating the energy score in the system code
    row.append('bedrooms')
    
    row_str = []
    for item in row:
        row_str.append(str(item))

    summary_csv.write(','.join(row_str) + '\n')

#for keeping next run separate:
summary_csv.write('\n')
summary_csv.close()
