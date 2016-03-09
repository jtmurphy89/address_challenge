#!/usr/bin/env python
import argparse
import csv
import os.path
import sys

import bundler
from data_types import Address, Letter, RETURN_TO_SENDER

TEST_DATA_DIR = 'data'

LEVEL4 = 'level4'
LEVELS = ('level1', 'level2a', 'level2b', 'level2c', 'level2d', 'level2e',
          'level3', LEVEL4)

RETURN_TO_SENDER_ADDRESS_ID = -1


def _load_input(buf):
    """ Loads a list of Letters from a buffer. The schema for the buffer should
    be:

    <id1>
    <addr1_line1>
    <addr1_line2>
    <addr1_line3>
    <id2>
    <addr2_line1>
    <addr2_line2>
    <addr2_line3>
    """

    letters = []
    while True:
        id = buf.readline()
        line1 = buf.readline()
        line2 = buf.readline()
        line3 = buf.readline()

        if id == '':  # EOF
            break

        address = Address(line1.strip(), line2.strip(), line3.strip())
        letter = Letter(int(id), address)
        letters.append(letter)

    return letters


def _load_output(buf):
    """ Loads a list of Bundles to use as golden data. Bundles are written one
    Bundle per line, and each line is a space-delimited list of the Letter IDs
    for the Bundle.

    For example:

    <id1> <id4> <id7>
    <id2>
    <id3> <id5> <id6
    """
    id_lists = []
    for line in buf:
        id_lists.append([int(id) for id in line.split()])

    for id_list in id_lists:
        assert sorted(id_list) == id_list

    return id_lists


def _verify_output(output, expected, input_data):
    # First do some data validations
    found_letters = set()
    duplicates = set()

    bundle_addresses = set()
    bundle_addr_duplicates = set()
    for bundle in output:
        if (bundle.address not in set([letter.address
                                       for letter in bundle.letters])
                and bundle.address != RETURN_TO_SENDER):
            message = ('ERROR: Could not find the following address in any '
                       'Letter in the Bundle:\n%s' % bundle.address)
            return False, message

        if bundle.address in bundle_addresses:
            bundle_addr_duplicates.add(bundle.address)
        else:
            bundle_addresses.add(bundle.address)

        for letter in bundle.letters:
            if letter in found_letters:
                duplicates.add(letter)
            else:
                found_letters.add(letter)

    missing_letters = set(input_data) - found_letters
    if len(missing_letters) > 0:
        message = 'ERROR: The following Letters were not found in output:\n'
        message += '\n'.join(str(letter) for letter in sorted(
            missing_letters, key=lambda l: l.id))

        return False, message

    if len(bundle_addr_duplicates) > 0:
        message = ('ERROR: Found more than one bundle for the following '
                   'addresses:\n')
        message += '\n'.join(str(dupe)
                             for dupe in sorted(bundle_addr_duplicates,
                                                key=lambda a: str(a)))
        return False, message

    if len(duplicates) > 0:
        message = 'ERROR: Found letters in more than one bundle:\n'
        message += '\n'.join(str(dupe) for dupe in sorted(duplicates,
                                                          key=lambda l: l.id))
        return False, message

    # For each Bundle, choose the minimum id of any Letter in the Bundle. Then,
    # for each Letter in the Bundle, make a map of id to the minimum id. Do the
    # same for the expected output and verify that the maps are the same.
    output_map = {}
    id_to_letter = {}
    for bundle in output:
        letters = sorted(bundle.letters, key=lambda l: l.id)
        if bundle.address == RETURN_TO_SENDER:
            canonical_match_id = RETURN_TO_SENDER_ADDRESS_ID
        else:
            canonical_match_id = letters[0].id

        for letter in letters:
            output_map[letter.id] = canonical_match_id
            id_to_letter[letter.id] = letter

    expected_map = {}
    for id_list in expected:
        for letter_id in id_list:
            expected_map[letter_id] = id_list[0]

    for k, v in output_map.iteritems():
        if expected_map[k] != v:
            message = ('The output did not match the expected values.\n'
                       'The first error was:\n\n')

            if expected_map[k] == RETURN_TO_SENDER_ADDRESS_ID:
                message += ('%s\n\nwas expected ' % id_to_letter[k] +
                            'to be returned to sender.')
            else:
                message += ('%s' % id_to_letter[k]
                            + '\n\nwas expected to be in the same bundle as'
                            '\n\n%s' % id_to_letter[expected_map[k]])
                if k != v:
                    message += ('\n\nand not in the same bundle as'
                                '\n\n%s' % id_to_letter[v])

            return False, message

    # TODO(ben): make sure every letter is in a Bundle

    return True, ''


