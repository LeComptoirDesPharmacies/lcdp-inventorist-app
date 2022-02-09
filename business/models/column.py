from business.utils import rsetattr, rgetattr


class Column:
    def __init__(self, excel_column_name, class_path, default_value=None):
        self.excel_column_name = excel_column_name
        self.class_path = class_path
        self.default_value = default_value

    def set_from_excel(self, obj, value):
        if value is not None:
            rsetattr(obj, self.class_path, value)
        elif self.default_value is not None:
            rsetattr(obj, self.class_path, self.default_value)

    def get_from_obj(self, obj):
        return rgetattr(obj, self.class_path)
