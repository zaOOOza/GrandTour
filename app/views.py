

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection

from app import models
from app.models import Route


# Create your views here.
@login_required(login_url='login')
def create_route(request):
    if request.user.has_perm('create_route'):
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
            if new_route in models.Route.objects.all():
                return redirect('/app/create_route')
            else:
                new_route.save()
                return redirect('/info')
    else:
        return HttpResponse('No access')


def route_filter(request, route_type=None, country=None, location=None):
    cursor = connection.cursor()
    query_filter = []
    if route_type is not None:
        query_filter.append(f"route_type='{route_type}'")
    if country is not None:
        query_filter.append(f"country='{country}'")
    if location is not None:
        query_filter.append(f"location='{location}'")

    filter_string = ' and '.join(query_filter)
    join_start = """ SELECT
    app_route.country,
    app_route.location,
    app_route.description,
    app_route.duration,
    app_route.stopping_point,
    app_route.route_type,
    start.name,
    finish.name
    FROM app_route
    JOIN app_places as start on 
    start.id = app_route.start_point
    
    JOIN app_places as finish on 
    finish.id = app_route.destination
    WHERE """ + filter_string

    cursor.execute(join_start)
    result = cursor.fetchall()

    dict_result = [{'country': i[0],
                    'location': i[1],
                    'description': i[2],
                    'duration': i[3],
                    'stop_point': i[4],
                    'route_type': i[5],
                    'start': i[6],
                    'finish': i[7]} for i in result]

    return render(request, 'filter_route.html', {'result': dict_result})


# info about all routes
def route_info(request):
    if request.user.is_authenticated:
        cursor = connection.cursor()
        info = """ SELECT
        app_route.id,
        app_route.country,
        app_route.location,
        app_route.description,
        app_route.duration,
        app_route.stopping_point,
        app_route.route_type,
        app_event.event_admin,
        app_event.approved_user,
        app_event.pending_user,
        app_event.price,
        app_event.start_date
        FROM app_route 
        JOIN app_event on 
        app_route.id == app_event.id_route
        """
        cursor.execute(info)
        result = cursor.fetchall()
        route = [{'id': i[0],
                  'country': i[1],
                  'location': i[2],
                  'description': i[3],
                  'duration': i[4],
                  'stop_point': i[5],
                  'route_type': i[6],
                  'event_admin': i[7],
                  'approved_user': i[8],
                  'pending_user': i[9],
                  'price': i[10],
                  'start_date': i[11]} for i in result]

        paginator = Paginator(route, 3)
        page = request.GET.get('page')
        route = paginator.get_page(page)
        return render(request, 'route_info.html', {'routes': route})
    else:
        return redirect('/login')


# Info about rating route
def route_review(request, id_route):
    review = models.Review.objects.all().filter(route_id=id_route)
    return render(request, 'route_review.html', {'reviews': review})


# Add new event to DataBase
@login_required(login_url='login')
def add_route_event(request, id_route):
    if request.user.has_perm('add_route'):
        if request.method == 'GET':
            return render(request, 'add_route_event.html')
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            price = request.POST.get('price')
            user_name = request.user.id
            new_event = models.Event(
                id_route=id_route,
                start_date=start_date,
                price=price,
                event_admin=user_name,
                approved_user=[],
                pending_user=[]
            )
            if new_event in models.Event.objects.all():
                return redirect(f'/app/1/add_event')
            else:
                new_event.save()
                return redirect('/info')
    else:
        return HttpResponse('No access')


# To do ...
def event_handler(request, event_id):
    if request.method == 'GET':
        event = models.Event.objects.all().filter(id=event_id)
        return render(request, 'event_heandler.html', {'event': event})


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
                return redirect('/info')
            else:
                return redirect('/login')
    else:
        return redirect('/info')


# Init user registration and add in to DataBase info about
def user_registration(request):
    if request.method == 'GET':
        return render(request, 'registration.html')
    if request.method == 'POST':
        chek = request.POST.get('username')
        if chek is None:
            user = User.objects.create_user(username=request.POST.get('username'),
                                            password=request.POST.get('password'),
                                            email=request.POST.get('email'),
                                            first_name=request.POST.get('first_name'),
                                            last_name=request.POST.get('last_name')
                                            )
            user.save()
            return redirect('/login')
        else:
            return redirect('/registration')


def logout_user(request):
    logout(request)
    return redirect('/login')
