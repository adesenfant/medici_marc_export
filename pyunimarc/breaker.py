#-*- coding: utf8-*-
__author__ = 'philippebazard'

class Breaker(object):
    """

    """
    def __iter__(self):
        return self

class MARCBreaker(Breaker):
    """
    A file of MARC records can converted to an ASCII (DOS) text file format using the MARCBreaker program. MARCBreaker
    generates a text file that is formatted the way MARCMaker requires (see the section on the MARCMaker input file above).
    This can be very useful for importing MARC data to non-MARC systems.

    TODO: Put here the decode_marc() function.
    """
