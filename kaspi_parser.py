import requests
import requests_html
from bs4 import BeautifulSoup
from requests_html import HTMLSession


def render_page(func):
    """ Decorator which renders JS code into HTML """

    def wrapper(*args, **kwargs):
        try:
            page = kwargs.get('page')
            additional_path = kwargs.get('additional_path')

            if not additional_path:
                additional_path = ''

            print(page, additional_path)

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

            return func(*args, response_html=_response.html.html, page=page, additional_path=additional_path)
        except Exception as e:
            print(e)

    return wrapper


class ParsePage:
    """ Parsing page for links of particular item """

    def __init__(self,
                 target_page: str,
                 parser: BeautifulSoup = BeautifulSoup,
                 desired_city: str = None,
                 desired_category: str = None,
                 desired_good: str = None
                 ) -> None:

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
    def get_links(self,
                  tag_name: str,
                  class_name: str,
                  response_html: str,
                  additional_path: str = '',
                  page: str = '',
                  ) -> list | None:
        """ Retrieves all categories included in page
            if desired_category has not been chosen """

        print(page)

        def get_links(page: str) -> list:
            # If page is rendered successfully we can try to get data from it
            content = self._parser(response_html, 'html.parser')

            # Find all links belongs to all categories
            relative_links = [_object['href'] for _object in content.findAll(tag_name, class_=class_name, href=True)]

            # Suppose we have some additional directories on server
            # like www.store.com/shop -> "/shop" is an additional part
            if not additional_path:
                page = page + additional_path

            # Create absolute links
            absolute_links = list(
                filter(lambda link: additional_path in link, map(lambda link: page + link, relative_links)))

            return absolute_links

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

kaspi = ParsePage('https://kaspi.kz')
# print(kaspi.get_links('a', 'nav__el-link', page='https://kaspi.kz', additional_path='/shop'))
print(kaspi.get_links('div', 'card__name', page='https://kaspi.kz/shop/c/tv_audio/'))

# technodom = ParsePage('https://www.technodom.kz')
# print(technodom.get_links('a', '', page='https://www.technodom.kz', additional_path='/catalog'))
