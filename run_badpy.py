from subprocess import call
from optparse import OptionParser
from constants import INCLUDE_MODULES, VER, DEFAULT_OUTPUT_DIR
from logger_init import *


module_str_list = ', '.join(INCLUDE_MODULES)

parser = OptionParser(version=VER)
parser.add_option("-o", "--output", dest="output", metavar="DIR", default=DEFAULT_OUTPUT_DIR, help="write files to dir, def. ./")
parser.add_option("-m", "--module", dest="modules", metavar="MODULE", action="append", choices=INCLUDE_MODULES,
                  default=[], help="modules list to fetch (def. all), available are: "+module_str_list)
parser.add_option("-e", "--module-exclude", dest="excludes", metavar="MODULE", action="append", choices=INCLUDE_MODULES,
                  default=[], help="modules list to exclude, available are: " + module_str_list)
(options, args) = parser.parse_args()

if not options.modules:
    options.modules = list(INCLUDE_MODULES)
if options.excludes:
    options.modules = list(set(options.modules) - set(options.excludes))

initialize_logger()
logging.getLogger('run_badpy')

# Having spaces around -- is important, this is a signal that Blender should stop parsing the arguments
# and allows to pass own arguments to Python.
call_blender = ['blender', '-b', '-P', 'badpy.py', '--']
call_args = [options.output, ', '.join(options.modules), ]
logging.info("RUN: %s '%s', '%s'" % (', '.join(call_blender), options.output, ', '.join(options.modules)))
call(call_blender+call_args)
