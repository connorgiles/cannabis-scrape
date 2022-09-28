import json
from buddi import BuddiClient
from dutchie import DutchieClient


def print_json(data):
    print(json.dumps(data, indent=2))


def print_buddi_menu(domain):
    print('Retrieving menu from', domain)
    client = BuddiClient(domain)
    menu = client.get_menu()
    assert len(menu) > 0
    print_json(menu)
    print('Found', len(menu), 'items')


def print_dutchie_menu(url):
    print('Retrieving menu from', url)
    client = DutchieClient(url=url)
    menu = client.get_menu()
    print_json(menu)
    print('Found', len(menu), 'items')


print_buddi_menu('https://bestcannabis.cc')

print_buddi_menu('https://www.theunderground.store')

print_dutchie_menu(
    'https://dutchie.com/embedded-menu/grasshopper-cannabis/products')

print_dutchie_menu(
    'https://dutchie.com/embedded-menu/cannabis-grey-bruce-owen-sound/products/')
