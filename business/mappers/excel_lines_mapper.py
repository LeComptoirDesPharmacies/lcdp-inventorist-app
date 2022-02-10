from business.mappers.excel_mapper import parameter_mapper, create_laboratory_sale_offer_mapper, add_update_policy, \
    create_update_product_mapper
from business.models.excel_line import ExcelLine
from business.models.excel_parameter import ExcelParameter
from business.models.update_policy import UpdatePolicy
from business.services.excel import excel_to_dict
from business.utils import ConditionalDict


class ExcelLinesMapper:
    def __init__(self, excel_path, excel_mapper):
        self._excel_mapper = excel_mapper
        self.excel_path = excel_path
        self.parameters = None
        self.unique_key = None

    def get_parameters(self):
        if not self.parameters:
            self.parameters = excel_to_dict(
                obj_class=ExcelParameter,
                excel_path=self.excel_path,
                excel_mapper=parameter_mapper,
                sheet_name="Parametre",
                header_row=1,
                min_row=2,
                max_row=2
            ).get(0, None)
        return self.parameters

    @property
    def excel_mapper(self):
        return self._excel_mapper

    def map_to_obj(self):
        parameters = self.get_parameters()
        return list(excel_to_dict(
            obj_class=ExcelLine,
            excel_path=self.excel_path,
            excel_mapper=self.excel_mapper,
            sheet_name=parameters.sheet_name,
            header_row=parameters.header_line,
            min_row=parameters.content_start_line,
            obj_unique_key=self.unique_key,
            custom_dict=ConditionalDict(
                condition_func=self.condition,
                before_insert_func=self.before_insert,
                merge_func=self.merge
            )
        ).values())

    @staticmethod
    def condition(key, value):
        return key is not None

    @staticmethod
    def before_insert(key, value):
        value.supervisor.identify_errors()
        return value

    @staticmethod
    def merge(key, old_obj, new_obj):
        return new_obj


class LaboratoryExcelLinesMapper(ExcelLinesMapper):
    def __init__(self, excel_path):
        super().__init__(excel_path, create_laboratory_sale_offer_mapper)
        self.unique_key = "sale_offer.product.principal_barcode"

    @staticmethod
    def merge(key, old_obj, new_obj):
        if old_obj.sale_offer.should_merge(new_obj.sale_offer):
            old_obj.sale_offer.merge(new_obj.sale_offer)
            return old_obj
        return new_obj


class ProductExcelLinesMapper(ExcelLinesMapper):
    def __init__(self, excel_path):
        super().__init__(excel_path, create_update_product_mapper)
        self.unique_key = "sale_offer.product.principal_barcode"
