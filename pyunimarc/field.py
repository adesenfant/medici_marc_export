# -*- coding: utf8-*-

from pyunimarc.constants import SUBFIELD_INDICATOR, END_OF_FIELD
from pyunimarc.marc8 import marc8_to_unicode

class Field(object):
    """

    """
    def __init__(self, tag, indicators=None, subfields=None, data=''):
        if indicators == None:
            indicators = []
        if subfields == None:
            subfields = []

        # attempt to normalize integer tags if necessary
        try:
            self.tag = '%03i' % int(tag)
        except ValueError:
            self.tag = '%03s' % tag

        # assume controlfields are numeric only; replicates ruby-marc behavior
        if self.tag < '010' and self.tag.isdigit():
            self.data = data
        else:
            self.indicator1, self.indicator2 = self.indicators = indicators
            self.subfields = subfields

    def __iter__(self):
        self.__pos = 0
        return self

    def __str__(self):
        """

        """
        if self.is_control_field():
            text = '=%s  %s' % (self.tag, self.data.replace(' ','\\'))
        else:
            text = '=%s  ' % (self.tag)
            for indicator in self.indicators:
                if indicator in (' ','\\'):
                    text += '\\'
                else:
                    text += '%s' % indicator
            for subfield in self:
                text += ('$%s%s' % subfield)
        return text

    def __getitem__(self, subfield):
        """
        Retrieve the first subfield with a given subfield code in a field:

            field['a']

        Handy for quick lookups.
        """
        subfields = self.get_subfields(subfield)
        if len(subfields) > 0:
            return subfields[0]
        return None

    def __contains__(self, subfield):
        """
        Allows a shorthand test of field membership:

            'a' in field

        """
        subfields = self.get_subfields(subfield)
        return len(subfields) > 0

    def __setitem__(self, code, value):
        """
        Set the values of the subfield code in a field:

            field['a'] = 'value'

        Raises KeyError if there is more than one subfield code.
        """
        subfields = self.get_subfields(code)
        if len(subfields) > 1:
            raise KeyError("more than one code '%s'" % code)
        elif len(subfields) == 0:
            raise KeyError("no code '%s'" % code)
        num_code = len(self.subfields)/2
        while num_code >= 0:
            if self.subfields[(num_code*2)-2] == code:
                self.subfields[(num_code*2)-1] = value
                break
            num_code -= 1

    def next(self):
        "Needed for iteration."
        while self.__pos < len(self.subfields):
            subfield = (self.subfields[ self.__pos ],
                self.subfields[ self.__pos+1 ])
            self.__pos += 2
            return subfield
        raise StopIteration

    def value(self):
        """
        Returns the field as a string without tag, indicators, and
        subfield indicators.
        """
        if self.is_control_field():
            return self.data
        value_list = []
        for subfield in self:
            value_list.append(subfield[1].strip())
        return ' '.join(value_list)

    def get_subfields(self, *codes):
        """
        get_subfields() accepts one or more subfield codes and returns
        a list of subfield values.  The order of the subfield values
        in the list will be the order that they appear in the field.

            print field.get_subfields('a')
            print field.get_subfields('a', 'b', 'z')
        """
        values = []
        for subfield in self:
            if subfield[0] in codes:
                values.append(subfield[1])
        return values

    def add_subfield(self, code, value):
        """
        Adds a subfield code/value pair to the field.

            field.add_subfield('u', 'http://www.loc.gov')
        """
        self.subfields.append(code)
        self.subfields.append(value)

    def delete_subfield(self, code):
        """
        Deletes the first subfield with the specified 'code' and returns
        its value:

            field.delete_subfield('a')

        If no subfield is found with the specified code None is returned.
        """
        try:
            index = self.subfields.index(code)
            value = self.subfields.pop(index + 1)
            self.subfields.pop(index)
            return value
        except ValueError:
            return None

    def is_control_field(self):
        """
        Returns true or false if the field is considered a control field.
        Control fields lack indicators and subfields.
        """
        if self.tag < '010' and self.tag.isdigit():
            return True
        return False

    def as_unimarc(self):
        """
        used during conversion of a field to raw marc
        """
        if self.is_control_field():
            return self.data + END_OF_FIELD
        marc = str(self.indicator1) + str(self.indicator2)
        for subfield in self:
            marc += SUBFIELD_INDICATOR + subfield[0] + subfield[1]
        return marc + END_OF_FIELD

    def format_field(self):
        """
        Returns the field as a string without tag, indicators, and
        subfield indicators. Like pymarc.Field.value(), but prettier
        (adds spaces, formats subject headings).
        """
        if self.is_control_field():
            return self.data
        fielddata = ''
        for subfield in self:
	    if subfield[0] == '6':
	    	continue
            if not self.is_subject_field():
                fielddata += ' %s' % subfield[1]
            else:
                if subfield[0] not in ('v', 'x', 'y', 'z'):
                    fielddata += ' %s' % subfield[1]
                else: fielddata += ' -- %s' % subfield[1]
        return fielddata.strip()

    def is_subject_field(self):
        """
        Returns True or False if the field is considered a subject
        field.  Used by format_field.
        """
        if self.tag.startswith('6'):
            return True
        return False

def map_marc8_field(f):
    if f.is_control_field():
        f.data = marc8_to_unicode(f.data)
    else:
        f.subfields = map(marc8_to_unicode, f.subfields)
    return f