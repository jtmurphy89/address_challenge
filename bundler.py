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
        if addy.is_bad_egg():
            bad_eggs.append([letter, addy])
        else:
            address = addy.make_address()
            bundle = bundle_dict.get(address, Bundle(address))
            bundle.add_letter(letter)
            bundle_dict[address] = bundle
            repairer.add_good_address(line1, line2, line3)
            print 'Good Address: ' + str(address)

    while bad_eggs:
        print len(bad_eggs)
        bad_letter, bad_addy = bad_eggs.pop(0)
        if not bad_addy.zip_code:
            print 'repair zip'
            repairer.repair_zip(bad_addy)
            print 'repaired zip: ' + str(bad_addy.make_address())
        elif not bad_addy.city:
            print 'repair city'
            repairer.repair_city_state_given_zip(bad_addy)
            print 'repaired city: ' + str(bad_addy.make_address())
        elif bad_addy.name.strip() == 'POSTAL CUSTOMER':
            print 'repair name'
            repairer.repair_name(bad_addy)
            print 'repaired name: ' + str(bad_addy.make_address())
        if not bad_addy.is_bad_egg():
            print 'never here...'
            good_addy = bad_addy.make_address()
            print str(good_addy)
            bundle = bundle_dict.get(good_addy, Bundle(good_addy))
            bundle.add_letter(bad_letter)
            bundle_dict[good_addy] = bundle
            repairer.add_good_address(good_addy.line1, good_addy.line2, good_addy.line3)
        else:
            bad_eggs.append([bad_letter, bad_addy])
        print bad_addy.name

    for bundle in bundle_dict.values():
        bundle.address = list(bundle.letters)[0].address
        l = [str(letter.id) for letter in bundle.letters]
        print l

    return bundle_dict.values()
