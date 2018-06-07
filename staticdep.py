import subprocess
import argparse
import json

index       = {}    # Symbols as keys and their location as value
objectFiles = []    # List of objects files included in the static lib


class ObjectFile:
    """Define an object file by its name, its dependencies and its defined /
    unresolved local (located in the static library) and global symbols.
    """
    def __init__(self, filename):
        self.filename     = filename    # The name of the object file
        self.defined      = []          # List of defined symbols
        self.unresLocal   = []          # List of unresolved but local symbols
        self.unresGlobal  = []          # List of other unresolved symbols
        self.dependencies = []          # List of the required object files

    def getFilename(self):
        return self.filename

    def setDefined(self, defined):
        for res in defined:
            self.defined.append(res)

    def getDefined(self):
        return self.defined

    def setUnresLocal(self, unresLocal):
        for unres in unresLocal:
            self.unresLocal.append(unres)

    def getUnresLocal(self):
        return self.unresLocal

    def setUnresGlobal(self, unresGlobal):
        for unres in unresGlobal:
            self.unresGlobal.append(unres)

    def getUnresGlobal(self):
        return self.unresGlobal

    def setDependencies(self, dependencies):
        for dep in dependencies:
            self.dependencies.append(dep)

    def getDependencies(self):
        return self.dependencies

    def __str__(self):
        return self.filename

    def __repr__(self):
        return self.filename


def buildObjectFiles(ar_output):
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
        splittedLine = line.split()
        symbolName, objectFile = splittedLine[0], splittedLine[2]
        index[symbolName] = objectFile

def getSymbols(nm_output, filename):
    """List object files on which 'filename' depends on and defined and unresolved symbols
    by searching for symbols in 'nm' output for 'filename'.

    Keyword arguments:
    nm_output -- the output of 'nm'
    filename  -- the name of the object file to analyze

    Return a tuple with all elements necessary to finish building an ObjectFile object.
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

    # Retrieve all symbols defined by the given object file
    defined = [symbol for symbol in index.keys() if index[symbol] == filename]

    # Iterate over each symbol to search for unresolved ones (Type 'U')
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

    return (list(dependencies), defined, unresLocal, unresGlobal)

def saveJSON(slib, outfile):
    """Build the JSON from the object list then save it in a file.

    Keyword arguments:
    slib    -- the name of the static library
    outfile -- the path of the output file
    """
    maindct    = {}    # The main dictionnary holding filetype, library name and content
    contentdct = {}    # Content of the static library and their dependencies

    # Indicate that the JSON file is the result of a static library analysis
    maindct["slib_analysis"] = True
    # Save the name of the static library
    maindct["Static library"] = slib
    # Then for each object file, save dependencies and defined / unresolved symbols
    for objectFile in objectFiles:
        attrdict = {}
        attrdict["Dependencies"]              = objectFile.getDependencies()
        attrdict["Defined symbols"]           = objectFile.getDefined()
        attrdict["Unresolved local symbols"]  = objectFile.getUnresLocal()
        attrdict["Unresolved global symbols"] = objectFile.getUnresGlobal()
        if (any(attrdict.values())):    # If object file has any symbol
            contentdct[objectFile.getFilename()] = attrdict
        else:    # Else we mark it as EMPTY
            contentdct[objectFile.getFilename()] = "EMPTY"
    maindct["Content"] = contentdct

    # Write the JSON representation in a text file
    try:
        with open(outfile, 'w') as out:
            json.dump(maindct, out, indent=4)
            print("JSON result of '{0}' analysis saved in '{1}'".format(slib, outfile))
    except IOError as e:
        print("I/O error on '{0}': {1}".format(outfile, e.strerror))
        return

def printSummary(slib):
    """Print a summary of the analysis."""
    nbObj     = len(objectFiles)   # The number of object file
    # The longest name length to adjust spacing for aesthetic purpose
    maxLength = max([len(obj.getFilename()) for obj in objectFiles])
    maxLength = max(maxLength, len("OBJ_FILE"))

    print("\nSUMMARY OF ANALYSIS")
    print("The static library '{0}' contains {1} object files:".format(slib, nbObj))
    print("  OBJ_FILE" + " "*(maxLength - len("OBJ_FILE")) + " <- DEPENDENCIES")
    for objectFile in objectFiles:
        filename     = objectFile.getFilename()
        dependencies = objectFile.getDependencies()
        # Build the line to be printed
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
    parser = argparse.ArgumentParser(description=
                                     "List the object file dependencies of a static library")
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
            outfile = slib[:-2] + ".json" # "/.../slib.json" by default
        except IndexError:
            outfile = "out.json"

    # Call "ar -t" on the static library, which lists its content
    try:
        ar_output = subprocess.check_output(["ar", "-t", slib], stderr=subprocess.DEVNULL).decode()
    except subprocess.CalledProcessError as e:
        print("Could not execute '{0}'".format(' '.join(e.cmd)))
        return
    ar_output = ar_output.splitlines()
    buildObjectFiles(ar_output)    # Build the list of object file

    # Call "nm -s" on the static library, which lists symbols and index of the archive
    try:
        nm_output = subprocess.check_output(["nm", "-s", slib], stderr=subprocess.DEVNULL).decode()
    except subprocess.CalledProcessError as e:
        print("Could not execute '{0}'".format(' '.join(e.cmd)))
        return
    nm_output = nm_output.splitlines()[2:]    # Index starts at 2 to ignore a blank line and a header
    buildIndex(nm_output)    # Create the index which associates symbols to their location

    # Iterate over the object files to create associated lists
    for objectFile in objectFiles:
        dependencies, defined, unresLocal, unresGlobal = getSymbols(nm_output, objectFile.getFilename())
        objectFile.setDependencies(dependencies)
        objectFile.setDefined(defined)
        objectFile.setUnresLocal(unresLocal)
        objectFile.setUnresGlobal(unresGlobal)

    # Finally save the JSON in a file
    saveJSON(slib, outfile)

    # If the '-s' option is set, also print a summary of the analysis
    if (parser.parse_args().s):
        printSummary(slib)


main()
