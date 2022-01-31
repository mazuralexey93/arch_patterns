from datetime import date
from views import Index, AnotherPage, Contact, \
    BulletinBoard, GoodsList, CreateGood, CategoryList, \
    CreateCategory, CopyGood


# front controller(middlewares)

def date_front(request):
    request['date'] = date.today()


def hello_front(request):
    request['hello'] = 'hello from custom middleware'


fronts = [date_front, hello_front]

# urls
routes = {
    '/': Index(),
    '/another_page/': AnotherPage(),
    '/contact/': Contact(),
    '/board/': BulletinBoard(),
    '/goods-list/': GoodsList(),
    '/create-good/': CreateGood(),
    '/category-list/': CategoryList(),
    '/create-category/': CreateCategory(),
    '/copy-good/': CopyGood()
}
