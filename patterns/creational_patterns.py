from copy import deepcopy
from datetime import datetime
from quopri import decodestring
from sqlite3 import connect

from .architectural_system_patterns import DomainObject
from .behavioral_patterns import FileWriter, Subject


class User:
    def __init__(self, name):
        self.name = name


class Seller(User):
    pass


class Buyer(User, DomainObject):
    def __init__(self, name):
        self.goods = []
        super().__init__(name)


#  Fabric method
class UserFactory:
    types = {
        'seller': Seller,
        'buyer': Buyer
    }

    @classmethod
    def create(cls, type_, name):
        return cls.types[type_](name)


#  Prototype pattern
class GoodPrototype:
    def clone(self):
        return deepcopy(self)


class Good(GoodPrototype, Subject):
    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.goods.append(self)
        self.buyers = []
        super().__init__()

    def __getitem__(self, item):
        return self.buyers[item]

    def add_buyer(self, buyer: Buyer):
        self.buyers.append(buyer)
        buyer.goods.append(self)
        self.notify()


class SimpleGood(Good):
    pass


class ActionGood(Good):
    pass


# Abstract factory pattern
class GoodFactory:
    types = {
        'simple_good': SimpleGood,
        'yacht': ActionGood
    }

    #  Fabric method pattern
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


# Facade pattern
class Engine:
    def __init__(self):
        self.sellers = []
        self.buyers = []
        self.goods = []
        self.categories = []

    @staticmethod
    def create_user(type_, name):
        return UserFactory.create(type_, name)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
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

    def get_buyer(self, name) -> Buyer:
        for item in self.buyers:
            if item.name == name:
                return item

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

    def __init__(self, name, writer=FileWriter()):
        self.name = name
        self.writer = writer

    def log(self, text):
        date = datetime.now()
        text = f'log---> {text}, {date}'
        print('logging', text, datetime.now())
        self.writer.write(text)


class BuyerMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'buyer'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name = item
            buyer = Buyer(name)
            buyer.id = id
            result.append(buyer)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Good(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"

        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = connect('patterns.sqlite')


# Data Mapper pattern
class MapperRegistry:
    mappers = {
        'buyer': BuyerMapper,
        #  'category': CategoryMapper
    }

    @staticmethod
    def get_mapper(obj):
        if isinstance(obj, Buyer):
            return BuyerMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')
