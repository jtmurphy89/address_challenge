import re


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

# for basic parsing ability
base_re = lambda x: '(?P<front>{front}){middle}(?P<back>{back})'.format(front=x[0], middle=x[1], back=x[2])

# basic junk to remove from address
junk = ['INC', 'LLC', 'LLP', '&', '.', ',']

# basic address pieces as seen in data
NAME_PREFIXES = ['MR', 'MS', 'MRS']
AMBIGUOUS_NAMES = ['POSTAL CUSTOMER', 'RESIDENT']
STREET_PREFIXES = ['NE', 'So?u?t?h?ea?s?t?', 'Po?s?t?\s?Of?f?i?c?e?\s?Box']
STREET_TYPE_LIST = ['Ave?n?u?e?', 'Pla?za?', 'Str?e?e?t?', 'Circ?l?e?', 'Terrace', 'Bo?u?le?va?r?d']
STREET_TYPE_DICT = {'A': 'AVE', 'P': 'PLZ', 'S': 'ST', 'C': 'CIR', 'B': 'BLVD'}
STREET_SUFFIXES = ['NW']
APT_LIST = ['Suite', 'Ste', 'Room', 'Apartment', 'Apt', '#', 'Unit']
STATE_DICT = {'CALIFORNIA': 'CA', 'CA': 'CA', 'OREGON': 'OR', 'OR': 'OR', 'NEW YORK': 'NY', 'NY': 'NY'}

# exceptions observed in data
exceptions = {
    'name': {'WILSON SONSINI GOODRICH  ROSATI': 'WSGR', 'DIAMOND JOE': 'JOE BIDEN',
             'SAN FRANCISCO FIRE DEPARTMENT': 'SFFD', 'JIM SMITH': 'JAMES SMITH',
             'THE WHITE HOUSE': 'BARACK OBAMA'},
    'street_name': {'THE WHITE HOUSE': '1600 PENNSYLVANIA AVE', 'EYE': 'I',
                    'MARTIN LUTHER KING JUNIOR': 'MLK JR', 'MARTIN LUTHER KING JR': 'MLK JR',
                    '5TH': 'FIFTH', 'KERNY': 'KEARNY'},
    'street_num': {'ONE': '1', '5TH': 'FIFTH'},
    'street_type': {'A': 'AVE', 'P': 'PLZ', 'S': 'ST', 'C': 'CIR', 'B': 'BLVD'},
    'city': {'SF': 'SAN FRANCISCO', 'WASHINGTON DC': ''},
    'state': {'CALIFORNIA': 'CA', 'CA': 'CA', 'OREGON': 'OR', 'OR': 'OR', 'NEW YORK': 'NY', 'NY': 'NY'}
}

WHITE_HOUSE_ADDRESS = Address('BARACK OBAMA',
                              '1600 PENNSYLVANIA AVENUE',
                              'WASHINGTON DC 20500')


# for each item in the address pieces list,

def handle_exceptions(key, data):
    if key in exceptions:
        data = data[0] if key is 'street_type' else data
        return exceptions[key].get(data, data)
    return data


def remove_junk(name, junk):
    for piece_of_junk in junk:
        name = name.replace(piece_of_junk, '').strip()
    return name


