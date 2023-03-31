import re
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from requests_html import HTMLSession


def render_page(func):
    """ Decorator which renders JS code into HTML """

    def wrapper(*args, **kwargs):
        try:
            page = kwargs.get('page')
            additional_path = kwargs.get('additional_path') if kwargs.get('additional_path') else ''

            # Expecting response from page
            _response = HTMLSession().get(page + additional_path)

            # Since server returns any other status codes than 200
            # we have nothing to parse at all
            if _response.status_code == 200:
                # Since we absolutely sure that most of new age marketplaces
                # use JavaScript to "hide" html content from clientside based
                # scripts, we first of all should render page to get html content
                _response.html.render(timeout=20)
            else:
                return

            return func(*args, response_html=_response.html, page=page, additional_path=additional_path)
        except Exception as e:
            print(e)

    return wrapper


class ParsePage:
    """ Parsing page for links of particular item """

    def __init__(self,
                 desired_city: str = None,
                 desired_category: str = None,
                 desired_good: str = None
                 ) -> None:

        # If we want parse particular city
        self.desired_city = desired_city
        # If we want parse particular category
        self.desired_category = desired_category
        # If we want parse particular good
        self.desired_good = desired_good

    @render_page
    def get_links(self,
                  response_html: str,
                  additional_path: str = '',
                  page: str = '',
                  ) -> Optional[List] | None:
        """ Retrieves all categories included in page
            if desired_category has not been chosen """

        def get_links(page: str) -> Optional[List]:
            # Find all links belongs to page
            return list(filter(lambda link: additional_path in link, [link for link in response_html.links]))

        if not self.desired_category:
            try:
                return get_links(page)
            except Exception as e:
                print(e)
                return
        else:
            print(f'Desired category {self.desired_category} is chosen! Searching this particular category only!')
            try:
                return [link for link in get_links(page) if self.desired_category in link]
            except Exception as e:
                print(e)
                return


class RetrieveData:
    """ Retrieves data of particular good from page """

    def __init__(self,
                title: tuple,
                price: tuple,
                installment_price: tuple,
                installment_duration: tuple,
                rating: tuple,
                image: tuple,
                reviews: tuple,
                description: tuple,
                product_code: tuple,
                availability: tuple,
                ) -> None:
        """ Each object in __init__ must be tuple (xpath, attrs)
            no worries if there is no attrs """

        self.title = title
        self.price = price
        self.installment_price = installment_price
        self.installment_duration = installment_duration
        self.rating = rating
        self.image = image
        self.reviews = reviews
        self.description = description
        self.product_code = product_code
        self.availability = availability

    @render_page
    def get_data(self,
                 response_html: str,
                 additional_path: str = '',
                 page: str = '',
                 ) -> Optional[Dict]:

        # Collection of retrieved data from the page
        parsed_data = {
            'title': None,
            'price': None,
            'installment_price': None,
            'installment_duration': None,
            'rating': None,
            'image': None,
            'reviews': None,
            'description': None,
            'product_code': None,
            'availability': None,
        }

        def fill_collection(_key: str, _xpath: str, attrs: str = None) -> None:
            """ Retrieves data from particular element
                and stores it inside of hash table """

            # Initialize parsed data for particular element
            data = None

            # Could be a situation when we simply has no needed element on the page
            if not _xpath:
                return

            if not attrs:
                try:
                    # Get text only data
                    data = response_html.xpath(_xpath)[0].text

                except Exception as e:
                    print(e)
            else:
                try:
                    # Get attributes data
                    data = response_html.xpath(_xpath)[0].attrs[attrs]

                except Exception as e:
                    print(e)

            # If data successfully parsed let's add it to hash table
            if data:
                parsed_data[_key] = re.sub(r'[\xa0\n]', '', str(data))
            else:
                return

        # Fill hash table with all parsed data
        for _key, xpath_attrs in self.__dict__.items():
            if len(xpath_attrs) > 1:
                fill_collection(_key, xpath_attrs[0], xpath_attrs[1])
            else:
                fill_collection(_key, xpath_attrs[0])

        return parsed_data


# kaspi = ParsePage()
# print(kaspi.get_links('a', 'nav__el-link', page='https://kaspi.kz', additional_path='/shop'))
# print(kaspi.get_links(page='https://kaspi.kz/shop/rydniy/c/accessories%20for%20steadicams/?q=')
# for link in kaspi.get_links(page='https://kaspi.kz/shop/rydniy/c/categories/'):
#     print(link)

# technodom = ParsePage('https://www.technodom.kz')
# print(technodom.get_links('a', '', page='https://www.technodom.kz', additional_path='/catalog'))

# for link in kaspi.get_links(page='https://kaspi.kz/shop/rydniy/c/categories/'):
#     print(kaspi.get_links(page=link))

# Kaspi
r = RetrieveData(
    ('/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/h1',),
    ('/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[3]/div[1]/div[2]',),
    ('/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[3]/div[2]/div[2]',),
    ('/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[3]/div[2]/div[3]',),
    ('/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[2]/span', 'class'),
    ('/html/body/div[1]/div[5]/div/div[1]/div/div[1]/div/div[1]/div/div[1]/ul/li/div/img', 'src'),
    ('/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[2]/a',),
    ('/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[2]',),
    ('/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[1]',),
    ('',),
    )

print(r.get_data(page='https://kaspi.kz/shop/p/igrovoi-tsentr-lemengkeku-logarifmicheskaja-doska-mul-tikolor-102413320/?c=392410000#!/item'))

# Sulpak
r1 = RetrieveData(
    ('/html/body/main/div[1]/div[2]/h1',),
    ('/html/body/main/div[2]/div[2]/div[1]/div[1]/div/div/div[3]/div[2]/div[2]/div[1]/div[2]',),
    ('',),
    ('',),
    ('',),
    ('/html/body/main/div[2]/div[2]/div[1]/div[1]/div/div/div[2]/div[1]/div[3]/div[1]/a[1]/picture/img', 'src'),
    ('/html/body/main/div[2]/div[2]/div[1]/div[1]/div/div/div[3]/div[1]/div[1]',),
    ('/html/body/main/div[2]/div[2]/div[1]/div[1]/div/div/div[2]/div[2]/div/p[2]',),
    ('',),
    ('',),
)

print(r1.get_data(page='https://www.sulpak.kz/g/vstraivaemiye_duhoviye_shkafiy_hansa_boes684620/ust_kamenogorsk'))

# self.title = title
# self.price = price
# self.installment_price = installment_price
# self.installment_duration = installment_duration
# self.rating = rating
# self.image = image
# self.reviews = reviews
# self.description = description
# self.product_code = product_code
# self.availability = availability