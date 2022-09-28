import requests

from client import MenuClient


def slug_from_url(url):
    """Extracts the slug from a dutchie url"""
    return url.split('embedded-menu/')[1].split('/')[0]


# Read GraphQL query template
# learn more: https://graphql.org/
def read_gql_query(name):
    """Reads a GraphQL query from a local file"""
    with open('./gql/dutchie/' + name+'.gql') as f:
        return f.read()


class DutchieClient(MenuClient):
    def __init__(self, slug=None, url=None, id=None):
        """Accepts a slug, url, or dispensary id"""
        self.session = requests.Session()

        if id is not None:
            self.dispensary_id = id
        elif slug is not None:
            self.dispensary_id = self.get_dispensary_id_for_slug(slug)
        elif url is not None:
            slug = slug_from_url(url)
            self.dispensary_id = self.get_dispensary_id_for_slug(slug)
        else:
            raise ValueError(
                'Must provide a id, slug, or url')

    def get_dispensaries_for_slug(self, slug):
        """Gets the dispensaries for a slug from Dutchie's API"""
        return self.session.get('https://dutchie.com/graphql', params={
            'operationName': 'ConsumerDispensaries',
            'variables': '{"dispensaryFilter":{"cNameOrID":"' + slug + '"}}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"405bec55de9825fce25977e552b394dd8ca8941b9be721e2186456851c450033"}}',
        }, ).json().get('data').get('filteredDispensaries')

    def get_dispensary_id_for_slug(self, slug):
        """Gets the dispensary id for a slug"""
        return self.get_dispensaries_for_slug(slug)[0].get('id')

    def get_menu_page(self, page):
        # Dutchie chose to use GraphQL for their API
        # Which is not great for public API consumption
        # But it works and allows us to reference nested structures

        request = {
            "operationName": "FilteredProducts",
            "query": read_gql_query('get_filtered_products'),
            "variables": {
                "page": page,
                "perPage": 100,
                "productsFilter": {
                    "dispensaryId": self.dispensary_id,
                    "pricingType": "rec",
                    "strainTypes": [],
                    "subcategories": [],
                    "Status": "Active",
                    "types": [],
                    "useCache": False,
                    "sortDirection": 1,
                    "sortBy": None,
                    "isDefaultSort": True,
                    "bypassOnlineThresholds": False,
                    "isKioskMenu": False,
                    "removeProductsBelowOptionThresholds": True
                },
            },
        }

        result = self.session.post(
            "https://dutchie.com/graphql", None, request)

        filtered_products = result.json().get('data').get('filteredProducts')

        data = filtered_products.get('products')
        total_pages = filtered_products.get('queryInfo').get('totalPages')

        return data, total_pages
