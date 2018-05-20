class ObjectFile:
    def __init__(self, filename):
        self.filename     = filename
        self.unresolved   = []
        self.dependencies = []

    def getFilename(self):
        return self.filename

    def setUnresolved(self, unresolved):
        for unres in unresolved:
            self.unresolved.append(unres)

    def getUnresolved(self):
        return self.unresolved

    def setDependencies(self, dependencies):
        for dep in dependencies:
            self.dependencies.append(dep)

    def getDependencies(self):
        return self.dependencies

    def __str__(self):
        return self.filename

    def __repr__(self):
        return self.filename
