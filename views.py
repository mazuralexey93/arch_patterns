from patterns.creational_patterns import Engine, Logger, MapperRegistry
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import EmailNotifier, SmsNotifier, ListView, CreateView, BaseSerializer
from patterns.architectural_system_patterns import UnitOfWork
from my_framework.templator import render

site = Engine()
logger = Logger('main')
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

routes = {}


@AppRoute(routes=routes, url='/')
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None), objects_list=site.categories)


@AppRoute(routes=routes, url='/contact/')
class Contact:
    @Debug(name='Contact')
    def __call__(self, request):
        return '200 OK', render('contact.html', hello=request.get('hello', None))


@AppRoute(routes=routes, url='/another_page/')
class AnotherPage:
    @Debug(name='AnotherPage')
    def __call__(self, request):
        return '200 OK', render('another_page.html')


# @AppRoute(routes=routes, url='/board/')
class BulletinBoard:
    def __call__(self, request):
        return '200 OK', render('board.html')


class NotFound404:
    @Debug(name='NotFound404')
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


@AppRoute(routes=routes, url='/goods-list/')
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


@AppRoute(routes=routes, url='/create-good/')
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
                good = site.create_good('simple_good', name, category)
                good.observers.append(email_notifier)
                good.observers.append(sms_notifier)
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


@AppRoute(routes=routes, url='/copy-good/')
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


@AppRoute(routes=routes, url='/create-category/')
class CreateCategory:
    @Debug(name='CreateCategory')
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


@AppRoute(routes=routes, url='/category-list/')
class CategoryList:
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html', objects_list=site.categories)


@AppRoute(routes=routes, url='/buyers-list/')
class BuyerListView(ListView):
    template_name = 'buyers_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('buyer')
        return mapper.all()


@AppRoute(routes=routes, url='/create-buyer/')
class BuyerCreateView(CreateView):
    template_name = 'create_buyer.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('buyer', name)
        site.buyers.append(new_obj)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()


@AppRoute(routes=routes, url='/add-buyer/')
class AddBuyerByGoodCreateView(CreateView):
    template_name = 'add_buyer.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['goods'] = site.goods
        context['buyers'] = site.buyers
        return context

    def create_obj(self, data: dict):
        good_name = data['good_name']
        good_name = site.decode_value(good_name)
        good = site.get_good(good_name)
        buyer_name = data['buyer_name']
        buyer_name = site.decode_value(buyer_name)
        buyer = site.get_buyer(buyer_name)
        good.add_buyer(buyer)


@AppRoute(routes=routes, url='/api/')
class CourseApi:
    @Debug(name='GoodsApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.goods).save()
