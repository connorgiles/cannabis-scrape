class MenuClient:
    """An abstract class for menu clients"""

    def get_menu_page(self, page):
        """
        Each client type must implement this method.

        Requires a page number to return the data and total pages in an enum.
        """
        raise NotImplementedError

    def get_menu(self,):
        """Gets full menu - paginating through all pages"""
        data, total_pages = self.get_menu_page(0)
        for page in range(1, total_pages):
            data.extend(self.get_menu_page(page)[0])
        return data
