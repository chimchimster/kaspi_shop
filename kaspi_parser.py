import requests_html
from bs4 import BeautifulSoup
from requests import Response
from requests_html import HTMLSession


def render_page(func):
    """ Decorator which renders JS code into HTML """

    def wrapper(*args, **kwargs):
        try:
            page = kwargs.get('page')

            # Expecting response from page
            _response = HTMLSession().get(page)

            # Since server returns any other status codes than 200
            # we have nothing to parse at all
            if _response.status_code == 200:
                # Since we absolutely sure that most of new age marketplaces
                # use JavaScript to "hide" html content from clientside based
                # scripts, we first of all should render page to get html content
                _response.html.render()
            else:
                return

            return func(*args, response_html=_response.html.html, page=page)
        except Exception as e:
            print(e)

    return wrapper


class MainPage:
    """ Parsing main page for links of particular category """

    def __init__(self,
                 main_page: str,
                 target_page: str,
                 parser: BeautifulSoup = BeautifulSoup,
                 desired_city: str = 'rudniy',
                 desired_category: str = None,
                 desired_good: str = None
                 ) -> None:

        # Apply main page
        self.main_page = main_page
        # Apply target page
        self.target_page = target_page
        # If we want parse particular city
        self.desired_city = desired_city
        # If we want parse particular category
        self.desired_category = desired_category
        # If we want parse particular good
        self.desired_good = desired_good
        # Apply parser
        self._parser = parser

    @render_page
    def get_links_of_cateogies(self, tag_name: str, class_name: str, response_html: str, page: str = None) -> list | None:
        """ Retrieves all categories included in page
            if desired_category has not been chosen """

        if not self.desired_category:
            try:
                # If page is rendered successfully we can try to get data from it
                content = self._parser(response_html, 'html.parser')

                # Find all links belongs to all categories
                relative_links = [_object['href'] for _object in content.findAll(tag_name, class_=class_name, href=True)]

                # Create absolute links
                absolute_links = list(map(lambda link: page + link, relative_links))

                return absolute_links
            except Exception as e:
                print(e)
                return
        else:
            return self.get_link_of_category()

    def get_link_of_category(self, ):
        pass


m = MainPage('https://kaspi.kz', 'https://kaspi.kz/shop')
print(m.get_links_of_cateogies('a', 'nav__el-link', page='https://kaspi.kz/shop'))

# session = requests_html.HTMLSession()
# response = session.get('https://kaspi.kz/shop/')
# print(response.status_code)
# response.html.render()
#
# soup = BeautifulSoup(response.html.html, 'html.parser')
#
# x = soup.findAll('a', class_='nav__el-link', href=True)
#
# for i in x:
#     print(i['href'])
