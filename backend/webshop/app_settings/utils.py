from configparser import ConfigParser
from itertools import chain
import os
from django.core.exceptions import ImproperlyConfigured


def get_variable(variable_name, default_value):
    if variable_name in os.environ:
        print(f"Reading variable {variable_name} from environment: {os.environ[variable_name]}")
        return os.environ[variable_name]
    else:
        print(f"Using default for variable {variable_name}: {default_value}")
        return default_value


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
