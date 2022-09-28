import requests
import urllib.parse

from client import MenuClient


def get_token(domain):
    url_encoded_domain = urllib.parse.quote_plus(domain)
    request_url = 'https://app.buddi.io/ropis/auth/get-token?domain=' + url_encoded_domain
    return requests.get(request_url).json().get('token')


class BuddiClient(MenuClient):
    def __init__(self, domain):
        self.domain = domain
        # Buddi has a token where the subject is the domain name 🤔
        self.token = get_token(domain)
        self.session = requests.Session()
        self.session.headers.update(
            {
                # make it look like we're the client to be authorized
                'authority': 'app.buddi.io',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9',
                'authorization': 'Bearer ' + self.token,
                'authorization-domain': domain,
                'origin': domain,
                'referer': domain,
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
                'utc-mins-offset': '-240',
            })

    def get_menu_page(self, page):
        result = self.session.get(
            # buddi starts their page at 1 - let's be consistent with 0
            'https://app.buddi.io/ropis/menu?page=' + str(page + 1)).json()

        # the last page is the total number of pages given
        # buddi starts their page at 1 - no need to adjust
        # for our desired interface of (data, page_count)
        total_pages = result.get('last_page')

        return result.get('data'), total_pages
