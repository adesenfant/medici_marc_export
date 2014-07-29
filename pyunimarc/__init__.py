# __init__.py

__version__ = '2.9.1'

from pyunimarc.record import *
from pyunimarc.field import *
from pyunimarc.exceptions import *
from pyunimarc.reader import *
from pyunimarc.writer import *
from pyunimarc.constants import *
from pyunimarc.marc8 import marc8_to_unicode, MARC8ToUnicode
from pyunimarc.marcxml import *

from pyunimarc.writer2 import *

if __name__ == "__main__":
    import doctest
    doctest.testmod()

