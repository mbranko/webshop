from configparser import ConfigParser
from itertools import chain
from django.core.exceptions import ImproperlyConfigured


def read_variable(file_name, variable_name):
    parser = ConfigParser()
    try:
        with open(file_name) as lines:
            lines = chain(("[top]",), lines)
            parser.read_file(lines)
        return parser['top'][variable_name]
    except IOError as ex:
        # ignorisi ovu gresku jer se javlja samo kod pravljenja Docker image-a
        return None
    except KeyError as ex:
        raise ImproperlyConfigured(f'Variable not found: {variable_name}')
