from copy import deepcopy
from datetime import datetime
from quopri import decodestring


class User:
    pass


class Seller(User):
    pass


class Buyer(User):
    pass


#  Fabric method
class UserFactory:
    types = {
        'seller': Seller,
        'buyer': Buyer
    }

    @classmethod
    def create(cls, type_):
        return cls.types[type_]()


#  Prototype
class GoodPrototype:
    def clone(self):
        return deepcopy(self)


class Good(GoodPrototype):
    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.goods.append(self)


class Car(Good):
    pass


class Yacht(Good):
    pass


class GoodFactory:
    types = {
        'car': Car,
        'yacht': Yacht
    }

    @classmethod
    def create(cls, type_, name, category):
        return cls.types[type_](name, category)


class Category:
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.goods = []

    def good_count(self):
        result = len(self.goods)
        if self.category:
            result += self.category.good_count()
        return result


class Engine:
    def __init__(self):
        self.sellers = []
        self.buyers = []
        self.goods = []
        self.categories = []

    @staticmethod
    def create_user(type_):
        return UserFactory.create(type_)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_good(type_, name, category):
        return GoodFactory.create(type_, name, category)

    def get_good(self, name):
        for item in self.goods:
            if item.name == name:
                return item
        return None

    @staticmethod
    def decode_value(val):
        bytes_value = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        str_decode_value = decodestring(bytes_value)
        return str_decode_value.decode('UTF-8')


#  Singleton
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('logging', text, datetime.now())
