import json
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from app import models
from mongo_utils import MongoDBConnection
from bson import ObjectId


# Create your views here.
def route_info(request):
    if request.user.is_authenticated:
        cursor = connection.cursor()
        info = f""" SELECT
        app_route.id,
        app_route.country,
        app_route.location,
        app_route.description,
        app_route.duration,
        app_route.stopping_point,
        app_route.route_type,
        app_event.event_admin,
        app_event.event_users,
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
                  'stopping_point': i[5],
                  'route_type': i[6],
                  'event_admin': i[7],
                  'event_users': i[8],
                  'price': i[9],
                  'start_date': i[10]} for i in result]

        with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
            collect = db['stop_point']
            stop_point = collect.find_one({"_id": ObjectId(route[0]['stopping_point'])})

        paginator = Paginator(route, 10)
        page = request.GET.get('page')
        route = paginator.get_page(page)
        return render(request, 'route_info.html', {'routes': route, 'stop_point': stop_point})


    else:
        return redirect('/login')


@login_required(login_url='login')
def create_route(request):
    if request.user.has_perm('create_route'):
        if request.method == 'GET':
            return render(request, 'create_route.html')
        if request.method == 'POST':
            start_point = request.POST.get('start_point')
            stopping_point = request.POST.get('stopping_point')
            destination = request.POST.get('destination')
            country = request.POST.get('country')
            location = request.POST.get('location')
            description = request.POST.get('description')
            route_type = request.POST.get('route_type')
            duration = request.POST.get('duration')

            models.validate_stopping_point(stopping_point)
            stop_list = json.loads(stopping_point)

            with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
                collect = db['stop_point']
                stop_point = collect.insert_one({'points': stop_list}).inserted_id

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
                stopping_point=stop_point
            )
            new_route.full_clean()
            new_route.save()
            return redirect('/info')
    else:
        return HttpResponse('No access')


# @login_required(login_url='login')
def add_route_event(request, id_route):
    if request.user.has_perm('add_route'):
        if request.method == 'GET':
            return render(request, 'add_route_event.html')
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            price = request.POST.get('price')
            # user_name = request.user.id
            new_event = models.Event(
                id_route=id_route,
                start_date=start_date,
                price=price,
                event_admin=1,
                event_users='asdasd'
            )
            # if new_event in models.Event.objects.all():
            #     return redirect(f'/app/1/add_event')
            # else:
            try:
                new_event.full_clean()
                new_event.save()
            except ValidationError:
                return HttpResponse('Date error')
            # return redirect('/info')
            return HttpResponse('Test')
    else:
        return HttpResponse('No access', status=401)


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


# Info about rating route
def route_review(request):
    if request.method == 'GET':
        return render(request, 'route_review.html')

    if request.method == 'POST':
        result = models.Review.objects.all().filter(route_id=request.POST.get('route_id'))
        if result:
            return HttpResponse(json.dumps([{"route_id": i.route_id,
                                             "review": i.review,
                                             "review_rate": i.review_rate} for i in result]),
                                content_type='application/json')
        else:
            return HttpResponse('No found review', status=404)


# Add new event to DataBase


# To do ...
def event_handler(request, event_id):
    if request.method == 'GET':
        cursor = connection.cursor()

        result = f"""SELECT 
        app_event.event_admin,
        app_event.price,
        app_event.start_date,
        app_event.event_users          
        FROM app_event
        WHERE app_event.id_route= {event_id} """
        cursor.execute(result)
        route = cursor.fetchall()

        new_result = [{'event_admin': itm[0],
                       'price': itm[1],
                       'start_date': itm[2],
                       'event_users': itm[3]} for itm in route]

        with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
            collect = db['event_user']
            event_user = collect.find_one({'_id': ObjectId(new_result[0]['event_users'])})

        users_pending = User.objects.filter(pk__in=event_user['pending'])
        users_approved = User.objects.filter(pk__in=event_user['approved'])

        list_users_pending = [{itm.id: itm.username} for itm in users_pending]
        list_users_approved = [{itm.id: itm.username} for itm in users_approved]

        new_result[0]['users_pending'] = list_users_pending
        new_result[0]['users_approved'] = list_users_approved
        return render(request, 'event_heandler.html', {'route': new_result})


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


def logout_user(request):
    logout(request)
    return redirect('/login')


def add_me(request, event_id):
    user = request.user.id
    event = models.Event.objects.filter(id=event_id).first()

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        event_user = db["event_user"]
        all_users = event_user.find_one({'_id': ObjectId(event.event_users)})

        if user in all_users['pending'] or user in all_users['approved']:
            return HttpResponse('You in list')
        else:
            all_users['pending'].append(user)
            event_user.update_one({'_id': ObjectId(event.event_users)}, {"$set": all_users}, upsert=False)

    return redirect('/info', *event_id)


def accept_user(request, event_id):
    if request.method == "GET":
        if request.user.is_superuser:
            event = models.Event.objects.filter(id=event_id).first()

            with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
                event_user = db['event_user']
                all_user = event_user.find_one({'_id': ObjectId(event.event_users)})
                pending_user = all_user.get('pending')
                context = {"pending_users": pending_user}
                return render(request, 'approved_user.html', context=context)
        else:
            return HttpResponse('No access')

    if request.method == 'POST':
        event = models.Event.objects.filter(id=event_id).first()
        approved_user = int(request.POST.get('user id'))

        with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
            event_user = db['event_user']
            all_user = event_user.find_one({'_id': ObjectId(event.event_users)})

            all_user['pending'].remove(approved_user)
            all_user['approved'].append(approved_user)
            event_user.update_one({'_id': ObjectId(event.event_users)}, {'$set': all_user}, upsert=False)
            return HttpResponse('User is accepted')
