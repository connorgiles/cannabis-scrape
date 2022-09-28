class MenuClient:
    def get_menu_page(self, page):
        raise NotImplementedError

    def get_menu(self,):
        data, total_pages = self.get_menu_page(0)
        for page in range(1, total_pages):
            data.extend(self.get_menu_page(page)[0])
        return data
