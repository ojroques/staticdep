import argparse
import json

def printLeaves(staticdep):
    """Print object files in the given static library that do not depend on any
    other object file also contained in this library.
    """
    slibContent = staticdep["Content"]   # Content of the static library
    totalObj    = len(slibContent)       # Number of object file in the static library
    nbIndepObj  = 0                      # Number of independent object files

    print("Object files in '{0}' that do not depend on any others are:"
          .format(staticdep["Static library"]))
    for objectName, value in slibContent.items():
        if (value['Dependencies'] == []):    # If there are no dependencies, object file is printed
            nbIndepObj += 1
            print("- " + objectName)
    print("which represents {0}/{1} of all object files or {2:.0f}%."
          .format(nbIndepObj, totalObj, (nbIndepObj / totalObj) * 100))

def verify(staticdep, objectlist, objectFiles):
    """Verify that there are no missing dependencies in a list of object file.

    Keyword arguments:
    staticdep   -- The dictionnary obtained from the JSON file
    objectlist  -- The name of the file containing the list to verify
    objectFiles -- The list of object files to verify
    """
    slibContent     = staticdep["Content"]    # Content of the static library
    # The longest name length to adjust spacing for aesthetic purpose
    maxLength       = max([len(name) for name in slibContent.keys()])
    maxLength       = max(maxLength, len("OBJ_FILE"))
    incompleteObj   = {}    # Object files (keys) with missing dependencies (values)

    # First, print each object file in the list with their dependencies
    # and find missing dependencies
    print("Dependencies in '{0}' of the {1} object files from '{2}':"
          .format(staticdep["Static library"], len(objectFiles), objectlist))
    print("  OBJ_FILE" + " "*(maxLength - len("OBJ_FILE")) + " <- DEPENDENCIES")
    for objectName in objectFiles:
        # First we must check that the given object file is indeed listed in the static library
        if (objectName in slibContent):
            dependencies = slibContent[objectName]["Dependencies"]
            # Set of missing dependencies (dependencies not in the object files list)
            difference   = set(dependencies) - set(objectFiles)
            # If there are missing dependencies, save them and the object file name
            if (difference):
                incompleteObj[objectName] = difference
            # Build the line to be printed
            line         = "- {0}".format(objectName) + " " * (maxLength - len(objectName))
            line        += " <- "
            if (dependencies == []):
                line += "No dependencies"
            else:
                line += ", ".join(dependencies)
            print(line)
        else:
            print("- No object file '{0}' found".format(objectName))

    # Then print object files with their missing dependencies if there are any
    if incompleteObj:
        print("\nThis list of object files is INCOMPLETE:")
        print("  OBJ_FILE" + " "*(maxLength - len("OBJ_FILE")) + " <- MISSING_DEPENDENCIES")
        for objectName, missingDep in incompleteObj.items():
            # Build the line to be printed
            line  = "- {0}".format(objectName) + " " * (maxLength - len(objectName))
            line += " <- "
            line += ", ".join(list(missingDep))
            print(line)
    else:
        print("This list of object files is COMPLETE")

def main():
    """The main function."""
    # Parse the argument line
    parser = argparse.ArgumentParser(description="Parse a JSON output file to print object \
                                     files that do not depend on any others (default behavior) \
                                     or verify if a list of object files is complete.")
    parser.add_argument("jsonfile", metavar="json_file",
                        help="the JSON file to parse")
    parser.add_argument("-v", metavar="object_list",
                        help="list of object files to verify (one per line in a separate txt file)")
    jsonfile   = parser.parse_args().jsonfile   # The name of the json output file
    objectlist = parser.parse_args().v          # Filename of the object file list

    # Retrieve the JSON analysis as a dictionnary
    try:
        with open(jsonfile, 'r') as infile:
            staticdep = json.load(infile)         # Load the JSON file
        if ("slib_analysis" not in staticdep):    # Check that format is correct
            raise json.JSONDecodeError("Not an analysis result", "", 0)
    except IOError as e:
        print("I/O error on '{0}': {1}".format(jsonfile, e.strerror))
        return
    except json.JSONDecodeError as e:
        print("Not a valid JSON document: {0}".format(e.msg))
        return

    # Decide what to print according to the given arguments
    if (objectlist == None):    # Print independent object files if no option '-v'
        printLeaves(staticdep)
    else:                       # Else verify that a list of object file is complete
        try:
            objectFiles = []   # The list of object file to verify
            with open(objectlist, 'r') as objfile:
                for line in objfile:
                    objectFiles.append(line.strip())
        except IOError as e:
            print("I/O error on '{0}': {1}".format(objectlist, e.strerror))
            return
        verify(staticdep, objectlist, objectFiles)


main()
