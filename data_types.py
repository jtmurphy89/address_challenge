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
