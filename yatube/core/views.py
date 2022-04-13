from django.shortcuts import render


def page_not_found(request, exception):
    '''Рендер кастомной страницы 404'''
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    '''Рендер кастомной страницы 403'''
    return render(request, 'core/403csrf.html')


def internal_server_error(request):
    '''Рендер кастомной страницы 500'''
    return render(request, 'core/500.html')
