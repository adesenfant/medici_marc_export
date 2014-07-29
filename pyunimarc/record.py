# -*- coding: utf8-*-

import re

from pyunimarc.exceptions import BaseAddressInvalid, RecordLeaderInvalid, \
        BaseAddressNotFound, RecordDirectoryInvalid, NoFieldsFound, \
        FieldNotFound
from pyunimarc.constants import LEADER_LEN, DIRECTORY_ENTRY_LEN, END_OF_RECORD
from pyunimarc.field import Field, SUBFIELD_INDICATOR, END_OF_FIELD, \
        map_marc8_field
from pyunimarc.marc8 import marc8_to_unicode

from converter.marc8codec import Marc8Codec
ENCODING = 'marc8'
#ENCODING = 'utf-8'

try:
    # the json module was included in the stdlib in python 2.6
    # http://docs.python.org/library/json.html
    import json
except ImportError:
    # simplejson 2.0.9 is available for python 2.4+
    # http://pypi.python.org/pypi/simplejson/2.0.9
    # simplejson 1.7.3 is available for python 2.3+
    # http://pypi.python.org/pypi/simplejson/1.7.3
    import simplejson as json

try:
    # izip_longest first appeared in python 2.6
    # http://docs.python.org/library/itertools.html#itertools.izip_longest
    from itertools import izip_longest
except ImportError:
    # itertools was introducted in python 2.3
    # we just define the required classes and functions
    # for 2.3 <= python < 2.6 here
    class ZipExhausted(Exception):
        pass

    def _next(obj):
        """
        ``next`` (http://docs.python.org/library/functions.html#next)
        was introduced in python 2.6 - and if we are here
        (no ``izip_longest``), than we need to define this."""
        return obj.next()

    def izip_longest(*args, **kwds):
        """
        Make an iterator that aggregates elements from each of the iterables.
        If the iterables are of uneven length, missing values are filled-in
        with fillvalue.
        Iteration continues until the longest iterable is exhausted.

        This function is available in the standard lib since 2.6.
        """
        # chain and repeat are available since python 2.3
        from itertools import chain, repeat

        # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
        fillvalue = kwds.get('fillvalue', '')
        counter = [len(args) - 1]
        def sentinel():
            if not counter[0]:
                raise ZipExhausted
            counter[0] -= 1
            yield fillvalue
        fillers = repeat(fillvalue)
        iterators = [chain(it, sentinel(), fillers) for it in args]
        try:
            while iterators:
                yield tuple(map(_next, iterators))
        except ZipExhausted:
            pass
        finally:
            del chain

isbn_regex = re.compile(r'([0-9\-xX]+)')

class Record(object):
    """
    Specific record label for Medici: ngm 22 450
    """

    def __init__(self, data='', to_unicode=False, force_utf8=False,
        hide_utf8_warnings=False, utf8_handling='strict', target=None):
        if target == "UNIMARC":
            self.leader = (' '*5) + 'ngm' + (' '*2) + '22' + (' '*8) + '450' + (' ')
        if target == "MARC21":
            self.leader = (' '*5) + 'ngm' + (' '*2) + '22' + (' '*8) + '45' + ('  ')
        self.fields = list()
        self.pos = 0
        self.force_utf8 = force_utf8
        if len(data) > 0:
            self.decode_marc(data, to_unicode=to_unicode,
                             force_utf8=force_utf8,
                             hide_utf8_warnings=hide_utf8_warnings,
                             utf8_handling=utf8_handling)
        elif force_utf8:
            self.leader = self.leader[0:9] + 'a' + self.leader[10:]

    def __str__(self):
        """

        """
        text_list = ['=LDR  %s' % self.leader]

        for field in self.fields:
            print field

        text_list.extend([str(field) for field in self.fields])
        print text_list
        text = '\n'.join(text_list) + '\n'
        return text


    def __iter__(self):
        self.__pos = 0
        return self

    def next(self):
        if self.__pos >= len(self.fields):
            raise StopIteration
        self.__pos += 1
        return self.fields[self.__pos - 1]

    def add_field(self, *fields):
        """

        """
        self.fields.extend(fields)

    def add_grouped_field(self, *fields):
        """

        """
        for f in fields:
            if len(self.fields) == 0 or not f.tag.isdigit():
                self.fields.append(f)
                continue
            self._sort_fields(f, 'grouped')

    def add_ordered_field(self, *fields):
        """

        """
        for f in fields:
            if len(self.fields) == 0 or not f.tag.isdigit():
                self.fields.append(f)
                continue
            self._sort_fields(f, 'ordered')

    def _sort_fields(self, field, mode):
        if mode == 'grouped':
            tag = int(field.tag[0])
        else:
            tag = int(field.tag)

        i, last_tag = 0, 0
        for selff in self.fields:
            i += 1
            if not selff.tag.isdigit():
                self.fields.insert(i - 1, field)
                break

            if mode == 'grouped':
                last_tag = int(selff.tag[0])
            else:
                last_tag = int(selff.tag)

            if last_tag > tag:
                self.fields.insert(i - 1, field)
                break
            if len(self.fields) == i:
                self.fields.append(field)
                break


    def get_fields(self, *args):
        """

        """
        if (len(args) == 0):
            return self.fields

        return [f for f in self.fields if f.tag in args]

    def as_unimarc(self):
        """

        """
        fields = ''
        directory = ''
        offset = 0

        # Sort field by tag order
        self.fields.sort(key=lambda field: field.tag, reverse=False)

        for field in self.fields:
            field_data = field.as_unimarc()
            print field
            if self.leader[9] == 'a' or self.force_utf8:
                field_data = field_data.encode(ENCODING)
            fields += field_data
            if field.tag.isdigit():
                directory += '%03d' % int(field.tag)
            else:
                directory += '%03s' % field.tag
            directory += '%04d%05d' % (len(field_data), offset)
            offset += len(field_data)

        # directory ends with an end of field
        directory += END_OF_FIELD

        # field data ends with an end of record
        fields += END_OF_RECORD

        # the base address where the directory ends and the field data begins
        base_address = LEADER_LEN + len(directory)

        # figure out the length of the record
        record_length = base_address + len(fields)

        # update the leader with the current record length and base address
        # the lengths are fixed width and zero padded
        self.leader = '%05d%s%05d%s' % \
            (record_length, self.leader[5:12], base_address, self.leader[17:])

        # return the encoded record
        if self.leader[9] == 'a' or self.force_utf8:
            return self.leader.encode(ENCODING) + directory.encode(ENCODING) + fields
        else:
            return self.leader + directory + fields


def map_marc8_record(r):
    r.fields = map(map_marc8_field, r.fields)
    l = list(r.leader)
    l[9] = 'a' # see http://www.loc.gov/marc/specifications/speccharucs.html
    r.leader = "".join(l)
    return r
