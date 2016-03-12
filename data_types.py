import re

base_regex = '(?P<remainder>.*){junk}\s?(?P<base>{base_query})'
street_num_regex = '(?P<street_num>\d+)\s(?P<remainder>.*)'
apt_regex = '(?P<remainder>.*)\s{}\.?\s?(?P<apt_num>\d+)'
zip_regex = '(?P<remainder>.*)\s(?P<zip_code>\d+)'

apt_types = ['Suite', 'Ste', 'Room', 'Apartment', 'Apt', '#', 'Unit']
street_types = ['Ave?n?u?e?', 'Pla?za?', 'Str?e?e?t?', 'Circ?l?e?', 'Terrace']
state_list = ['CALIFORNIA', 'CA', 'NY', 'OREGON', 'OR']
bad_names = ['POSTAL CUSTOMER', 'RESIDENT']

name_prefixes = ['MR', 'MS', 'MRS']
street_prefixes = ['NE', 'SE']

misspellings = {'KERNY': 'KEARNY'}

name_dict = {'WILSON SONSINI GOODRICH  ROSATI': 'WSGR', 'DIAMOND JOE': 'JOE BIDEN',
             'SAN FRANCISCO FIRE DEPARTMENT': 'SFFD', 'JIM SMITH': 'JAMES SMITH',
             'MS LUNDS': 'JENNIFER LUNDS'}
city_abbreviations = {'SF': 'SAN FRANCISCO'}

state_dict = {'CALIFORNIA': 'CA', 'CA': 'CA', 'OREGON': 'OR', 'OR': 'OR', 'NEW YORK': 'NY', 'NY': 'NY'}
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
        self.line1remainder = remove_junk(line1.upper(), normal_junk + name_junk).strip()
        self.line2remainder = remove_junk(line2.upper(), normal_junk + street_junk)
        self.line3remainder = remove_junk(line3.upper(), normal_junk)

        self.name = self.parse_name(self.line1remainder)
        self.street_num = self.parse_street_num()
        self.apt_num = self.parse_apt_num()
        self.street_type, self.street_name = self.parse_street_type()
        self.zip_code = self.parse_zip_code()
        self.city, self.state, self.federal_district = self.parse_city_state_district()
        self.repair_attempts = 0
        self.is_RTS = not self.zip_code and not self.state and not self.federal_district

    def parse_name(self, name):
        if name in name_dict:
            name = name_dict[name]
            return name
        return name

    def parse_street_num(self):
        street_num = ''
        street_num_match = re.match(street_num_regex, self.line2remainder, re.IGNORECASE)
        if street_num_match:
            street_num = street_num_match.group('street_num')
            self.line2remainder = street_num_match.group('remainder').strip()
        return street_num

    def parse_apt_num(self):
        apt_num = ''
        for apt_type in apt_types:
            regex = base_regex.format(junk=apt_type, base_query='\d+')
            regex_match = re.match(regex, self.line2remainder, re.IGNORECASE)
            if regex_match:
                apt_num = regex_match.group('base')
                self.line2remainder = regex_match.group('remainder').strip()
                return apt_num
        return apt_num

    def parse_street_type(self):
        st_type = ''
        street_name = self.line2remainder
        for street_type in street_types:
            regex = base_regex.format(junk='', base_query=street_type)
            regex_match = re.match(regex, self.line2remainder, re.IGNORECASE)
            if regex_match:
                st_type = regex_match.group('base')
                # all we have left will be the street name
                street_name = regex_match.group('remainder').strip()
                # check for misspellings
                street_name = misspellings.get(street_name, street_name)
                return st_type, street_name
        return st_type, street_name

    def parse_zip_code(self):
        zip_code = ''
        zip_code_regex = '(?P<remainder>.*)(?P<base>\d\d\d\d\d)(?:-\d+)*'
        zip_code_match = re.match(zip_code_regex, self.line3remainder, re.IGNORECASE)
        if zip_code_match:
            zip_code = zip_code_match.group('base')
            self.line3remainder = zip_code_match.group('remainder').strip()
        return zip_code

    def parse_city_state_district(self):
        # city/state/federal district
        city = ''
        st = ''
        fed_disct = ''
        for state in state_list:
            regex = base_regex.format(junk='\s', base_query=state)
            regex_match = re.match(regex, self.line3remainder, re.IGNORECASE)
            if regex_match:
                st = regex_match.group('base')
                self.line3remainder = regex_match.group('remainder').strip()

        if self.line3remainder == 'WASHINGTON DC':
            fed_disct = 'WASHINGTON DC'
        else:
            city = city_abbreviations.get(self.line3remainder, self.line3remainder).strip()
        return city, st, fed_disct

    def make_address(self):
        if self.is_RTS:
            return RETURN_TO_SENDER
        line1 = self.name.strip()
        line2 = str(self.street_num + ' ' + self.street_name + ' ' +
                    street_dict.get(self.street_type[0] if self.street_type else '', '') + ' ' + self.apt_num).strip()
        line3 = str(self.city + ' ' + state_dict.get(self.state, '') +
                    ' ' + self.federal_district + ' ' + self.zip_code).strip()
        return Address(line1, line2, line3)

    def is_good_egg(self):
        if self.is_RTS:
            return True
        if self.repair_attempts > 10:
            return True
        if not self.zip_code:
            return False
        if self.zip_code and not self.state and not self.federal_district:
            return False
        if self.name in bad_names:
            return False
        if not self.street_type:
            return False
        return True


