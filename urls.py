from datetime import date

from views import BulletinBoard


# front controller(middlewares)
def date_front(request):
    request['date'] = date.today()


def hello_front(request):
    request['hello'] = 'hello from custom middleware'


fronts = [date_front, hello_front]

old_routes = {
    '/board/': BulletinBoard()
}
