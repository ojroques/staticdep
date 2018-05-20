class ObjectFile:
    """Define an object file by its name, its dependencies and its unresolved
    local (located in the static library) and global symbols.
    """
    def __init__(self, filename):
        self.filename     = filename    # The name of the object file
        self.unresLocal   = []          # List of unresolved but local symbols
        self.unresGlobal  = []          # List of other unresolved symbols
        self.dependencies = []          # List of the required object files

    def getFilename(self):
        return self.filename

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
