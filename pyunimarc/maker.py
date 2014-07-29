#-*- coding: utf8-*-
__author__ = 'philippebazard'

from pyunimarc import Record, WriteNeedsRecord

class Maker(object):

    def write(self, record):
        pass

class MARCMaker(Maker):
    """
    MARCMaker generates the ISO 2709 (MARC) record structure by converting simple ASCII (DOS) text files
    that already include MARC content designators (tags, indicators, and subfield codes),
    and the special textual “flags” that identify the beginning and end of each record, field, and subfield.
    Once the source records have been created and saved as a DOS file, converting the records to MARC is a quick step.

    Put here the as_marc() function
    """
    def __init__(self, filename):
        """
        You need to pass in a filename string.
        """
        super(MARCMaker, self).__init__()
        self.filename = filename

    def write(self, record):
        """
        Opens the file and closes it.
        """
        if not isinstance(record, Record):
            raise WriteNeedsRecord
        with open(self.filename, 'w') as f:
            f.write(record.as_unimarc())
