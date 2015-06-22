"""
support for command line scripts with Argh and ConfigParser 
"""

import logging as log
from configparser import ConfigParser, NoOptionError
from argh import ArghParser



def get_parser_and_config(config_fname):
    """
    Return an argument parser for argh and a configuration parser
    
    The argument parser can be used with argh.add_commands and argh.dispatch.
    The configuration parser is initialized by reading configuration file(s) 
    specified with the "-c"/"--config" command line option in sys.argv,
    or by reading config_fname otherwise.
    """
    # Create argument parser.
    # Do not add help, because any "-h" or "--help" option must be handled 
    # by argh instead of the standard argument parser.
    arg_parser = ArghParser(add_help=False)
    
    # Add the option for one or more config files, including a default.
    # It is not possible to use nargs="+", because then argparse consumes 
    # *all* arguments, leaving nothing to dispatch to argh.
    arg_parser.add_argument(
        "-c",
        "--config",
        metavar="CONFIG_FILE:[CONFIG_FILE ...]",
        default=config_fname,
        help="colon-separated ordered list of configuration files, "
        "where later configurations override earlier ones")

    # Parse the "-c"/"--config" option (if any), 
    # leaving all others to for argh 
    namespace = arg_parser.parse_known_args()[0]
    
    # Now add the standard help option, to be handled/displayed by argh
    arg_parser.add_argument(
        '-h', '--help',
        action='help', 
        help='show this help message and exit') 
    
    # Read the config file(s)
    config_parser = ConfigParser(allow_no_value=True)
    cfg_filenames = namespace.config.split(":")
    read_ok = config_parser.read(cfg_filenames)
    
    # Non-existing config files are silently ignored by ConfigParser, 
    # but we want an error message
    for fname in cfg_filenames:        
        if  fname not in read_ok:
            arg_parser.error(
                "config file {!r} not found".format(fname))
    
    return arg_parser, config_parser



def get_option(config, section, option):
    "get value as non-empty string or None"
    try:
        value = config.get(section, option)
    except (KeyError, NoOptionError): 
        # case 1: option is not defined
        log.warn(
            "option {!r} undefined in configuration file(s)".format(option))
        return None
    
    if value is '':
        # case 2: option is defined without a value (i.e. "opt =")
        return None
    
    return value


def get_option_int(config, section, option):
    "get value as int or None"
    value = get_option(config, section, option)
    
    if value:
        # may raise value error
        return int(value)
    
    
def get_option_bool(config, section, option):
    "get value as bool" 
    # check first if a value is defined, otherwise return False
    if get_option(config, section, option):
        # '1', 'yes', 'true', 'on' --> True
        # '0', 'no', 'false', 'off' --> False
        return config.getboolean(section, option)
