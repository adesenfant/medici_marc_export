# -*- coding: utf8-*-
from pyunimarc import Record, WriteNeedsRecord

class Writer(object):

    def write(self, record):
        pass

class MARCWriter2(Writer):
    """
    TODO: ...
    """
    def __init__(self, filename):
        """
        You need to pass in a filename string.
        """
        super(MARCWriter2, self).__init__()
        self.filename = filename

    def write(self, record):
        """
        Opens the file and closes it.
        """
        if not isinstance(record, Record):            raise WriteNeedsRecord
        with open(self.filename, 'w') as f:
            f.write(record.as_unimarc())
