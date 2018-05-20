import subprocess
import argparse
import json
from objectfile import ObjectFile

index = {}
objectFiles = []

def buildIndex(nm_output):
    """Build the archive index from the output of nm."""

    # Isolate the archive index and add symbols and their location to the index
    for line in nm_output:
        if (line == ""):
            break
        elif (line != "Archive index:"):
            splittedLine = line.split()
            symbolName, objectFile = splittedLine[0], splittedLine[2]
            index[symbolName] = objectFile

def getContent(ar_output):
    """Retrieve the files listed in the archive. For each file,
    create a new ObjectFile and add it to the global list of object files.
    """
    for filename in ar_output:
        objectFiles.append(ObjectFile(filename))

def getDependencies(nm_output, filename):
    dependencies = set()
    unresolved   = set()

    try:
        i0 = nm_output.index(filename + ":")
    except ValueError:
        print("Symbol {0} was not found!".format(filename))
        return

    for line in nm_output[i0 + 1:]:
        if (line == ""):
            break
        splittedLine = line.split()
        symbolType, symbolName = splittedLine[-2], splittedLine[-1]
        if (symbolType == 'U'):
            unresolved.add(symbolName)
            if (symbolName in index):
                dependencies.add(index[symbolName])

    return (list(unresolved), list(dependencies))

def saveJSON(outfile):
    objdict = {}
    for objectFile in objectFiles:
        attrdict = {}
        attrdict["Dependencies"]          = objectFile.getDependencies()
        attrdict["Unresolved symbols"]    = objectFile.getUnresolved()
        objdict[objectFile.getFilename()] = attrdict

    with open(outfile, 'w') as out:
        json.dump(objdict, out, sort_keys=True, indent=4)

def main():
    parser = argparse.ArgumentParser(description="List the object file dependencies of a static library")
    parser.add_argument("slib", metavar="static_library",
                        help="the static library to analyze")
    parser.add_argument("-o", nargs=1, metavar="outfile",
                        help="the name of the output file (default: static_library.json)")
    slib    = parser.parse_args().slib
    outfile = parser.parse_args().o
    if (outfile == None):
        try:
            outfile = slib[:-2] + ".json"
        except IndexError:
            outfile = "out.json"

    # Call "ar -t" on the static library, which lists its content
    try:
        ar_output = subprocess.check_output(["ar", "-t", slib]).decode()
    except subprocess.CalledProcessError:
        print("Could not execute 'ar -t {0}'".format(slib))
        return
    ar_output = ar_output.splitlines()
    getContent(ar_output)

    # Call "nm -s" on the static library, which lists symbols and index of the archive
    try:
        nm_output = subprocess.check_output(["nm", "-s", slib]).decode()
    except subprocess.CalledProcessError:
        print("Could not execute 'nm -s {0}'".format(slib))
        return
    nm_output = nm_output.splitlines()[1:]
    buildIndex(nm_output)

    for objectFile in objectFiles:
        unresolved, dependencies = getDependencies(nm_output, objectFile.getFilename())
        objectFile.setUnresolved(unresolved)
        objectFile.setDependencies(dependencies)

    saveJSON(outfile)

main()
