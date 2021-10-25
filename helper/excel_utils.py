import xlwings

class A2Reader:
    def __init__(self, datasheet, rows):
        """
        Args:
            datasheet: Filepath to datasheet
            rows: Row number of last row with data
        """
        self.wb = xlwings.Book(datasheet)
        self.sheet = self.wb.sheets[0]
        self.rows = rows

        self.rowdict = {}
        pos_count = {'DF': 0, 'EF': 0, 'FH': 0, 'FG': 0}
        pos_tables = [5, 7, 8, 9]

        for row in range(1, self.rows + 1):
            curr_val = self.sheet.range(f'C{row}').value
            if curr_val in pos_count.keys():
                key = f'{curr_val}{pos_tables[pos_count[curr_val]]}'
                pos_count[curr_val] += 1
            else:
                key = curr_val

            self.rowdict[key] = row

    def keyrow(self, key: str, table=None):
        """
        Returns row by KEY in Column C of the datasheet

        Args:
            key: Key to search (non case-sensitive)

        Returns: Row number
        """

        return self.rowdict[f'{key.upper()}{"" if table is None else table}']
