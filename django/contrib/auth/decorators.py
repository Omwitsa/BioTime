#coding=utf-8
try:
    from functools import update_wrapper, wraps
except ImportError:
    from django.utils.functional import update_wrapper, wraps  # Python 2.3, 2.4 fallback.

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from mysite.api.code import LOGINREQ_CODE,NOTPERM_CODE
from django.utils import simplejson as json
from django.http import HttpResponse

def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    if not login_url:
        from django.conf import settings
        login_url = settings.LOGIN_URL

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            tup = login_url, redirect_field_name, path
            return HttpResponseRedirect('%s?%s=%s' % tup)
        return wraps(view_func)(_wrapped_view)
    return decorator
#WDMS API 专用
def user_passes_test_api(test_func):

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            decorator_dic = {}
            decorator_dic['message'] = 'Login Required'
            decorator_dic['code'] = LOGINREQ_CODE
            return HttpResponse(json.dumps(decorator_dic))
        return wraps(view_func)(_wrapped_view)
    return decorator
#WDMS API 专用
def user_passes_test_api_perm(test_func):

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            decorator_dic = {}
            decorator_dic['message'] = "Don't Have Permission"
            decorator_dic['code'] = NOTPERM_CODE
            return HttpResponse(json.dumps(decorator_dic))
        return wraps(view_func)(_wrapped_view)
    return decorator

def login_required(function=None, login_url=None,redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def api_login_required(function=None):
#WDMS API 专用
    actual_decorator = user_passes_test_api(
        lambda u: u.is_authenticated(),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def api_permission_required(perm):
#WDMS API 专用
    return user_passes_test_api_perm(lambda u: u.has_perm(perm))

def permission_required(perm, login_url=None):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    """
    return user_passes_test(lambda u: u.has_perm(perm), login_url=login_url)
