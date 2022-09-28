import requests
import json

from menu import MenuClient

# GraphQL query template
# see: https://graphql.org/
GQL_FILTERED_PRODUCTS = """
query FilteredProducts($productsFilter: productsFilterInput!, $page: Int, $perPage: Int) {
  filteredProducts(filter: $productsFilter, page: $page, perPage: $perPage) {
    products {
      ...consumerBaseProductFragment
      brand {
        id
        _id
        description
        imageUrl
        name
        __typename
      }
      popularSortKey
      cannabinoidsV2 {
        value
        unit
        cannabinoid {
          name
          __typename
        }
        __typename
      }
      __typename
    }
    queryInfo {
      totalCount
      totalPages
      __typename
    }
    __typename
  }
}
fragment consumerBaseProductFragment on Products {
  _id
  id
  AdditionalOptions
  brandId
  brandName
  description
  effects
  CBD
  CBDContent {
    unit
    range
    __typename
  }
  comingSoon
  createdAt
  DispensaryID
  enterpriseProductId
  Image
  images {
    url
    description
    active
    __typename
  }
  imgixSettings {
    productCard {
      border
      mark
      markscale
      markpad
      fit
      __typename
    }
    productModal {
      border
      mark
      markscale
      markpad
      fit
      __typename
    }
    __typename
  }
  measurements {
    netWeight {
      unit
      values
      __typename
    }
    volume {
      unit
      values
      __typename
    }
    __typename
  }
  medicalOnly
  medicalPrices
  medicalSpecialPrices
  wholesalePrices
  Name
  nonArmsLength
  Options
  limitsPerCustomer {
    key
    value
    __typename
  }
  manualInventory {
    option
    inventory
    __typename
  }
  POSMetaData {
    canonicalID
    canonicalBrandName
    children {
      option
      quantity
      quantityAvailable
      kioskQuantityAvailable
      standardEquivalent {
        value
        unit
        __typename
      }
      recEquivalent {
        value
        unit
        __typename
      }
      __typename
    }
    __typename
  }
  Prices
  pricingTierData {
    generatedTiersId
    tiersId
    tiersName
    tiers {
      startWeight
      endWeight
      price
      pricePerGram
      weightUOM
      __typename
    }
    __typename
  }
  recOnly
  recPrices
  recSpecialPrices
  special
  specialData {
    bogoSpecials {
      bogoConditionLogicOperator
      bogoConditions {
        _id
        brandId
        brandIds
        brandName
        brandNames
        categoryIds
        categoryName
        categoryNames
        enterpriseProductId
        productGroup
        productId
        productIds
        quantity
        selectedCategoriesAndSubcategories
        subcategoryIds
        subcategoryNames
        weight
        weightOperator
        __typename
      }
      bogoRewardLogicOperator
      bogoRewards {
        _id
        brandId
        brandIds
        brandName
        brandNames
        categoryIds
        categoryName
        categoryNames
        dollarDiscount
        enterpriseProductId
        productGroup
        productId
        productIds
        percentDiscount
        quantity
        selectedCategoriesAndSubcategories
        subcategoryIds
        subcategoryNames
        targetPrice
        weight
        __typename
      }
      discountToCart {
        _id
        enabled
        discountType
        value
        __typename
      }
      discountBehavior
      discountStacking
      discountPrecedence
      endStamp
      excludedProducts {
        conditions {
          _id
          key
          Name
          __typename
        }
        rewards {
          _id
          key
          Name
          __typename
        }
        __typename
      }
      isRecurring
      itemsForAPrice {
        _id
        enabled
        value
        __typename
      }
      menuType
      recurringEndDate
      redemptionLimit
      specialId
      specialName
      stackingBehavior
      totalQuantity {
        enabled
        maxQuantity
        quantity
        quantityOperator
        __typename
      }
      totalWeight {
        enabled
        weight
        weightOperator
        __typename
      }
      totalSpend {
        enabled
        maximumSpend
        minimumSpend
        spendOperator
        __typename
      }
      qualifyingOptions
      __typename
    }
    saleSpecials {
      discount
      discountStacking
      menuType
      percentDiscount
      source
      sourceId
      specialId
      specialName
      specialRestrictions
      stackingBehavior
      stackingMode
      targetPrice
      __typename
    }
    __typename
  }
  Status
  strainType
  subcategory
  THC
  THCContent {
    unit
    range
    __typename
  }
  type
  vapeTaxApplicable
  weight
  featured {
    current
    startTime
    endTime
    __typename
  }
  isBelowThreshold
  isBelowKioskThreshold
  optionsBelowThreshold
  optionsBelowKioskThreshold
  cName
  pastCNames
  brandLogo
  bottleDepositTaxCents
  __typename
}
"""


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
            "query": GQL_FILTERED_PRODUCTS
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
