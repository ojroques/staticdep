import argparse
import json

def printNodes(staticdep):
    """Print object files in the given static library that do not depend on any
    other object files also contained in this library.
    """
    slibContent = staticdep["Content"]   # Content of the static library
    totalObj    = len(slibContent)       # Number of object file in the static library
    nbIndepObj  = 0                      # Number of independent object files
    print("Object files in '{0}' that do not depend on any others are:".format(staticdep["Static library"]))
    for objectName, value in slibContent.items():
        if (value['Dependencies'] == []):
            nbIndepObj += 1
            print("- " + objectName)
    print("which represents {0}/{1} of all object files or {2:2.0f}%.".format(nbIndepObj, totalObj, (nbIndepObj / totalObj) * 100))

def verify(staticdep, objectlist, objectFiles):
    """Verify that there are no missing dependencies in a list of object files."""
    slibContent     = staticdep["Content"]
    maxLength       = max([len(name) for name in slibContent.keys()])
    maxLength       = max(maxLength, len("OBJ_FILE"))
    uncompleteObj   = {}

    print("Dependencies in '{0}' of object files listed in '{1}':".format(staticdep["Static library"], objectlist))
    print("  OBJ_FILE" + " "*(maxLength - len("OBJ_FILE")) + " <- DEPENDENCIES")
    for objectName in objectFiles:
        dependencies = slibContent[objectName]["Dependencies"]
        difference   = set(dependencies) - set(objectFiles)
        if difference:
            uncompleteObj[objectName] = difference
        # Build the line to be print
        line         = "- {0}".format(objectName) + " " * (maxLength - len(objectName))
        line        += " <- "
        if (dependencies == []):
            line += "No dependencies"
        else:
            line += ", ".join(dependencies)
        print(line)

    if uncompleteObj:
        print("This list of object files is UNCOMPLETE:")
        print("  OBJ_FILE" + " "*(maxLength - len("OBJ_FILE")) + " <- MISSING DEPENDENCIES")
        for objectName, missingDep in uncompleteObj.items():
            line  = "- {0}".format(objectName) + " " * (maxLength - len(objectName))
            line += " <- "
            line += ", ".join(list(missingDep))
            print(line)
    else:
        print("This list of object files is COMPLETE")

def main():
    """The main function."""
    # Parse the argument line
    parser = argparse.ArgumentParser(description="Parse a JSON output file to print object files that do not depend on any others (default behavior) or verify if a list of object files is complete.")
    parser.add_argument("jsonfile", metavar="json_file",
                        help="the JSON file to parse")
    parser.add_argument("-v", metavar="object_list",
                        help="list of object files to verify (one per line in a separate txt file)")
    jsonfile   = parser.parse_args().jsonfile   # The name of the json output file
    objectlist = parser.parse_args().v          # List of object files

    try:
        with open(jsonfile, 'r') as infile:
            staticdep = json.load(infile)    # The loaded JSON file
        if ("slib_analysis" not in staticdep):
            raise json.JSONDecodeError("Not an analysis result", "", 0)
    except IOError as e:
        print("I/O error on '{0}': {1}".format(jsonfile, e.strerror))
        return
    except json.JSONDecodeError as e:
        print("Not a valid JSON document: {0}".format(e.msg))
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
        verify(staticdep, objectlist, objectFiles)


main()
