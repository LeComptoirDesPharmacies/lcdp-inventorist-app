class SupervisedEntity:
    def __init__(self, supervisor):
        self.supervisor = supervisor
        supervisor.register(self)

    def report_errors(self):
        pass


class Supervisor:
    def __init__(self):
        self._errors = []
        self.registered_entity = []

    def register(self, entity):
        self.registered_entity.append(entity)

    def identify_errors(self):
        self._errors = [error for entity in self.registered_entity for error in entity.report_errors()]

    def has_one_error_of(self, error_enum_cls):
        for error in self.errors:
            if isinstance(error, error_enum_cls):
                return True
        return False

    @property
    def errors(self):
        return self._errors

    @property
    def readable_errors(self):
        return repr([error.value for error in self._errors])


