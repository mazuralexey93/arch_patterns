from time import time


# Decorator pattern
class AppRoute:
    def __init__(self, routes, url):
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        self.routes[self.url] = cls()


class Debug:
    def __init__(self, name):
        self.name = name

    def __call__(self, cls):
        def timeit(method):
            def timed(*args, **kwargs):
                time_start = time()
                result = method(*args, **kwargs)
                time_end = time()
                delta = time_start - time_end

                print(f'logging Debug : {self.name} выполнялся {delta:2.3f} ms')
                return result

            return timed

        return timeit(cls)
