from data_types import *


def bundle_mail(letters):
    """ Given a collection of letters, return a list (or other iterable) of
    Bundles such that:

    - Every Letter is placed in exactly one Bundle
    - The destination of the Bundle matches the address of the Letter
    """

    # create dict of address:bundle pairs
    bundle_dict = {}
    for letter in letters:
    	addy = letter.address
    	bundle = bundle_dict.get(addy, Bundle(addy))
    	bundle.add_letter(letter)
    	bundle_dict[addy] = bundle

    return bundle_dict.values()