class CanonicalizedAddress(object):
    address_pieces = ['name', 'street_num', 'apt_num', 'street_prefix', 'street_suffix', 'street_type', 'street_name',
                      'zip_code', 'federal_district', 'state', 'city']

    def __init__(self, line1, line2, line3):
        self.line1 = remove_junk(line1.upper(), junk)
        self.line2 = remove_junk(line2.upper(), junk)
        self.line3 = remove_junk(line3.upper(), junk)
        self.address_data = {addy_key: self.canonicalizer(addy_key) for addy_key in self.address_pieces}
        self.repair_attempts = 0
        self.is_RTS = not self.address_data['zip_code'] and not self.address_data['state'] and not self.address_data[
            'federal_district']
        self.is_white_house = True if self.address_data['name'] == 'BARACK OBAMA' else False

    def canonicalizer(self, key):
        parsed_data = ''
        re_list = []
        line_number = 3 if key in ['city', 'state', 'federal_district', 'zip_code'] else 2
        query_line = self.line2 if line_number is 2 else self.line3
        # this will flag which direction we are parsing with the regex
        query = ''
        remainder = ''
        if key is 'name':
            first_name = self.line1.split(' ', 1)[0]
            short_name = self.line1.split(' ', 1)[1] if first_name in NAME_PREFIXES else self.line1
            return handle_exceptions(key, short_name)
        if key is 'city':
            return handle_exceptions('city', self.line3)
        if key is 'street_name':
            return handle_exceptions('street_name', self.line2)
        if key is 'federal_district':
            if self.line3 == 'WASHINGTON DC':
                parsed_data = self.line3
            return parsed_data
        if key is 'street_num':
            re_list = [base_re(['\d+', '\s', '.*'])] + [base_re([blah, '\s', '.*']) for blah in ['ONE', '5TH', 'FIFTH']]
            query = 'front'
            remainder = 'back'
        if key is 'apt_num':
            re_list = [base_re(['.*', apt_type + '\s?', '\d+']) for apt_type in APT_LIST]
            query = 'back'
            remainder = 'front'
        if key is 'street_prefix':
            re_list = [base_re([prefix, '\s', '.*']) for prefix in STREET_PREFIXES]
            query = 'front'
            remainder = 'back'
        if key is 'street_suffix':
            re_list = [base_re(['.*', '\s', suffix]) for suffix in STREET_SUFFIXES]
            query = 'back'
            remainder = 'front'
        if key is 'street_type':
            re_list = [base_re(['.*', '', st_type]) for st_type in STREET_TYPE_LIST]
            query = 'back'
            remainder = 'front'
        if key is 'zip_code':
            re_list = [base_re(['.*', '', '\d\d\d\d\d']) + '(?:-\d+)*']
            query = 'back'
            remainder = 'front'
        if key is 'state':
            re_list = [base_re(['.*', '\s', state]) for state in STATE_DICT]
            query = 'back'
            remainder = 'front'
        # if we make it here, there should be at _most_ one match...
        match = filter(None, [re.match(item, query_line, re.IGNORECASE) for item in re_list])
        if match:
            parsed_data = handle_exceptions(key, match[0].group(query).strip())
            self.update_address_line(line_number, match[0].group(remainder).strip())
        return parsed_data

    def update_address_line(self, line_num, line_remainder):
        if line_num is 2:
            self.line2 = line_remainder
        if line_num is 3:
            self.line3 = line_remainder

    def make_address(self):
        # this is a little hairy...
        if self.is_RTS:
            return RETURN_TO_SENDER
        if self.is_white_house:
            return WHITE_HOUSE_ADDRESS
        line1 = self.address_data['name']
        line2a = self.address_data['street_num'] + ' ' + self.address_data['street_prefix']
        line2b = self.address_data['street_name'] + ' ' + self.address_data['street_type'] + ' ' + self.address_data[
            'apt_num']
        line3a = self.address_data['city'] + ' ' + self.address_data['state'] + ' ' + self.address_data[
            'federal_district']
        line3b = self.address_data['zip_code']
        line2 = line2a.strip() + ' ' + line2b.strip()
        line3 = line3a.strip() + ' ' + line3b.strip()
        return Address(line1, line2.strip(), line3.strip())

    def has_bad_state_fd(self):
        return self.address_data['zip_code'] and not self.address_data['state'] and not self.address_data[
            'federal_district']

    def has_no_zip(self):
        return not self.address_data['zip_code']

    def has_ambiguous_name(self):
        return self.address_data['name'] in AMBIGUOUS_NAMES

    def has_no_street_type(self):
        return not self.address_data['street_type']

    def has_name_prefix(self):
        return self.line1.split(' ', 1)[0] in NAME_PREFIXES

    def is_lost_cause(self):
        return self.repair_attempts > 10

    def queue_score(self):
        score = len(filter(lambda x: x == '', self.address_data.items()))
        return score + 1 if self.has_name_prefix() else score

    def is_good_egg(self):
        if self.is_lost_cause() or self.is_RTS or self.is_white_house:
            return True
        is_bad_egg = (self.has_bad_state_fd() or self.has_no_zip() or self.has_ambiguous_name() or
                      self.has_no_street_type() or self.has_name_prefix())
        if is_bad_egg:
            return False
        return True


