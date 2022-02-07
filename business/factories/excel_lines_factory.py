from business.factories.receipts import add_update_policy, OverwriteColumn
from business.models.excel_line import ExcelLine
from business.models.update_policy import UpdatePolicy


class ExcelLinesBuilder:
    def __init__(self, rows, receipt):
        self.excel_lines = []
        self.receipt = receipt
        self.rows = rows

    def clean_lines(self):
        self.excel_lines = list(filter(lambda l: l.sale_offer.product.principal_barcode is not None, self.excel_lines))

    def get_lines(self):
        return self.excel_lines

    def build(self):
        for row in self.rows:
            current_line = self.__build_line(row)
            if len(self.excel_lines) > 0:
                self.excel_lines = self.merge_duplicate(current_line)
            else:
                self.excel_lines.append(current_line)
        self.clean_lines()
        return self

    def __build_line(self, row):
        line = ExcelLine()
        for idx, column in enumerate(self.receipt):
            if isinstance(column, OverwriteColumn):
                column.set_from_default_value(line)
            else:
                column.set_from_excel(line, row[idx].value)
        line.supervisor.identify_errors()
        return line

    def merge_duplicate(self, current_line):
        return self.excel_lines + [current_line]


class LaboratoryExcelLinesBuilder(ExcelLinesBuilder):
    def __init__(self, rows, receipt):
        super().__init__(rows, receipt)
        self.receipt = add_update_policy(receipt, UpdatePolicy.PRODUCT_BARCODE)

    def merge_duplicate(self, current_line):
        last_line = self.excel_lines[-1]
        if last_line.sale_offer.should_merge(current_line.sale_offer):
            last_line.sale_offer.merge(current_line.sale_offer)
            return self.excel_lines[:-1] + [last_line]
        return self.excel_lines + [current_line]
