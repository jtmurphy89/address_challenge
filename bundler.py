from data_types import *
from collections import deque


def bundle_mail(letters):
    """ Given a collection of letters, return a list (or other iterable) of
    Bundles such that:

    - Every Letter is placed in exactly one Bundle
    - The destination of the Bundle matches the address of the Letter
    """
    letter_queue = deque(
        [(letter, AddressParser(letter.address.line1, letter.address.line2, letter.address.line3)) for letter in
         letters])
    bundle_dict = {}
    repairer = AddressRepairer()

    while letter_queue:
        letter, parsed_letter = letter_queue.popleft()
        if parsed_letter.is_good_egg():
            repairer.validate_address(parsed_letter)
            standardized_address = parsed_letter.make_address()
            bundle = bundle_dict.get(standardized_address, Bundle(standardized_address))
            bundle.add_letter(letter)
            bundle_dict[standardized_address] = bundle
            repairer.add_good_address(parsed_letter)
            print 'good addy: ' + str(letter.id) + ': ' + str(standardized_address)
        else:
            repairer.repair_address(parsed_letter)
            letter_queue.append((letter, parsed_letter))

    for bundle in bundle_dict.values():
        if bundle.address is not RETURN_TO_SENDER:
            bundle.address = list(bundle.letters)[0].address
        l = [str(letter.id) for letter in bundle.letters]
        print l

    return bundle_dict.values()
