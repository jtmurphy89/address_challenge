from data_types import *
line1 = 'The White House'.replace(',','').replace('.','').upper()
line2 = ''.replace(',','').replace('.','').upper()
line3 = 'Washington, DC'.replace(',','').upper()
a = CanonicalizedAddress(line1,line2,line3)
print a.address_data
print str(a.make_address())
