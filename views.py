from patterns.creational_patterns import Engine, Logger, Category
from my_framework.templator import render

site = Engine()
logger = Logger('main')


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.categories)


class Contact:
    def __call__(self, request):
        return '200 OK', render('contact.html', hello=request.get('hello', None))


class AnotherPage:
    def __call__(self, request):
        return '200 OK', render('another_page.html')


class BulletinBoard:
    def __call__(self, request):
        return '200 OK', render('board.html')


class NotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


class GoodsList:
    def __call__(self, request):
        logger.log('Список товаров')
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('goods_list.html',
                                    objects_list=category.goods,
                                    name=category.name,
                                    id=category.id)
        except KeyError:
            return '200 OK', 'No goods have been added yet'


class CreateGood:
    category_id = -1

    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            name = data['name']
            name = site.decode_value(name)
            category = None

            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))
                good = site.create_good('car', name, category)
                site.goods.append(good)

            return '200 OK', render('goods_list.html',
                                    objects_list=category.goods,
                                    name=category.name,
                                    id=category.id)
        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))
                return '200 OK', render('create_good.html',
                                        name=category.name,
                                        id=category.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


class CopyGood:
    def __call__(self, request):
        request_params = request['request_params']
        new_good = ''

        try:
            name = request_params['name']
            existing_good = site.get_good(name)
            if existing_good:
                new_name = f'copy_{name}'
                new_good = existing_good.clone()
                new_good.name = new_name
                site.goods.append(new_good)
            return '200 OK', render('goods_list.html',
                                    objects_list=site.goods,
                                    name=new_good.category.name)

        except KeyError:
            return '200 OK', 'No goods have been added yet'


class CreateCategory:
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            name = data['name']
            name = site.decode_value(name)
            category_id = data.get('category_id')
            category = None

            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)
            site.categories.append(new_category)

            return '200 OK', render('index.html', objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('create_category.html', categories=categories)


class CategoryList:
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html', objects_list=site.categories)


