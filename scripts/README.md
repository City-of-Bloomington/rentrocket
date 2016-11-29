Scripts
==============

This directory contains a number of different back-end helper scripts. 

Data Import
-------------------

Once there is a spreadsheet that contains the raw information that needs to be imported, there are a number of different scripts to handle the import process in:

https://github.com/City-of-Bloomington/rentrocket/tree/master/scripts

There are different versions due to the different formats that we received the information in. Many of the "convert_..." ones do similar tasks that are tailored to the corresponding format.

Eventually, we worked toward creating a standard format for the bulk import data to be in:

http://rentrocket.org/static/rentrocket-bulk_data_template.xls

The script to import that data (after converting it to a csv) is:

https://github.com/City-of-Bloomington/rentrocket/blob/master/scripts/import_master_template.py

That script serves as documentation for the steps that need to be completed when adding new addresses to the system.

For the address standardization process specifically, the import script calls a helper function "address_search()" that is part of the main application's code base. That function is available here:

https://github.com/City-of-Bloomington/rentrocket/blob/master/rentrocket/helpers.py

That function does some cleanup of the address before passing it on to the Google maps API for normalization / standardization. We needed to use a source with addresses at a national level. Given the API request limits that Google imposes, and the prohibitive cost for more requests, that may not have been the best choice in hindsight. 


