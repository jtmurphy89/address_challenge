from data_types import *
line1 = 'Santa Claus'.replace(',','').replace('.','').upper()
line2 = 'Workshop'.replace(',','').replace('.','').upper()
line3 = 'North Pole'.replace(',','').upper()
a = AddressParser(line1,line2,line3)
print a.name
print a.street_num
print a.street_name
print a.street_type
print a.city
print a.state
print a.federal_district
print a.zip_code