def _data_for_level(level_name, include_output=True):
    """ Loads the input and expected output data for a given level. """
    INPUT_FILE_BASE = 'input.txt'
    OUTPUT_FILE_BASE = 'output.txt'

    input_file_name = os.path.join(TEST_DATA_DIR, level_name, INPUT_FILE_BASE)
    output_file_name = os.path.join(TEST_DATA_DIR, level_name, OUTPUT_FILE_BASE)

    with open(input_file_name) as input_file:
        input_data = _load_input(input_file)

    if include_output:
        with open(output_file_name) as output_file:
            expected_output = _load_output(output_file)
    else:
        expected_output = None

    return input_data, expected_output


def _run_test(level_name):
    """ Tests the program against data from a certain level. """
    input_data, expected_output = _data_for_level(level_name)

    print 'Running test %s' % level_name
    program_output = bundler.bundle_mail(input_data)

    passed, message = _verify_output(program_output, expected_output,
                                     input_data)

    if len(message) > 0:
        print ''
        print message

    print '----------------------------'
    if passed:
        print 'Success!'
    else:
        print 'Fail'

    return passed


def _dump_bundles(level_name, output_file, fmt='table'):
    """ Prints the bundles to stdout """
    input_data, _ = _data_for_level(level_name, False)

    program_output = bundler.bundle_mail(input_data)

    if fmt == 'csv':
        _dump_csv(program_output, output_file)
    elif fmt == 'table':
        _dump_table(program_output, output_file)
    else:
        raise ValueError('Unexpected value: %s' % fmt)


def _dump_table(program_output, output_file):
    for bundle in program_output:
        output_file.write('%s\n\n' % bundle.address)
        for letter in bundle.letters:
            output_file.write('\t%s\n' % str(letter))
        output_file.write('\n')


def _dump_csv(program_output, output_file):
    writer = csv.writer(output_file)
    writer.writerow(('Destination Address', 'Letters'))
    for bundle in program_output:
        row = [bundle.address] + sorted(bundle.letters, key=lambda l: l.id)
        writer.writerow(row)


def _parse_arguments():
    NON_LEVEL_COMMANDS = ('all',)
    parser = argparse.ArgumentParser(
        description=('Entry point for the Address Reconciliation problem. See '
                     'the INSTRUCTIONS for an overview. Commands are:'))
    parser.add_argument('command', choices=LEVELS + NON_LEVEL_COMMANDS,
                        help="Command to run. The commands that start with "
                        "'level' will run the test for that level. 'all' will "
                        "run all level tests in order, stopping at the first "
                        "failure. The exception is 'level4', which will print "
                        "the bundles to stdout.")
    parser.add_argument('--csv', action='store_true',
                        help="When running the 'level4' command, print output "
                        "in CSV format instead of the plain text table format")
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help="File to print the output for the 'level4' "
                        "command. Defaults to stdout.")
    return parser.parse_args()


def main():
    args = _parse_arguments()
    fmt = 'csv' if args.csv else 'table'
    if args.command == LEVEL4:
        _dump_bundles(LEVEL4, args.output, fmt)
    elif args.command in LEVELS:
        _run_test(args.command)
    elif args.command == 'all':
        for level in LEVELS:
            if level == LEVEL4:
                _dump_bundles(LEVEL4, args.output, fmt)
            else:
                if not _run_test(level):
                    break
    else:
        raise Exception("Invalid command")

if __name__ == '__main__':
    main()
