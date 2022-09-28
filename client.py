'''
Each menu type will extend MenuClient
'''


class MenuClient:

    def get_menu_page(self, page):
        # Each client type must implement this method
        raise NotImplementedError

    def get_menu(self,):
        # Gets full menu - paginating through all pages
        data, total_pages = self.get_menu_page(0)
        for page in range(1, total_pages):
            data.extend(self.get_menu_page(page)[0])
        return data
