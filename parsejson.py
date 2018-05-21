import argparse
import json
import copy

def printNodes(staticdep):
    """Print object files in the given static library that do not depend on any
    other object files also contained in this library.
    """
    nbIndepObj = 0                            # Number of independent object files
    totalObj   = len(staticdep.keys()) - 1    # The static library name is not counted
    print("Object files in '{0}' that do not depend on any others are:".format(staticdep["Static library"]))
    for objectName, value in staticdep.items():
        if (objectName != "Static library" and value['Dependencies'] == []):
            nbIndepObj += 1
            print("- " + objectName)
    print("which represents {0}/{1} of all object files or {2:2.0f}%.".format(nbIndepObj, totalObj, (nbIndepObj / totalObj) * 100))

def main():
    """The main function."""
    # Parse the argument line
    parser = argparse.ArgumentParser(description="Parse a JSON output file to print object files that do not depend on any others (default behavior) or verify if a list of object files is complete.")
    parser.add_argument("jsonfile", metavar="json_file",
                        help="the JSON file to parse")
    parser.add_argument("-v", metavar="object_list",
                        help="list of object files (one per line in a separate txt file) to verify")
    jsonfile   = parser.parse_args().jsonfile   # The name of the json output file
    objectlist = parser.parse_args().v          # List of object files

    try:
        with open(jsonfile, 'r') as infile:
            staticdep = json.load(infile)    # The loaded JSON file
    except IOError as e:
        print("I/O error on '{0}': {1}".format(jsonfile, e.strerror))
        return

    if (objectlist == None):
        printNodes(staticdep)
    else:
        try:
            objectFiles = []   # The list of object files to verify
            with open(objectlist, 'r') as objfile:
                for line in objfile:
                    objectFiles.append(line.strip())
        except IOError as e:
            print("I/O error on '{0}': {1}".format(objectlist, e.strerror))
            return


main()
