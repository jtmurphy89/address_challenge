import re
from difflib import SequenceMatcher

base_regex = '(?P<remainder>.*){junk}\s?(?P<base>{base_query})'
street_num_regex = '(?P<street_num>\d+)\s(?P<remainder>.*)'
apt_regex = '(?P<remainder>.*)\s{}\.?\s?(?P<apt_num>\d+)'
zip_regex = '(?P<remainder>.*)\s(?P<zip_code>\d+)'

apt_types = ['Suite', 'Ste', 'Room', 'Apartment', 'Apt', '#', 'Unit']
street_types = ['Ave?n?u?e?', 'Pla?za?', 'Str?e?e?t?', 'Circ?l?e?']
state_list = ['CALIFORNIA', 'CA']
bad_names = ['POSTAL CUSTOMER']

name_dict = {'WILSON SONSINI GOODRICH  ROSATI': 'WSGR', 'DIAMOND JOE': 'JOE BIDEN'}
city_abbreviations = {'SF': 'SAN FRANCISCO'}
state_dict = {'CALIFORNIA': 'CA', 'CA': 'CA'}
street_dict = {'A': 'AVE', 'P': 'PLZ', 'S': 'ST', 'C': 'CIR'}

normal_junk = [',', '.']
street_junk = ['NW']
name_junk = ['INC', 'LLC', '&']


def remove_junk(name, junk):
    for piece_of_junk in junk:
        name = name.replace(piece_of_junk, '').strip()
    return name


class Address(object):
    def __init__(self, line1, line2, line3):
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3

    def __str__(self):
        """ DO NOT EDIT: This method is required by the test runner. """
        return '\t'.join((self.line1, self.line2, self.line3))

    def __eq__(self, other):
        """ DO NOT EDIT: This method is required by the test runner. """
        return (self.line1 == other.line1
                and self.line2 == other.line2
                and self.line3 == other.line3)

    def __hash__(self):
        """ DO NOT EDIT: This method is required by the test runner. """
        return hash((self.line1, self.line2, self.line3))


class Letter(object):
    def __init__(self, id, address):
        self.id = id
        self.address = address

    def __eq__(self, other):
        """ DO NOT EDIT: This method is required by the test runner. """
        return self.id == other.id

    def __hash__(self):
        """ DO NOT EDIT: This method is required by the test runner. """
        return hash(self.id)

    def __str__(self):
        """ DO NOT EDIT: This method is required by the test runner. """
        return 'Letter id: %d\t%s' % (self.id, self.address)


class Bundle(object):
    def __init__(self, address):
        self.address = address
        self.letters = set()

    def add_letter(self, letter):
        """ DO NOT EDIT: This method is required by the test runner. """
        self.letters.add(letter)

    def add_letters(self, letters):
        """ DO NOT EDIT: This method is required by the test runner. """
        for letter in letters:
            self.add_letter(letter)


RETURN_TO_SENDER = Address('RETURN_TO_SENDER',
                           'RETURN_TO_SENDER',
                           'RETURN_TO_SENDER')
""" This special identifier is used in Level 3. See the INSTRUCTIONS.
"""


class AddressParser(object):
    def __init__(self, line1, line2, line3):
        # initialize the name and everything else to none
        self.name = remove_junk(line1.upper(), normal_junk + name_junk)
        self.line2remainder = remove_junk(line2.upper(), normal_junk + street_junk)
        self.line3remainder = remove_junk(line3.upper(), normal_junk)
        self.street_num = ''
        self.apt_num = ''
        self.street_type = ''
        self.street_name = ''
        self.zip_code = ''
        self.federal_district = ''
        self.state = ''
        self.city = ''

        # make sure name isn't an exception
        if self.name in name_dict:
            self.name = name_dict[self.name]

        # street num
        street_num_match = re.match(street_num_regex, self.line2remainder, re.IGNORECASE)
        if street_num_match:
            self.street_num = street_num_match.group('street_num')
            self.line2remainder = street_num_match.group('remainder').strip()

        # apartment num
        for apt_type in apt_types:
            regex = base_regex.format(junk=apt_type, base_query='\d+')
            regex_match = re.match(regex, self.line2remainder, re.IGNORECASE)
            if regex_match:
                self.apt_num = regex_match.group('base')
                self.line2remainder = regex_match.group('remainder').strip()

        # street type
        for street_type in street_types:
            regex = base_regex.format(junk='', base_query=street_type)
            regex_match = re.match(regex, self.line2remainder, re.IGNORECASE)
            if regex_match:
                self.street_type = regex_match.group('base')
                # all we have left will be the street name
                self.street_name = regex_match.group('remainder').strip()

        # zip code
        zip_code_regex = '(?P<remainder>.*)(?P<base>\d\d\d\d\d)(?:-\d+)*'
        zip_code_match = re.match(zip_code_regex, self.line3remainder, re.IGNORECASE)
        if zip_code_match:
            self.zip_code = zip_code_match.group('base')
            self.line3remainder = zip_code_match.group('remainder').strip()

        # city/state/federal district
        for state in state_list:
            regex = base_regex.format(junk='', base_query=state)
            regex_match = re.match(regex, self.line3remainder, re.IGNORECASE)
            if regex_match:
                self.state = regex_match.group('base')
                self.line3remainder = regex_match.group('remainder').strip()

        if self.line3remainder == 'WASHINGTON DC':
            self.federal_district = 'WASHINGTON DC'
        else:
            self.city = city_abbreviations.get(self.line3remainder, self.line3remainder)

    def make_address(self):
        line1 = self.name.strip()
        line2 = str(self.street_num + ' ' + self.street_name + ' ' +
                    street_dict.get(self.street_type[0], '') + ' ' + self.apt_num).strip()
        line3 = str(self.city + ' ' + state_dict.get(self.state, '') +
                    ' ' + self.federal_district + ' ' + self.zip_code).strip()
        return Address(line1, line2, line3)

    def is_bad_egg(self):
        if not self.zip_code:
            return True
        if not self.city and not self.state and not self.federal_district:
            return True
        # if self.name in bad_names:
        #     return True
        return False


class AddressRepairer(object):
    def __init__(self):
        self.good_addresses = []

    def add_good_address(self, line1, line2, line3):
        self.good_addresses.append(AddressParser(line1, line2, line3))

    def repair_zip(self, parsed_address):
        for good_address in self.good_addresses:
            match = (parsed_address.city == good_address.city and
                     parsed_address.state == good_address.state and
                     parsed_address.federal_district == good_address.federal_district and
                     parsed_address.make_address().line2 == good_address.make_address().line2)
            if match:
                parsed_address.zip_code = good_address.zip_code
                print 'match found for zip code!'

    def repair_city_state_given_zip(self, parsed_address):
        for good_address in self.good_addresses:
            if parsed_address.zip_code == good_address.zip_code:
                parsed_address.city = good_address.city
                parsed_address.state = good_address.state
                parsed_address.federal_district = good_address.federal_district
        #     return parsed_address
        # return parsed_address

    def repair_name(self, parsed_address):
        for good_address in self.good_addresses:
            if parsed_address.make_address().line2 == good_address.make_address().line2:
                parsed_address.name = good_address.name
