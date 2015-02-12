from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.http.response import HttpResponseBase
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout, login as auth_login
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import UserSerializer


def base_login(request, data, redirect_view="users.views.about_me"):
    if request.user.is_authenticated():
        return redirect(redirect_view)

    form = AuthenticationForm(data=data)
    if request.method == 'POST':
        if form.is_valid():
            if form.get_user() is not None:
                auth_login(request, form.get_user())
                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                return redirect(redirect_view)
            else:
                form.clean()

    request.session.set_test_cookie()

    return form


def login(request):
    result = base_login(request, data=request.POST)

    if isinstance(result, HttpResponseBase):
        return result

    current_site = get_current_site(request)

    context = {
        'form': result,
        'site': current_site,
        'site_name': current_site.name,
    }

    if result.non_field_errors() or len(result.errors):
        response = TemplateResponse(request, 'users/login.html', context, status=403)
    else:
        response = TemplateResponse(request, 'users/login.html', context)
    return response


@login_required
def about_me(request):
    return TemplateResponse(request, 'users/about.html', {'user': request.user})


@login_required
def logout(request):
    auth_logout(request)
    return redirect("users.views.login")


@api_view(['GET', 'POST'])
def rest_login(request):
    result = base_login(request, data=request.data, redirect_view='users.views.rest_about_me')

    if isinstance(result, HttpResponseBase):
        return result

    if request.method == 'GET':
        return Response({'result': None})

    return Response({'result': 'fail'}, status=401)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def rest_about_me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes((IsAuthenticated, ))
def rest_logout(request):
    auth_logout(request)
    return Response(None, status=204)