class AddressRepairer(object):
    zip_filter = ['city', 'state', 'federal_district', 'street_name']
    city_st_fd_filter = ['zip_code']
    name_filter = ['street_num', 'street_name']
    street_type_filter = ['street_num', 'street_name']

    def __init__(self):
        self.good_addresses = []
        self.street_prefix_lookup = {}
        self.apt_num_lookup = {}

    def add_good_address(self, parsed_address):
        self.good_addresses.append(parsed_address)
        self.apt_num_lookup[tuple(self.filtered_list(parsed_address, ['name', 'street_num', 'street_name']))] = [
            parsed_address.address_data['apt_num'], parsed_address.address_data['zip_code']]
        if parsed_address.address_data['street_prefix']:
            self.street_prefix_lookup[parsed_address.address_data['street_name']] = parsed_address.address_data[
                'street_prefix']

    # if there's nothing left to repair, then check for correctness
    def correctness_check(self, parsed_address):
        if parsed_address.address_data['street_name'] in self.street_prefix_lookup:
            parsed_address.address_data['street_prefix'] = self.street_prefix_lookup[
                parsed_address.address_data['street_name']]
        apt_lookup = tuple(self.filtered_list(parsed_address, ['name', 'street_num', 'street_name']))
        if apt_lookup in self.apt_num_lookup:
            num, zip_code = self.apt_num_lookup[apt_lookup]
            parsed_address.address_data['apt_num'] = num
            parsed_address.address_data['zip_code'] = zip_code

    def repair_address(self, parsed_address):
        if parsed_address.has_no_zip():
            self.repair_address_part(parsed_address, 'zip_code', self.zip_filter)
        elif parsed_address.has_bad_state_fd():
            self.repair_address_part(parsed_address, 'city', self.city_st_fd_filter)
            self.repair_address_part(parsed_address, 'state', self.city_st_fd_filter)
            self.repair_address_part(parsed_address, 'federal_district', self.city_st_fd_filter)
        elif parsed_address.has_name_prefix():
            self.repair_name_prefix(parsed_address)
        elif parsed_address.has_ambiguous_name():
            self.repair_ambiguous_name(parsed_address)
        elif parsed_address.has_no_street_type():
            self.repair_address_part(parsed_address, 'street_type', self.street_type_filter)
        parsed_address.repair_attempts += 1

    def repair_address_part(self, parsed_address, key, filter_type):
        repair_key = self.filtered_list(parsed_address, filter_type)
        query_set = [self.filtered_list(good_addy, filter_type) for good_addy in self.good_addresses]
        if repair_key in query_set:
            parsed_address.address_data[key] = self.good_addresses[query_set.index(repair_key)].address_data[key]

    def repair_name_prefix(self, parsed_address):
        repair_key = [parsed_address.address_data[item] for item in ['name'] + self.name_filter]
        query_set = [self.filter_good_last_name(addy) for addy in self.good_addresses]
        if repair_key in query_set:
            parsed_address.address_data['name'] = self.good_addresses[query_set.index(repair_key)].address_data['name']

    def repair_ambiguous_name(self, parsed_address):
        repair_key = parsed_address.make_address().line2
        query_set = [a.make_address().line2 for a in self.good_addresses]
        if repair_key in query_set:
            parsed_address.address_data['name'] = self.good_addresses[query_set.index(repair_key)].address_data['name']
        else:
            parsed_address.is_RTS = True

    def filtered_list(self, address, map_filter):
        return [address.address_data[item] for item in map_filter]

    def filter_good_last_name(self, a):
        return [a.address_data['name'].replace(a.address_data['name'].split(' ', 1)[0], '').strip(),
                a.address_data['street_num'], a.address_data['street_name']]