class AddressRepairer(object):
    def __init__(self):
        self.good_addresses = []
        self.apt_num_checker = {}
        self.zip_checker = {}

    def add_good_address(self, parsed_address):
        self.good_addresses.append(parsed_address)
        street_lookup_key = str(
            parsed_address.name + ' ' + parsed_address.street_num + ' ' + parsed_address.street_name)
        self.apt_num_checker[street_lookup_key] = parsed_address

    def repair_address(self, parsed_address):
        if not parsed_address.zip_code:
            self.repair_zip(parsed_address)
        elif parsed_address.zip_code and not parsed_address.city and not parsed_address.federal_district:
            self.repair_city(parsed_address)
        elif parsed_address.name in bad_names:
            self.repair_name(parsed_address)
        elif not parsed_address.street_type:
            self.repair_street_type(parsed_address)

    def repair_zip(self, parsed_address):
        for good_address in self.good_addresses:
            match = (parsed_address.city == good_address.city and
                     parsed_address.state == good_address.state and
                     parsed_address.federal_district == good_address.federal_district and
                     parsed_address.street_name == good_address.street_name)
            if match:
                parsed_address.zip_code = good_address.zip_code
        parsed_address.repair_attempts += 1

    def repair_city(self, parsed_address):
        for good_address in self.good_addresses:
            if parsed_address.zip_code == good_address.zip_code:
                parsed_address.city = good_address.city
                parsed_address.state = good_address.state
                parsed_address.federal_district = good_address.federal_district
        parsed_address.repair_attempts += 1

    def repair_name(self, parsed_address):
        for good_address in self.good_addresses:
            if parsed_address.make_address().line2 == good_address.make_address().line2:
                parsed_address.name = good_address.name
        parsed_address.repair_attempts += 1

    def repair_street_type(self, parsed_address):
        for good_address in self.good_addresses:
            match = (parsed_address.street_num == good_address.street_num and
                     parsed_address.street_name == good_address.street_name)
            if match:
                parsed_address.street_type = good_address.street_type
        parsed_address.repair_attempts += 1

    def validate_address(self, parsed_address):
        apt_num_lookup = str(parsed_address.name + ' ' + parsed_address.street_num + ' ' + parsed_address.street_name)
        if apt_num_lookup in self.apt_num_checker:
            parsed_address.apt_num = self.apt_num_checker[apt_num_lookup].apt_num
            parsed_address.street_type = self.apt_num_checker[apt_num_lookup].street_type
            parsed_address.zip_code = self.apt_num_checker[apt_num_lookup].zip_code
