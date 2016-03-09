# Address Delivery #

## Challenge Guidelines ##

We are giving you this challenge to have you write code dealing with a
challenge similar to those we face every day at Judicata. It will require you
to recognize and model patterns in data. We also want to see you write clear,
maintainable code. This challenge is designed to be open-ended, and you are not
expected to complete all of the levels. We ask that you spend about 4 hours
writing the solution you submit, but feel free to take longer to come to your
solution.

## Problem Statement ##

You are the manager of a Post Office distribution center. Your responsibility is
to take the incoming mail and give it to the letter carriers for delivery. The
letter carriers require that all mail be collected into bundles so that each
unique destination receives one bundle with all of its mail.

### Data Format and Types ###

For the rest of this description, there will be a subtle distinction between
'destinations' and 'addresses.' An 'address' will refer to a single instance of
an address appearing on a piece of mail. A 'destination' will refer to the
conceptual place a piece of mail is going. As described below, there will be
mail with different addresses that should be delivered to the same destination.

All mail is addressed using a simplified version of U.S. street
addresses. Addresses have the format:

    Name
    Street and number, or P.O. Box
    City, State ZIP Code

For example:

    Barack Obama
    1600 Pennsylvania Ave
    Washington, DC 20500

    Judicata, Inc.
    330 Townsend St, Suite 240
    San Francisco, CA 94107

The data structures we will provide for this challenge are defined in
`data_types.py`. They are Address, Letter, and Bundle.

The Address class is a representation of the U.S. street address format
described above. Its class definition is:

    class Address(object):
        def __init__(self, line1, line2, line3):
            self.line1 = line1
            self.line2 = line2
            self.line3 = line3

`line1` corresponds to the name on the address, `line2` to the street or PO Box,
and `line3` to the city, state, and ZIP code.

The input to your program will be a list of Letters. Letters are defined as:

    class Letter(object):
        def __init__(self, id, address):
            self.id = id
            self.address = address

`Letter.id` is simply a unique identifier for that particular Letter. More than
one Letter may have identical addresses, so the `id` field allows for
disambiguation. `address` is an Address as defined above.

The output of your program will be a list of Bundles. The Bundle class
definition is:

    class Bundle(object):
        def __init__(self, address):
            self.address = address
            self.letters = set()

`Bundle.address` is the destination for all the Letters in the set `letters`.

### The Task ###

Your task is to implement `bundle_mail` in `bundle.py`. `bundle_mail` is a
function which takes a list of Letters and returns a list of Bundles. The
objective is to group all Letters going to the same destination into the same
Bundle.

Note that this does not mean their `address` fields will be identical. For
example, look at:

    Judicata, Inc.
    330 Townsend St, Suite 240
    San Francisco, CA 94107

and

    Judicata
    330 Townsend St, Suite 240
    San Francisco, CA 94107

These two addresses have the same destination, even though the first lines are
slightly different. We will start looking at ways differing addresses can refer
to the same destination in Level 2. For Level 1, we will only consider
`Addresses` the same if they are exactly identical.

To be a little more rigorous, given a list of Letters, L, return a list of
Bundles, B, such that:

- Each Letter in L belongs to the `letters` set of exactly one Bundle in B.
- All letters in a single Bundle refer to the same destination.
- All letters referring to the same destination are in the same Bundle (or,
  equivalently, no two Bundles refer to the same destination).

## Ground Rules ##
Before we dive into Level 1, please read through this list of ground rules:

- Please do not edit `run.py`, the existing methods in `data_types.py`, or any
  of the files in the `data/` folder. These are used to run the test for each
  level. You may be interested in looking at the `input.txt` files in the
  subfolders of `data/` to see which addresses you are trying to bundle.

- You may add whatever functions and classes you need to `bundle.py` as well as
  `data_types.py`. You may add other files and modules as you see fit.

- Please do not use external libraries. Anything in the standard library is
  fine.

- The Levels of this challenge are meant to build on each other. You do not need
  to save snapshots of your work at each level. You may simply submit your final
  product from the last level you complete.

