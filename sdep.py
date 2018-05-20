import subprocess
import argparse
import json
from objectfile import ObjectFile    # A class to represent an object file

index = {}          # Symbols as keys and their location as value
objectFiles = []    # List of objects files included in the static lib

def getContent(ar_output):
    """Retrieve the files listed in the archive. For each file,
    create a new ObjectFile and add it to the global list of object files.
    """
    for filename in ar_output:
        objectFiles.append(ObjectFile(filename))

def buildIndex(nm_output):
    """Build the archive index from the output of nm."""
    for line in nm_output:
        if (line == ""):
            break
        elif (line != "Archive index:"):
            splittedLine = line.split()
            symbolName, objectFile = splittedLine[0], splittedLine[2]
            index[symbolName] = objectFile

def getDependencies(nm_output, filename):
    """List object files on which 'filename' depends on by searching for
    unresolved symbols in 'nm' output.
    """
    dependencies = set()    # Required object files
    unresLocal   = []       # Unresolved local (in the static lib) symbols
    unresGlobal  = []       # Unresolved global symbols

    # Get line number of the object file in nm output
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

def saveJSON(outfile):
    """Build the JSON from the object list then save it in a file."""
    objdict = {}
    for objectFile in objectFiles:
        attrdict = {}
        attrdict["Dependencies"]              = objectFile.getDependencies()
        attrdict["Unresolved local symbols"]  = objectFile.getUnresLocal()
        attrdict["Unresolved global symbols"] = objectFile.getUnresGlobal()
        objdict[objectFile.getFilename()] = attrdict

    with open(outfile, 'w') as out:
        json.dump(objdict, out, indent=4)

def main():
    """The main function."""
    # Parse the argument line
    parser = argparse.ArgumentParser(description="List the object file dependencies of a static library")
    parser.add_argument("slib", metavar="static_library",
                        help="the static library to analyze")
    parser.add_argument("-o", nargs=1, metavar="outfile",
                        help="the name of the output file (default: static_library.json)")
    slib    = parser.parse_args().slib    # The name of the static library
    outfile = parser.parse_args().o       # The name of the output file
    if (outfile == None):
        try:
            outfile = slib[:-2] + ".json" # "slib.json" by default
        except IndexError:
            outfile = "out.json"

    # Call "ar -t" on the static library, which lists its content
    try:
        ar_output = subprocess.check_output(["ar", "-t", slib]).decode()
    except subprocess.CalledProcessError:
        print("Could not execute 'ar -t {0}'".format(slib))
        return
    ar_output = ar_output.splitlines()
    getContent(ar_output)    # Create the list of object file

    # Call "nm -s" on the static library, which lists symbols and index of the archive
    try:
        nm_output = subprocess.check_output(["nm", "-s", slib]).decode()
    except subprocess.CalledProcessError:
        print("Could not execute 'nm -s {0}'".format(slib))
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
    saveJSON(outfile)


main()
