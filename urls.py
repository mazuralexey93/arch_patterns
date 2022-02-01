from datetime import date


# front controller(middlewares)
def date_front(request):
    request['date'] = date.today()


def hello_front(request):
    request['hello'] = 'hello from custom middleware'


fronts = [date_front, hello_front]
