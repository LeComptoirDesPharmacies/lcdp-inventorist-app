from business.models.excel_line import ExcelLine


class ExcelLineBuilder:
    def __init__(self, rows, receipt):
        self.excel_lines = []
        self.receipt = receipt
        self.rows = rows

    def __build_line(self, row):
        line = ExcelLine()
        for key, func in self.receipt.items():
            func(line, row[key].value)
        line.supervisor.identify_errors()
        return line

    def get_lines(self):
        return self.excel_lines

    def build(self):
        for row in self.rows:
            current_line = self.__build_line(row)
            if len(self.excel_lines) > 0:
                excel_lines = self.merge_duplicate(current_line)
                self.excel_lines = excel_lines
            else:
                self.excel_lines.append(current_line)
        return self

    def merge_duplicate(self, current_line):
        last_line = self.excel_lines[-1]
        if last_line.sale_offer.should_merge(current_line.sale_offer):
            last_line.sale_offer.merge(current_line.sale_offer)
            return self.excel_lines[:-1] + [last_line]
        return self.excel_lines[:-1] + [last_line, current_line]
