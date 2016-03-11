from data_types import *


def bundle_mail(letters):
    """ Given a collection of letters, return a list (or other iterable) of
    Bundles such that:

    - Every Letter is placed in exactly one Bundle
    - The destination of the Bundle matches the address of the Letter
    """

    bundle_dict = {}
    repairer = AddressRepairer()
    bad_eggs = []
    for letter in letters:
        line1 = letter.address.line1
        line2 = letter.address.line2
        line3 = letter.address.line3
        addy = AddressParser(line1, line2, line3)
        if not addy.zip_code:
            bad_eggs.append([letter, addy])
        else:
            address = str(addy.make_address())
            bundle = bundle_dict.get(address, Bundle(address))
            bundle.add_letter(letter)
            bundle_dict[address] = bundle
            repairer.add_good_address(line1, line2, line3)

    for (bad_letter, bad_addy) in bad_eggs:
        if not bad_addy.zip_code:
            addy = str(repairer.repair_zip(bad_addy).make_address())
            bundle = bundle_dict.get(addy, Bundle(addy))
            bundle.add_letter(bad_letter)
            bundle_dict[addy] = bundle
            repairer.add_good_address(line1, line2, line3)

    for bundle in bundle_dict.values():
        bundle.address = list(bundle.letters)[0].address

    return bundle_dict.values()
