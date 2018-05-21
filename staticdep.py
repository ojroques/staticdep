import subprocess
import argparse
import json
from objectfile import ObjectFile    # A class to represent an object file

index = {}          # Symbols as keys and their location as value
objectFiles = []    # List of objects files included in the static lib

def getContent(ar_output):
    """Retrieve the object files listed in the archive. For each file,
    create a new ObjectFile and add it to the global list of object files.
    """
    for filename in ar_output:
        objectFiles.append(ObjectFile(filename))

def buildIndex(nm_output):
    """Build the archive index from the output of nm. This index contains
    each (local) symbol and its location.
    """
    for line in nm_output:
        if (line == ""):
            break
        elif (line != "Archive index:"):
            splittedLine = line.split()
            symbolName, objectFile = splittedLine[0], splittedLine[2]
            index[symbolName] = objectFile

def getDependencies(nm_output, filename):
    """List object files on which 'filename' depends on by searching for
    unresolved symbols in 'nm' output for 'filename'.
    """
    dependencies = set()    # Required object files
    unresLocal   = []       # Unresolved local (in the static lib) symbols
    unresGlobal  = []       # Unresolved global symbols

    # Get line number in the nm output of the object file
    try:
        i0 = nm_output.index(filename + ":")
    except ValueError:
        print("Symbol {0} was not found!".format(filename))
        return

    # Iterate over each symbol to search for the unresolved ones (Type 'U')
    for line in nm_output[i0 + 1:]:
        if (line == ""):
            break
        splittedLine = line.split()
        symbolType, symbolName = splittedLine[-2], splittedLine[-1]
        if (symbolType == 'U'):
            if (symbolName in index):    # If the symbol location is known
                unresLocal.append({symbolName: index[symbolName]})
                dependencies.add(index[symbolName])
            else:
                unresGlobal.append(symbolName)

    return (list(dependencies), unresLocal, unresGlobal)

def saveJSON(slib, outfile):
    """Build the JSON from the object list then save it in a file."""
    objdict = {}

    # First, save the name of the static library
    objdict["Static library"] = slib
    # Then for each object file, save dependencies and unresolved symbols
    for objectFile in objectFiles:
        attrdict = {}
        attrdict["Dependencies"]              = objectFile.getDependencies()
        attrdict["Unresolved local symbols"]  = objectFile.getUnresLocal()
        attrdict["Unresolved global symbols"] = objectFile.getUnresGlobal()
        objdict[objectFile.getFilename()]     = attrdict

    # Write the JSON representation in a text file
    try:
        with open(outfile, 'w') as out:
            json.dump(objdict, out, indent=4)
            print("JSON result of '{0}' analysis saved as '{1}'".format(slib, outfile))
    except IOError as e:
        print("I/O error on '{0}': {1}".format(outfile, e.strerror))
        return

def printSummary(slib):
    """Print a summary of the analysis."""
    nbObj     = len(objectFiles)   # The static library name is not counted
    # The longest name length to adjust spacing for aesthetic purpose
    maxLength = max([len(obj.getFilename()) for obj in objectFiles])
    maxLength = max(maxLength, len("OBJ_FILE"))

    print("\nSUMMARY OF ANALYSIS")
    print("The static library '{0}' contains {1} object files:".format(slib, nbObj))
    print("- OBJ_FILE" + " "*(maxLength - len("OBJ_FILE")) + " <- DEPENDENCIES")
    for objectFile in objectFiles:
        filename     = objectFile.getFilename()
        dependencies = objectFile.getDependencies()
        line         = "- {0}".format(filename) + " " * (maxLength - len(filename))
        line        += " <- "
        if (dependencies == []):
            line += "No dependencies"
        else:
            line += ", ".join(dependencies)
        print(line)

def main():
    """The main function."""
    # Parse the argument line
    parser = argparse.ArgumentParser(description="List the object file dependencies of a static library")
    parser.add_argument("slib", metavar="static_library",
                        help="the static library to analyze")
    parser.add_argument("-o", metavar="outfile",
                        help="name of the output file (default: static_library.json)")
    parser.add_argument("-s", action="store_true",
                        help="print a summary of the analysis")
    slib    = parser.parse_args().slib    # Name of the static library
    outfile = parser.parse_args().o       # Name of the output file
    if (outfile == None):
        try:
            outfile = slib[:-2] + ".json" # "slib.json" by default
        except IndexError:
            outfile = "out.json"

    # Call "ar -t" on the static library, which lists its content
    try:
        ar_output = subprocess.check_output(["ar", "-t", slib]).decode()
    except subprocess.CalledProcessError as e:
        print("Could not execute '{0}'".format(' '.join(e.cmd)))
        return
    ar_output = ar_output.splitlines()
    getContent(ar_output)    # Create the list of object file

    # Call "nm -s" on the static library, which lists symbols and index of the archive
    try:
        nm_output = subprocess.check_output(["nm", "-s", slib]).decode()
    except subprocess.CalledProcessError as e:
        print("Could not execute '{0}'".format(' '.join(e.cmd)))
        return
    nm_output = nm_output.splitlines()[1:]
    buildIndex(nm_output)    # Create the index which associates symbols to their location

    # Iterate over the object files to create associated lists
    for objectFile in objectFiles:
        dependencies, unresLocal, unresGlobal = getDependencies(nm_output, objectFile.getFilename())
        objectFile.setUnresLocal(unresLocal)
        objectFile.setUnresGlobal(unresGlobal)
        objectFile.setDependencies(dependencies)

    # Finally save the JSON in a file
    saveJSON(slib, outfile)

    # If the '-s' option is set, also print a summary of the analysis
    if (parser.parse_args().s):
        printSummary(slib)


main()
