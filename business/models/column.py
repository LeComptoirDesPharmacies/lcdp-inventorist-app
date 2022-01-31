from business.utils import rsetattr, rgetattr


class Column:
    def __init__(self, excel_column_name, class_path):
        self.excel_column_name = excel_column_name
        self.class_path = class_path

    def set_from_excel(self, obj, value):
        rsetattr(obj, self.class_path, value)

    def get_from_obj(self, obj):
        return rgetattr(obj, self.class_path)


class OverwriteColumn(Column):
    def __init__(self, excel_column_name, class_path, value):
        super().__init__(excel_column_name, class_path)
        self.value = value

    def set_from_default_value(self, obj):
        rsetattr(obj, self.class_path, self.value)
