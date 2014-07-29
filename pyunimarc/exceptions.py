#-*- coding: utf8-*-

class PyunimarcException(Exception):
    pass

class RecordLengthInvalid(PyunimarcException):
    def __str__(self):
        return "Invalid record length in first 5 bytes of record"

class RecordLeaderInvalid(PyunimarcException):
    def __str__(self):
        return "Unable to extract record leader"

class RecordDirectoryInvalid(PyunimarcException):
    def __str__(self):
        return "Invalid directory"

class NoFieldsFound(PyunimarcException):
    def __str__(self):
        return "Unable to locate fields in record data"

class BaseAddressInvalid(PyunimarcException):
    def __str__(self):
        return "Base address exceeds size of record"

class BaseAddressNotFound(PyunimarcException):
    def __str__(self):
        return "Unable to locate base address of record"

class WriteNeedsRecord(PyunimarcException):
    def __str__(self):
        return "Write requires a pymarc.Record object as an argument"

class NoActiveFile(PyunimarcException):
    def __str__(self):
        return "There is no active file to write to in call to write"

class FieldNotFound(PyunimarcException):
    def __str__(self):
        return "Record does not contain the specified field"
