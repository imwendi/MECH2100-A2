import xlwings

class A2Reader:
    def __init__(self, datasheet):
        """
        Args:
            datasheet: Filepath to datasheet
            rows: Row number of last row with data
        """
        self.wb = xlwings.Book(datasheet)
        self.sheet = self.wb.sheets[0]
        self.tabledict = {}

        # Populate tabledict
        tab_search_row = 2
        while len(self.tabledict) < 10:
            tab_search_val = self.sheet.range(f'D{tab_search_row}').value
            if tab_search_val is not None and tab_search_val in range(1, 11):
                new_tab_dict = {}
                key_search_row = tab_search_row + 1
                key_search_val = self.sheet.range(f'C{key_search_row}').value

                while key_search_val is not None and key_search_val != 'Table':
                    new_tab_dict[key_search_val] = key_search_row
                    key_search_row = key_search_row + 1
                    key_search_val = self.sheet.range(f'C{key_search_row}').value

                self.tabledict[tab_search_val] = new_tab_dict

            tab_search_row += 1

    def keyrow(self, key, table):
        """
        Returns row by KEY in Column C of the datasheet

        Args:
            key: Key to search (non case-sensitive)
            table: Table to search key in

        Returns: Row number
        """

        return self.tabledict[table][key.upper()]
