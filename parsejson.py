import argparse
import json
from objectfile import ObjectFile    # A class to represent an object file

def main():
    """The main function."""
    # Parse the argument line
    parser = argparse.ArgumentParser(description="Parse a JSON output file to print object files that do not depend on any others (default behavior) or verify if a list of object files is complete.")
    parser.add_argument("jsonfile", metavar="json_file",
                        help="the JSON file to parse")
    parser.add_argument("-v", metavar="object_list",
                        help="list of object files (one per line in a separate txt file) to verify")
    jsonfile   = parser.parse_args().jsonfile   # The name of the json output file
    objectlist = parser.parse_args().v          # The list of object files

    try:
        with open(jsonfile, 'r') as infile:
            pass
    except IOError as e:
        print("I/O error on '{0}': {1}".format(jsonfile, e.strerror))
        return

    if (objectlist == None):
        pass
    else:
        try:
            with open(objectlist, 'r') as objfile:
                pass
        except IOError as e:
            print("I/O error on '{0}': {1}".format(objectlist, e.strerror))
            return


main()
