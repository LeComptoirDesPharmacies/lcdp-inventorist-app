class Laboratory:
    def __init__(self):
        self._id = None
        self._name = None

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, laboratory_id):
        self._id = laboratory_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

