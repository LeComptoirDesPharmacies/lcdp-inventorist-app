from business.models.errors import GetOrCreateLaboratoryError
from business.models.supervisor import SupervisedEntity


class Laboratory(SupervisedEntity):
    def __init__(self, supervisor):
        super().__init__(supervisor)
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

    def report_errors(self):
        errors = []
        if not self.name:
            errors.append(GetOrCreateLaboratoryError.INVALID_LABORATORY_NAME)
        return errors
