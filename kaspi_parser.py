import requests_html
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
                  ) -> list | None:
        """ Retrieves all categories included in page
            if desired_category has not been chosen """

        def get_links(page: str) -> list:
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
                title_xpath: str,
                price_xpath: str,
                instatement_price_xpath: str,
                instatement_duration_xpath: str,
                rating_xpath: str,
                image_xpath: str,
                reviews_xpath: str,
                description_xpath: str,
                product_code_xpath: str,
                ) -> None:

        self.title_xpath = title_xpath
        self.price_xpath = price_xpath
        self.instatement_price_xpath = instatement_price_xpath
        self.instatement_duration_xpath = instatement_duration_xpath
        self.rating_xpath = rating_xpath
        self.image_xpath = image_xpath
        self.reviews_xpath = reviews_xpath
        self.description_xpath = description_xpath
        self.product_code_xpath = product_code_xpath

    @render_page
    def get_data(self,
                 response_html: str,
                 additional_path: str = '',
                 page: str = '',
                 ):

        title = response_html.xpath(self.title_xpath)[0].text
        print(title)
        price = response_html.xpath(self.price_xpath)[0].text
        print(price)
        instatement_price = response_html.xpath(self.instatement_price_xpath)[0].text
        print(instatement_price)
        instatement_duration = response_html.xpath(self.instatement_duration_xpath)[0].text
        print(instatement_duration)
        rating = response_html.xpath(self.rating_xpath)[0].attrs['class']
        print(rating)
        image = response_html.xpath(self.image_xpath)[0].attrs['src']
        print(image)
        reviews = response_html.xpath(self.reviews_xpath)[0].text
        print(reviews)
        description = response_html.xpath(self.description_xpath)[0].text
        print(description)
        product_code = response_html.xpath(self.product_code_xpath)[0].text
        print(product_code)


# kaspi = ParsePage()
# print(kaspi.get_links('a', 'nav__el-link', page='https://kaspi.kz', additional_path='/shop'))
# print(kaspi.get_links(page='https://kaspi.kz/shop/rydniy/c/accessories%20for%20steadicams/?q=')
# for link in kaspi.get_links(page='https://kaspi.kz/shop/rydniy/c/categories/'):
#     print(link)

# technodom = ParsePage('https://www.technodom.kz')
# print(technodom.get_links('a', '', page='https://www.technodom.kz', additional_path='/catalog'))

# for link in kaspi.get_links(page='https://kaspi.kz/shop/rydniy/c/categories/'):
#     print(kaspi.get_links(page=link))

r = RetrieveData(title_xpath='/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/h1',
                 price_xpath='/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[3]/div[1]/div[2]',
                 instatement_price_xpath='/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[3]/div[2]/div[2]',
                 instatement_duration_xpath='/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[3]/div[2]/div[3]',
                 rating_xpath='/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[2]/span',
                 image_xpath='/html/body/div[1]/div[5]/div/div[1]/div/div[1]/div/div[1]/div/div[1]/ul/li/div/img',
                 reviews_xpath='/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[2]/a',
                 description_xpath='/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[2]',
                 product_code_xpath='/html/body/div[1]/div[5]/div/div[1]/div/div[2]/div/div[1]/div[1]',
                 )

r.get_data(page='https://kaspi.kz/shop/p/igrovoi-tsentr-lemengkeku-logarifmicheskaja-doska-mul-tikolor-102413320/?c=392410000#!/item')