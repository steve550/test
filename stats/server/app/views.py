# Create your views here.
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from django.http import HttpResponse
from django.http import FileResponse
from django.http import HttpResponseServerError
import json
import datetime
import pytz
import os
import numpy as np
from django import template
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from google.cloud import storage
import urllib2
import cv2
from time import time
import xxhash
import traceback, sys


register = template.Library()

@csrf_exempt
def index(request):
    if request.method == 'POST':
       username = request.POST['username']
       password = request.POST['password']
       if Post.objects.filter(username=username, password=password).exists():
           return Response('success')
       else:
            return Response('fail')
    return HttpResponse('success')


@csrf_exempt
def userexceptions(request):
    if request.method == 'GET':
        user_id = request.GET.get("user_id", "all")
        exceptions = Exceptions.objects(user=user_id).all().order_by("-date_time")
        exceptions_list = []
        for exception in exceptions:
            exceptions_list.append(exception)
        return render_to_response('exceptions.html',
                                  {'exceptions': exceptions_list, 'user_ids': Exceptions.objects().distinct(field="user")})
    return HttpResponse('success')

@csrf_exempt
def exceptions(request):
    if request.method == 'GET':
        exceptions = Exceptions.objects().all().order_by("-date_time")
        for exception in exceptions:
            print exception.exception
            print exception.date_time
            print exception.user
        """for v in exceptions:
            v = v.replace("\\n","\n")"""
        users = Exceptions.objects().distinct(field="user")
        return render_to_response('exceptions.html',
                                  {'exceptions': exceptions,'user_ids' : users})

    if request.method == 'POST':
        json_data =json.loads(request.body)
        Exceptions.objects.create(exception = json_data.get('exception'),user = json_data.get('user_id'),date_time = json_data.get('date_time'))
    return HttpResponse('success')

def google_auth(user_id, password):
    try:
        result = urllib2.urlopen("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=" + password)
        content = result.read()
        json_data = json.loads(content)
        if user_id == json_data.get("email"):
            return True
    except:
        pass
    return False

