from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse

from app import models
from app.models import Route


# Create your views here.

def create_route(request):
    if request.method == 'GET':
        return render(request, 'create_route.html')
    if request.method == 'POST':
        start_point = request.POST.get('start_point')
        destination = request.POST.get('destination')
        country = request.POST.get('country')
        location = request.POST.get('location')
        description = request.POST.get('description')
        route_type = request.POST.get('route_type')
        duration = request.POST.get('duration')

        str_object = models.Places.objects.get(name=start_point)
        dest_obj = models.Places.objects.get(name=destination)

        new_route = models.Route(
            start_point=str_object.id,
            destination=dest_obj.id,
            country=country,
            location=location,
            description=description,
            route_type=route_type,
            duration=duration,
            stopping_point={}
        )
        new_route.save()
    return HttpResponse('create route')


def route_filter(request, route_type=None, country=None, location=None):
    query_filter = {}
    if route_type is not None:
        query_filter['route_type'] = route_type
    if country is not None:
        query_filter['country'] = country
    if location is not None:
        query_filter['location'] = location

    result = models.Route.objects.all().filter(**query_filter)
    return HttpResponse([{'country': itm.country, 'id': itm.id} for itm in result])


# Info about chosen route
# to doo , show all info about select route!!!
def route_detail(request, id_route):
    result = models.Route.objects.all()
    return render(request, "display_route_info.html", {'details': result})


# info about all routes
def route_info(request):
    route = Route.objects.all()
    paginator = Paginator(route, 3)
    page = request.GET.get('page')
    route = paginator.get_page(page)
    return render(request, 'route_info.html', {'routes': route})


# Info about rating route
def route_review(request, id_route):
    review = models.Review.objects.all().filter(route_id=id_route)
    return render(request, 'route_review.html', {'reviews': review})


# Add new event to DataBase
def add_route_event(request, id_route):
    if request.method == 'GET':
        return render(request, 'add_route_event.html')
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        price = request.POST.get('price')
        new_event = models.Event(
            id_route=id_route,
            start_date=start_date,
            price=price,
            event_admin=1,
            approved_user=[],
            pending_user=[]
        )
        new_event.save()
    return HttpResponse(f'<h3>{id_route}, add route event</h3>')


# To do ...
def event_handler(request, id_route):
    return HttpResponse(f'<h3>{id_route}, event handler</h3>')


# Init user login
def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'login.html')
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse('User is login')
            else:
                return HttpResponse('No User'), redirect('/login')
    else:
        return HttpResponse('<a href="logout">logout</a>')


# Init user registration and add in to DataBase info about
def user_registration(request):
    if request.method == 'GET':
        return render(request, 'registration.html')
    if request.method == 'POST':
        user = User.objects.create_user(username=request.POST.get('username'),
                                        password=request.POST.get('password'),
                                        email=request.POST.get('email'),
                                        first_name=request.POST.get('first_name'),
                                        last_name=request.POST.get('last_name')
                                        )
        user.save()
        return HttpResponse('User is create'), redirect('/login')


def logout_user(request):
    logout(request)
    return redirect('/login')
