import requests
import json

from client import MenuClient


def get_dispensaries_for_slug(slug):
    return requests.get('https://dutchie.com/graphql', params={
        'operationName': 'ConsumerDispensaries',
        'variables': '{"dispensaryFilter":{"cNameOrID":"' + slug + '"}}',
        'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"405bec55de9825fce25977e552b394dd8ca8941b9be721e2186456851c450033"}}',
    }, ).json().get('data').get('filteredDispensaries')


def get_dispensary_id_for_slug(slug):
    return get_dispensaries_for_slug(slug)[0].get('id')


def slug_from_url(url):
    return url.split('embedded-menu/')[1].split('/')[0]


# Read GraphQL query template
# learn more: https://graphql.org/
def read_gql_query(name):
    with open('./gql/dutchie/' + name+'.gql') as f:
        return f.read()


class DutchieClient(MenuClient):
    def __init__(self, slug=None, url=None, id=None):
        if id is not None:
            self.dispensary_id = id
        elif slug is not None:
            self.dispensary_id = get_dispensary_id_for_slug(slug)
        elif url is not None:
            slug = slug_from_url(url)
            self.dispensary_id = get_dispensary_id_for_slug(slug)
        else:
            raise ValueError(
                'Must provide a id, slug, or url')

        self.session = requests.Session()

    def get_menu_page(self, page=0, per_page=100):
        # Dutchie chose to use GraphQL for their API
        # Which is not great for public API consumption
        # But it works and allows us to reference nested structures
        result = self.session.post("https://dutchie.com/graphql", None, {
            "operationName": "FilteredProducts",
            "variables": {
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
                "page": page,
                "perPage": per_page
            },
            "query": read_gql_query('get_filtered_products')
        }).json()

        data = result.get('data').get('filteredProducts').get('products')
        total_pages = result.get('data').get(
            'filteredProducts').get('queryInfo').get('totalPages')

        return data, total_pages

    def get_menu(self):
        data, total_pages = self.get_menu_page(0)
        for page in range(1, total_pages):
            data.extend(self.get_menu_page(page)[0])
        return data


# can use any of the 3 options
# will get ID from slug or url under the hood
GRASSHOPPER_DISPENSARY_ID = "616ef8771f58c900a352b56b"
GRASSHOPPER_DISPENSARY_SLUG = "grasshopper-cannabis"
GRASSHOPPER_DISPENSARY_URL = "https://dutchie.com/embedded-menu/grasshopper-cannabis/products"

GREY_BRUCE_URL = 'https://dutchie.com/embedded-menu/cannabis-grey-bruce-owen-sound/products'

client = DutchieClient(url=GRASSHOPPER_DISPENSARY_URL)
print(json.dumps(client.get_menu(), indent=2))
