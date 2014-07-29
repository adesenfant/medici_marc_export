# -*- coding: utf8-*-

from pyunimarc import Record, WriteNeedsRecord

class Writer(object):

    def write(self, record):
        pass

class MARCWriter(Writer):
    """
    TODO
    """

    def __init__(self, file_handle):
        """
        You need to pass in a file like object.
        """
        super(MARCWriter, self).__init__()
        self.file_handle = file_handle

    def write(self, record):
        """
        Writes a record.
        """
        print record
        if not isinstance(record, Record):
            raise WriteNeedsRecord
        self.file_handle.write(record.as_unimarc())

    def close(self):
        """
        Closes the file.
        """
        self.file_handle.close()
        self.file_handle = None

