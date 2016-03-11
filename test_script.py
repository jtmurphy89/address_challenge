from data_types import *
line1 = 'Wilson Sonsini Goodrich & Rosati'.replace(',','').replace('.','').upper()
line2 = '139 Townsend Street, Suite 150'.replace(',','').replace('.','').upper()
line3 = 'San Francisco, CA 94404'.replace(',','').upper()
a = AddressParser(line1,line2,line3)
print a.name
print a.street_num
print a.street_name
print a.street_type
print a.apt_num
print a.city
print a.state 
print a.federal_district
print a.zip_code