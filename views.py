from my_framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None))


class Contact:
    def __call__(self, request):
        return '200 OK', render('contact.html', hello=request.get('hello', None))


class AnotherPage:
    def __call__(self, request):
        return '200 OK', render('another_page.html')

