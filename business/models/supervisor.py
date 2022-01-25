class SupervisedEntity:
    def __init__(self, supervisor):
        self.supervisor = supervisor
        supervisor.register(self)

    def rapport_errors(self):
        pass


class Supervisor:
    def __init__(self):
        self.errors = []
        self.success = []
        self.registered_entity = []

    def register(self, entity):
        self.registered_entity.append(entity)

    def identify_errors(self):
        self.errors = [error for entity in self.registered_entity for error in entity.rapport_errors()]

    def has_one_error_of(self, error_enum_cls):
        for error in self.errors:
            if isinstance(error, error_enum_cls):
                return True
        return False