def nearby_dates(current_date, limit=3):
    dates = []
    current_datetime = datetime.datetime.strptime(current_date, "%Y-%m-%d")
    dates.append(current_date)
    for i in range(1, limit):
        dates.append((current_datetime + datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
        dates.append((current_datetime - datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
    return dates

def total_duration(events):
    delta = datetime.timedelta()
    for event in events:
        if event.start_time and event.end_time:
            delta  = delta + event.end_time - event.start_time
    seconds = int(delta.total_seconds())
    return '{:}:{:02}:{:02}'.format(seconds // 3600, seconds % 3600 // 60, seconds % 60)

def qa_duration(events):
    delta = datetime.timedelta()
    for event in events.filter(event_id__endswith = "_qa"):
        if event.start_time and event.end_time:
            delta  = delta + event.end_time - event.start_time
    seconds = int(delta.total_seconds())
    return '{:}:{:02}:{:02}'.format(seconds // 3600, seconds % 3600 // 60, seconds % 60)

def non_qa_duration(events):
    delta = datetime.timedelta()
    for event in events.filter(event_id__endswith = "_main"):
        if event.start_time and event.end_time:
            delta  = delta + event.end_time - event.start_time
    seconds = int(delta.total_seconds())
    return '{:}:{:02}:{:02}'.format(seconds // 3600, seconds % 3600 // 60, seconds % 60)

total_files_finished = 0
class Summary():
    def __init__(self, event_id, file_hash, duration, last_end_time):
        self.event_id = event_id
        self.file_hash = file_hash
        self.duration = duration
        self.last_end_time = last_end_time

    def add_duration(self, start_time, end_time):
        self.duration = self.duration + end_time - start_time
        if end_time > self.last_end_time:
            self.last_end_time = end_time

def get_summaries(events):
    global total_files_finished
    summaries = {}
    for event in events:
        total_files_finished += 1
        key = "{:}:{:}".format(event.event_id, event.file_sha256)
        if not summaries.has_key(key):
            summaries[key] =\
                Summary(event.event_id, event.file_sha256, datetime.timedelta(),
                        datetime.datetime.utcfromtimestamp(0))
        summaries[key].add_duration(event.start_time, event.end_time)
    return summaries.values()



@csrf_exempt
def view(request):
    if request.method == 'GET':
        user_id = request.GET.get("user_id", "all")
        ist_timezone = pytz.timezone("Asia/Kolkata")
        date = request.GET.get("date", datetime.datetime.now(ist_timezone).strftime("%Y-%m-%d"))

        datetime_start_of_day = datetime.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=ist_timezone)
        utc_datetime_start_of_day = datetime_start_of_day.astimezone(pytz.UTC)
        datetime_end_of_day = (datetime.datetime.strptime(date, "%Y-%m-%d") + \
                              datetime.timedelta(days=1) -\
                              datetime.timedelta(seconds=1)).\
            replace(tzinfo=ist_timezone)
        utc_datetime_end_of_day = datetime_end_of_day.astimezone(pytz.UTC)

        user_ids = EventModel.objects().distinct(field="user_id")
        if user_id == "all":
            events = EventModel.objects(
                                    end_time__lte=utc_datetime_end_of_day,
                                    end_time__gt=utc_datetime_start_of_day).\
                order_by("user_id", "event_id",
                         "-end_time")
        else:
            events = EventModel.objects(user_id=user_id,
                                    end_time__lte=utc_datetime_end_of_day,
                                    end_time__gt=utc_datetime_start_of_day).\
                order_by("user_id", "event_id",
                         "-end_time")
        events_list = []
        for event in events:
            events_list.append(event)
        def event_end_time(event):
            return event.end_time
        events_list.sort(key=event_end_time, reverse=True)

        summaries = get_summaries(events)
        def summary_last_end_time(summary):
            return summary.last_end_time
        summaries.sort(key=summary_last_end_time, reverse=True)

        return render_to_response('viewevents.html',
                                  {'events': events_list,
                                   'user_ids': sorted(user_ids),
                                   "display_dates": sorted(nearby_dates(date)),
                                   'current_user_id': user_id,
                                   'current_date': date,
                                   'total_duration': total_duration(events),
                                   'qa_duration': qa_duration(events),
                                   'non_qa_duration': non_qa_duration(events),
                                   'summaries': summaries,
                                   'total_files_finished' : total_files_finished
                                   })
    return HttpResponse('success')


def write_file_to_local(hash,file):
    filename, file_extension = os.path.splitext(file.name)
    for chunk in hash.chunks():
        filename = chunk
    curr_dir =os.getcwd()
    path = '%s/%s%s' % (curr_dir, filename, file_extension)
    """uniq = 1
    while os.path.exists(path):
        path = '%s%s_%d%s' % (path,filename, uniq, file_extension)
        uniq += 1"""
    with open(path, 'w+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return path

@csrf_exempt
def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        path = write_file_to_local(request.FILES['hash'], request.FILES['myfile'])
        fs = FileSystemStorage()
        fs.url(path)
        blob_name = os.path.basename(path)
        client = storage.Client()
        bucket = client.get_bucket('steveuploadtest')
        blob = storage.Blob(blob_name, bucket=bucket)
        blob.upload_from_filename(path)
        os.remove(path)
        return HttpResponse('success')
    return render(request, 'upload.html')


@csrf_exempt
def flow(request):
    if request.method == 'POST' and request.FILES.get('image') is not None and\
            request.FILES.get('next_image') is not None:
        def store_temp_file(file_object):
            temp_file_path = "/tmp/deepenstatsserver/" + file_object.name
            if not os.path.exists(os.path.dirname(temp_file_path)):
                os.makedirs(os.path.dirname(temp_file_path))
            with open(temp_file_path, 'wb+') as f:
                for chunk in file_object.chunks():
                    f.write(chunk)
            return temp_file_path
        temp_image_path = store_temp_file(request.FILES['image'])
        temp_next_image_path = store_temp_file(request.FILES['next_image'])

        image = cv2.imread(temp_image_path, 0)
        next_image = cv2.imread(temp_next_image_path, 0)

        start_time = time()
        flow_file_path = ""
        try:
            dense_optical_flow = cv2.optflow.createOptFlow_DIS()
            optical_flow = dense_optical_flow.calc(image, next_image, None)

            h = xxhash.xxh64()
            h.update(optical_flow)
            flow_file_path = '/tmp/deepenstatsserver/' + h.hexdigest() + ".npz"
            np.savez_compressed(flow_file_path, a=optical_flow)
            return FileResponse(open(flow_file_path, "rb"))

        except:
            traceback.print_tb(sys.exc_info()[2])
        finally:
            os.remove(temp_image_path)
            os.remove(temp_next_image_path)
            print("Flow time", time() - start_time)

    return HttpResponseServerError()


