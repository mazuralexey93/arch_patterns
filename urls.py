from datetime import date
from views import Index, AnotherPage, Contact


# front controller(middlewares)

def date_front(request):
    request['date'] = date.today()


def hello_front(request):
    request['hello'] = 'hello'


fronts = [date_front, hello_front]

# urls
routes = {
    '/': Index(),
    '/another_page/': AnotherPage(),
    '/contact/': Contact(),
}
