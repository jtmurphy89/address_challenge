from data_types import *
import re

abbreviations = {'A':'AVENUE', 'S':'STREET', 'C':'CIRCLE', 'P':'PLAZA' }


def canonicalize_address(addy):
	""" Given an address, returns a standard, reformatted address in all caps 
		with no abbreviations in the street name nor any distinction b/t Apt, 
		Suite, #, etc.

	 """
	m = re.match(r"""
		(?P<street_num>[0-9]+)\s   # it should have a street number
		(?P<street_name>\w+\s?\w+?)\s   # the street name could possibly have 2 words in it
		(?P<street_type>\w+)[.]?[,]?\s?   # the street type could possibly be followed by a period or a comma or a space
		(?P<room_type>\w*)\s?   # there may or may not be a room type (or even a room number)
		(?P<room_num>\w*)""", addy.line2.upper(), re.VERBOSE).groupdict()
	
	# un-abbreviate the street type in standard format and strip away any blank spaces at the end
	m['street_type'] = abbreviations[m['street_type'][0]]
	new_line2 = '{street_num} {street_name} {street_type} {room_num}'.format(**m).strip()
	return Address(addy.line1.upper(), new_line2, addy.line3.upper())

	



def bundle_mail(letters):
    """ Given a collection of letters, return a list (or other iterable) of
    Bundles such that:

    - Every Letter is placed in exactly one Bundle
    - The destination of the Bundle matches the address of the Letter
    """

    bundle_dict = {}
    for letter in letters:
    	addy = canonicalize_address(letter.address)
    	bundle = bundle_dict.get(addy, Bundle(addy))
    	bundle.add_letter(letter)
    	bundle_dict[addy] = bundle


    for bundle in bundle_dict.values():
    	bundle.address = list(bundle.letters)[0].address

    return bundle_dict.values()