- This challenge is primarily about getting the correct answer for the data. We
  are not looking for a clever or speedy algorithm. We are looking for a well
  developed model of the data and the challenge of understanding addresses.

- As mentioned in the introduction, we expect you to spend about 3 hours on this
  challenge. You will probably not complete all the levels in this time,
  especially since Level 4 is deliberately open-ended. You will not fail the
  question if you don't complete all the levels. We want to see whatever you
  solution you have with around 3 hours work.

## Level 1 ##

The purpose of this level is to familiarize yourself with the challenge and with
the tools you will be using for Levels 2 and 3.

Implement `bundle_mail` in bundle.py as described above. In Level 1, you should
consider `Addresses` to be the same only if all three lines of the address are
exactly identical. Once that is done, you can run

    $ python run.py level1

to check your output. If your program works, `run.py` should print the word
"Success!" when it is done. Otherwise, it will print a description of what went
wrong and the word "Fail".

## Level 2 ##

In Level 2, we start exploring the ways that addresses can differ while still
referring to the same destination. There are 5 parts of Level 2, levels a-e. You
can run them with the following commands:

    $ python run.py level2a
    $ python run.py level2b
    $ python run.py level2c
    $ python run.py level2d
    $ python run.py level2e

Each of the parts of Level 2 highlight a way for Letters with differing
Addresses to belong to the same Bundle. Try running your Level 1 code on Level
2a:

    $ python run.py level2a

You should see the following output:

    Running test level2a

    The output did not match the expected values.
    The first error was:

    Letter id: 2    Barack Obama    1600 Pennsylvania Avenue        Washington, DC 20500

    was expected to be in the same bundle as

    Letter id: 1    Barack Obama    1600 Pennsylvania Ave   Washington, DC 20500
    ----------------------------
    Fail

In this case, 'Avenue' has been abbreviated as 'Ave'. You should modify your
code to recognize these two addresses as the same. Once that is done, fix any
other issues you find in Level 2a.

Parts b through e contain similar challenges. Work through each of these levels
until you can pass all of them.

## Level 3 ##

Sometimes, you will not know where to deliver a Letter. The Address may not
contain enough information to be a full destination, or you may not be able to
decide which Bundle a Letter belongs to. In that case, you have no choice but
to return the Letter to the sender. Create a special Bundle with the Address
constant `data_types.RETURN_TO_SENDER`. When you need to return a Letter to the
sender, you may place it in that Bundle.

As in Level 2, run

    $ python run.py level3

to see examples of what kind of mail needs to be returned to the sender.

## Level 4 ##

While you have solved some of the challenges with bundling mail, there are still
many others out there. It is now up to you to find those issues and figure out
solutions. Are there Letters that should be in the same Bundle but are not? What
do you need to return to sender? Is there any mail in the wrong Bundle? These
are all challenges you should think about when looking through the data.

Now, a word of warning: There is a lot of data here, and lots of different
issues that you can tackle. You are not expected to get all of them. You should
spend about 3 hours total across all levels of this challenge, and you do not
need to spend more than that to track down every corner case in this Level.

The way you run this Level is a little different from the others. If you run

    $ python run.py level4

you will notice the output is different from what you have seen so far. You are
seeing the bundles your code is generating being written back to you. The
default format is:

    bundle1.address.line1	bundle1.address.line2	bundle1.address.line3

        Letter id: bundle1.letters[0].id	bundle1.letters[0].line1	bundle1.letters[0].line2	bundle1.letters[0].line3
        Letter id: bundle1.letters[1].id	bundle1.letters[1].line1	bundle1.letters[1].line2	bundle1.letters[1].line3

    bundle2.address.line1	bundle2.address.line2	bundle2.address.line3

        Letter id: bundle2.letters[0].id	bundle2.letters[0].line1	bundle2.letters[0].line2	bundle2.letters[0].line3

You may also receive output in csv format. This format has one Bundle per row,
where the first column is the `address` of the Bundle, and the subsequent
columns contain the Letters from `letters`.
per column:

    $ python run.py level4 --csv

Good luck!
