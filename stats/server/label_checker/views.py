from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView # normal response return API data
from rest_framework.response import Response
from rest_framework import status

# Json Parser
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import JSONParser
from django.core.files.storage import FileSystemStorage


from google.cloud import storage
from google.cloud import datastore
from google.oauth2 import service_account

import sys, os
from os.path import basename
import cv2
import numpy as np
import json
import re
import math
from shapely.geometry import Polygon
from dominate import document
from dominate.tags import *
import argparse
from collections import defaultdict
import operator
from os import listdir
import glob

from .models import Dataset
from .models import Document
from .models import MissingPolygon
from .models import MissingObject
from .models import WrongId
from .models import LabeledCorrectly

from .forms import InputForm

from .serializers import MissingPolygonSerializer
from .serializers import MissingObjectSerializer
from .serializers import WrongIdSerializer
from .serializers import LabeledCorrectlySerializer


@csrf_exempt
def home(request):
    ext_allowed = ['json']
    if request.method == 'POST':
        form = InputForm(request.POST)
        #if form.is_valid():
        #field = form.cleaned_data['image_1']
        #field = request.POST['image_1']

        #myform = form.save(commit=False)
        #form.save()
        '''
        NOTE: replace received_json_data['attribute_name'] to request.POST['attribute_name'] to get the input from the API and enable line number 89,
        (return JsonResponse(json_output))
        '''
        received_json_data = json.loads(request.body)
        print(received_json_data)
        cwd = os.getcwd()
        os.chdir("..")
        dir_path = os.getcwdu()
        os.chdir(cwd)
        private_key_cloud_path = dir_path+'/storage_key/'+'DeepenAIMain-e00ba37028bf.json'
        #received_json_data['private_key_cloud'] = private_key_cloud_path
        private_key_cloud = os.getcwd()
        private_key_cloud = private_key_cloud.replace("server", "")
        private_key_cloud = private_key_cloud+'storage_key/DeepenAIMain-e00ba37028bf.json'
        #received_json_data['private_key_cloud'] = private_key_cloud
        received_json_data['private_key_cloud'] = {
  "type": "service_account",
  "project_id": "deepen-161721",
  "private_key_id": "e00ba37028bf3cd8fc612b5679ea3db36db244b6",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDJBldHYDzEq1ss\nLDu5BYu/Ol10T70seFqfk5l7LdvOB/JaPx/3JX26syTIQqtOGoz7ivU9xdT1FzCF\n453gYOtv+jKExYPp57z3JU01CDReGi5LVw9sP5vjwLeGTzq89SQZAgKtk6CQUjzm\nHl7Tzv3315l5g5Ye3mzIZlxtmc+r1tAXZdLTfeL9yG5l1KxvxytEtt9254R81fiq\nCfzuF/tOZXD1MuFyzAvQA5kaq69eCyM3wEX6SP81exKemEH7SqfGM6Nk7kInun6M\noaBl+Zyg9uuifRRoipklyle0ytBqHiv2DyYHas0PWCnC6gIY0/7mzJercad4nLnq\nsbxp89VTAgMBAAECggEAH32tTYKfcmWvlidlwbHDNxUzD6XwKhe+hpIOMJQ6AzgO\neKG75bELVaR7ph1/jXAuVrdpfKBRoIVd9hN2p3A3YabNpCv24r0JRqQiyKR846Lx\nTp8YTOpYBuEpPtKJjpFOctZ0SfG+7OzdGmV2kHK0KU+ufLEm4rYQT4Jth0PZmv74\nLFwFOlAyJbfIwYIsF5aVLL6i6JhAxtwcQz9M1T4nxp7TxaWln6vbxIDUTPCJLzJ9\nLR8s8IOb1W+mdHH87lcL0tZ0AHDutldDCLIQ2ojTjqdQ+3yyCuGH/COdZXBDWUmE\nVwZEoWJ/MJGBE7VsH0ceeCPdZQP0QNFeDNwFPgFknQKBgQDl7kAP9FZH7xYd+/Vz\nhV61Nu9MAYo7OvGG7uXd4YI4QTsc3iOdcCJEReUdGsazVML0WKO196nwdySQBkcg\nzsM6eG2/6Dbgvk1IJecaKJu7aH8LUF/a4tcTdWrv1dM2xW1oUAhq3CK3nP5Clkgb\nUbuYZ4D+lbWpc/U4cyZ8srZqNwKBgQDf0Rh0umOmurcwjRuJ6Xsn/DRtkDDhGWAC\nSRWugHkPi+wXnBemUrGsTQy5Bb70cAY0/YyL1C2EiZy+XOjaP9ExySWVHhzgY44R\nb32uO9Qle1+Pj0bENiFdxoZ9wCFo59uGgXfcB7ue07gnzUEX/s6/T5kPJRX9eaxo\nqbmNMIwvxQKBgQDM5CHyFalNMKBk18FBz/c1RF65PCYR4dSYiQoNTobb2kTy1ICo\nKuReMmqYJOQrqbyQQOyhmrC0t3a9YNrBQX52/BnQiP1eCDaVtDDb/pPHzLZpPpYs\nVzeQ/3Drh39Pr15vNeJKVyAYvq1UaNaYgZzJknJAaugWuF4sj3AcbqRewQKBgQC7\nndLLXsdUJ2aSq2avV+omHZNxWJKwzw2dPNiQ/B7/OkLBk9Z7VQydK8WDf96PlyyM\n1RIw0L8LQDQFm2qSMTbSbhQ0CRcZvjqEQRpwqLRwaxgzBl7C8cFMk7N/zEP1ZY6v\nFO59onnTbRUNQFDVpYJ3+miKuoLRhWJSJhxlz5FkJQKBgGAj+EZkt2CzMZa3Qxlg\nfsq1TPAkbudEfXKXVPunzn1pCrd+joMoJeV9JmvGNHvHu/14pH1caQR4gFvq3+Vw\nwBX/XaRpjeVUeEtj5Ut4xoKoUOwfES8JSi+/Ht8mbIMBoTWvbnKaoXwukasUtgOs\nghXyXDcgJ84nu3MABu2sF29c\n-----END PRIVATE KEY-----\n",
  "client_email": "marium-service-account-476@deepen-161721.iam.gserviceaccount.com",
  "client_id": "109573070042334906628",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/marium-service-account-476%40deepen-161721.iam.gserviceaccount.com"
}
        neural_network_file = get_neural_network(received_json_data['private_key_cloud'],received_json_data['image_storage'],
                                                 received_json_data['client_name'])
        if(received_json_data['bounding_box'].encode("utf-8") == 'on'):
            json_output, summary = init_system_for_bounding_box_QA(received_json_data['label_1'],
                                                        neural_network_file,
                                                        received_json_data['batch_script'].encode("utf-8"),
                                                         received_json_data['count_of_images'], received_json_data['instance_mask_path'],received_json_data['manual_labels'])
        else:
            json_output, summary = init_system_for_polygon_QA(received_json_data['image_1'].encode("utf-8"), received_json_data['image_2'].encode("utf-8"),
                                                     received_json_data['label_1'].encode("utf-8"), received_json_data['label_2'].encode("utf-8"),
                                                     received_json_data['semantic_seg'].encode("utf-8"), received_json_data['private_key_cloud'].encode("utf-8"),
                                                     received_json_data['image_storage'].encode("utf-8"), received_json_data['image_folder'].encode("utf-8"),
                                                     received_json_data['batch_script'].encode("utf-8"), received_json_data['count_of_images'],
                                                     received_json_data['instance_mask_path'], received_json_data['deepflow_results_path_on_cloud'],received_json_data['manual_labels'])

        #if(len(json_output) <= 1 and len(summary) <= 1):
        with open('summary.json', 'w') as outfile:
            json.dump(summary, outfile)
        with open('json_response.json', 'w') as outfile:
            json.dump(json_output, outfile)

        print(">> completed")

        response_incorrect_labels = {'incorrect_labels':json_output}
        return JsonResponse(response_incorrect_labels)
        #else:
        #    print "not valid"
        #    print(form.errors.as_data())
        #    raise Http404
    else:
        form = InputForm()

    return render(request, 'home.html', {'form':form})
"""
"""
def get_connection_to_cloud(private_key_location, bucket_name):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = private_key_location
    storage_client = storage.Client()

    # get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    return bucket
"""
"""
def get_neural_network(private_key_location, bucket_name,file_name):
    neural_network = {"0000000000.png": {"car": {"car:1": {"box": [252.72775572538376, 175.72607472538948, 45.06894725561142, 26.15530416369438], "box_score": 98.71659874916077}, "car:3": {"box": [320.59666299819946, 179.96399849653244, 28.94347608089447, 17.577610909938812], "box_score": 88.7819230556488}, "car:2": {"box": [567.8326907157898, 175.0100813806057, 39.96949875354767, 32.34432265162468], "box_score": 97.37609624862671}, "car:5": {"box": [407.53298968076706, 172.24064469337463, 22.787893295288086, 16.287535429000854], "box_score": 64.77833390235901}, "car:4": {"box": [297.4102532565594, 183.750182390213, 22.951108664274216, 15.427082777023315], "box_score": 77.33832597732544}}}, "0000000001.png": {"car": {"car:8": {"box": [313.56017249822617, 179.06728014349937, 26.694476008415222, 18.626097589731216], "box_score": 87.8588080406189}, "car:7": {"box": [239.53025981783867, 174.91500824689865, 50.935669004917145, 27.77029573917389], "box_score": 97.79289364814758}, "car:6": {"box": [567.1195696592331, 174.57490414381027, 40.6566356420517, 32.555848360061646], "box_score": 98.82203340530396}}}, "0000000002.png": {"car": {"car:11": {"box": [303.59926012158394, 178.74771729111671, 29.07959684729576, 18.56127753853798], "box_score": 86.77765727043152}, "car:10": {"box": [225.7700512111187, 174.47064444422722, 53.11804300546646, 29.58931401371956], "box_score": 97.16570973396301}, "car:9": {"box": [566.7242549657822, 174.31332170963287, 42.704054832458496, 32.70091116428375], "box_score": 98.15561771392822}}, "bench": {"bench:1": {"box": [5.473549269139767, 186.3282322883606, 73.40938798338175, 34.33609753847122], "box_score": 72.27413654327393}}}, "0000000003.png": {"car": {"car:13": {"box": [567.3014218211174, 173.13648015260696, 42.58212912082672, 34.2453271150589], "box_score": 95.23866176605225}, "car:12": {"box": [207.6786852478981, 173.75704273581505, 59.74504226446152, 29.858607798814774], "box_score": 99.01330471038818}, "car:15": {"box": [268.5211514532566, 182.2473518550396, 24.883727431297302, 16.419600695371628], "box_score": 64.08243775367737}, "car:14": {"box": [293.3477100133896, 177.8496690094471, 33.588312685489655, 18.78553256392479], "box_score": 84.96617078781128}}}}
    return neural_network
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = private_key_location
    bucket = storage.Client().get_bucket(bucket_name)
    blob = bucket.blob('Neural_network_files/'+file_name+ '.json')
    neural_network = blob.download_as_string()
    return neural_network

def get_bucket_of_images(private_key_location, bucket_name, image_folder):
    bucket = get_connection_to_cloud(private_key_location, bucket_name)
    h = os.getcwd()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = private_key_location
    storage_client = storage.Client()

    # get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs()

    image_list = []

    for folder in blobs:
        get_images = folder.name.rsplit("/", 1)
        if(get_images[0] == image_folder):
            image_list = get_images[1]
    return image_list

def getImages(im1, im2, private_key_location, bucket_name, image_folder):
    bucket = get_connection_to_cloud(private_key_location, bucket_name)

    # get the image
    blob1 = bucket.get_blob(image_folder + '/' + im1)
    blob2 = bucket.get_blob(image_folder + '/' + im2)

    img1_file = "img1"
    img2_file = "img2"
    blob1.download_to_filename(img1_file)
    blob2.download_to_filename(img2_file)

    return img1_file, img2_file
    #return cv2.imdecode(np.fromstring(img1, dtype=np.int8), cv2.IMREAD_COLOR), \
    #       cv2.imdecode(np.fromstring(img2, dtype=np.int8), cv2.IMREAD_COLOR)

#@csrf_exempt
class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser, JSONParser)

    def post(self, request, format=None):

        for filename, file in request.FILES.iteritems():
            name = request.FILES[filename].name
            print(name.content_type)
        #upload_file = request.FILES['documents/1/']
        #destination = open(upload_file.name, 'r')
        #...

        # do some stuff

        #...
        return Response({'received data' : request.data})

class MissingPolygonListView(APIView):
    def get(self, request):
        missing_polygon = MissingPolygon.objects.all()
        serializer = MissingPolygonSerializer(missing_polygon, many=True)
        return Response(serializer.data)

    def post(self):
        pass

class MissingObjectListView(APIView):
    def get(self, request):
        missing_object = MissingObject.objects.all()
        serializer = MissingObjectSerializer(missing_object, many=True)
        return Response(serializer.data)

    def post(self):
        pass

class WrongIdListView(APIView):
    def get(self, request):
        wrong_id = WrongId.objects.all()
        serializer = WrongIdSerializer(wrong_id, many=True)
        return Response(serializer.data)

    def post(self):
        pass

class LabeledCorrectlyListView(APIView):
    def get(self, request):
        labeled_correctly = LabeledCorrectly.objects.all()
        serializer = LabeledCorrectlySerializer(labeled_correctly, many=True)
        return Response(serializer.data)

    def post(self):
        pass

def index(request):
    all_datasets = Datasets.objects.all()
    return render(request, 'label_checker/index.html', {'all_datasets': all_datasets})

def detail(request, dataset_id):
    dataset = get_object_or_404(Datasets, pk=dataset_id)
    return render(request, 'label_checker/detail.html', {'dataset': dataset})


def create_new_bucket(storage_client, request, new_bucket_name):
    # Creates the new bucket
    bucket = storage_client.create_bucket(new_bucket_name)
    print('Bucket {} created.'.format(bucket.name))

def input(request):
    if request.method == 'GET':
        #get image 1
        response = HttpResponse()
        response.write("<p>Got the input.</p>")

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('list'))
    else:
        form = DocumentForm()  # An empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'list.html',
        {'documents': documents, 'form': form}
)

def get_images_and_convert_into_grey_scale(im1, im2):
    img1 = cv2.imread(im1)
    img2 = cv2.imread(im2)

    #compute grey scale images
    img1_grey = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_grey = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    return img1, img2, img1_grey, img2_grey

def apply_deep_flow(im_grey1, im_grey2):
  deep_flow = cv2.optflow.createOptFlow_DeepFlow()
  deepflow = deep_flow.calc(im_grey1, im_grey2, None)
  return deepflow

"""
for computing ground truth instance contours
"""
def compute_ground_truth(path, true_json_file,manual_labels=None):
    file_path = path + true_json_file

    if(os.path.exists(file_path)):
        fs = FileSystemStorage()
        fs.url(file_path)
        print(file_path)

        with open(file_path) as json_file:
            #json_true_data = json.load(json_file)
            json_true_data = manual_labels

        true_list = {}

        all_true_pts = []  # np.array([])
        for type in json_true_data:
            for object in json_true_data[type]:
                if "polygons" in json_true_data[type][object]:
                    polygons = json_true_data[type][object]["polygons"]
                    true_list[object] = polygons[0]

        return true_list
    print("label 2 file failed")


"""
get the predicted instance points
"""
def computed_predicted_output(path, old_json_file, deepflow, img1_shape):
    file_path = path + old_json_file
    pred_list_deepflow = {}
    all_pred_pts_deepflow = []

    if (os.path.exists(file_path)):
        fs = FileSystemStorage()
        fs.url(file_path)
        print(file_path)
        with open(file_path) as json_file:
            json_data = json.load(json_file)

        for type in json_data:
            for object in json_data[type]:
                if "polygons" in json_data[type][object]:
                    polygons = json_data[type][object]["polygons"]
                    for polygon in polygons:
                        pts = np.array(polygon, np.int32)
                        pts = pts.reshape((-1, 1, 2))
                        # move points
                        for i in xrange(pts.shape[0]):
                            if pts[i, 0, 0] >= img1_shape[1]:
                                x_idx = img1_shape[1] - 1
                            else:
                                x_idx = pts[i, 0, 0]

                            # deepflow
                            #print("new points", pts[i, 0, 0], pts[i, 0, 1], x_idx)
                            if(x_idx < img1_shape[1]):
                            #if(deepflow[pts[i, 0, 1], x_idx, 0] < len(deepflow) and deepflow[pts[i, 0, 1], x_idx, 1] < len(deepflow)):
                                #print(deepflow[pts[i, 0, 1], x_idx, 0])
                                #print(deepflow[pts[i, 0, 1], x_idx, 1])
                                new_x = pts[i, 0, 0] + deepflow[pts[i, 0, 1], x_idx, 0]
                                new_y = pts[i, 0, 1] + deepflow[pts[i, 0, 1], x_idx, 1]
                                #print("new_x ", new_x, "new_y ", new_y)
                                pts[i, 0, 0] = new_x
                                pts[i, 0, 1] = new_y
                                all_pred_pts_deepflow.append(tuple((new_x, new_y)))

                    pred_list_deepflow[object] = all_pred_pts_deepflow
                    all_pred_pts_deepflow = []

        return pred_list_deepflow
    print("label 1 file failed")



def find_area_of_intersection(polygon1, polygon2, shape):
    canvas1 = np.zeros(shape, dtype=np.uint8)
    canvas2 = np.zeros(shape, dtype=np.uint8)

    # for polygon in polygon1:
    cv2.fillPoly(canvas1, np.array([polygon1], dtype=np.int32), 255)
    # for polygon in polygon2:
    cv2.fillPoly(canvas2, np.array([polygon2], dtype=np.int32), 255)

    mask = cv2.bitwise_and(canvas1, canvas2)

    (_, contours, hierarchy) = cv2.findContours(mask.copy(), cv2.RETR_CCOMP,
                                                cv2.CHAIN_APPROX_TC89_L1)
    contours = [[y[0].tolist() for y in x] for x in contours]

    area = []
    for contour in contours:
        area.append(cv2.contourArea(np.array(contour)))

    if (len(area) > 0):
        return max(area)
    else:
        return 0


"""
@param: list1 = ground_truth_dict
@param:list2 = predicted_dict
"""


def find_missing_object(list1, list2, final_result, is_semantic):
    if (len(list1) < 0 or len(list2) < 0):
        return

    for key in final_result.keys():
        name = key.split(":")
        if (is_semantic and (name[0] in get_list_of_background())):
            continue

        elif (((key in list1) and (key not in list2)) or
                  ((key not in list1) and (key in list2))):
            final_result[key] = "missing object"

    return final_result


"""
"""


def init_all_ids(list1, list2, final_result, is_semantic):
    all_keys = set(list1.keys() + list2.keys())
    for key in all_keys:
        name = key.split(":")
        if ((is_semantic) and (name[0] in get_list_of_background())):
            final_result[name[0]] = "unclassified"
        else:
            final_result[key] = "unclassified"
    return final_result


"""
"""


def find_overlapping_polygons(polygon1, polygon2, shape):
    if (len(polygon1) < 3 or len(polygon2) < 3):
        return 0
    p1 = Polygon(polygon1)
    p2 = Polygon(polygon2)
    area = 0
    result = p1.intersects(p2)
    if (result):
        area = find_area_of_intersection(polygon1, polygon2, shape)
    return area


"""
"""


def find_id_mismatch(list1, list2, final_result, shape, is_semantic):
    for key1 in list1.keys():
        name1 = key1.split(":")
        if (is_semantic and (name1[0] in get_list_of_background())):
            continue
        for key2 in list2.keys():
            name2 = key2.split(":")
            if (is_semantic and (name2[0] in get_list_of_background())):
                continue
            elif not key2 == key1:
                area = find_overlapping_polygons(list1[key1], list2[key2], shape)
                if (area >= 700):
                    if (final_result[key1] == "unclassified"):
                        final_result[key1] = "wrong id"
                    elif (final_result[key2] == "unclassified"):
                        final_result[key2] = "wrong id"
    return final_result


"""
find point distance, threshold is of 8 for correct labeling
"""


def find_point_distance(list1, list2, final_result, is_semantic, severity_score):
    final_result_deepflow = {}
    for key in list1:
        name = key.split(":")
        if (is_semantic and (name[0] in get_list_of_background())):
            continue
        else:
            abs_dist_deepflow = []
            if (key in list2):
                for i in list2[key]:
                    dist_deepflow = cv2.pointPolygonTest(np.array(list1[key]), i, True)
                    abs_dist_deepflow.append(abs(dist_deepflow))

                # find absolute average
                arithmetic_mean = reduce(lambda x, y: x + y, abs_dist_deepflow) / len(abs_dist_deepflow)
                final_result_deepflow[key] = arithmetic_mean

                if (8 <= final_result_deepflow[key] <= 12 and final_result[key] == "unclassified"):
                    final_result[key] = "missing polygon"
                    x1, y1 = separate_xy(list1[key])
                    area1 = find_area_of_polygon(x1, y1)
                    x2, y2 = separate_xy(list2[key])
                    area2 = find_area_of_polygon(x2, y2)
                    if (max(area1, area2) > 500):
                        severity_score[key] = (1 - (final_result_deepflow[key] / 12))
                elif (final_result_deepflow[key] < 8):
                    final_result[key] = "labeled correctly"
            else:
                final_result[key] = "missing object"

    return final_result


"""
"""


def separate_xy(poly):
    # separate points in to x and y coordinates
    x = []
    y = []
    for i in poly:
        x.append(i[0])
        y.append(i[1])
    return x, y


"""
#using shoelace formula
"""
def find_area_of_polygon(x, y):
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


"""
"""
def print_results(final_result):
    for keys, values in final_result.items():
        print(keys, ":", values)


"""
#find area
"""
def get_combined_area(polygons1, polygons2, shape, is_semantic, intersection=False):
    canvas1 = np.zeros(shape, dtype=np.uint8)
    canvas2 = np.zeros(shape, dtype=np.uint8)

    if (is_semantic):
        for polygon in polygons1:
            cv2.fillPoly(canvas1, np.array([polygon], dtype=np.int32), 255)

        for polygon in polygons2:
            cv2.fillPoly(canvas2, np.array([polygon], dtype=np.int32), 255)
    else:
        cv2.fillPoly(canvas1, np.array([polygons1], dtype=np.int32), 255)
        cv2.fillPoly(canvas2, np.array([polygons2], dtype=np.int32), 255)

    if intersection:
        mask = cv2.bitwise_and(canvas1, canvas2)
    else:
        mask = cv2.bitwise_or(canvas1, canvas2)
    (_, contours, hierarchy) = cv2.findContours(mask.copy(), cv2.RETR_CCOMP,
                                                cv2.CHAIN_APPROX_TC89_L1)

    contours = [[y[0].tolist() for y in x] for x in contours]
    # if len(contours) == 0:
    #    return 0
    # contours_after_holes = utils.get_contours_from_hierarchy(contours, hierarchy[0])
    area = 0
    for contour in contours:
        area = area + cv2.contourArea(np.array(contour))

    return area


"""
"""
def check_metric(img, polygons1, polygons2, shape, name, is_semantic):
    overlay1 = img.copy()
    overlay2 = img.copy()
    opacity = 0.7

    img2 = img.copy()
    canvas1 = np.zeros(shape, dtype=np.uint8)
    canvas2 = np.zeros(shape, dtype=np.uint8)

    if (is_semantic):
        for polygon in polygons1:
            cv2.fillPoly(overlay1, np.array([polygon], dtype=np.int32), (0, 255, 0))

        cv2.addWeighted(overlay1, opacity, img, 1 - opacity, 0, img)
        for polygon in polygons2:
            cv2.fillPoly(overlay2, np.array([polygon], dtype=np.int32), (0, 0, 255))

        cv2.addWeighted(overlay2, opacity, img2, 1 - opacity, 0, img2)
        cv2.imwrite('groundtruth' + name + '.jpg', img)
        cv2.imwrite('predicted' + name + '.jpg', img2)
    else:
        # for polygon in polygons1:
        cv2.fillPoly(overlay1, np.array([polygons1], dtype=np.int32), 255)
        cv2.addWeighted(overlay1, opacity, img, 1 - opacity, 0, img)
        # for polygon in polygons2:
        cv2.fillPoly(overlay2, np.array([polygons2], dtype=np.int32), (255, 0, 255))
        cv2.addWeighted(overlay2, opacity, img2, 1 - opacity, 0, img2)

        name = name.split(":")
        cv2.imwrite('groundtruth' + name[0] + name[1] + '.jpg', img)
        cv2.imwrite('predicted' + name[0] + name[1] + '.jpg', img2)


"""
"""
def similarity_measure(polygon1, polygon2, image_shape, is_semantic):
    max_intersection_over_union = -1

    intersection_area = get_combined_area(polygon1, polygon2, image_shape, is_semantic, intersection=True)
    union_area = get_combined_area(polygon1, polygon2,
                                   image_shape, is_semantic, intersection=False)
    intersection_over_union = intersection_area / union_area
    return intersection_over_union


"""
"""


def enable_semantic_segmentation_of_background(true_list, pred_list_deepflow, img_shape, final_result, severity_score):
    background_list = get_list_of_background()
    true_polygons = defaultdict(list)
    pred_polygons = defaultdict(list)

    for key in true_list:
        object_name = key.split(":")
        if object_name[0].encode('utf8') in background_list:
            my_object = object_name[0].encode("utf8")

            if my_object in true_polygons:
                true_polygons[my_object].append(true_list[key])
            else:
                true_polygons[my_object] = []
                true_polygons[my_object].append(true_list[key])

    for key in pred_list_deepflow:
        object_name = key.split(":")
        if object_name[0].encode('utf8') in background_list:
            my_object = object_name[0].encode("utf8")
            if my_object in pred_polygons:
                pred_polygons[my_object].append(pred_list_deepflow[key])
            else:
                pred_polygons[my_object] = []
                pred_polygons[my_object].append(pred_list_deepflow[key])

    # match areas
    for key in true_polygons:
        if key in pred_polygons:
            res = similarity_measure(true_polygons[key], pred_polygons[key], img_shape, is_semantic=True)
            if res >= 0.7:
                final_result[key] = "labeled correctly"
            else:
                final_result[key] = "missing polygon"
                severity_score[key] = res
    return final_result, true_polygons, pred_polygons


"""
"""


def test_results_for_polygon(img_grey_shape, true_list, pred_list, final_result, severity_score, is_semantic):
    # test cases
    if not is_semantic:
        init_all_ids(true_list, pred_list, final_result, is_semantic)

    # check for missing object
    final_result_semantic = find_missing_object(true_list, pred_list, final_result, is_semantic)

    # correctly labeled
    final_result_semantic = find_point_distance(true_list, pred_list, final_result_semantic, is_semantic, severity_score)

    # check for id mismatch
    final_result_semantic = find_id_mismatch(true_list, pred_list, final_result_semantic, img_grey_shape, is_semantic)

    return final_result_semantic
"""
"""
def construct_output(true_list, pred_list, json_output, key, tag, severity_score, wrong_label):
    polygon = {
        'ground truth': true_list,
        'predicted': pred_list,
        'severity score': severity_score,
        'wrong label': wrong_label
    }
    json_output[tag][key] = polygon

"""
"""

def generate_summary(true_list, pred_list, final_result, true_polygons, pred_polygons, sequence, mode,
                     severity_score, BB_mapping, is_semantic, wrong_label):
    # generating summary
    #print_results(final_result)
    json_output = {}
    json_output['missing object'] = {}
    json_output['labeled correctly'] = {}
    json_output['wrong id'] = {}
    json_output[mode] = {}
    if(mode == 'missing bounding box'):
        json_output['extra bounding box'] = {}
    json_output['unclassified'] = {}

    if(mode == 'missing bounding box'):
        summary = {'missing object': 0, 'labeled correctly': 0, 'wrong id': 0, mode: 0, 'unclassified': 0, 'extra bounding box': 0}
    else:
        summary = {'missing object': 0, 'labeled correctly': 0, 'wrong id': 0, mode: 0, "unclassified": 0}

    with document(title='Results') as doc:
        for keys, values in final_result.items():
            #print(keys, values)
            if (values == "missing object"):
                summary['missing object'] += 1
                if(mode == 'missing bounding box'):
                    construct_output("", pred_list[keys.encode('utf8')],
                                     json_output, keys.encode('utf8'), 'missing object', "", "")
                else:
                    if(keys.encode('utf8') in true_list):
                        #json_output['missing object'][keys.encode('utf8')] = {}
                        construct_output(true_list[keys.encode('utf8')], "",
                                         json_output, keys.encode('utf8'), 'missing object', "", "")
                    elif(keys.encode('utf8') in pred_list):
                        construct_output("", pred_list[keys.encode('utf8')],
                                         json_output, keys.encode('utf8'), 'missing object', "", "")

            elif(values == "extra bounding box"):
                summary['extra bounding box'] += 1
                if not(keys.encode('utf8') in true_list):
                    construct_output(true_list[BB_mapping[keys.encode('utf8')]], "", json_output, keys.encode('utf8'),
                                     'extra bounding box', "", "")
                else:
                    construct_output(true_list[keys.encode('utf8')], "",
                                 json_output, keys.encode('utf8'), 'extra bounding box', "", "")

            elif (values == "labeled correctly"):
                summary['labeled correctly'] += 1
                # json_output['labeled correctly'].append(keys.encode('utf8'))
                if (is_semantic and (":" not in keys)):
                    construct_output(true_polygons[keys.encode('utf8')], pred_polygons[keys.encode('utf8')],
                                     json_output,
                                     keys.encode('utf8'), 'labeled correctly', "", "")
                elif(mode == "missing polygon"):
                    construct_output(true_list[keys.encode('utf8')], pred_list[keys.encode('utf8')],
                                     json_output, keys.encode('utf8'), 'labeled correctly', "", "")
                else:
                    construct_output(true_list[keys.encode('utf8')], pred_list[BB_mapping[keys.encode('utf8')]],
                                     json_output, keys.encode('utf8'), 'labeled correctly', "", "")
            elif (values == "wrong id"):
                summary['wrong id'] += 1
                if (is_semantic and (":" not in keys)):
                    construct_output(true_polygons[keys.encode('utf8')], pred_polygons[keys.encode('utf8')],
                                     json_output, keys.encode('utf8'), 'wrong id', "", "")
                else:
                    if ((mode == 'missing bounding box') and (keys in BB_mapping)):
                        if (keys in wrong_label):
                            construct_output(true_list[keys.encode('utf8')], pred_list[BB_mapping[keys.encode('utf8')]],
                                     json_output, keys.encode('utf8'), 'wrong id', "", wrong_label[keys.encode('utf8')])
                        else:
                            construct_output(true_list[keys.encode('utf8')], pred_list[BB_mapping[keys.encode('utf8')]],
                                             json_output, keys.encode('utf8'), 'wrong id', "", "")
                    else:
                        construct_output(true_list[keys.encode('utf8')], pred_list[keys.encode('utf8')],
                                         json_output, keys.encode('utf8'), 'wrong id', "", "")

            elif (values == mode):
                summary[mode] += 1
                if (is_semantic and (":" not in keys)):
                    construct_output(true_polygons[keys.encode('utf8')], pred_polygons[keys.encode('utf8')],
                                     json_output, keys.encode('utf8'), mode, severity_score[keys], "")
                else:
                    if((mode == 'missing bounding box') and (keys in BB_mapping)):
                        # please check for severity score here
                        construct_output(true_list[keys.encode('utf8')], pred_list[BB_mapping[keys.encode('utf8')]],
                                         json_output, keys.encode('utf8'), mode, "", "")
                    else:
                        construct_output(true_list[keys.encode('utf8')], pred_list[keys.encode('utf8')],
                                             json_output, keys.encode('utf8'), mode, "", "")


            elif (values == "unclassified"):
                summary['unclassified'] += 1
                if (is_semantic and (":" not in keys)):
                    construct_output(true_polygons[keys.encode('utf8')], pred_polygons[keys.encode('utf8')],
                                     json_output, keys.encode('utf8'), 'unclassified', "", "")

                elif (mode == "missing polygon"):
                    construct_output(true_list[keys.encode('utf8')], pred_list[keys.encode('utf8')],
                                     json_output, keys.encode('utf8'), 'unclassified', "", "")
                else:
                    if(keys in true_list and not (keys in pred_list)):
                        construct_output(true_list[keys.encode('utf8')], "",
                                         json_output, keys.encode('utf8'), 'unclassified', "", "")
                    elif(keys in pred_list and not (keys in true_list)):
                        construct_output("", pred_list[keys.encode('utf8')],
                                     json_output, keys.encode('utf8'), 'unclassified', "", "")
                    else:
                        construct_output(true_list[keys.encode('utf8')], pred_list[keys.encode('utf8')],
                                         json_output, keys.encode('utf8'), 'unclassified', "", "")
            # finding mapping manually

            '''#TODO disabling the output images
            img3 = img1.copy()
            img4 = img2.copy()
            name = keys + "_" + str(sequence)
            if (values != "labeled correctly" and values != "missing object"):
                if (is_semantic and (":" not in keys)):
                    check_metric(img4, true_polygons[keys.encode('utf8')], pred_polygons[keys.encode('utf8')],
                                 img_grey.shape, name, is_semantic=True)
                elif (keys in severity_score or values == "wrong id"):
                    check_metric(img4, true_list[keys.encode('utf8')], pred_list[keys.encode('utf8')], img_grey.shape,
                                 name, is_semantic=False)
            '''
    return summary, json_output


"""
"""
def get_severity_score(severity_score):
    tuples_of_severity_score = severity_score.items()
    severity_score_sorted = sorted(tuples_of_severity_score, key=operator.itemgetter(1))
    return severity_score_sorted


"""
"""
def calculate_severity_score_for_unclassified_objects(list1, list2, image_shape, final_result, severity_score):
    for keys, values in final_result.items():
        if (values == "unclassified" and (":" in keys)):
            res = similarity_measure(list1[keys], list2[keys], image_shape, is_semantic=False)
            if 0.01 < res < 0.8:
                x1, y1 = separate_xy(list1[keys])
                area1 = find_area_of_polygon(x1, y1)
                x2, y2 = separate_xy(list2[keys])
                area2 = keys, find_area_of_polygon(x2, y2)
                if (max(area1, area2) > 500):
                    severity_score[keys] = res
            if res == 0.0:
                final_result[keys] = "wrong id"
    return severity_score


"""
clean everything
"""
def cleanup(file):
    os.remove(file)
    return

"""
get the list of background in semantic segmentation
"""
def get_list_of_background():
  background = ["sky", "building", "trees", "sidewalk", "road lane", "parking", "fence", "grass", "curb"] #for Zippy
  return background

"""
"""
#def get_deepflow_results(img1, img2, deepflow_file_path):
def get_deepflow_results(channel0_img, channel1_img, scaling_coeff):
    deepflow_datastruct = np.load(scaling_coeff)

    channel0 = cv2.imread(channel0_img)
    channel1 = cv2.imread(channel1_img)

    deepflow_results = np.zeros((channel0.shape[0], channel0.shape[1], 2))
    deepflow_results[:, :, 0] = channel0[:, :, 0]
    deepflow_results[:, :, 1] = channel1[:, :, 0]

    channel0_min = deepflow_datastruct[0]
    channel0_max = deepflow_datastruct[1]

    channel1_min = deepflow_datastruct[2]
    channel1_max = deepflow_datastruct[3]

    channel0_range = channel0_max - channel0_min
    channel1_range = channel1_max - channel1_min

    deepflow_results = deepflow_results.astype(np.float32)

    deepflow_results[:, :, 0] = (((deepflow_results[:, :, 0] * channel0_range) / 255.0) + channel0_min)
    deepflow_results[:, :, 1] = (((deepflow_results[:, :, 1] * channel1_range) / 255.0) + channel1_min)

    return deepflow_results

"""
"""
def fetch_deepflow_results(img1_name, img2_name, private_key_location, bucket_name, deepflow_file_path):
    bucket = get_connection_to_cloud(private_key_location, bucket_name)

    im1 = img1_name.split(".")
    im2 = img2_name.split(".")

    channel0_img = bucket.get_blob(deepflow_file_path + '/' + im1[0] + '_' + im2[0] + '_channel0.jpg')
    channel1_img = bucket.get_blob(deepflow_file_path + '/' + im1[0] + '_' + im2[0] + '_channel1.jpg')
    scaling_coeff = bucket.get_blob(deepflow_file_path + '/' + im1[0] + '_' + im2[0] + '_scalingcoeff.npy')

    ch0 = "channel0_image"
    ch1 = "channel1_image"
    s_coeff = "scaling_coefficient"

    channel0_img.download_to_filename(ch0)
    channel1_img.download_to_filename(ch1)
    scaling_coeff.download_to_filename(s_coeff)

    return ch0, ch1, s_coeff

"""
"""
def process_polygon_images(im1, im2, label1, label2, private_key_location, bucket_name, image_folder, sequence, enabled_semantic, path, deepflow_file_path,manual_labels=None):
    #=============== For local processing of images, deepflow results on the local machine =================#
    #img1, img2 = getImages(im1, im2, private_key_location, bucket_name, image_folder)
    #img1, img2, img1_grey, img2_grey = get_images_and_convert_into_grey_scale(img1, img2)
    #deepflow = apply_deep_flow(img1_grey, img2_grey)
    #========================================================================================================
    channel0_img, channel1_img, scaling_coeff = fetch_deepflow_results(im1, im2, private_key_location, bucket_name, deepflow_file_path)
    deepflow_results = get_deepflow_results(channel0_img, channel1_img, scaling_coeff)

    img2_grey_shape = (deepflow_results.shape[0], deepflow_results.shape[1])
    true_list = compute_ground_truth(path, label2,manual_labels=manual_labels)

    pred_list_deepflow = computed_predicted_output(path, label1, deepflow_results, img2_grey_shape)

    final_result = {}
    severity_score = {}
    # sequence = 0


    if (enabled_semantic == 'on'):
        final_result = init_all_ids(true_list, pred_list_deepflow, final_result, is_semantic=True)

        final_result, true_polygons, pred_polygons = enable_semantic_segmentation_of_background(true_list,
                                                                                                pred_list_deepflow,
                                                                                                img2_grey_shape, final_result,
                                                                                                severity_score)
        final_result = test_results_for_polygon(img2_grey_shape, true_list, pred_list_deepflow, final_result, severity_score, is_semantic=True)
        severity_score = calculate_severity_score_for_unclassified_objects(true_list, pred_list_deepflow,
                                                                           img2_grey_shape, final_result,
                                                                           severity_score)
        summary, json_output = generate_summary(true_list, pred_list_deepflow, final_result, true_polygons,
                                                pred_polygons, sequence, "missing polygon", severity_score, "", True, "")
        # severity_score = get_severity_score(severity_score)
        # print type(severity_score)
        # html_results.append(get_result_in_html(img1, img2, final_result, severity_score, sequence, html_files,
        #                                       is_semantic=True))

    else:
        final_result = test_results_for_polygon(img2_grey_shape, true_list, pred_list_deepflow, final_result, severity_score, is_semantic=False)
        severity_score = calculate_severity_score_for_unclassified_objects(true_list, pred_list_deepflow,
                                                                           img2_grey_shape, final_result,
                                                                           severity_score)
        summary, json_output = generate_summary(true_list, pred_list_deepflow, final_result, "", "",
                                                sequence, "missing polygon", severity_score, "", False, "")
        # severity_score = get_severity_score(severity_score)
        # html_results.append(get_result_in_html(files[0], files[1], final_result, severity_score, sequence, html_files,
        #                                       is_semantic=False))

    cleanup("channel0_image")
    cleanup("channel1_image")
    cleanup("scaling_coefficient")
    return json_output, summary
"""
"""
def init_system_for_polygon_QA(im1, im2, label1, label2, semantic_seg, private_key_location, bucket_name, image_folder,
                               batch_script, count_of_images, instance_mask_path, deepflow_file_path,manual_labels=None):
    if(batch_script == 'on'):
        slice_of_files, slice_of_masks = process_batch_script(im1, label1, instance_mask_path, count_of_images, private_key_location, bucket_name, image_folder, "")

        json_output_list = []
        summary_list = []
        for i in range(0, len(slice_of_files)):
            sequence = i
            files = slice_of_files[i: i + 2]
            masks = slice_of_masks[i: i + 2]

            if (len(files) > 1 and len(masks) > 1):
                print("======Working on=====")
                print("-filename", files)
                print("-masks", masks)

                json_output, summary = process_polygon_images(files[0].encode("utf8"), files[1].encode("utf8"),
                                       masks[0].encode("utf8"), masks[1].encode("utf8"), private_key_location, bucket_name,
                                                              image_folder, sequence, semantic_seg, instance_mask_path, deepflow_file_path,manual_labels=manual_labels)

                new_key = {}
                new_key[files[0] + "_" + files[1]] = json_output
                json_output_list.append(new_key)
                new_key = {}
                new_key[files[0] + "_" + files[1]] = summary
                summary_list.append(new_key)

        return json_output_list, summary_list
    else:
        json_output, summary = process_polygon_images(im1, im2, label1, label2, private_key_location, bucket_name,
                                                      image_folder, 0, semantic_seg, "", deepflow_file_path,manual_labels=None)
        return json_output, summary

"""
"""
def ground_truth_for_deepScale_BB(list, path, manual_labels):
    file1 = path + list

    if(os.path.exists(file1)):
        fs = FileSystemStorage()
        fs.url(file1)

        with open(file1) as json_file:
            #true_data1 = json.load(json_file)
            true_data1 = manual_labels

        if(true_data1 == {}):
            return {}

        true_list1 = {}

        max = 0
        for type in true_data1:
            category = type.split(':')
            if(category[0] == "vehicle"):
                true_list1["car:" + category[1]] = true_data1[type]
                if(max < int(category[1])):
                    max = int(category[1])
            elif(category[0] != "vehicle|occluded"):
                true_list1[type] = true_data1[type]
        max += 1
        for type in true_data1:
            category = type.split(':')
            if(category[0] == "vehicle|occluded"):
                true_list1["car:" + str(max)] = true_data1[type]
                max += 1

        return true_list1

    print("Label files aren't readable")
"""
"""
def compute_ground_truth_for_BB(list, path,manual_labels):
    #file1 = 'Files/documents/' + list
    """file1 = path + list
    print(file1)

    if (os.path.exists(file1)):
        fs = FileSystemStorage()
        fs.url(file1)

        with open(file1) as json_file:
            true_data1 = json.load(json_file)

        true_list1 = {}

        for type in true_data1:
            for object in true_data1[type]:
                if "box" in true_data1[type][object]:
                    boxes = true_data1[type][object]["box"]
                    true_list1[object] = boxes
                else:
                    true_list1[object] = []

        return true_list1
    print("Label files aren't readable")"""
    true_data1 = manual_labels
    true_list1 = {}

    for type in true_data1:
        for object in true_data1[type]:
            if "box" in true_data1[type][object]:
                boxes = true_data1[type][object]["box"]
                true_list1[object] = boxes
            else:
                true_list1[object] = []

    return true_list1


"""
"""
def compute_predicted_output_for_BB(pred_label, im_name):
    """pred_file = 'Files/documents/' + pred_label

    if (os.path.exists(pred_file)):
        fs = FileSystemStorage()
        fs.url(pred_file)

        with open(pred_file) as json_file:
            pred_data = json.load(json_file)
        pred_data =pred_label
        if (pred_data == {}):
            return {}, {}

        pred_list = {}
        box_score = {}

        for img in pred_data:
            if(img == im_name):
                for type in pred_data[img]:
                    for object in pred_data[img][type]:
                        if "box" in pred_data[img][type][object]:
                            boxes = pred_data[img][type][object]["box"]
                            pred_list[object] = boxes
                        else:
                            pred_list[object] = []

                        if "box_score" in pred_data[img][type][object]:
                            score = pred_data[img][type][object]["box_score"]
                            box_score[object] = score
    else:
        print(pred_file + " does not exist")"""

    pred_data = pred_label
    if (pred_data == {}):
        return {}, {}

    pred_list = {}
    box_score = {}

    for img in pred_data:
        if (img == im_name):
            for type in pred_data[img]:
                for object in pred_data[img][type]:
                    if "box" in pred_data[img][type][object]:
                        boxes = pred_data[img][type][object]["box"]
                        pred_list[object] = boxes
                    else:
                        pred_list[object] = []

                    if "box_score" in pred_data[img][type][object]:
                        score = pred_data[img][type][object]["box_score"]
                        box_score[object] = score
    return pred_list, box_score

"""
"""
def getImageName(im_name):
    im_name = im_name.rsplit('.', 1)
    #im_name = im_name[0].split('_')
    #return im_name[-1]
    return im_name[0]+'.png'

"""
"""
def visualize_BB(boxT, boxP):
    canvas1 = np.zeros((600, 800), dtype=np.uint8)
    cv2.rectangle(canvas1, (boxT[0], boxT[1]), (boxT[2] + boxT[0], boxT[3] + boxT[1]), (255,255,255), 2)
    cv2.rectangle(canvas1, (boxP[0], boxP[1]), (boxP[2] + boxP[0], boxP[3] + boxP[1]), (255,255,255), 2)
    cv2.imshow("img", canvas1)
    cv2.waitKey()
    cv2.destroyAllWindows()
    return

"""
"""
def bb_intersection_over_union(boxT, boxP):
    #visualize_BB(boxT, boxP)
    # determine the (x, y)-coordinates of the intersection rectangle
    xT = max(boxT[0], boxP[0])
    yT = max(boxT[1], boxP[1])
    xP = min(boxT[0] + boxT[2], boxP[0] + boxP[2])
    yP = min(boxT[1] + boxT[3], boxP[1] + boxP[3])

    # no intersection
    if xT > xP or yT > yP:
        return 0

    # compute the area of intersection rectangle
    interArea = (xP - xT + 1) * (yP - yT + 1)

    # compute the area of both the prediction and ground-truth
    # rectangles
    boxTArea = (boxT[2] + 1) * (boxT[3] + 1)
    boxPArea = (boxP[2] + 1) * (boxP[3] + 1)

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the intersection area
    iou = interArea / float(boxTArea + boxPArea - interArea)

    # return the intersection over union value
    return iou
"""
"""
def get_predicted_labels_from_cloud(predicted_label, private_key_location, bucket_name, image_folder):
    bucket = get_connection_to_cloud(private_key_location, bucket_name)
    blob1 = bucket.get_blob(image_folder + '/' + predicted_label)
    predicted_label_file = "predicted_label_BB"
    blob1.download_to_filename(predicted_label_file)
    return predicted_label_file

"""
"""
'''
def check_for_missing_BB(true_label, pred_label, final_result):
    #using jaccard distance
    iou_score = {}
    for keys in final_result:
        if final_result[keys] == "unclassified":
            iou = bb_intersection_over_union(true_label[keys], pred_label[keys])
            iou_score[keys] = iou
            if(0.7 <= iou <= 1):
                final_result[keys] = 'labeled correctly'
            elif(0.2 <= iou <= 0.6):
                final_result[keys] = 'missing bounding box'
            elif(iou > 1):
                final_result[keys] = 'wrong id'
    return final_result, iou_score
'''

def find_missing_object_BB(true_label, pred_label, final_result, BB_mapping, wrong_label):
    true_label_num = []
    iou_score = {}
    current_iou = {}

    for kt in true_label:
        label = kt.split(":")
        true_label_num.append(int(label[1].encode('utf8')))

    random_number = max(true_label_num)
    for kt in true_label:
        if (true_label[kt] == []):
            continue
        labeled = False
        same_label = False
        for kp in pred_label:
            #find iou
            iou = bb_intersection_over_union(true_label[kt], pred_label[kp])
            current_iou[kp] = iou

            if (kt == kp):
                same_label = True

        max_iou = max(current_iou.iteritems(), key=operator.itemgetter(1)) # kp = iou

        if(0.7 <= max_iou[1] <= 1):
            # if it's a match and the id aren't the same, mark both of them as wrong label
            get_id_kt = kt.split(":")
            get_id_kp = max_iou[0].split(":")
            if((get_id_kp[0] != get_id_kt[0]) and (get_id_kt[0] != "pedestrian" and get_id_kp[0] != "person")):
                #print("different id", kt, max_iou[0])
                wrong_label[kt] = max_iou[0]
                final_result[kt] = "wrong id"
            else:
                final_result[kt] = 'labeled correctly'

            labeled = True
            BB_mapping[kt] = max_iou[0]
            if max_iou[0] not in true_label:
                final_result[max_iou[0]] = 'done'
            iou_score[kt] = max_iou[1]

        elif (0.5 <= max_iou[1] < 0.7):
            final_result[kt] = 'missing bounding box'
            BB_mapping[kt] = max_iou[0]
            if max_iou[0] not in true_label:
                final_result[max_iou[0]] = 'done'
            labeled = True
            iou_score[kt] = max_iou[1]

        if(not labeled and same_label):
            #generate random label for pred_label and labeled as missing object
            identity = max_iou[0].split(":")
            current_random_number = random_number
            new_label = identity[0] + ":" + str(current_random_number + 1)
            final_result[new_label] = 'extra bounding box'
            if(final_result[kt] == 'unclassified'):
                final_result[kt] = 'done'
            BB_mapping[new_label] = kt
            iou_score[new_label] = ""
            random_number = current_random_number + 1

        elif(not labeled and not same_label):
            final_result[kt] = 'extra bounding box'
            iou_score[kt] = ""

    #rest of the unclassified objects as missing labels
    for keys in final_result:
        if(final_result[keys] == 'unclassified'):
            if((keys in pred_label)):
                final_result[keys] = 'missing object'
                iou_score[keys] = ""

    return final_result, BB_mapping, iou_score, wrong_label

"""
# wrong id -> wrong label
"""
def check_for_wrong_id_BB(final_result, box_score):
    for keys in final_result:
        if(final_result[keys] != 'missing object' and final_result[keys] != 'wrong id' and final_result[keys] != 'extra object'):
            if(keys in box_score and box_score[keys] <= 0.6):
                final_result[keys] = 'wrong id'
    return final_result
"""
"""
def test_results_for_BB(true_label, pred_label, final_result, box_score, BB_mapping, wrong_label):

    final_result = init_all_ids(true_label, pred_label, final_result, 0)
    final_result, BB_mapping, iou_score, wrong_label = find_missing_object_BB(true_label, pred_label, final_result, BB_mapping, wrong_label)
    final_result = check_for_wrong_id_BB(final_result, box_score)
    return final_result, iou_score, BB_mapping, wrong_label

"""
"""
def mark_everything_as_extra_bounding_box_and_missing_objects(list, tag):
    final_result = {}
    for key in list:
        final_result[key] = tag

    return final_result

"""
"""
def check_cases_for_labels(true_label, predicted_labels):
    if(true_label == {} and predicted_labels == {}):
        return {},{}
    elif(true_label != {} and predicted_labels == {}):
        # all extra bounding boxes
        final_result = mark_everything_as_extra_bounding_box_and_missing_objects(true_label, "extra bounding box")
        summary, json_output = generate_summary(true_label, predicted_labels, final_result, "", "", 0, "missing bounding box",
                         "", "", False, "")

    elif(true_label == {} and predicted_labels != {}):
        # all missing_objects
        final_result = mark_everything_as_extra_bounding_box_and_missing_objects(predicted_labels, "missing object")
        summary, json_output = generate_summary(true_label, predicted_labels, final_result, "", "", 0, "missing bounding box",
                                                "", "", False, "")

    return summary, json_output

"""
"""
def process_BB_images(mask, pred_label, instance_mask_path, manual_labels):
    wrong_label = {}

    true_label = compute_ground_truth_for_BB(mask, instance_mask_path,manual_labels)
    #true_label = ground_truth_for_deepScale_BB(mask, instance_mask_path, manual_labels)

    pred_label, box_score = compute_predicted_output_for_BB(pred_label, getImageName(mask).encode("utf8"))
    #pred_label, box_score = compute_predicted_output_for_BB(pred_label, getImageName(mask).encode("utf8") + ".jpg") # for deepscale

    if(true_label == {} or pred_label == {}):
        summary, json_output = check_cases_for_labels(true_label, pred_label)

    else:
        final_result = {}
        BB_mapping = {}
        # testing
        final_result, iou_score, BB_mapping, wrong_label = test_results_for_BB(true_label, pred_label, final_result, box_score,
                                                                  BB_mapping, wrong_label)
        summary, json_output = generate_summary(true_label, pred_label, final_result, "", "", 0, "missing bounding box",
                                                iou_score, BB_mapping, False, wrong_label)
    #print("Sumary", summary)
    return json_output, summary

"""
"""
def init_system_for_bounding_box_QA(label1, pred_label, batch_script, count_of_images, instance_mask_path, manual_labels):
    if(batch_script == 'on'):
        slice_of_files, slice_of_masks = process_batch_script("", label1, instance_mask_path, count_of_images, "", "", "", pred_label)
        json_output_list = []
        summary_list = []
        for masks in slice_of_masks:
            print("======Working on=====")
            print("-file", masks)

            json_output, summary = process_BB_images(masks, pred_label, instance_mask_path,manual_labels)
            new_key = {}

            #TODO instead of "masks", use filename of image
            new_key[masks] = json_output
            json_output_list.append(new_key)
            new_key = {}
            new_key[masks] = summary
            summary_list.append(new_key)
        #TODO uncomment
        #os.remove(pred_label)
        return json_output_list, summary_list

    else:
        json_output, summary = process_BB_images(label1, pred_label,manual_labels)
        #TODO uncomment
        #os.remove(pred_label)
        return json_output, summary


# image_path = "" in Bounding box mode
def process_batch_script(starting_img, starting_mask_file, instance_mask_path, count, private_key_location, bucket_name, image_folder, predicted_label):
    all_files = []
    all_mask = []

    # if BB mode is enabled
    if(bucket_name == ""):
        #TODO uncomment it
        #pred_label_file = get_predicted_labels_from_cloud(predicted_label, private_key_location, bucket_name, image_folder)
        pred_label_file = {"0000000387.png": {"car": {"car:2": {"box": [290, 181, 129, 67], "box_score": 0.9746655225753784}, "car:1": {"box": [840, 163, 187, 68], "box_score": 0.9970182180404663}, "car:3": {"box": [543, 177, 129, 42], "box_score": 0.9698275923728943}}, "traffic light": {"traffic light:2": {"box": [994, 45, 29, 69], "box_score": 0.6369136571884155}, "traffic light:1": {"box": [410, 36, 30, 77], "box_score": 0.7750337719917297}}}, "0000000084.png": {"car": {"car:2": {"box": [368, 188, 93, 55], "box_score": 0.9277219772338867}, "car:1": {"box": [19, 191, 283, 150], "box_score": 0.9573765397071838}, "car:4": {"box": [891, 186, 379, 183], "box_score": 0.9213622212409973}, "car:5": {"box": [497, 182, 29, 29], "box_score": 0.7581731081008911}, "car:3": {"box": [441, 185, 49, 41], "box_score": 0.9228635430335999}, "car:6": {"box": [767, 158, 102, 35], "box_score": 0.6718591451644897}}}, "0000000090.png": {"car": {"car:2": {"box": [813, 156, 114, 45], "box_score": 0.9805456399917603}, "car:7": {"box": [1137, 136, 64, 42], "box_score": 0.8121716976165771}, "car:1": {"box": [220, 194, 161, 93], "box_score": 0.9859094023704529}, "car:4": {"box": [460, 188, 39, 36], "box_score": 0.8591427803039551}, "car:8": {"box": [1188, 132, 54, 46], "box_score": 0.8017651438713074}, "car:5": {"box": [491, 185, 37, 30], "box_score": 0.8533581495285034}, "car:3": {"box": [363, 194, 77, 59], "box_score": 0.9318259954452515}, "car:6": {"box": [421, 191, 50, 45], "box_score": 0.8431958556175232}}}, "0000000212.png": {"car": {"car:2": {"box": [195, 173, 239, 120], "box_score": 0.9307055473327637}, "car:5": {"box": [100, 188, 91, 35], "box_score": 0.6116049885749817}, "car:1": {"box": [509, 184, 80, 47], "box_score": 0.931103527545929}, "car:3": {"box": [20, 195, 163, 75], "box_score": 0.9043330550193787}, "car:4": {"box": [436, 184, 62, 43], "box_score": 0.8715549111366272}}}, "0000000324.png": {"car": {"car:2": {"box": [835, 192, 393, 172], "box_score": 0.9700451493263245}, "car:7": {"box": [572, 176, 38, 16], "box_score": 0.6909756064414978}, "car:1": {"box": [417, 183, 74, 49], "box_score": 0.9839493632316589}, "car:4": {"box": [2, 211, 273, 162], "box_score": 0.954171895980835}, "car:5": {"box": [471, 179, 46, 40], "box_score": 0.9120708107948303}, "car:3": {"box": [757, 185, 139, 96], "box_score": 0.9699203372001648}, "car:6": {"box": [716, 180, 72, 66], "box_score": 0.8599551320075989}}}, "0000000249.png": {"car": {"car:2": {"box": [481, 179, 68, 43], "box_score": 0.9577532410621643}, "car:7": {"box": [545, 181, 27, 29], "box_score": 0.681269645690918}, "car:1": {"box": [747, 187, 136, 84], "box_score": 0.9726612567901611}, "car:4": {"box": [717, 179, 77, 62], "box_score": 0.8703230619430542}, "car:5": {"box": [1118, 175, 122, 55], "box_score": 0.7209230065345764}, "car:3": {"box": [973, 167, 187, 53], "box_score": 0.8913610577583313}, "car:6": {"box": [686, 173, 32, 26], "box_score": 0.6886581182479858}}}, "0000000054.png": {"car": {"car:2": {"box": [421, 185, 89, 59], "box_score": 0.9742445349693298}, "car:1": {"box": [1, 210, 166, 137], "box_score": 0.9788706302642822}, "car:4": {"box": [730, 164, 100, 39], "box_score": 0.9099180102348328}, "car:5": {"box": [630, 179, 38, 28], "box_score": 0.8365549445152283}, "car:3": {"box": [290, 196, 103, 60], "box_score": 0.9640413522720337}, "car:6": {"box": [497, 185, 34, 37], "box_score": 0.8215130567550659}}}, "0000000073.png": {"car": {"car:2": {"box": [821, 160, 159, 62], "box_score": 0.9346104264259338}, "car:7": {"box": [371, 183, 85, 60], "box_score": 0.7330623269081116}, "car:1": {"box": [101, 203, 214, 113], "box_score": 0.984687864780426}, "car:9": {"box": [489, 182, 29, 31], "box_score": 0.6099200248718262}, "car:4": {"box": [685, 178, 91, 64], "box_score": 0.9148581624031067}, "car:8": {"box": [949, 148, 209, 95], "box_score": 0.6153654456138611}, "car:5": {"box": [457, 183, 45, 35], "box_score": 0.8447722792625427}, "car:3": {"box": [1006, 163, 233, 103], "box_score": 0.9291452765464783}, "car:6": {"box": [328, 208, 75, 47], "box_score": 0.7732630968093872}}}, "0000000349.png": {"truck": {"truck:1": {"box": [478, 149, 82, 58], "box_score": 0.7901889681816101}}, "car": {"car:2": {"box": [5, 182, 121, 64], "box_score": 0.9110985398292542}, "car:1": {"box": [341, 182, 81, 31], "box_score": 0.9712475538253784}, "car:3": {"box": [632, 174, 67, 25], "box_score": 0.8903414011001587}, "car:4": {"box": [443, 175, 52, 48], "box_score": 0.8442079424858093}}}, "0000000390.png": {"car": {"car:2": {"box": [517, 178, 131, 45], "box_score": 0.9866195917129517}, "car:1": {"box": [245, 186, 150, 71], "box_score": 0.9974358677864075}, "car:3": {"box": [969, 161, 202, 70], "box_score": 0.9666877388954163}}, "traffic light": {"traffic light:2": {"box": [1006, 37, 33, 78], "box_score": 0.7821778059005737}, "traffic light:1": {"box": [394, 32, 31, 80], "box_score": 0.8638713359832764}}}, "0000000234.png": {"car": {"car:2": {"box": [689, 196, 204, 125], "box_score": 0.9604493975639343}, "car:7": {"box": [776, 174, 117, 50], "box_score": 0.7699170112609863}, "car:1": {"box": [1, 253, 106, 121], "box_score": 0.9788370132446289}, "car:4": {"box": [1064, 175, 116, 62], "box_score": 0.9180659055709839}, "car:8": {"box": [386, 190, 47, 34], "box_score": 0.6994044780731201}, "car:5": {"box": [562, 189, 68, 46], "box_score": 0.9069154858589172}, "car:3": {"box": [48, 212, 205, 143], "box_score": 0.9424455761909485}, "car:6": {"box": [997, 161, 247, 210], "box_score": 0.7917468547821045}}}, "0000000299.png": {"car": {"car:2": {"box": [423, 184, 85, 56], "box_score": 0.9827620387077332}, "car:10": {"box": [979, 175, 34, 29], "box_score": 0.6091548204421997}, "car:1": {"box": [903, 206, 345, 165], "box_score": 0.9878365397453308}, "car:11": {"box": [706, 180, 33, 40], "box_score": 0.6007965803146362}, "car:4": {"box": [786, 181, 171, 112], "box_score": 0.9334864616394043}, "car:9": {"box": [693, 178, 27, 37], "box_score": 0.6366659998893738}, "car:8": {"box": [518, 185, 30, 30], "box_score": 0.6511958241462708}, "car:7": {"box": [552, 178, 38, 23], "box_score": 0.7382466793060303}, "car:5": {"box": [490, 184, 40, 39], "box_score": 0.8202780485153198}, "car:3": {"box": [744, 182, 83, 68], "box_score": 0.9457211494445801}, "car:6": {"box": [720, 181, 44, 47], "box_score": 0.8145397901535034}}}, "0000000067.png": {"car": {"car:2": {"box": [188, 200, 229, 141], "box_score": 0.9958301186561584}, "car:10": {"box": [1005, 153, 81, 36], "box_score": 0.658178448677063}, "car:1": {"box": [2, 265, 165, 106], "box_score": 0.9968895316123962}, "car:9": {"box": [1084, 148, 43, 42], "box_score": 0.6914463639259338}, "car:4": {"box": [1125, 137, 105, 52], "box_score": 0.7746449112892151}, "car:8": {"box": [762, 167, 84, 44], "box_score": 0.7072922587394714}, "car:7": {"box": [660, 182, 58, 50], "box_score": 0.7302263379096985}, "car:5": {"box": [480, 187, 38, 27], "box_score": 0.7711318731307983}, "car:3": {"box": [834, 165, 212, 68], "box_score": 0.9815356135368347}, "car:6": {"box": [411, 189, 63, 44], "box_score": 0.7551238536834717}}}, "0000000392.png": {"car": {"car:2": {"box": [498, 178, 136, 46], "box_score": 0.9869825839996338}, "car:1": {"box": [214, 186, 165, 77], "box_score": 0.9983812570571899}, "car:3": {"box": [1054, 157, 178, 73], "box_score": 0.9114763140678406}}, "traffic light": {"traffic light:2": {"box": [356, 34, 33, 76], "box_score": 0.61495441198349}, "traffic light:1": {"box": [385, 27, 32, 83], "box_score": 0.7221698760986328}}}, "0000000075.png": {"car": {"car:2": {"box": [698, 178, 108, 75], "box_score": 0.9388156533241272}, "car:7": {"box": [339, 182, 101, 67], "box_score": 0.7941372394561768}, "car:1": {"box": [4, 209, 251, 145], "box_score": 0.9942399263381958}, "car:4": {"box": [1064, 140, 179, 137], "box_score": 0.8761947751045227}, "car:8": {"box": [486, 182, 29, 27], "box_score": 0.6698446273803711}, "car:5": {"box": [855, 155, 194, 70], "box_score": 0.8503472208976746}, "car:3": {"box": [448, 183, 53, 35], "box_score": 0.9042798280715942}, "car:6": {"box": [289, 206, 92, 58], "box_score": 0.8192065358161926}}}, "0000000034.png": {"car": {"car:2": {"box": [718, 178, 144, 96], "box_score": 0.9815627336502075}, "car:5": {"box": [555, 177, 30, 22], "box_score": 0.7289672493934631}, "car:1": {"box": [6, 208, 264, 135], "box_score": 0.9952360987663269}, "car:3": {"box": [259, 200, 137, 78], "box_score": 0.9098406434059143}, "car:4": {"box": [391, 179, 76, 58], "box_score": 0.892219066619873}}, "traffic light": {"traffic light:1": {"box": [130, 124, 60, 38], "box_score": 0.630174458026886}}}, "0000000270.png": {"truck": {"truck:1": {"box": [708, 175, 56, 47], "box_score": 0.6180938482284546}}, "car": {"car:2": {"box": [471, 190, 50, 47], "box_score": 0.9457545280456543}, "car:5": {"box": [453, 191, 49, 55], "box_score": 0.7815825343132019}, "car:1": {"box": [155, 192, 233, 144], "box_score": 0.9928465485572815}, "car:3": {"box": [152, 179, 100, 45], "box_score": 0.9442690014839172}, "car:4": {"box": [363, 187, 103, 84], "box_score": 0.9092879891395569}}}, "0000000292.png": {"car": {"car:2": {"box": [771, 196, 132, 87], "box_score": 0.9484956860542297}, "car:5": {"box": [717, 188, 34, 44], "box_score": 0.695819079875946}, "car:1": {"box": [486, 189, 68, 40], "box_score": 0.9610612988471985}, "car:3": {"box": [736, 189, 77, 61], "box_score": 0.8990222215652466}, "car:4": {"box": [572, 184, 33, 22], "box_score": 0.7010758519172668}}}, "0000000206.png": {"car": {"car:2": {"box": [347, 185, 83, 47], "box_score": 0.9140787124633789}, "car:1": {"box": [16, 174, 265, 120], "box_score": 0.9672872424125671}, "car:3": {"box": [277, 188, 59, 39], "box_score": 0.7414765357971191}}}, "0000000138.png": {"car": {"car:2": {"box": [255, 189, 140, 85], "box_score": 0.9755529165267944}, "car:5": {"box": [699, 180, 53, 48], "box_score": 0.7455455660820007}, "car:1": {"box": [764, 177, 239, 147], "box_score": 0.9924309849739075}, "car:3": {"box": [712, 182, 113, 76], "box_score": 0.9396414756774902}, "car:4": {"box": [381, 187, 64, 60], "box_score": 0.9286859035491943}}}, "0000000232.png": {"car": {"car:2": {"box": [641, 195, 170, 104], "box_score": 0.9491802453994751}, "car:7": {"box": [352, 190, 47, 32], "box_score": 0.8474681973457336}, "car:1": {"box": [1, 241, 130, 125], "box_score": 0.9909095168113708}, "car:4": {"box": [527, 189, 65, 42], "box_score": 0.9326242208480835}, "car:5": {"box": [734, 172, 98, 48], "box_score": 0.890730082988739}, "car:3": {"box": [61, 213, 182, 121], "box_score": 0.9342249631881714}, "car:6": {"box": [906, 131, 354, 240], "box_score": 0.8556821346282959}}}, "0000000297.png": {"car": {"car:2": {"box": [445, 187, 79, 49], "box_score": 0.9730058908462524}, "car:7": {"box": [693, 180, 31, 37], "box_score": 0.6577087640762329}, "car:1": {"box": [847, 199, 303, 158], "box_score": 0.9947104454040527}, "car:4": {"box": [732, 181, 69, 62], "box_score": 0.9136014580726624}, "car:8": {"box": [527, 186, 28, 28], "box_score": 0.6495000123977661}, "car:5": {"box": [714, 184, 40, 42], "box_score": 0.703996479511261}, "car:3": {"box": [765, 185, 135, 88], "box_score": 0.9190099835395813}, "car:6": {"box": [506, 186, 35, 34], "box_score": 0.7036169171333313}}}, "0000000120.png": {"car": {"car:2": {"box": [734, 180, 140, 88], "box_score": 0.9892025589942932}, "car:7": {"box": [661, 176, 53, 38], "box_score": 0.8029983043670654}, "car:1": {"box": [941, 186, 297, 179], "box_score": 0.9969835877418518}, "car:4": {"box": [693, 179, 67, 61], "box_score": 0.9485086798667908}, "car:8": {"box": [89, 191, 78, 37], "box_score": 0.7922719120979309}, "car:5": {"box": [344, 185, 110, 64], "box_score": 0.927222728729248}, "car:3": {"box": [13, 202, 291, 137], "box_score": 0.984637439250946}, "car:6": {"box": [468, 175, 62, 35], "box_score": 0.8238258361816406}}}, "0000000095.png": {"bus": {"bus:1": {"box": [16, 168, 167, 60], "box_score": 0.8389025926589966}}, "car": {"car:2": {"box": [-2, 211, 245, 161], "box_score": 0.9726496338844299}, "car:10": {"box": [1190, 138, 53, 41], "box_score": 0.6045350432395935}, "car:1": {"box": [851, 150, 159, 59], "box_score": 0.9926764965057373}, "car:9": {"box": [653, 175, 72, 37], "box_score": 0.6622274518013}, "car:4": {"box": [225, 201, 139, 91], "box_score": 0.9432229399681091}, "car:8": {"box": [806, 158, 64, 45], "box_score": 0.6779627799987793}, "car:7": {"box": [457, 186, 48, 36], "box_score": 0.8501766324043274}, "car:5": {"box": [409, 190, 58, 47], "box_score": 0.9426515698432922}, "car:3": {"box": [347, 196, 77, 64], "box_score": 0.9497901201248169}, "car:6": {"box": [1148, 132, 84, 46], "box_score": 0.8742880821228027}}}, "0000000325.png": {"car": {"car:2": {"box": [1, 217, 228, 153], "box_score": 0.9750224947929382}, "car:7": {"box": [560, 176, 39, 15], "box_score": 0.805506706237793}, "car:1": {"box": [406, 182, 78, 52], "box_score": 0.9880131483078003}, "car:4": {"box": [464, 178, 47, 43], "box_score": 0.9482867121696472}, "car:5": {"box": [901, 200, 366, 166], "box_score": 0.9251099824905396}, "car:3": {"box": [770, 182, 163, 105], "box_score": 0.9703783988952637}, "car:6": {"box": [725, 184, 75, 65], "box_score": 0.894868016242981}}}, "0000000305.png": {"car": {"car:2": {"box": [797, 188, 207, 116], "box_score": 0.9864305257797241}, "car:7": {"box": [531, 180, 38, 26], "box_score": 0.7570412755012512}, "car:1": {"box": [325, 190, 130, 79], "box_score": 0.9959322810173035}, "car:9": {"box": [694, 180, 29, 40], "box_score": 0.6050765514373779}, "car:4": {"box": [433, 186, 68, 52], "box_score": 0.8964986801147461}, "car:8": {"box": [481, 187, 41, 37], "box_score": 0.6107698678970337}, "car:5": {"box": [922, 191, 319, 174], "box_score": 0.8948568105697632}, "car:3": {"box": [740, 186, 95, 71], "box_score": 0.9666081070899963}, "car:6": {"box": [712, 180, 51, 52], "box_score": 0.8176233768463135}}}, "0000000435.png": {"traffic light": {"traffic light:2": {"box": [349, 9, 39, 101], "box_score": 0.6846799850463867}, "traffic light:1": {"box": [1046, 28, 33, 78], "box_score": 0.8480047583580017}}}, "0000000295.png": {"car": {"car:2": {"box": [756, 185, 100, 76], "box_score": 0.9291151165962219}, "car:7": {"box": [930, 176, 53, 27], "box_score": 0.6903219819068909}, "car:1": {"box": [460, 186, 79, 46], "box_score": 0.9394450187683105}, "car:9": {"box": [714, 184, 33, 43], "box_score": 0.6179988384246826}, "car:4": {"box": [958, 164, 280, 204], "box_score": 0.8771268725395203}, "car:8": {"box": [693, 180, 27, 36], "box_score": 0.6782776117324829}, "car:5": {"box": [725, 184, 51, 52], "box_score": 0.814027726650238}, "car:3": {"box": [811, 199, 206, 117], "box_score": 0.9204069375991821}, "car:6": {"box": [564, 183, 33, 20], "box_score": 0.712069571018219}}}, "0000000300.png": {"car": {"car:2": {"box": [949, 218, 294, 153], "box_score": 0.9836916923522949}, "car:7": {"box": [551, 179, 38, 21], "box_score": 0.7140944004058838}, "car:1": {"box": [410, 186, 91, 57], "box_score": 0.9861654043197632}, "car:9": {"box": [705, 180, 33, 40], "box_score": 0.6238923072814941}, "car:4": {"box": [751, 185, 86, 71], "box_score": 0.945615828037262}, "car:8": {"box": [693, 178, 26, 37], "box_score": 0.6567478775978088}, "car:5": {"box": [720, 181, 55, 51], "box_score": 0.8879624605178833}, "car:3": {"box": [797, 180, 198, 123], "box_score": 0.9557434320449829}, "car:6": {"box": [481, 183, 49, 41], "box_score": 0.8798078298568726}}}, "0000000089.png": {"car": {"car:2": {"box": [804, 156, 114, 42], "box_score": 0.9662362337112427}, "car:7": {"box": [1109, 138, 79, 38], "box_score": 0.7905411720275879}, "car:1": {"box": [258, 196, 143, 80], "box_score": 0.9889461398124695}, "car:9": {"box": [531, 180, 34, 23], "box_score": 0.6354150176048279}, "car:4": {"box": [466, 186, 40, 34], "box_score": 0.9073395133018494}, "car:8": {"box": [1058, 141, 61, 35], "box_score": 0.6580848693847656}, "car:5": {"box": [428, 188, 54, 44], "box_score": 0.8088415265083313}, "car:3": {"box": [380, 192, 69, 55], "box_score": 0.9396007657051086}, "car:6": {"box": [496, 182, 35, 30], "box_score": 0.7951662540435791}}}, "0000000256.png": {"car": {"car:2": {"box": [759, 189, 143, 85], "box_score": 0.9793558716773987}, "car:1": {"box": [837, 204, 335, 160], "box_score": 0.9992533326148987}, "car:4": {"box": [442, 185, 84, 54], "box_score": 0.9695881605148315}, "car:5": {"box": [534, 187, 30, 30], "box_score": 0.7638999223709106}, "car:3": {"box": [1120, 184, 122, 58], "box_score": 0.9752179980278015}, "car:6": {"box": [692, 176, 39, 32], "box_score": 0.6907699108123779}}}, "0000000048.png": {"car": {"car:2": {"box": [1, 185, 211, 183], "box_score": 0.9656900763511658}, "car:7": {"box": [1173, 152, 71, 38], "box_score": 0.6683396100997925}, "car:1": {"box": [199, 190, 154, 94], "box_score": 0.9834933280944824}, "car:4": {"box": [703, 162, 92, 34], "box_score": 0.9377422332763672}, "car:5": {"box": [619, 175, 43, 25], "box_score": 0.8613365292549133}, "car:3": {"box": [386, 186, 63, 43], "box_score": 0.9610053300857544}, "car:6": {"box": [483, 182, 56, 40], "box_score": 0.8466175198554993}}}, "0000000221.png": {"car": {"car:2": {"box": [736, 177, 69, 48], "box_score": 0.9495809078216553}, "car:7": {"box": [823, 173, 106, 60], "box_score": 0.8968074917793274}, "car:1": {"box": [343, 195, 123, 67], "box_score": 0.9802675247192383}, "car:9": {"box": [177, 184, 32, 22], "box_score": 0.6948872208595276}, "car:4": {"box": [0, 190, 61, 36], "box_score": 0.9427633881568909}, "car:8": {"box": [210, 189, 39, 31], "box_score": 0.7158277034759521}, "car:5": {"box": [422, 178, 81, 42], "box_score": 0.9338555932044983}, "car:3": {"box": [480, 164, 261, 149], "box_score": 0.9443548917770386}, "car:6": {"box": [220, 189, 67, 39], "box_score": 0.9287443161010742}}}, "0000000039.png": {"car": {"car:2": {"box": [776, 180, 311, 179], "box_score": 0.9858745336532593}, "car:7": {"box": [505, 179, 36, 26], "box_score": 0.7052662968635559}, "car:1": {"box": [3, 206, 282, 139], "box_score": 0.9889556765556335}, "car:4": {"box": [538, 177, 35, 26], "box_score": 0.8886762857437134}, "car:8": {"box": [973, 161, 128, 29], "box_score": 0.6828433275222778}, "car:5": {"box": [409, 181, 50, 50], "box_score": 0.844856321811676}, "car:3": {"box": [299, 178, 126, 79], "box_score": 0.9218388199806213}, "car:6": {"box": [695, 166, 72, 26], "box_score": 0.7693796753883362}}}, "0000000413.png": {"car": {"car:1": {"box": [189, 191, 213, 100], "box_score": 0.9848991632461548}}, "traffic light": {"traffic light:2": {"box": [348, 13, 41, 100], "box_score": 0.7110307812690735}, "traffic light:3": {"box": [401, 47, 36, 62], "box_score": 0.6207802295684814}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.7986816167831421}}}, "0000000044.png": {"car": {"car:2": {"box": [129, 179, 212, 117], "box_score": 0.9522278308868408}, "car:7": {"box": [486, 180, 33, 29], "box_score": 0.8037569522857666}, "car:1": {"box": [990, 257, 249, 117], "box_score": 0.9816095232963562}, "car:4": {"box": [421, 183, 56, 39], "box_score": 0.8985955715179443}, "car:8": {"box": [629, 175, 31, 23], "box_score": 0.7277402281761169}, "car:5": {"box": [325, 181, 93, 70], "box_score": 0.8865336775779724}, "car:3": {"box": [692, 162, 86, 31], "box_score": 0.9252758026123047}, "car:6": {"box": [513, 179, 42, 31], "box_score": 0.8395282030105591}}}, "0000000086.png": {"car": {"car:2": {"box": [967, 202, 279, 170], "box_score": 0.9914359450340271}, "car:10": {"box": [1060, 142, 57, 34], "box_score": 0.6650902628898621}, "car:1": {"box": [3, 205, 220, 165], "box_score": 0.9969071745872498}, "car:9": {"box": [1110, 137, 125, 42], "box_score": 0.7418941259384155}, "car:4": {"box": [421, 187, 58, 45], "box_score": 0.9599652290344238}, "car:8": {"box": [1024, 145, 54, 31], "box_score": 0.7499045133590698}, "car:7": {"box": [485, 183, 35, 30], "box_score": 0.7579111456871033}, "car:5": {"box": [780, 156, 66, 38], "box_score": 0.8093511462211609}, "car:3": {"box": [333, 189, 108, 66], "box_score": 0.9717093110084534}, "car:6": {"box": [510, 181, 35, 25], "box_score": 0.7997150421142578}}}, "0000000094.png": {"car": {"car:2": {"box": [846, 152, 145, 56], "box_score": 0.9777039289474487}, "car:7": {"box": [465, 185, 47, 36], "box_score": 0.8275423645973206}, "car:1": {"box": [1, 206, 282, 154], "box_score": 0.9827334880828857}, "car:9": {"box": [652, 175, 67, 34], "box_score": 0.6242262125015259}, "car:4": {"box": [420, 190, 53, 44], "box_score": 0.9285261631011963}, "car:8": {"box": [1132, 137, 80, 41], "box_score": 0.6518684029579163}, "car:5": {"box": [263, 199, 120, 81], "box_score": 0.9200889468193054}, "car:3": {"box": [369, 194, 66, 60], "box_score": 0.9589313864707947}, "car:6": {"box": [1170, 139, 72, 40], "box_score": 0.8666847348213196}}}, "0000000088.png": {"car": {"car:2": {"box": [805, 157, 102, 39], "box_score": 0.9427608847618103}, "car:10": {"box": [747, 156, 66, 37], "box_score": 0.6098042130470276}, "car:1": {"box": [286, 193, 132, 75], "box_score": 0.9713841080665588}, "car:9": {"box": [441, 186, 46, 43], "box_score": 0.6912768483161926}, "car:4": {"box": [1145, 133, 93, 45], "box_score": 0.9015946388244629}, "car:8": {"box": [499, 181, 34, 27], "box_score": 0.792600691318512}, "car:7": {"box": [1046, 143, 63, 32], "box_score": 0.8198978900909424}, "car:5": {"box": [397, 190, 65, 51], "box_score": 0.8912859559059143}, "car:3": {"box": [1, 266, 94, 109], "box_score": 0.9243125915527344}, "car:6": {"box": [473, 184, 37, 33], "box_score": 0.8562509417533875}}}, "0000000315.png": {"car": {"car:2": {"box": [0, 217, 190, 154], "box_score": 0.9857941269874573}, "car:7": {"box": [733, 184, 71, 69], "box_score": 0.898410975933075}, "car:1": {"box": [167, 196, 213, 123], "box_score": 0.9901187419891357}, "car:9": {"box": [690, 179, 37, 40], "box_score": 0.7900831699371338}, "car:5": {"box": [767, 187, 190, 107], "box_score": 0.9539072513580322}, "car:3": {"box": [900, 196, 341, 173], "box_score": 0.9654972553253174}, "car:6": {"box": [354, 192, 101, 71], "box_score": 0.925536036491394}, "car:12": {"box": [706, 181, 43, 47], "box_score": 0.616064727306366}, "car:10": {"box": [718, 180, 52, 58], "box_score": 0.7355047464370728}, "car:11": {"box": [606, 175, 49, 17], "box_score": 0.6343947052955627}, "car:4": {"box": [485, 180, 52, 36], "box_score": 0.9572625756263733}, "car:8": {"box": [1154, 178, 87, 35], "box_score": 0.8684915900230408}}}, "0000000432.png": {"traffic light": {"traffic light:2": {"box": [349, 9, 39, 102], "box_score": 0.6935340762138367}, "traffic light:3": {"box": [403, 48, 34, 61], "box_score": 0.6179264783859253}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.8012667894363403}}}, "0000000210.png": {"car": {"car:2": {"box": [450, 184, 79, 47], "box_score": 0.956360936164856}, "car:1": {"box": [134, 175, 243, 116], "box_score": 0.9600496888160706}, "car:3": {"box": [1, 201, 95, 71], "box_score": 0.8464049696922302}, "car:4": {"box": [375, 183, 64, 42], "box_score": 0.8306782245635986}}}, "0000000051.png": {"car": {"car:2": {"box": [344, 193, 81, 53], "box_score": 0.9780433177947998}, "car:5": {"box": [628, 180, 35, 28], "box_score": 0.858053982257843}, "car:1": {"box": [18, 195, 268, 129], "box_score": 0.9780561923980713}, "car:3": {"box": [713, 166, 94, 36], "box_score": 0.9772623777389526}, "car:4": {"box": [458, 187, 69, 47], "box_score": 0.921442985534668}}}, "0000000233.png": {"car": {"car:2": {"box": [670, 193, 178, 114], "box_score": 0.959244966506958}, "car:7": {"box": [962, 129, 307, 243], "box_score": 0.8042767643928528}, "car:1": {"box": [0, 247, 125, 123], "box_score": 0.9700970649719238}, "car:4": {"box": [548, 191, 62, 41], "box_score": 0.8562096357345581}, "car:8": {"box": [539, 187, 34, 35], "box_score": 0.6352209448814392}, "car:5": {"box": [754, 174, 108, 46], "box_score": 0.8351269364356995}, "car:3": {"box": [59, 213, 186, 136], "box_score": 0.9387009143829346}, "car:6": {"box": [370, 190, 41, 32], "box_score": 0.8334476947784424}}}, "0000000350.png": {"truck": {"truck:1": {"box": [459, 154, 124, 55], "box_score": 0.6841269135475159}}, "car": {"car:2": {"box": [0, 184, 88, 59], "box_score": 0.9523778557777405}, "car:1": {"box": [342, 182, 80, 32], "box_score": 0.9639047980308533}, "car:3": {"box": [629, 174, 70, 25], "box_score": 0.9028293490409851}, "car:4": {"box": [433, 176, 56, 51], "box_score": 0.8720820546150208}}, "person": {"person:1": {"box": [700, 170, 19, 44], "box_score": 0.6090476512908936}}}, "0000000332.png": {"car": {"car:2": {"box": [918, 195, 319, 176], "box_score": 0.9853590726852417}, "car:7": {"box": [605, 170, 50, 21], "box_score": 0.6371370553970337}, "car:1": {"box": [285, 184, 131, 80], "box_score": 0.9953445792198181}, "car:4": {"box": [730, 178, 90, 71], "box_score": 0.9655516147613525}, "car:5": {"box": [382, 177, 85, 61], "box_score": 0.9319088459014893}, "car:3": {"box": [768, 183, 208, 119], "box_score": 0.9761081337928772}, "car:6": {"box": [477, 176, 52, 19], "box_score": 0.7629954814910889}}}, "0000000411.png": {"car": {"car:1": {"box": [230, 186, 199, 94], "box_score": 0.9604621529579163}}, "traffic light": {"traffic light:2": {"box": [348, 13, 41, 100], "box_score": 0.6986322402954102}, "traffic light:1": {"box": [1047, 27, 32, 78], "box_score": 0.8699784278869629}}}, "0000000033.png": {"car": {"car:2": {"box": [710, 178, 132, 85], "box_score": 0.9787096977233887}, "car:5": {"box": [557, 176, 29, 22], "box_score": 0.6355572938919067}, "car:1": {"box": [66, 203, 234, 122], "box_score": 0.979377031326294}, "car:3": {"box": [284, 197, 122, 72], "box_score": 0.9656241536140442}, "car:4": {"box": [401, 179, 68, 56], "box_score": 0.923004686832428}}}, "0000000111.png": {"car": {"car:2": {"box": [0, 216, 165, 152], "box_score": 0.9877917170524597}, "car:7": {"box": [728, 183, 128, 84], "box_score": 0.9491584300994873}, "car:1": {"box": [796, 185, 295, 160], "box_score": 0.991346538066864}, "car:9": {"box": [650, 179, 35, 30], "box_score": 0.8233998417854309}, "car:5": {"box": [447, 186, 60, 41], "box_score": 0.9507887959480286}, "car:3": {"box": [201, 195, 191, 91], "box_score": 0.9877753257751465}, "car:6": {"box": [678, 179, 64, 49], "box_score": 0.9503358602523804}, "car:12": {"box": [93, 199, 42, 28], "box_score": 0.6424588561058044}, "car:10": {"box": [380, 191, 65, 59], "box_score": 0.7763623595237732}, "car:11": {"box": [557, 174, 43, 22], "box_score": 0.6663028597831726}, "car:4": {"box": [1059, 157, 188, 112], "box_score": 0.979229748249054}, "car:8": {"box": [502, 181, 32, 28], "box_score": 0.9060617685317993}}}, "0000000397.png": {"car": {"car:2": {"box": [486, 181, 104, 48], "box_score": 0.9168306589126587}, "car:1": {"box": [115, 193, 202, 97], "box_score": 0.9872178435325623}, "car:3": {"box": [444, 189, 54, 47], "box_score": 0.7359540462493896}}, "traffic light": {"traffic light:2": {"box": [365, 20, 34, 87], "box_score": 0.7316389679908752}, "traffic light:3": {"box": [413, 51, 34, 54], "box_score": 0.6008095145225525}, "traffic light:1": {"box": [1035, 31, 34, 80], "box_score": 0.7317097187042236}}}, "0000000294.png": {"car": {"car:2": {"box": [744, 186, 100, 76], "box_score": 0.9368464946746826}, "car:7": {"box": [709, 184, 37, 41], "box_score": 0.6833895444869995}, "car:1": {"box": [471, 187, 77, 42], "box_score": 0.979846179485321}, "car:9": {"box": [693, 181, 28, 37], "box_score": 0.6229783892631531}, "car:4": {"box": [902, 164, 341, 204], "box_score": 0.788524866104126}, "car:8": {"box": [565, 183, 33, 20], "box_score": 0.6409621834754944}, "car:5": {"box": [722, 186, 44, 47], "box_score": 0.7450514435768127}, "car:3": {"box": [802, 198, 177, 101], "box_score": 0.9274415969848633}, "car:6": {"box": [923, 178, 48, 27], "box_score": 0.6914599537849426}}}, "0000000141.png": {"car": {"car:2": {"box": [328, 193, 89, 67], "box_score": 0.9467197060585022}, "car:1": {"box": [147, 193, 194, 110], "box_score": 0.9841110706329346}, "car:4": {"box": [735, 183, 165, 109], "box_score": 0.9225674867630005}, "car:5": {"box": [714, 184, 65, 60], "box_score": 0.8510822653770447}, "car:3": {"box": [861, 187, 409, 182], "box_score": 0.9305132031440735}, "car:6": {"box": [883, 167, 48, 19], "box_score": 0.7345442771911621}}}, "0000000110.png": {"car": {"car:2": {"box": [238, 194, 166, 86], "box_score": 0.9797629714012146}, "car:10": {"box": [650, 179, 35, 31], "box_score": 0.7668414115905762}, "car:1": {"box": [775, 186, 246, 136], "box_score": 0.9937226176261902}, "car:11": {"box": [561, 176, 41, 20], "box_score": 0.7019846439361572}, "car:4": {"box": [1, 209, 220, 164], "box_score": 0.9775422811508179}, "car:9": {"box": [372, 186, 82, 61], "box_score": 0.8151038885116577}, "car:8": {"box": [504, 182, 34, 25], "box_score": 0.8435758948326111}, "car:7": {"box": [673, 180, 66, 46], "box_score": 0.9265620112419128}, "car:5": {"box": [455, 186, 55, 38], "box_score": 0.9609059691429138}, "car:3": {"box": [1013, 156, 231, 105], "box_score": 0.9794822335243225}, "car:6": {"box": [719, 181, 111, 79], "box_score": 0.9560086727142334}}}, "0000000074.png": {"car": {"car:2": {"box": [1026, 153, 217, 121], "box_score": 0.9116098880767822}, "car:7": {"box": [355, 183, 92, 63], "box_score": 0.6851890087127686}, "car:1": {"box": [27, 206, 260, 123], "box_score": 0.9897499680519104}, "car:4": {"box": [691, 177, 98, 72], "box_score": 0.8717148900032043}, "car:5": {"box": [312, 206, 84, 52], "box_score": 0.8593275547027588}, "car:3": {"box": [455, 184, 50, 33], "box_score": 0.8908759951591492}, "car:6": {"box": [835, 158, 177, 65], "box_score": 0.8402484655380249}}}, "0000000160.png": {"car": {"car:2": {"box": [164, 181, 154, 64], "box_score": 0.9501232504844666}, "car:1": {"box": [0, 209, 94, 44], "box_score": 0.9686335921287537}, "car:3": {"box": [857, 171, 90, 40], "box_score": 0.8564083576202393}, "car:4": {"box": [966, 165, 90, 41], "box_score": 0.820539653301239}}, "person": {"person:2": {"box": [1118, 124, 82, 199], "box_score": 0.7661539912223816}, "person:3": {"box": [1175, 145, 68, 183], "box_score": 0.6585947275161743}, "person:1": {"box": [1052, 129, 71, 187], "box_score": 0.8804903626441956}}}, "0000000262.png": {"car": {"car:2": {"box": [378, 184, 106, 76], "box_score": 0.9606282114982605}, "car:7": {"box": [589, 179, 39, 19], "box_score": 0.6324527859687805}, "car:1": {"box": [832, 192, 327, 168], "box_score": 0.9930029511451721}, "car:4": {"box": [464, 183, 56, 55], "box_score": 0.8565865755081177}, "car:5": {"box": [693, 175, 49, 37], "box_score": 0.7735474705696106}, "car:3": {"box": [512, 185, 40, 36], "box_score": 0.8843990564346313}, "car:6": {"box": [278, 177, 69, 33], "box_score": 0.7164218425750732}}}, "0000000001.png": {"car": {"car:2": {"box": [691, 184, 69, 60], "box_score": 0.9771574139595032}, "car:5": {"box": [860, 194, 375, 170], "box_score": 0.8198211193084717}, "car:1": {"box": [375, 195, 82, 56], "box_score": 0.9785254597663879}, "car:3": {"box": [731, 183, 143, 98], "box_score": 0.9611034393310547}, "car:4": {"box": [493, 190, 38, 25], "box_score": 0.9136881828308105}}}, "0000000235.png": {"car": {"car:2": {"box": [29, 217, 228, 150], "box_score": 0.9275143146514893}, "car:7": {"box": [406, 190, 45, 32], "box_score": 0.6727198362350464}, "car:1": {"box": [715, 196, 228, 135], "box_score": 0.977423906326294}, "car:4": {"box": [1122, 174, 120, 75], "box_score": 0.8820837736129761}, "car:5": {"box": [0, 266, 96, 110], "box_score": 0.8466560244560242}, "car:3": {"box": [584, 190, 64, 44], "box_score": 0.8923272490501404}, "car:6": {"box": [803, 174, 119, 53], "box_score": 0.8269653916358948}}}, "0000000371.png": {"traffic light": {"traffic light:2": {"box": [863, 92, 20, 43], "box_score": 0.6182298064231873}, "traffic light:1": {"box": [504, 88, 22, 50], "box_score": 0.6414366960525513}}, "car": {"car:2": {"box": [1, 208, 307, 163], "box_score": 0.982258677482605}, "car:1": {"box": [339, 176, 139, 54], "box_score": 0.9833094477653503}, "car:3": {"box": [635, 175, 99, 34], "box_score": 0.9052457213401794}}, "person": {"person:1": {"box": [1009, 159, 75, 149], "box_score": 0.9684236645698547}}}, "0000000172.png": {"car": {"car:2": {"box": [1056, 158, 188, 62], "box_score": 0.9795382618904114}, "car:1": {"box": [887, 169, 151, 60], "box_score": 0.9963670969009399}, "car:3": {"box": [180, 191, 76, 39], "box_score": 0.8707664012908936}}}, "0000000036.png": {"car": {"car:2": {"box": [738, 179, 183, 112], "box_score": 0.98167484998703}, "car:7": {"box": [635, 175, 32, 19], "box_score": 0.6342229247093201}, "car:1": {"box": [1, 215, 190, 160], "box_score": 0.9959815740585327}, "car:4": {"box": [362, 178, 88, 64], "box_score": 0.87714684009552}, "car:5": {"box": [550, 177, 33, 23], "box_score": 0.8263264298439026}, "car:3": {"box": [181, 201, 181, 94], "box_score": 0.9686710238456726}, "car:6": {"box": [518, 178, 30, 24], "box_score": 0.77107173204422}}}, "0000000439.png": {"traffic light": {"traffic light:2": {"box": [348, 9, 41, 103], "box_score": 0.6691097617149353}, "traffic light:3": {"box": [397, 45, 39, 68], "box_score": 0.6436433792114258}, "traffic light:1": {"box": [1047, 28, 33, 77], "box_score": 0.7634375691413879}}}, "0000000193.png": {"bicycle": {"bicycle:1": {"box": [960, 197, 86, 54], "box_score": 0.9598286747932434}}, "car": {"car:2": {"box": [170, 183, 89, 49], "box_score": 0.9332517385482788}, "car:1": {"box": [1135, 194, 107, 81], "box_score": 0.9569047689437866}, "car:3": {"box": [2, 177, 112, 107], "box_score": 0.8246899247169495}}}, "0000000253.png": {"car": {"car:2": {"box": [1045, 182, 201, 64], "box_score": 0.9882459044456482}, "car:1": {"box": [789, 198, 209, 119], "box_score": 0.9983521699905396}, "car:4": {"box": [741, 191, 105, 69], "box_score": 0.9574688673019409}, "car:5": {"box": [693, 183, 44, 27], "box_score": 0.8697063326835632}, "car:3": {"box": [466, 191, 69, 47], "box_score": 0.9742550849914551}, "car:6": {"box": [543, 191, 31, 27], "box_score": 0.7597994208335876}}}, "0000000393.png": {"car": {"car:2": {"box": [491, 178, 135, 48], "box_score": 0.9828181266784668}, "car:1": {"box": [200, 187, 168, 79], "box_score": 0.9984431862831116}, "car:3": {"box": [1097, 159, 147, 72], "box_score": 0.9668485522270203}}, "traffic light": {"traffic light:2": {"box": [375, 24, 39, 86], "box_score": 0.6804470419883728}, "traffic light:1": {"box": [1023, 34, 31, 74], "box_score": 0.8357365727424622}}}, "0000000170.png": {"car": {"car:2": {"box": [1042, 161, 191, 58], "box_score": 0.9618776440620422}, "car:1": {"box": [879, 171, 143, 57], "box_score": 0.9901973009109497}, "car:3": {"box": [204, 192, 71, 36], "box_score": 0.7847387790679932}, "car:4": {"box": [8, 187, 200, 80], "box_score": 0.6483801603317261}}}, "0000000037.png": {"car": {"car:2": {"box": [0, 222, 137, 144], "box_score": 0.9904136061668396}, "car:7": {"box": [693, 164, 62, 25], "box_score": 0.632985532283783}, "car:1": {"box": [752, 179, 208, 130], "box_score": 0.9913690686225891}, "car:4": {"box": [546, 177, 34, 23], "box_score": 0.8592029213905334}, "car:5": {"box": [342, 178, 100, 66], "box_score": 0.777636706829071}, "car:3": {"box": [126, 199, 212, 110], "box_score": 0.9700499773025513}, "car:6": {"box": [514, 178, 33, 23], "box_score": 0.7078331708908081}}}, "0000000155.png": {"car": {"car:2": {"box": [223, 177, 132, 55], "box_score": 0.9289019703865051}, "car:5": {"box": [68, 200, 94, 35], "box_score": 0.7131004333496094}, "car:1": {"box": [869, 206, 387, 163], "box_score": 0.9644235372543335}, "car:3": {"box": [812, 169, 102, 36], "box_score": 0.8973763585090637}, "car:4": {"box": [9, 206, 97, 45], "box_score": 0.7999427318572998}}, "person": {"person:2": {"box": [973, 140, 43, 89], "box_score": 0.6880326867103577}, "person:1": {"box": [910, 141, 54, 116], "box_score": 0.9302460551261902}}}, "0000000283.png": {"truck": {"truck:1": {"box": [749, 171, 121, 88], "box_score": 0.6900899410247803}}, "car": {"car:2": {"box": [267, 190, 150, 117], "box_score": 0.9713241457939148}, "car:1": {"box": [2, 211, 293, 162], "box_score": 0.9818135499954224}, "car:3": {"box": [531, 180, 49, 30], "box_score": 0.9339221119880676}, "car:4": {"box": [722, 184, 37, 45], "box_score": 0.8416131138801575}}}, "0000000148.png": {"car": {"car:2": {"box": [755, 180, 176, 115], "box_score": 0.9731940031051636}, "car:5": {"box": [323, 175, 84, 41], "box_score": 0.826288104057312}, "car:1": {"box": [74, 195, 221, 133], "box_score": 0.9771835803985596}, "car:3": {"box": [0, 216, 88, 160], "box_score": 0.9574213624000549}, "car:4": {"box": [869, 202, 395, 170], "box_score": 0.86271733045578}}}, "0000000099.png": {"car": {"car:2": {"box": [913, 145, 225, 71], "box_score": 0.9560494422912598}, "car:7": {"box": [802, 158, 106, 51], "box_score": 0.6632405519485474}, "car:1": {"box": [1, 216, 260, 147], "box_score": 0.9806379079818726}, "car:4": {"box": [246, 202, 123, 86], "box_score": 0.8952389359474182}, "car:5": {"box": [429, 189, 63, 42], "box_score": 0.8848881721496582}, "car:3": {"box": [360, 195, 78, 54], "box_score": 0.9357872009277344}, "car:6": {"box": [670, 175, 74, 50], "box_score": 0.8752729296684265}}}, "0000000282.png": {"car": {"car:2": {"box": [300, 195, 131, 99], "box_score": 0.9690874218940735}, "car:5": {"box": [718, 188, 36, 43], "box_score": 0.8314996361732483}, "car:1": {"box": [62, 214, 267, 154], "box_score": 0.9798446893692017}, "car:3": {"box": [0, 225, 74, 151], "box_score": 0.955437421798706}, "car:4": {"box": [535, 183, 49, 31], "box_score": 0.9352631568908691}}}, "0000000238.png": {"car": {"car:2": {"box": [799, 210, 362, 161], "box_score": 0.9782713055610657}, "car:7": {"box": [627, 184, 49, 40], "box_score": 0.6726489663124084}, "car:1": {"box": [0, 215, 252, 158], "box_score": 0.9823871850967407}, "car:4": {"box": [643, 185, 65, 51], "box_score": 0.84515380859375}, "car:5": {"box": [794, 177, 93, 33], "box_score": 0.8045679330825806}, "car:3": {"box": [896, 169, 124, 47], "box_score": 0.9135031700134277}, "car:6": {"box": [449, 185, 56, 35], "box_score": 0.7981003522872925}}}, "0000000386.png": {"car": {"car:2": {"box": [306, 180, 120, 65], "box_score": 0.9763012528419495}, "car:1": {"box": [803, 163, 181, 68], "box_score": 0.9982300400733948}, "car:3": {"box": [551, 177, 124, 42], "box_score": 0.9631522297859192}}}, "0000000046.png": {"car": {"car:2": {"box": [2, 183, 288, 151], "box_score": 0.9395138025283813}, "car:7": {"box": [1102, 156, 86, 30], "box_score": 0.6858472228050232}, "car:1": {"box": [696, 164, 90, 30], "box_score": 0.947178304195404}, "car:4": {"box": [266, 185, 122, 79], "box_score": 0.9013143181800842}, "car:8": {"box": [477, 182, 33, 28], "box_score": 0.6470133066177368}, "car:5": {"box": [627, 175, 33, 24], "box_score": 0.8006128072738647}, "car:3": {"box": [407, 185, 58, 40], "box_score": 0.9225978255271912}, "car:6": {"box": [502, 180, 45, 34], "box_score": 0.7583976984024048}}}, "0000000399.png": {"car": {"car:2": {"box": [457, 181, 112, 53], "box_score": 0.9365252256393433}, "car:1": {"box": [53, 195, 237, 114], "box_score": 0.9901662468910217}, "car:3": {"box": [420, 201, 45, 35], "box_score": 0.7221683263778687}}, "traffic light": {"traffic light:2": {"box": [398, 38, 44, 70], "box_score": 0.7542615532875061}, "traffic light:3": {"box": [1040, 28, 33, 78], "box_score": 0.679771363735199}, "traffic light:1": {"box": [351, 13, 42, 98], "box_score": 0.7893452048301697}}}, "0000000284.png": {"car": {"car:2": {"box": [0, 215, 254, 154], "box_score": 0.9570510387420654}, "car:1": {"box": [218, 185, 178, 128], "box_score": 0.9796231389045715}, "car:3": {"box": [526, 174, 43, 30], "box_score": 0.8906130790710449}, "car:4": {"box": [724, 175, 45, 49], "box_score": 0.8537501096725464}}}, "0000000203.png": {"bicycle": {"bicycle:1": {"box": [1168, 207, 71, 63], "box_score": 0.6843584179878235}}, "car": {"car:2": {"box": [289, 184, 83, 48], "box_score": 0.9593141078948975}, "car:1": {"box": [6, 177, 215, 114], "box_score": 0.9668086171150208}, "car:3": {"box": [220, 185, 70, 39], "box_score": 0.6993681192398071}}}, "0000000316.png": {"car": {"car:2": {"box": [944, 195, 298, 177], "box_score": 0.9661645889282227}, "car:10": {"box": [696, 181, 34, 42], "box_score": 0.6594367623329163}, "car:1": {"box": [95, 199, 267, 137], "box_score": 0.9854280352592468}, "car:9": {"box": [516, 181, 33, 30], "box_score": 0.7350122332572937}, "car:4": {"box": [0, 236, 111, 138], "box_score": 0.9481654167175293}, "car:8": {"box": [712, 182, 65, 54], "box_score": 0.7682840824127197}, "car:7": {"box": [738, 188, 91, 76], "box_score": 0.8632327914237976}, "car:5": {"box": [480, 181, 52, 38], "box_score": 0.9159725904464722}, "car:3": {"box": [779, 190, 224, 123], "box_score": 0.9641099572181702}, "car:6": {"box": [329, 194, 115, 77], "box_score": 0.8641180992126465}}}, "0000000298.png": {"car": {"car:2": {"box": [434, 186, 82, 52], "box_score": 0.9743859767913818}, "car:7": {"box": [713, 181, 44, 46], "box_score": 0.6973012685775757}, "car:1": {"box": [877, 206, 372, 165], "box_score": 0.9866873621940613}, "car:4": {"box": [736, 183, 77, 60], "box_score": 0.8960051536560059}, "car:8": {"box": [700, 179, 31, 39], "box_score": 0.6586962938308716}, "car:5": {"box": [497, 185, 40, 36], "box_score": 0.7953787446022034}, "car:3": {"box": [783, 182, 148, 100], "box_score": 0.9479999542236328}, "car:6": {"box": [555, 179, 37, 23], "box_score": 0.7656958699226379}}}, "0000000169.png": {"car": {"car:2": {"box": [1037, 161, 182, 57], "box_score": 0.9711779952049255}, "car:5": {"box": [233, 199, 53, 26], "box_score": 0.6164177060127258}, "car:1": {"box": [876, 171, 140, 55], "box_score": 0.9900302886962891}, "car:3": {"box": [14, 185, 205, 80], "box_score": 0.8634716272354126}, "car:4": {"box": [1218, 176, 25, 35], "box_score": 0.7350622415542603}}}, "0000000268.png": {"car": {"car:2": {"box": [193, 182, 80, 37], "box_score": 0.9724931120872498}, "car:7": {"box": [701, 175, 53, 43], "box_score": 0.6967891454696655}, "car:1": {"box": [241, 189, 178, 113], "box_score": 0.9935504198074341}, "car:4": {"box": [493, 185, 46, 41], "box_score": 0.9369157552719116}, "car:5": {"box": [1098, 309, 144, 64], "box_score": 0.9141585826873779}, "car:3": {"box": [397, 188, 85, 72], "box_score": 0.9521413445472717}, "car:6": {"box": [470, 189, 46, 48], "box_score": 0.861660361289978}}}, "0000000189.png": {"bicycle": {"bicycle:1": {"box": [911, 193, 77, 50], "box_score": 0.9866320490837097}}, "car": {"car:2": {"box": [2, 181, 84, 101], "box_score": 0.9193198680877686}, "car:1": {"box": [1070, 178, 175, 82], "box_score": 0.9926649928092957}, "car:3": {"box": [138, 183, 93, 48], "box_score": 0.8972317576408386}, "car:4": {"box": [73, 188, 51, 38], "box_score": 0.6975300312042236}}}, "0000000322.png": {"car": {"car:2": {"box": [17, 203, 320, 154], "box_score": 0.9584362506866455}, "car:10": {"box": [669, 172, 37, 19], "box_score": 0.66645747423172}, "car:1": {"box": [435, 182, 77, 45], "box_score": 0.973343014717102}, "car:11": {"box": [1041, 177, 102, 44], "box_score": 0.6166906356811523}, "car:4": {"box": [792, 188, 237, 145], "box_score": 0.9230419397354126}, "car:9": {"box": [593, 175, 37, 16], "box_score": 0.7499663829803467}, "car:8": {"box": [934, 212, 313, 158], "box_score": 0.8100115060806274}, "car:7": {"box": [712, 180, 47, 53], "box_score": 0.8195984363555908}, "car:5": {"box": [0, 190, 87, 25], "box_score": 0.8894622921943665}, "car:3": {"box": [739, 182, 110, 82], "box_score": 0.9302366375923157}, "car:6": {"box": [478, 179, 48, 38], "box_score": 0.8678804039955139}}}, "0000000198.png": {"bicycle": {"bicycle:1": {"box": [1045, 201, 96, 58], "box_score": 0.9763941168785095}}, "car": {"car:2": {"box": [222, 181, 88, 48], "box_score": 0.9563153386116028}, "car:1": {"box": [0, 175, 160, 112], "box_score": 0.9690552353858948}, "car:3": {"box": [146, 183, 64, 40], "box_score": 0.9073352217674255}}}, "0000000331.png": {"car": {"car:2": {"box": [883, 187, 370, 184], "box_score": 0.976464033126831}, "car:1": {"box": [309, 181, 119, 77], "box_score": 0.9888982176780701}, "car:4": {"box": [763, 183, 174, 105], "box_score": 0.9686427712440491}, "car:5": {"box": [731, 178, 74, 68], "box_score": 0.8690447211265564}, "car:3": {"box": [400, 177, 74, 56], "box_score": 0.9708518981933594}, "car:6": {"box": [481, 174, 47, 19], "box_score": 0.600178062915802}}}, "0000000441.png": {"traffic light": {"traffic light:2": {"box": [348, 9, 41, 102], "box_score": 0.6783093810081482}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.8296838998794556}}}, "0000000355.png": {"truck": {"truck:1": {"box": [373, 154, 79, 39], "box_score": 0.7046063542366028}}, "car": {"car:2": {"box": [625, 175, 76, 26], "box_score": 0.9399995803833008}, "car:1": {"box": [364, 186, 95, 67], "box_score": 0.9562972784042358}, "car:3": {"box": [502, 175, 81, 31], "box_score": 0.8841618895530701}, "car:4": {"box": [180, 193, 33, 25], "box_score": 0.843962550163269}}, "person": {"person:1": {"box": [729, 172, 26, 57], "box_score": 0.6814106702804565}}}, "0000000259.png": {"car": {"car:2": {"box": [924, 221, 315, 150], "box_score": 0.9966999888420105}, "car:1": {"box": [789, 190, 204, 109], "box_score": 0.9970543384552002}, "car:4": {"box": [695, 178, 41, 31], "box_score": 0.8361056447029114}, "car:5": {"box": [524, 186, 36, 32], "box_score": 0.8181710243225098}, "car:3": {"box": [415, 184, 96, 63], "box_score": 0.9691590070724487}, "car:6": {"box": [594, 179, 37, 19], "box_score": 0.7679959535598755}}}, "0000000071.png": {"car": {"car:2": {"box": [0, 224, 231, 153], "box_score": 0.9581412672996521}, "car:7": {"box": [353, 203, 70, 42], "box_score": 0.6953318119049072}, "car:1": {"box": [199, 197, 157, 89], "box_score": 0.9842199683189392}, "car:4": {"box": [941, 162, 268, 87], "box_score": 0.925860583782196}, "car:5": {"box": [468, 184, 44, 32], "box_score": 0.8503372073173523}, "car:3": {"box": [677, 180, 77, 56], "box_score": 0.9476632475852966}, "car:6": {"box": [804, 163, 123, 52], "box_score": 0.7599267959594727}}}, "0000000145.png": {"car": {"car:2": {"box": [1, 200, 236, 168], "box_score": 0.9803445339202881}, "car:1": {"box": [778, 186, 311, 173], "box_score": 0.995344340801239}, "car:4": {"box": [218, 191, 143, 98], "box_score": 0.9424143433570862}, "car:5": {"box": [342, 175, 86, 42], "box_score": 0.7883419394493103}, "car:3": {"box": [730, 186, 110, 87], "box_score": 0.9508671760559082}, "car:6": {"box": [1014, 284, 230, 91], "box_score": 0.7372975945472717}}, "person": {"person:2": {"box": [798, 159, 27, 30], "box_score": 0.600988507270813}, "person:1": {"box": [826, 155, 25, 51], "box_score": 0.6079440712928772}}}, "0000000414.png": {"car": {"car:1": {"box": [163, 193, 215, 106], "box_score": 0.9889350533485413}}, "traffic light": {"traffic light:2": {"box": [350, 14, 39, 98], "box_score": 0.6606155633926392}, "traffic light:3": {"box": [404, 49, 33, 59], "box_score": 0.6269470453262329}, "traffic light:1": {"box": [1047, 28, 33, 77], "box_score": 0.860438883304596}}}, "0000000018.png": {"car": {"car:2": {"box": [180, 200, 61, 35], "box_score": 0.9476331472396851}, "car:7": {"box": [640, 167, 77, 36], "box_score": 0.7009828090667725}, "car:1": {"box": [1009, 136, 82, 40], "box_score": 0.9643099904060364}, "car:4": {"box": [17, 208, 72, 34], "box_score": 0.887376070022583}, "car:8": {"box": [483, 179, 37, 34], "box_score": 0.6821368336677551}, "car:5": {"box": [93, 202, 94, 34], "box_score": 0.8368509411811829}, "car:3": {"box": [413, 190, 62, 44], "box_score": 0.9452595710754395}, "car:6": {"box": [458, 188, 41, 34], "box_score": 0.8328502178192139}}}, "0000000348.png": {"truck": {"truck:1": {"box": [490, 144, 96, 64], "box_score": 0.8036701679229736}}, "car": {"car:2": {"box": [451, 170, 49, 50], "box_score": 0.944851279258728}, "car:5": {"box": [0, 187, 62, 50], "box_score": 0.8140153288841248}, "car:1": {"box": [341, 181, 80, 32], "box_score": 0.9945939183235168}, "car:3": {"box": [36, 183, 98, 58], "box_score": 0.9040904641151428}, "car:4": {"box": [635, 175, 61, 24], "box_score": 0.8737102150917053}}}, "0000000444.png": {"traffic light": {"traffic light:2": {"box": [348, 10, 41, 102], "box_score": 0.7148458957672119}, "traffic light:1": {"box": [1047, 27, 32, 78], "box_score": 0.7442396879196167}}}, "0000000418.png": {"car": {"car:1": {"box": [19, 199, 311, 144], "box_score": 0.9886187314987183}}, "traffic light": {"traffic light:2": {"box": [349, 14, 40, 99], "box_score": 0.6627245545387268}, "traffic light:3": {"box": [399, 47, 38, 63], "box_score": 0.6479381322860718}, "traffic light:1": {"box": [1047, 28, 32, 77], "box_score": 0.8745437860488892}}}, "0000000302.png": {"car": {"car:2": {"box": [762, 188, 125, 80], "box_score": 0.9730395674705505}, "car:7": {"box": [694, 177, 28, 39], "box_score": 0.7084278464317322}, "car:1": {"box": [382, 186, 103, 66], "box_score": 0.9932990074157715}, "car:4": {"box": [732, 183, 59, 55], "box_score": 0.8891890048980713}, "car:8": {"box": [707, 179, 33, 45], "box_score": 0.6385800838470459}, "car:5": {"box": [467, 184, 54, 45], "box_score": 0.8850505948066711}, "car:3": {"box": [840, 184, 267, 162], "box_score": 0.9478753805160522}, "car:6": {"box": [543, 179, 38, 23], "box_score": 0.7983914613723755}}}, "0000000405.png": {"car": {"car:2": {"box": [408, 185, 92, 60], "box_score": 0.6723969578742981}, "car:1": {"box": [0, 208, 185, 163], "box_score": 0.9871196746826172}}, "traffic light": {"traffic light:2": {"box": [351, 14, 38, 98], "box_score": 0.7648630738258362}, "traffic light:3": {"box": [409, 48, 28, 54], "box_score": 0.6437888741493225}, "traffic light:1": {"box": [1046, 26, 34, 78], "box_score": 0.9204411506652832}}}, "0000000273.png": {"car": {"car:2": {"box": [1, 190, 319, 182], "box_score": 0.9756407737731934}, "car:1": {"box": [287, 184, 144, 108], "box_score": 0.9780682921409607}, "car:4": {"box": [456, 186, 60, 50], "box_score": 0.9390884041786194}, "car:5": {"box": [715, 173, 62, 52], "box_score": 0.6039741635322571}, "car:3": {"box": [416, 191, 66, 64], "box_score": 0.9536802768707275}, "car:6": {"box": [567, 178, 36, 23], "box_score": 0.6017624735832214}}}, "0000000242.png": {"car": {"car:2": {"box": [957, 233, 285, 142], "box_score": 0.9919977784156799}, "car:7": {"box": [868, 179, 119, 40], "box_score": 0.719337522983551}, "car:1": {"box": [1, 238, 163, 135], "box_score": 0.997894823551178}, "car:4": {"box": [691, 188, 82, 58], "box_score": 0.9184585213661194}, "car:8": {"box": [655, 178, 29, 24], "box_score": 0.6329329013824463}, "car:5": {"box": [674, 185, 48, 43], "box_score": 0.8093237280845642}, "car:3": {"box": [976, 168, 180, 63], "box_score": 0.9812894463539124}, "car:6": {"box": [480, 183, 61, 38], "box_score": 0.7311214804649353}}}, "0000000072.png": {"car": {"car:2": {"box": [959, 161, 280, 99], "box_score": 0.9647368788719177}, "car:7": {"box": [338, 207, 79, 44], "box_score": 0.7998365163803101}, "car:1": {"box": [156, 201, 180, 97], "box_score": 0.9739385843276978}, "car:4": {"box": [681, 180, 84, 59], "box_score": 0.9490146636962891}, "car:8": {"box": [382, 186, 78, 54], "box_score": 0.6955646276473999}, "car:5": {"box": [811, 162, 142, 58], "box_score": 0.8409373164176941}, "car:3": {"box": [1, 261, 105, 112], "box_score": 0.9589017629623413}, "car:6": {"box": [462, 183, 46, 35], "box_score": 0.8313432335853577}}}, "0000000114.png": {"car": {"car:2": {"box": [764, 180, 203, 120], "box_score": 0.9871275424957275}, "car:7": {"box": [493, 180, 37, 29], "box_score": 0.8475971817970276}, "car:1": {"box": [45, 199, 285, 132], "box_score": 0.9917138814926147}, "car:4": {"box": [695, 180, 75, 55], "box_score": 0.9643734097480774}, "car:8": {"box": [655, 178, 38, 34], "box_score": 0.8191702365875244}, "car:5": {"box": [423, 185, 69, 46], "box_score": 0.9506639242172241}, "car:3": {"box": [312, 192, 103, 72], "box_score": 0.9734776616096497}, "car:6": {"box": [885, 198, 370, 173], "box_score": 0.9240030646324158}}}, "0000000070.png": {"car": {"car:2": {"box": [471, 184, 43, 29], "box_score": 0.8724921345710754}, "car:7": {"box": [1203, 135, 41, 48], "box_score": 0.738163411617279}, "car:1": {"box": [248, 197, 124, 80], "box_score": 0.952497124671936}, "car:9": {"box": [861, 149, 187, 79], "box_score": 0.6648290157318115}, "car:4": {"box": [899, 161, 257, 80], "box_score": 0.817700982093811}, "car:8": {"box": [794, 165, 107, 47], "box_score": 0.7154961228370667}, "car:5": {"box": [384, 183, 85, 54], "box_score": 0.801794707775116}, "car:3": {"box": [671, 180, 72, 53], "box_score": 0.8491073846817017}, "car:6": {"box": [0, 210, 307, 167], "box_score": 0.7997602820396423}}, "person": {"person:1": {"box": [146, 251, 31, 49], "box_score": 0.6473255753517151}}}, "0000000267.png": {"car": {"car:2": {"box": [1020, 230, 221, 144], "box_score": 0.9783560633659363}, "car:7": {"box": [1, 200, 81, 46], "box_score": 0.7800921201705933}, "car:1": {"box": [275, 189, 162, 103], "box_score": 0.9931768178939819}, "car:4": {"box": [498, 186, 46, 41], "box_score": 0.9305042028427124}, "car:5": {"box": [414, 188, 78, 68], "box_score": 0.9012472033500671}, "car:3": {"box": [212, 180, 74, 38], "box_score": 0.9613547921180725}, "car:6": {"box": [480, 189, 47, 45], "box_score": 0.8936144113540649}}}, "0000000123.png": {"car": {"car:2": {"box": [1, 208, 173, 157], "box_score": 0.9848024249076843}, "car:1": {"box": [768, 180, 202, 123], "box_score": 0.9948552846908569}, "car:4": {"box": [708, 179, 89, 71], "box_score": 0.9518268704414368}, "car:5": {"box": [452, 176, 66, 39], "box_score": 0.8762442469596863}, "car:3": {"box": [274, 189, 148, 78], "box_score": 0.9628678560256958}, "car:6": {"box": [675, 176, 56, 47], "box_score": 0.848601222038269}}}, "0000000059.png": {"car": {"car:2": {"box": [447, 188, 64, 53], "box_score": 0.9533616304397583}, "car:7": {"box": [982, 143, 58, 32], "box_score": 0.6343652009963989}, "car:1": {"box": [318, 191, 155, 95], "box_score": 0.987037181854248}, "car:9": {"box": [882, 154, 59, 26], "box_score": 0.6076852083206177}, "car:4": {"box": [636, 179, 51, 37], "box_score": 0.9241887331008911}, "car:8": {"box": [490, 185, 35, 22], "box_score": 0.6339683532714844}, "car:5": {"box": [790, 163, 94, 43], "box_score": 0.8889548182487488}, "car:3": {"box": [131, 206, 181, 100], "box_score": 0.9503239393234253}, "car:6": {"box": [715, 166, 51, 34], "box_score": 0.6715168356895447}}}, "0000000398.png": {"car": {"car:2": {"box": [470, 181, 110, 51], "box_score": 0.9311830401420593}, "car:1": {"box": [86, 193, 223, 107], "box_score": 0.9909295439720154}, "car:3": {"box": [430, 191, 66, 46], "box_score": 0.817857563495636}}, "traffic light": {"traffic light:2": {"box": [1039, 30, 32, 79], "box_score": 0.6766507625579834}, "traffic light:3": {"box": [401, 43, 44, 64], "box_score": 0.6702885031700134}, "traffic light:1": {"box": [353, 19, 42, 90], "box_score": 0.8035933971405029}}}, "0000000415.png": {"car": {"car:1": {"box": [132, 192, 235, 118], "box_score": 0.9940793514251709}}, "traffic light": {"traffic light:2": {"box": [347, 14, 42, 97], "box_score": 0.6865081787109375}, "traffic light:3": {"box": [399, 47, 38, 62], "box_score": 0.6451274752616882}, "traffic light:1": {"box": [1047, 28, 32, 79], "box_score": 0.7921919226646423}}}, "0000000085.png": {"car": {"car:2": {"box": [353, 188, 100, 61], "box_score": 0.9540911316871643}, "car:7": {"box": [513, 181, 30, 25], "box_score": 0.710361659526825}, "car:1": {"box": [902, 192, 344, 178], "box_score": 0.977161705493927}, "car:4": {"box": [431, 185, 54, 44], "box_score": 0.9039536714553833}, "car:5": {"box": [782, 157, 99, 37], "box_score": 0.9023416042327881}, "car:3": {"box": [1, 196, 269, 170], "box_score": 0.9260804653167725}, "car:6": {"box": [493, 184, 30, 28], "box_score": 0.7852526307106018}}}, "0000000058.png": {"car": {"car:2": {"box": [459, 187, 56, 49], "box_score": 0.9511991143226624}, "car:7": {"box": [488, 184, 38, 23], "box_score": 0.6068483591079712}, "car:1": {"box": [349, 192, 134, 85], "box_score": 0.951525092124939}, "car:4": {"box": [761, 162, 107, 43], "box_score": 0.8472265005111694}, "car:5": {"box": [634, 179, 47, 34], "box_score": 0.7811149954795837}, "car:3": {"box": [175, 201, 156, 85], "box_score": 0.8707641363143921}, "car:6": {"box": [970, 142, 54, 32], "box_score": 0.6768905520439148}}}, "0000000069.png": {"car": {"car:2": {"box": [1175, 134, 68, 51], "box_score": 0.9274187088012695}, "car:10": {"box": [843, 154, 172, 73], "box_score": 0.6799958348274231}, "car:1": {"box": [3, 203, 366, 169], "box_score": 0.938440203666687}, "car:9": {"box": [473, 185, 39, 30], "box_score": 0.7638711333274841}, "car:4": {"box": [288, 197, 99, 65], "box_score": 0.9188708066940308}, "car:8": {"box": [382, 204, 53, 37], "box_score": 0.7658916711807251}, "car:7": {"box": [782, 164, 97, 48], "box_score": 0.8011035323143005}, "car:5": {"box": [882, 167, 231, 69], "box_score": 0.8906086087226868}, "car:3": {"box": [668, 183, 70, 51], "box_score": 0.9256382584571838}, "car:6": {"box": [1128, 146, 49, 43], "box_score": 0.807677686214447}}}, "0000000369.png": {"car": {"car:2": {"box": [295, 177, 135, 51], "box_score": 0.9536327719688416}, "car:1": {"box": [107, 198, 251, 160], "box_score": 0.9946734309196472}, "car:3": {"box": [630, 175, 102, 32], "box_score": 0.9213138818740845}, "car:4": {"box": [477, 177, 81, 37], "box_score": 0.7052013278007507}}, "person": {"person:1": {"box": [944, 163, 59, 128], "box_score": 0.9113381505012512}}}, "0000000429.png": {"traffic light": {"traffic light:2": {"box": [348, 13, 41, 98], "box_score": 0.6894542574882507}, "traffic light:1": {"box": [1047, 28, 32, 79], "box_score": 0.7810109853744507}}}, "0000000226.png": {"car": {"car:2": {"box": [486, 187, 129, 75], "box_score": 0.9674784541130066}, "car:10": {"box": [372, 181, 34, 30], "box_score": 0.697647213935852}, "car:1": {"box": [12, 204, 112, 96], "box_score": 0.9783158898353577}, "car:9": {"box": [984, 158, 59, 64], "box_score": 0.7322254776954651}, "car:4": {"box": [562, 168, 91, 36], "box_score": 0.9456179738044739}, "car:8": {"box": [190, 183, 48, 33], "box_score": 0.7564980387687683}, "car:7": {"box": [1064, 155, 172, 78], "box_score": 0.866199254989624}, "car:5": {"box": [-1, 217, 82, 130], "box_score": 0.9355447888374329}, "car:3": {"box": [672, 141, 385, 209], "box_score": 0.9458471536636353}, "car:6": {"box": [385, 183, 58, 38], "box_score": 0.8975347280502319}}}, "0000000082.png": {"car": {"car:2": {"box": [1073, 143, 172, 125], "box_score": 0.9619277119636536}, "car:7": {"box": [503, 184, 28, 26], "box_score": 0.7725652456283569}, "car:1": {"box": [794, 183, 309, 171], "box_score": 0.9891997575759888}, "car:4": {"box": [456, 186, 43, 36], "box_score": 0.9035009741783142}, "car:8": {"box": [753, 159, 97, 34], "box_score": 0.7067040205001831}, "car:5": {"box": [144, 190, 211, 114], "box_score": 0.8969380855560303}, "car:3": {"box": [393, 187, 82, 50], "box_score": 0.9575483202934265}, "car:6": {"box": [2, 239, 180, 119], "box_score": 0.839935839176178}}}, "0000000357.png": {"truck": {"truck:1": {"box": [322, 152, 97, 56], "box_score": 0.8052999377250671}}, "car": {"car:2": {"box": [317, 189, 122, 84], "box_score": 0.9388632774353027}, "car:1": {"box": [623, 176, 81, 27], "box_score": 0.9437673091888428}, "car:3": {"box": [153, 182, 72, 39], "box_score": 0.9214755892753601}, "car:4": {"box": [501, 174, 78, 31], "box_score": 0.790012538433075}}, "person": {"person:1": {"box": [744, 167, 26, 66], "box_score": 0.7232078909873962}}}, "0000000388.png": {"car": {"car:2": {"box": [882, 162, 194, 70], "box_score": 0.9854727387428284}, "car:1": {"box": [533, 177, 134, 44], "box_score": 0.9894188642501831}, "car:3": {"box": [276, 180, 140, 69], "box_score": 0.9778433442115784}}, "traffic light": {"traffic light:1": {"box": [408, 35, 28, 76], "box_score": 0.8073177933692932}}}, "0000000190.png": {"bicycle": {"bicycle:1": {"box": [922, 193, 77, 51], "box_score": 0.952012300491333}}, "car": {"car:2": {"box": [146, 184, 93, 47], "box_score": 0.909060537815094}, "car:1": {"box": [1084, 181, 160, 83], "box_score": 0.9859163165092468}, "car:3": {"box": [1, 177, 90, 102], "box_score": 0.863640308380127}}}, "0000000096.png": {"car": {"car:2": {"box": [3, 219, 197, 150], "box_score": 0.9705504179000854}, "car:10": {"box": [643, 176, 29, 26], "box_score": 0.6260802149772644}, "car:1": {"box": [858, 149, 180, 62], "box_score": 0.9892101883888245}, "car:9": {"box": [659, 175, 66, 41], "box_score": 0.6466737389564514}, "car:4": {"box": [331, 199, 80, 63], "box_score": 0.9328092336654663}, "car:8": {"box": [809, 158, 74, 45], "box_score": 0.7957871556282043}, "car:7": {"box": [452, 188, 48, 36], "box_score": 0.8293837904930115}, "car:5": {"box": [398, 191, 62, 49], "box_score": 0.9004534482955933}, "car:3": {"box": [185, 201, 163, 106], "box_score": 0.9512052536010742}, "car:6": {"box": [1173, 130, 71, 51], "box_score": 0.8892301917076111}}}, "0000000184.png": {"bicycle": {"bicycle:1": {"box": [852, 188, 71, 46], "box_score": 0.9692868590354919}}, "car": {"car:2": {"box": [0, 183, 71, 99], "box_score": 0.8753920197486877}, "car:1": {"box": [991, 174, 210, 74], "box_score": 0.9816111922264099}, "car:3": {"box": [109, 183, 98, 51], "box_score": 0.7912434339523315}, "car:4": {"box": [1210, 193, 34, 49], "box_score": 0.6470858454704285}}}, "0000000005.png": {"car": {"car:2": {"box": [314, 193, 109, 68], "box_score": 0.9828755855560303}, "car:1": {"box": [792, 183, 292, 166], "box_score": 0.9948704242706299}, "car:4": {"box": [482, 185, 38, 26], "box_score": 0.8055354952812195}, "car:5": {"box": [307, 192, 42, 26], "box_score": 0.7834891080856323}, "car:3": {"box": [720, 178, 102, 84], "box_score": 0.9807573556900024}, "car:6": {"box": [580, 173, 36, 19], "box_score": 0.6686621308326721}}}, "0000000271.png": {"truck": {"truck:1": {"box": [707, 175, 60, 48], "box_score": 0.7273092269897461}}, "car": {"car:2": {"box": [135, 179, 97, 46], "box_score": 0.9487941861152649}, "car:1": {"box": [92, 192, 275, 166], "box_score": 0.9945202469825745}, "car:4": {"box": [442, 192, 55, 60], "box_score": 0.9117995500564575}, "car:5": {"box": [349, 187, 120, 92], "box_score": 0.9013149738311768}, "car:3": {"box": [475, 187, 52, 46], "box_score": 0.9131519198417664}, "car:6": {"box": [571, 179, 37, 23], "box_score": 0.7338244915008545}}}, "0000000011.png": {"car": {"car:2": {"box": [115, 204, 213, 120], "box_score": 0.9413849711418152}, "car:7": {"box": [640, 174, 44, 31], "box_score": 0.6380432844161987}, "car:1": {"box": [812, 182, 273, 175], "box_score": 0.9958173632621765}, "car:4": {"box": [599, 176, 44, 20], "box_score": 0.7087150812149048}, "car:5": {"box": [457, 186, 45, 35], "box_score": 0.6546576619148254}, "car:3": {"box": [144, 201, 40, 27], "box_score": 0.7764376997947693}, "car:6": {"box": [502, 178, 36, 29], "box_score": 0.6439080834388733}}}, "0000000368.png": {"car": {"car:2": {"box": [632, 175, 96, 32], "box_score": 0.9526825547218323}, "car:1": {"box": [182, 187, 202, 141], "box_score": 0.9704447388648987}, "car:3": {"box": [475, 178, 105, 35], "box_score": 0.8254008889198303}, "car:4": {"box": [275, 177, 128, 49], "box_score": 0.6129506230354309}}, "person": {"person:1": {"box": [917, 164, 58, 116], "box_score": 0.9649611711502075}}}, "0000000374.png": {"handbag": {"handbag:1": {"box": [1146, 246, 45, 34], "box_score": 0.6690793037414551}}, "car": {"car:2": {"box": [626, 174, 112, 36], "box_score": 0.9347003102302551}, "car:1": {"box": [415, 175, 138, 56], "box_score": 0.9423569440841675}, "car:3": {"box": [0, 161, 67, 60], "box_score": 0.8771877884864807}}, "person": {"person:1": {"box": [1136, 159, 94, 194], "box_score": 0.8909866213798523}}}, "0000000224.png": {"car": {"car:2": {"box": [-1, 206, 72, 89], "box_score": 0.9680054187774658}, "car:10": {"box": [282, 179, 31, 22], "box_score": 0.7783907651901245}, "car:1": {"box": [426, 190, 127, 72], "box_score": 0.9686920642852783}, "car:9": {"box": [853, 171, 78, 51], "box_score": 0.7853971719741821}, "car:4": {"box": [502, 173, 89, 37], "box_score": 0.9542906284332275}, "car:8": {"box": [306, 185, 39, 32], "box_score": 0.7932144999504089}, "car:7": {"box": [951, 169, 138, 67], "box_score": 0.87637859582901}, "car:5": {"box": [113, 187, 66, 34], "box_score": 0.9006069302558899}, "car:3": {"box": [567, 160, 321, 177], "box_score": 0.9672849774360657}, "car:6": {"box": [322, 187, 57, 37], "box_score": 0.8907973170280457}}}, "0000000379.png": {"car": {"car:2": {"box": [398, 177, 109, 52], "box_score": 0.9439576268196106}, "car:1": {"box": [560, 173, 156, 63], "box_score": 0.9809070229530334}}, "traffic light": {"traffic light:1": {"box": [470, 63, 22, 62], "box_score": 0.6606988310813904}}}, "0000000035.png": {"car": {"car:2": {"box": [725, 178, 162, 106], "box_score": 0.9732947945594788}, "car:1": {"box": [2, 211, 230, 158], "box_score": 0.9896281957626343}, "car:4": {"box": [378, 180, 83, 60], "box_score": 0.8337442874908447}, "car:5": {"box": [552, 178, 32, 22], "box_score": 0.8036327362060547}, "car:3": {"box": [225, 200, 154, 88], "box_score": 0.969067394733429}, "car:6": {"box": [520, 178, 30, 24], "box_score": 0.6480507850646973}}}, "0000000204.png": {"car": {"car:2": {"box": [8, 177, 232, 115], "box_score": 0.9207627177238464}, "car:1": {"box": [309, 187, 83, 45], "box_score": 0.9264850616455078}, "car:3": {"box": [236, 187, 65, 41], "box_score": 0.7943981885910034}}}, "0000000366.png": {"car": {"car:2": {"box": [632, 175, 93, 32], "box_score": 0.9757989645004272}, "car:5": {"box": [138, 180, 74, 36], "box_score": 0.7321848273277283}, "car:1": {"box": [230, 180, 101, 48], "box_score": 0.9819452166557312}, "car:3": {"box": [274, 192, 129, 98], "box_score": 0.9603028893470764}, "car:4": {"box": [481, 177, 100, 34], "box_score": 0.7627378106117249}}, "person": {"person:1": {"box": [876, 165, 34, 74], "box_score": 0.7883806228637695}}}, "0000000078.png": {"car": {"car:2": {"box": [728, 177, 146, 98], "box_score": 0.9827039837837219}, "car:7": {"box": [291, 189, 127, 74], "box_score": 0.7771013975143433}, "car:1": {"box": [0, 232, 92, 142], "box_score": 0.9947875738143921}, "car:9": {"box": [198, 217, 127, 72], "box_score": 0.6027513146400452}, "car:4": {"box": [476, 183, 35, 31], "box_score": 0.8880133032798767}, "car:8": {"box": [745, 161, 73, 27], "box_score": 0.6354336738586426}, "car:5": {"box": [922, 154, 254, 78], "box_score": 0.8572249412536621}, "car:3": {"box": [1130, 146, 114, 138], "box_score": 0.9375935196876526}, "car:6": {"box": [430, 184, 66, 41], "box_score": 0.8470265865325928}}}, "0000000205.png": {"car": {"car:2": {"box": [327, 186, 82, 47], "box_score": 0.9410925507545471}, "car:1": {"box": [6, 179, 250, 116], "box_score": 0.9690235257148743}, "car:3": {"box": [257, 186, 58, 40], "box_score": 0.6956828236579895}, "car:4": {"box": [391, 179, 91, 38], "box_score": 0.6489114165306091}}}, "0000000139.png": {"bus": {"bus:1": {"box": [700, 136, 79, 93], "box_score": 0.6457775831222534}}, "car": {"car:2": {"box": [226, 186, 152, 97], "box_score": 0.9728078842163086}, "car:1": {"box": [780, 179, 286, 167], "box_score": 0.987911581993103}, "car:3": {"box": [717, 180, 131, 88], "box_score": 0.9352006912231445}, "car:4": {"box": [352, 187, 83, 63], "box_score": 0.7793406844139099}}}, "0000000178.png": {"truck": {"truck:1": {"box": [0, 189, 106, 94], "box_score": 0.6224297881126404}}, "car": {"car:2": {"box": [1115, 163, 128, 68], "box_score": 0.9826404452323914}, "car:1": {"box": [922, 173, 179, 64], "box_score": 0.9961856007575989}, "car:3": {"box": [118, 192, 93, 43], "box_score": 0.7595808506011963}}}, "0000000023.png": {"car": {"car:2": {"box": [425, 190, 55, 41], "box_score": 0.9690297842025757}, "car:1": {"box": [359, 193, 82, 54], "box_score": 0.9742333292961121}, "car:4": {"box": [665, 171, 74, 46], "box_score": 0.8620672225952148}, "car:5": {"box": [1068, 131, 109, 51], "box_score": 0.7799257636070251}, "car:3": {"box": [2, 205, 100, 44], "box_score": 0.9188222289085388}, "car:6": {"box": [465, 180, 43, 37], "box_score": 0.6932110786437988}}}, "0000000261.png": {"car": {"car:2": {"box": [393, 185, 102, 70], "box_score": 0.9850897789001465}, "car:7": {"box": [510, 188, 35, 37], "box_score": 0.6609690189361572}, "car:1": {"box": [814, 193, 273, 144], "box_score": 0.9911758899688721}, "car:4": {"box": [695, 177, 44, 34], "box_score": 0.8411176800727844}, "car:8": {"box": [590, 180, 38, 19], "box_score": 0.6572209596633911}, "car:5": {"box": [520, 185, 39, 33], "box_score": 0.8205699920654297}, "car:3": {"box": [1025, 270, 216, 107], "box_score": 0.9472775459289551}, "car:6": {"box": [469, 185, 52, 52], "box_score": 0.6960752010345459}}}, "0000000337.png": {"truck": {"truck:1": {"box": [633, 151, 69, 44], "box_score": 0.6386439204216003}}, "car": {"car:2": {"box": [479, 177, 52, 27], "box_score": 0.981694757938385}, "car:1": {"box": [69, 192, 239, 133], "box_score": 0.9851081967353821}, "car:4": {"box": [288, 187, 116, 81], "box_score": 0.91057288646698}, "car:5": {"box": [883, 201, 363, 167], "box_score": 0.8293936252593994}, "car:3": {"box": [753, 182, 170, 102], "box_score": 0.9758934378623962}, "car:6": {"box": [584, 175, 48, 21], "box_score": 0.7215569019317627}}}, "0000000307.png": {"car": {"car:2": {"box": [832, 190, 284, 156], "box_score": 0.9910440444946289}, "car:7": {"box": [465, 186, 49, 43], "box_score": 0.8409122228622437}, "car:1": {"box": [267, 194, 163, 91], "box_score": 0.9921534657478333}, "car:9": {"box": [706, 180, 44, 49], "box_score": 0.697015106678009}, "car:4": {"box": [754, 187, 122, 82], "box_score": 0.9453268051147461}, "car:8": {"box": [524, 179, 41, 28], "box_score": 0.7861964702606201}, "car:5": {"box": [407, 189, 78, 58], "box_score": 0.9125993847846985}, "car:3": {"box": [1060, 237, 183, 138], "box_score": 0.9739054441452026}, "car:6": {"box": [724, 182, 54, 58], "box_score": 0.8550424575805664}}}, "0000000135.png": {"car": {"car:2": {"box": [321, 189, 109, 69], "box_score": 0.9854265451431274}, "car:7": {"box": [5, 189, 137, 58], "box_score": 0.7273157238960266}, "car:1": {"box": [733, 178, 153, 105], "box_score": 0.9869175553321838}, "car:4": {"box": [413, 190, 53, 49], "box_score": 0.9354473352432251}, "car:5": {"box": [0, 203, 68, 53], "box_score": 0.890285074710846}, "car:3": {"box": [952, 213, 287, 157], "box_score": 0.9490500688552856}, "car:6": {"box": [694, 180, 70, 64], "box_score": 0.8047338128089905}}}, "0000000312.png": {"car": {"car:2": {"box": [1045, 236, 197, 142], "box_score": 0.9836604595184326}, "car:10": {"box": [581, 175, 50, 15], "box_score": 0.7097152471542358}, "car:1": {"box": [812, 187, 261, 146], "box_score": 0.9898002743721008}, "car:11": {"box": [703, 177, 38, 46], "box_score": 0.6465844511985779}, "car:4": {"box": [296, 191, 136, 86], "box_score": 0.9679649472236633}, "car:9": {"box": [1109, 176, 105, 47], "box_score": 0.7386765480041504}, "car:8": {"box": [716, 178, 58, 58], "box_score": 0.8190717101097107}, "car:7": {"box": [736, 183, 126, 82], "box_score": 0.9395793676376343}, "car:5": {"box": [502, 179, 49, 32], "box_score": 0.954674243927002}, "car:3": {"box": [1, 207, 325, 158], "box_score": 0.9782257676124573}, "car:6": {"box": [407, 189, 74, 57], "box_score": 0.9497126936912537}}}, "0000000027.png": {"car": {"car:2": {"box": [288, 197, 118, 72], "box_score": 0.9756026268005371}, "car:5": {"box": [1135, 135, 109, 56], "box_score": 0.6063655614852905}, "car:1": {"box": [389, 194, 67, 51], "box_score": 0.9854759573936462}, "car:3": {"box": [444, 181, 64, 44], "box_score": 0.8907878398895264}, "car:4": {"box": [671, 176, 81, 60], "box_score": 0.8680151104927063}}}, "0000000445.png": {"traffic light": {"traffic light:2": {"box": [348, 9, 41, 103], "box_score": 0.6583351492881775}, "traffic light:3": {"box": [399, 47, 38, 63], "box_score": 0.6114200353622437}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.7585621476173401}}}, "0000000310.png": {"car": {"car:2": {"box": [919, 194, 326, 172], "box_score": 0.989471435546875}, "car:10": {"box": [728, 181, 49, 57], "box_score": 0.6683017611503601}, "car:1": {"box": [128, 196, 246, 135], "box_score": 0.9934990406036377}, "car:9": {"box": [572, 176, 42, 14], "box_score": 0.693293571472168}, "car:4": {"box": [352, 188, 104, 72], "box_score": 0.9715904593467712}, "car:8": {"box": [708, 179, 48, 51], "box_score": 0.8049057722091675}, "car:7": {"box": [740, 184, 80, 70], "box_score": 0.866731584072113}, "car:5": {"box": [435, 187, 61, 52], "box_score": 0.9481726884841919}, "car:3": {"box": [784, 185, 180, 110], "box_score": 0.9894508719444275}, "car:6": {"box": [510, 178, 51, 31], "box_score": 0.9010972380638123}}}, "0000000097.png": {"car": {"car:2": {"box": [0, 231, 137, 139], "box_score": 0.9677603840827942}, "car:10": {"box": [783, 158, 80, 47], "box_score": 0.6366914510726929}, "car:1": {"box": [877, 147, 189, 66], "box_score": 0.9830504059791565}, "car:9": {"box": [646, 176, 26, 27], "box_score": 0.6437906622886658}, "car:4": {"box": [304, 200, 96, 71], "box_score": 0.9392129778862}, "car:8": {"box": [665, 176, 60, 48], "box_score": 0.6774891018867493}, "car:7": {"box": [824, 156, 73, 49], "box_score": 0.7928379774093628}, "car:5": {"box": [385, 193, 68, 52], "box_score": 0.9148540496826172}, "car:3": {"box": [118, 207, 203, 120], "box_score": 0.9434385299682617}, "car:6": {"box": [445, 188, 54, 39], "box_score": 0.8187998533248901}}}, "0000000420.png": {"car": {"car:1": {"box": [2, 205, 295, 163], "box_score": 0.9928683638572693}}, "traffic light": {"traffic light:2": {"box": [398, 46, 39, 64], "box_score": 0.6528732180595398}, "traffic light:3": {"box": [349, 13, 40, 98], "box_score": 0.6478581428527832}, "traffic light:1": {"box": [1047, 28, 32, 77], "box_score": 0.8570944666862488}}}, "0000000281.png": {"truck": {"truck:1": {"box": [736, 181, 106, 78], "box_score": 0.6728821992874146}}, "car": {"car:2": {"box": [0, 210, 167, 163], "box_score": 0.9717029929161072}, "car:5": {"box": [717, 188, 33, 43], "box_score": 0.794631838798523}, "car:1": {"box": [152, 210, 205, 142], "box_score": 0.98172527551651}, "car:3": {"box": [332, 195, 113, 90], "box_score": 0.9655036926269531}, "car:4": {"box": [539, 185, 41, 29], "box_score": 0.9380283355712891}}}, "0000000132.png": {"car": {"car:2": {"box": [373, 181, 83, 57], "box_score": 0.9586735963821411}, "car:1": {"box": [3, 213, 195, 154], "box_score": 0.9748932123184204}, "car:4": {"box": [856, 181, 411, 188], "box_score": 0.9084997773170471}, "car:5": {"box": [438, 179, 46, 45], "box_score": 0.8235896229743958}, "car:3": {"box": [710, 175, 117, 78], "box_score": 0.9373878836631775}, "car:6": {"box": [683, 171, 58, 56], "box_score": 0.7449380159378052}}}, "0000000137.png": {"car": {"car:2": {"box": [279, 192, 128, 78], "box_score": 0.9695627093315125}, "car:1": {"box": [756, 181, 200, 127], "box_score": 0.9914182424545288}, "car:3": {"box": [702, 182, 103, 74], "box_score": 0.9377233982086182}, "car:4": {"box": [393, 189, 59, 57], "box_score": 0.904811441898346}}}, "0000000066.png": {"car": {"car:2": {"box": [251, 195, 186, 122], "box_score": 0.9810761213302612}, "car:7": {"box": [755, 167, 83, 44], "box_score": 0.6911836266517639}, "car:1": {"box": [3, 224, 263, 151], "box_score": 0.9911706447601318}, "car:4": {"box": [981, 156, 73, 33], "box_score": 0.7565451264381409}, "car:8": {"box": [483, 186, 33, 26], "box_score": 0.6453995704650879}, "car:5": {"box": [1098, 140, 62, 47], "box_score": 0.7461605668067932}, "car:3": {"box": [825, 167, 193, 62], "box_score": 0.9705702662467957}, "car:6": {"box": [417, 185, 58, 46], "box_score": 0.7360861897468567}}}, "0000000083.png": {"car": {"car:2": {"box": [450, 185, 46, 39], "box_score": 0.9202631115913391}, "car:7": {"box": [1141, 161, 101, 121], "box_score": 0.6738210320472717}, "car:1": {"box": [384, 188, 84, 51], "box_score": 0.9513531923294067}, "car:4": {"box": [766, 160, 96, 34], "box_score": 0.882038414478302}, "car:5": {"box": [96, 191, 232, 127], "box_score": 0.8495187163352966}, "car:3": {"box": [830, 184, 403, 183], "box_score": 0.9188488125801086}, "car:6": {"box": [500, 183, 29, 27], "box_score": 0.7002856731414795}}}, "0000000236.png": {"car": {"car:2": {"box": [743, 206, 260, 139], "box_score": 0.9688056111335754}, "car:7": {"box": [1177, 172, 67, 79], "box_score": 0.6454541087150574}, "car:1": {"box": [3, 218, 259, 150], "box_score": 0.9924724102020264}, "car:4": {"box": [605, 189, 66, 46], "box_score": 0.8416297435760498}, "car:5": {"box": [422, 189, 47, 32], "box_score": 0.7130143046379089}, "car:3": {"box": [825, 170, 129, 53], "box_score": 0.8633373379707336}, "car:6": {"box": [596, 185, 43, 42], "box_score": 0.684389591217041}}}, "0000000215.png": {"car": {"car:2": {"box": [606, 181, 83, 49], "box_score": 0.9554967880249023}, "car:1": {"box": [139, 200, 135, 67], "box_score": 0.9791716933250427}, "car:4": {"box": [530, 182, 64, 41], "box_score": 0.784588098526001}, "car:5": {"box": [0, 201, 58, 40], "box_score": 0.7271189093589783}, "car:3": {"box": [295, 173, 233, 122], "box_score": 0.9234709739685059}, "car:6": {"box": [216, 184, 90, 41], "box_score": 0.6521729826927185}}}, "0000000130.png": {"truck": {"truck:1": {"box": [676, 134, 72, 82], "box_score": 0.6643624305725098}}, "car": {"car:2": {"box": [1025, 192, 211, 180], "box_score": 0.9837470650672913}, "car:1": {"box": [775, 176, 284, 147], "box_score": 0.9985080361366272}, "car:4": {"box": [391, 176, 79, 50], "box_score": 0.9523577690124512}, "car:5": {"box": [701, 173, 93, 67], "box_score": 0.9165364503860474}, "car:3": {"box": [0, 189, 275, 180], "box_score": 0.9727855324745178}, "car:6": {"box": [444, 176, 50, 39], "box_score": 0.7075382471084595}}}, "0000000021.png": {"car": {"car:2": {"box": [0, 211, 32, 30], "box_score": 0.8263798952102661}, "car:7": {"box": [473, 183, 41, 35], "box_score": 0.6321171522140503}, "car:1": {"box": [386, 193, 70, 50], "box_score": 0.9619129300117493}, "car:4": {"box": [441, 192, 47, 38], "box_score": 0.7933667898178101}, "car:8": {"box": [132, 205, 67, 33], "box_score": 0.6060602068901062}, "car:5": {"box": [1043, 136, 101, 43], "box_score": 0.7785692811012268}, "car:3": {"box": [39, 207, 104, 38], "box_score": 0.7993154525756836}, "car:6": {"box": [1201, 142, 43, 31], "box_score": 0.6413356065750122}}}, "0000000257.png": {"truck": {"truck:1": {"box": [132, 148, 146, 87], "box_score": 0.6163446307182312}}, "car": {"car:2": {"box": [866, 204, 383, 166], "box_score": 0.9857068657875061}, "car:7": {"box": [596, 178, 35, 19], "box_score": 0.6970316171646118}, "car:1": {"box": [768, 187, 154, 95], "box_score": 0.9886183738708496}, "car:4": {"box": [693, 175, 48, 33], "box_score": 0.7926143407821655}, "car:5": {"box": [530, 185, 33, 31], "box_score": 0.7910633087158203}, "car:3": {"box": [434, 183, 81, 57], "box_score": 0.9626229405403137}, "car:6": {"box": [1153, 194, 91, 56], "box_score": 0.7506435513496399}}}, "0000000098.png": {"car": {"car:2": {"box": [40, 209, 256, 139], "box_score": 0.9626378417015076}, "car:10": {"box": [665, 176, 71, 45], "box_score": 0.6477964520454407}, "car:1": {"box": [894, 146, 205, 69], "box_score": 0.973261296749115}, "car:9": {"box": [884, 145, 106, 62], "box_score": 0.6606735587120056}, "car:4": {"box": [281, 204, 104, 77], "box_score": 0.89809250831604}, "car:8": {"box": [796, 160, 83, 46], "box_score": 0.7553523182868958}, "car:7": {"box": [835, 157, 75, 49], "box_score": 0.8285631537437439}, "car:5": {"box": [437, 189, 56, 38], "box_score": 0.8975536227226257}, "car:3": {"box": [371, 193, 75, 53], "box_score": 0.9487394094467163}, "car:6": {"box": [0, 249, 61, 124], "box_score": 0.845464289188385}}}, "0000000277.png": {"car": {"car:2": {"box": [410, 184, 80, 66], "box_score": 0.9603710770606995}, "car:1": {"box": [39, 186, 310, 178], "box_score": 0.9914724230766296}, "car:4": {"box": [554, 176, 42, 26], "box_score": 0.7606067061424255}, "car:5": {"box": [715, 170, 88, 61], "box_score": 0.737855076789856}, "car:3": {"box": [332, 193, 103, 89], "box_score": 0.9189735054969788}, "car:6": {"box": [0, 176, 109, 52], "box_score": 0.6534297466278076}}}, "0000000426.png": {"car": {"car:1": {"box": [0, 259, 93, 114], "box_score": 0.9378021955490112}}, "traffic light": {"traffic light:2": {"box": [349, 13, 40, 98], "box_score": 0.6766049861907959}, "traffic light:3": {"box": [404, 49, 33, 59], "box_score": 0.6379714012145996}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.8256919384002686}}}, "0000000333.png": {"car": {"car:2": {"box": [969, 214, 275, 160], "box_score": 0.990917980670929}, "car:7": {"box": [610, 173, 45, 18], "box_score": 0.6128292083740234}, "car:1": {"box": [779, 186, 242, 135], "box_score": 0.9922842383384705}, "car:4": {"box": [734, 180, 101, 78], "box_score": 0.9358751177787781}, "car:5": {"box": [371, 180, 86, 63], "box_score": 0.9175235629081726}, "car:3": {"box": [256, 185, 143, 88], "box_score": 0.9894806146621704}, "car:6": {"box": [471, 176, 59, 22], "box_score": 0.6485903263092041}}}, "0000000381.png": {"car": {"car:2": {"box": [370, 176, 124, 58], "box_score": 0.9801148772239685}, "car:1": {"box": [614, 168, 170, 65], "box_score": 0.994749128818512}, "car:3": {"box": [587, 185, 41, 31], "box_score": 0.6528324484825134}}, "traffic light": {"traffic light:1": {"box": [455, 57, 24, 65], "box_score": 0.6944209337234497}}}, "0000000384.png": {"car": {"car:2": {"box": [331, 180, 144, 60], "box_score": 0.9565045237541199}, "car:1": {"box": [724, 164, 179, 68], "box_score": 0.9946818947792053}, "car:3": {"box": [566, 177, 124, 42], "box_score": 0.9546626210212708}}, "traffic light": {"traffic light:1": {"box": [460, 68, 32, 51], "box_score": 0.6125860810279846}}}, "0000000012.png": {"car": {"car:2": {"box": [49, 205, 254, 137], "box_score": 0.9637360572814941}, "car:5": {"box": [454, 187, 51, 36], "box_score": 0.7724611759185791}, "car:1": {"box": [842, 184, 361, 180], "box_score": 0.9825835824012756}, "car:3": {"box": [113, 202, 57, 31], "box_score": 0.7951770424842834}, "car:4": {"box": [602, 176, 48, 21], "box_score": 0.7873468399047852}}}, "0000000151.png": {"car": {"car:2": {"box": [0, 198, 206, 169], "box_score": 0.9659098982810974}, "car:5": {"box": [799, 169, 57, 35], "box_score": 0.6017757058143616}, "car:1": {"box": [784, 191, 277, 156], "box_score": 0.996648371219635}, "car:3": {"box": [265, 177, 124, 47], "box_score": 0.8707709908485413}, "car:4": {"box": [130, 197, 79, 30], "box_score": 0.77870112657547}}, "person": {"person:2": {"box": [852, 150, 35, 50], "box_score": 0.7034747004508972}, "person:1": {"box": [893, 146, 37, 50], "box_score": 0.8279553651809692}}}, "0000000278.png": {"truck": {"truck:1": {"box": [724, 172, 85, 63], "box_score": 0.6579007506370544}}, "car": {"car:2": {"box": [1, 185, 319, 188], "box_score": 0.9447660446166992}, "car:5": {"box": [0, 177, 74, 33], "box_score": 0.6903064250946045}, "car:1": {"box": [394, 187, 84, 69], "box_score": 0.9582890272140503}, "car:3": {"box": [297, 196, 118, 107], "box_score": 0.8994660377502441}, "car:4": {"box": [551, 176, 42, 27], "box_score": 0.8342848420143127}}}, "0000000250.png": {"car": {"car:2": {"box": [478, 182, 72, 46], "box_score": 0.9706684350967407}, "car:7": {"box": [603, 178, 34, 19], "box_score": 0.6093224287033081}, "car:1": {"box": [758, 189, 150, 92], "box_score": 0.9943594336509705}, "car:4": {"box": [991, 176, 196, 52], "box_score": 0.8913564085960388}, "car:5": {"box": [1136, 176, 105, 53], "box_score": 0.8872609734535217}, "car:3": {"box": [722, 185, 76, 61], "box_score": 0.9308426976203918}, "car:6": {"box": [548, 183, 31, 29], "box_score": 0.7603908777236938}}}, "0000000064.png": {"car": {"car:2": {"box": [0, 225, 89, 86], "box_score": 0.9263109564781189}, "car:7": {"box": [1060, 139, 81, 45], "box_score": 0.6814674139022827}, "car:1": {"box": [7, 203, 364, 171], "box_score": 0.9541905522346497}, "car:4": {"box": [341, 196, 124, 87], "box_score": 0.8923365473747253}, "car:8": {"box": [486, 184, 34, 26], "box_score": 0.6269865036010742}, "car:5": {"box": [740, 165, 78, 40], "box_score": 0.8219950795173645}, "car:3": {"box": [805, 165, 129, 57], "box_score": 0.9194984436035156}, "car:6": {"box": [651, 179, 52, 45], "box_score": 0.7351232767105103}}}, "0000000038.png": {"truck": {"truck:1": {"box": [174, 131, 84, 79], "box_score": 0.7011807560920715}}, "car": {"car:2": {"box": [329, 176, 105, 72], "box_score": 0.9190633296966553}, "car:7": {"box": [510, 177, 34, 24], "box_score": 0.6577358841896057}, "car:1": {"box": [763, 178, 251, 154], "box_score": 0.9950142502784729}, "car:4": {"box": [58, 204, 254, 120], "box_score": 0.9050245881080627}, "car:5": {"box": [0, 247, 50, 128], "box_score": 0.8997551202774048}, "car:3": {"box": [542, 176, 35, 25], "box_score": 0.9173314571380615}, "car:6": {"box": [419, 179, 51, 48], "box_score": 0.8682094216346741}}}, "0000000434.png": {"traffic light": {"traffic light:2": {"box": [348, 9, 41, 103], "box_score": 0.6708604097366333}, "traffic light:3": {"box": [399, 47, 38, 63], "box_score": 0.6238192319869995}, "traffic light:1": {"box": [1047, 29, 32, 77], "box_score": 0.7615506052970886}}}, "0000000427.png": {"traffic light": {"traffic light:2": {"box": [406, 50, 31, 58], "box_score": 0.6128215193748474}, "traffic light:3": {"box": [349, 14, 40, 98], "box_score": 0.6092425584793091}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.8137506246566772}}}, "0000000241.png": {"car": {"car:2": {"box": [905, 225, 345, 144], "box_score": 0.9890775680541992}, "car:7": {"box": [668, 183, 47, 41], "box_score": 0.6833433508872986}, "car:1": {"box": [0, 230, 199, 143], "box_score": 0.9965652823448181}, "car:4": {"box": [686, 188, 73, 56], "box_score": 0.9212674498558044}, "car:5": {"box": [477, 183, 58, 36], "box_score": 0.8601454496383667}, "car:3": {"box": [950, 168, 170, 60], "box_score": 0.98850017786026}, "car:6": {"box": [854, 177, 114, 34], "box_score": 0.7225910425186157}}}, "0000000361.png": {"car": {"car:2": {"box": [346, 189, 88, 60], "box_score": 0.9809073805809021}, "car:5": {"box": [490, 180, 84, 31], "box_score": 0.8963461518287659}, "car:1": {"box": [60, 203, 305, 165], "box_score": 0.9849280714988708}, "car:3": {"box": [625, 178, 86, 29], "box_score": 0.9752383232116699}, "car:4": {"box": [155, 184, 88, 41], "box_score": 0.932994544506073}}, "person": {"person:1": {"box": [790, 173, 37, 77], "box_score": 0.9180878400802612}}}, "0000000419.png": {"car": {"car:1": {"box": [2, 200, 311, 154], "box_score": 0.9841967225074768}}, "traffic light": {"traffic light:2": {"box": [349, 14, 40, 98], "box_score": 0.6763821840286255}, "traffic light:3": {"box": [400, 47, 37, 62], "box_score": 0.6175524592399597}, "traffic light:1": {"box": [1047, 27, 33, 78], "box_score": 0.8293085098266602}}}, "0000000093.png": {"car": {"car:2": {"box": [61, 204, 252, 131], "box_score": 0.9637749195098877}, "car:10": {"box": [519, 184, 35, 24], "box_score": 0.6491963267326355}, "car:1": {"box": [831, 155, 143, 53], "box_score": 0.9923861026763916}, "car:11": {"box": [652, 177, 62, 33], "box_score": 0.627554178237915}, "car:4": {"box": [297, 199, 101, 74], "box_score": 0.9450370073318481}, "car:9": {"box": [1110, 139, 79, 42], "box_score": 0.6774428486824036}, "car:8": {"box": [760, 161, 84, 39], "box_score": 0.7090192437171936}, "car:7": {"box": [1154, 142, 67, 37], "box_score": 0.7099160552024841}, "car:5": {"box": [429, 191, 52, 42], "box_score": 0.9317774772644043}, "car:3": {"box": [385, 195, 61, 55], "box_score": 0.9481322765350342}, "car:6": {"box": [474, 187, 40, 33], "box_score": 0.8482577800750732}}}, "0000000019.png": {"car": {"car:2": {"box": [1021, 139, 95, 40], "box_score": 0.9412153363227844}, "car:7": {"box": [479, 183, 40, 33], "box_score": 0.6151598691940308}, "car:1": {"box": [402, 192, 67, 46], "box_score": 0.9746043682098389}, "car:4": {"box": [452, 191, 43, 36], "box_score": 0.8341589570045471}, "car:5": {"box": [82, 205, 95, 35], "box_score": 0.7944628596305847}, "car:3": {"box": [0, 210, 72, 36], "box_score": 0.8751932382583618}, "car:6": {"box": [167, 203, 59, 35], "box_score": 0.6187031865119934}}}, "0000000222.png": {"car": {"car:2": {"box": [507, 163, 280, 152], "box_score": 0.9269348978996277}, "car:7": {"box": [255, 190, 62, 36], "box_score": 0.8451735973358154}, "car:1": {"box": [373, 194, 119, 69], "box_score": 0.9598338603973389}, "car:9": {"box": [213, 183, 31, 22], "box_score": 0.6633735299110413}, "car:4": {"box": [35, 189, 67, 34], "box_score": 0.8975831270217896}, "car:8": {"box": [240, 188, 40, 31], "box_score": 0.7723499536514282}, "car:5": {"box": [446, 176, 84, 40], "box_score": 0.8972514271736145}, "car:3": {"box": [774, 173, 72, 49], "box_score": 0.9076287150382996}, "car:6": {"box": [863, 169, 115, 66], "box_score": 0.8692728281021118}}}, "0000000125.png": {"car": {"car:2": {"box": [720, 178, 109, 86], "box_score": 0.9751509428024292}, "car:5": {"box": [679, 173, 66, 53], "box_score": 0.9046310782432556}, "car:1": {"box": [802, 179, 288, 168], "box_score": 0.997312605381012}, "car:3": {"box": [438, 174, 70, 44], "box_score": 0.9500702023506165}, "car:4": {"box": [207, 187, 188, 96], "box_score": 0.9487413763999939}}}, "0000000272.png": {"car": {"car:2": {"box": [320, 188, 130, 97], "box_score": 0.9494273066520691}, "car:1": {"box": [12, 188, 338, 178], "box_score": 0.9899507164955139}, "car:4": {"box": [464, 187, 58, 49], "box_score": 0.9229276776313782}, "car:5": {"box": [710, 174, 62, 52], "box_score": 0.7491632103919983}, "car:3": {"box": [429, 193, 60, 61], "box_score": 0.937595009803772}, "car:6": {"box": [121, 179, 92, 30], "box_score": 0.6852220296859741}}}, "0000000311.png": {"car": {"car:2": {"box": [61, 196, 294, 157], "box_score": 0.9919718503952026}, "car:10": {"box": [702, 177, 38, 44], "box_score": 0.6064997911453247}, "car:1": {"box": [799, 186, 218, 119], "box_score": 0.9958223104476929}, "car:9": {"box": [711, 177, 55, 55], "box_score": 0.7460270524024963}, "car:4": {"box": [327, 190, 117, 79], "box_score": 0.9592326879501343}, "car:8": {"box": [579, 174, 44, 15], "box_score": 0.7592654824256897}, "car:7": {"box": [507, 177, 53, 32], "box_score": 0.9226731061935425}, "car:5": {"box": [423, 188, 66, 54], "box_score": 0.9438410401344299}, "car:3": {"box": [972, 211, 271, 162], "box_score": 0.9827037453651428}, "car:6": {"box": [736, 185, 109, 75], "box_score": 0.9367995262145996}}}, "0000000159.png": {"car": {"car:2": {"box": [965, 165, 62, 42], "box_score": 0.9255120754241943}, "car:5": {"box": [0, 234, 24, 39], "box_score": 0.6086456179618835}, "car:1": {"box": [178, 182, 148, 62], "box_score": 0.9643692374229431}, "car:3": {"box": [2, 211, 87, 41], "box_score": 0.9197555184364319}, "car:4": {"box": [859, 172, 79, 38], "box_score": 0.8975608348846436}}, "person": {"person:2": {"box": [1099, 138, 70, 173], "box_score": 0.7208546996116638}, "person:1": {"box": [1023, 132, 64, 177], "box_score": 0.9234351515769958}}}, "0000000127.png": {"car": {"car:2": {"box": [118, 191, 238, 120], "box_score": 0.9856641292572021}, "car:5": {"box": [856, 185, 392, 188], "box_score": 0.9176139235496521}, "car:1": {"box": [743, 171, 150, 108], "box_score": 0.98664790391922}, "car:3": {"box": [691, 174, 70, 56], "box_score": 0.9553733468055725}, "car:4": {"box": [423, 176, 65, 46], "box_score": 0.9235198497772217}}}, "0000000412.png": {"car": {"car:1": {"box": [211, 186, 208, 98], "box_score": 0.9575838446617126}}, "traffic light": {"traffic light:2": {"box": [349, 13, 40, 99], "box_score": 0.7203973531723022}, "traffic light:3": {"box": [401, 47, 36, 62], "box_score": 0.6292983889579773}, "traffic light:1": {"box": [1047, 28, 32, 77], "box_score": 0.848894476890564}}}, "0000000029.png": {"truck": {"truck:1": {"box": [1174, 130, 69, 63], "box_score": 0.9394557476043701}}, "car": {"car:2": {"box": [232, 196, 149, 81], "box_score": 0.9801326990127563}, "car:1": {"box": [365, 193, 80, 55], "box_score": 0.9823644161224365}, "car:3": {"box": [678, 177, 93, 65], "box_score": 0.9582850933074951}, "car:4": {"box": [433, 178, 57, 47], "box_score": 0.8549205660820007}}}, "0000000317.png": {"car": {"car:2": {"box": [998, 217, 241, 154], "box_score": 0.9686623215675354}, "car:7": {"box": [718, 182, 66, 61], "box_score": 0.8566717505455017}, "car:1": {"box": [12, 201, 329, 161], "box_score": 0.9899175763130188}, "car:9": {"box": [513, 181, 33, 30], "box_score": 0.8032434582710266}, "car:5": {"box": [743, 187, 108, 83], "box_score": 0.9421387910842896}, "car:3": {"box": [800, 192, 255, 140], "box_score": 0.9559196829795837}, "car:6": {"box": [303, 192, 126, 85], "box_score": 0.8675317764282227}, "car:12": {"box": [1057, 179, 78, 49], "box_score": 0.6022846698760986}, "car:10": {"box": [983, 180, 76, 38], "box_score": 0.6980786323547363}, "car:11": {"box": [1172, 182, 68, 45], "box_score": 0.6301054358482361}, "car:4": {"box": [472, 181, 58, 39], "box_score": 0.9444756507873535}, "car:8": {"box": [695, 181, 42, 44], "box_score": 0.8254036903381348}}}, "0000000016.png": {"car": {"car:2": {"box": [206, 198, 59, 32], "box_score": 0.9613783955574036}, "car:10": {"box": [105, 205, 41, 26], "box_score": 0.6056549549102783}, "car:1": {"box": [0, 226, 133, 138], "box_score": 0.9844124913215637}, "car:9": {"box": [0, 208, 49, 27], "box_score": 0.7172145247459412}, "car:4": {"box": [128, 199, 85, 32], "box_score": 0.8766889572143555}, "car:8": {"box": [468, 186, 37, 34], "box_score": 0.7740907669067383}, "car:7": {"box": [490, 179, 38, 32], "box_score": 0.8023058772087097}, "car:5": {"box": [428, 189, 56, 41], "box_score": 0.8685492873191833}, "car:3": {"box": [54, 204, 67, 31], "box_score": 0.9159563183784485}, "car:6": {"box": [1128, 318, 115, 56], "box_score": 0.8676739931106567}}}, "0000000020.png": {"car": {"car:2": {"box": [0, 214, 51, 36], "box_score": 0.912716269493103}, "car:7": {"box": [478, 185, 40, 32], "box_score": 0.6384671926498413}, "car:1": {"box": [394, 195, 70, 47], "box_score": 0.9764018654823303}, "car:4": {"box": [447, 193, 45, 36], "box_score": 0.8539792895317078}, "car:8": {"box": [151, 206, 68, 37], "box_score": 0.6329010128974915}, "car:5": {"box": [71, 208, 92, 36], "box_score": 0.7818137407302856}, "car:3": {"box": [1032, 138, 98, 42], "box_score": 0.8898416757583618}, "car:6": {"box": [659, 176, 59, 38], "box_score": 0.6419626474380493}}}, "0000000010.png": {"car": {"car:2": {"box": [169, 201, 182, 103], "box_score": 0.938788890838623}, "car:5": {"box": [600, 176, 39, 19], "box_score": 0.637342631816864}, "car:1": {"box": [789, 179, 217, 153], "box_score": 0.9923121333122253}, "car:3": {"box": [646, 175, 38, 23], "box_score": 0.8117754459381104}, "car:4": {"box": [462, 188, 43, 31], "box_score": 0.7144961953163147}}}, "0000000152.png": {"car": {"car:2": {"box": [0, 212, 168, 155], "box_score": 0.9828365445137024}, "car:1": {"box": [793, 192, 339, 174], "box_score": 0.9925221800804138}, "car:4": {"box": [804, 171, 63, 34], "box_score": 0.7971972823143005}, "car:5": {"box": [118, 199, 80, 32], "box_score": 0.7761723399162292}, "car:3": {"box": [259, 177, 128, 48], "box_score": 0.8889330625534058}, "car:6": {"box": [235, 186, 41, 24], "box_score": 0.6629073023796082}}, "person": {"person:2": {"box": [862, 149, 41, 59], "box_score": 0.7319419980049133}, "person:1": {"box": [906, 146, 42, 53], "box_score": 0.8068485856056213}}}, "0000000314.png": {"car": {"car:2": {"box": [224, 195, 176, 102], "box_score": 0.9917775392532349}, "car:10": {"box": [596, 176, 41, 16], "box_score": 0.6704572439193726}, "car:1": {"box": [0, 213, 243, 160], "box_score": 0.9928269982337952}, "car:9": {"box": [1126, 180, 115, 46], "box_score": 0.7798401117324829}, "car:4": {"box": [869, 188, 379, 181], "box_score": 0.9651131629943848}, "car:8": {"box": [705, 179, 56, 48], "box_score": 0.8125852346420288}, "car:7": {"box": [725, 182, 69, 67], "box_score": 0.9141712188720703}, "car:5": {"box": [491, 180, 51, 35], "box_score": 0.961617112159729}, "car:3": {"box": [756, 185, 160, 101], "box_score": 0.976392388343811}, "car:6": {"box": [378, 191, 85, 65], "box_score": 0.9143760204315186}}}, "0000000124.png": {"car": {"car:2": {"box": [2, 219, 103, 149], "box_score": 0.9885700345039368}, "car:1": {"box": [785, 182, 235, 140], "box_score": 0.9990541338920593}, "car:4": {"box": [712, 179, 103, 79], "box_score": 0.9706459641456604}, "car:5": {"box": [670, 173, 67, 49], "box_score": 0.9443576335906982}, "car:3": {"box": [248, 189, 160, 83], "box_score": 0.974541425704956}, "car:6": {"box": [446, 176, 65, 39], "box_score": 0.9137051105499268}}}, "0000000293.png": {"car": {"car:2": {"box": [742, 189, 86, 65], "box_score": 0.9319092631340027}, "car:7": {"box": [527, 188, 31, 31], "box_score": 0.6162401437759399}, "car:1": {"box": [785, 195, 137, 93], "box_score": 0.9363871216773987}, "car:4": {"box": [718, 188, 43, 45], "box_score": 0.7904608845710754}, "car:5": {"box": [570, 184, 33, 21], "box_score": 0.6335533857345581}, "car:3": {"box": [478, 188, 63, 42], "box_score": 0.9245670437812805}, "car:6": {"box": [694, 183, 28, 35], "box_score": 0.6178159713745117}}}, "0000000180.png": {"bicycle": {"bicycle:1": {"box": [822, 191, 62, 40], "box_score": 0.9153279662132263}}, "car": {"car:2": {"box": [1140, 165, 103, 70], "box_score": 0.9824123978614807}, "car:1": {"box": [938, 172, 194, 69], "box_score": 0.9860776662826538}, "car:3": {"box": [109, 193, 97, 43], "box_score": 0.8250130414962769}}}, "0000000192.png": {"bicycle": {"bicycle:1": {"box": [947, 195, 80, 52], "box_score": 0.9647000432014465}}, "car": {"car:2": {"box": [161, 183, 92, 48], "box_score": 0.9131097793579102}, "car:1": {"box": [1118, 188, 123, 81], "box_score": 0.9583296179771423}, "car:3": {"box": [2, 176, 97, 106], "box_score": 0.8175802230834961}}}, "0000000265.png": {"car": {"car:2": {"box": [910, 200, 335, 168], "box_score": 0.9834256768226624}, "car:7": {"box": [238, 179, 74, 33], "box_score": 0.7282609343528748}, "car:1": {"box": [323, 189, 138, 90], "box_score": 0.9847128391265869}, "car:4": {"box": [437, 187, 71, 61], "box_score": 0.8982957005500793}, "car:5": {"box": [502, 188, 43, 38], "box_score": 0.8964353203773499}, "car:3": {"box": [4, 194, 127, 49], "box_score": 0.9540573954582214}, "car:6": {"box": [700, 179, 53, 37], "box_score": 0.8330099582672119}}}, "0000000443.png": {"traffic light": {"traffic light:2": {"box": [348, 10, 41, 101], "box_score": 0.7144879102706909}, "traffic light:3": {"box": [399, 47, 38, 62], "box_score": 0.6230176687240601}, "traffic light:1": {"box": [1047, 28, 33, 77], "box_score": 0.7822064757347107}}}, "0000000100.png": {"car": {"car:2": {"box": [214, 203, 137, 96], "box_score": 0.9421151280403137}, "car:7": {"box": [925, 144, 130, 73], "box_score": 0.784126341342926}, "car:1": {"box": [0, 218, 229, 157], "box_score": 0.9718202948570251}, "car:9": {"box": [656, 177, 29, 33], "box_score": 0.7269256711006165}, "car:13": {"box": [671, 175, 51, 44], "box_score": 0.6132574081420898}, "car:5": {"box": [421, 190, 66, 43], "box_score": 0.9231513738632202}, "car:3": {"box": [949, 143, 232, 76], "box_score": 0.9307329654693604}, "car:6": {"box": [682, 176, 74, 52], "box_score": 0.8919944763183594}, "car:12": {"box": [524, 180, 30, 21], "box_score": 0.6174155473709106}, "car:10": {"box": [498, 183, 34, 28], "box_score": 0.7179926633834839}, "car:11": {"box": [467, 186, 38, 36], "box_score": 0.6243886947631836}, "car:4": {"box": [339, 196, 90, 60], "box_score": 0.9280790090560913}, "car:8": {"box": [825, 156, 111, 56], "box_score": 0.7568947672843933}}}, "0000000150.png": {"car": {"car:2": {"box": [933, 223, 307, 149], "box_score": 0.9876092672348022}, "car:5": {"box": [1074, 156, 50, 19], "box_score": 0.6199209094047546}, "car:1": {"box": [773, 188, 238, 144], "box_score": 0.9914159178733826}, "car:3": {"box": [1, 197, 239, 164], "box_score": 0.9839205145835876}, "car:4": {"box": [285, 178, 109, 44], "box_score": 0.9473941922187805}}, "person": {"person:2": {"box": [879, 147, 35, 47], "box_score": 0.7053951621055603}, "person:1": {"box": [820, 150, 54, 47], "box_score": 0.7369205355644226}}}, "0000000301.png": {"car": {"car:2": {"box": [1011, 234, 230, 141], "box_score": 0.9716736078262329}, "car:7": {"box": [725, 183, 59, 51], "box_score": 0.791740894317627}, "car:1": {"box": [397, 186, 98, 60], "box_score": 0.9908979535102844}, "car:4": {"box": [813, 183, 233, 137], "box_score": 0.9368376135826111}, "car:8": {"box": [706, 180, 36, 42], "box_score": 0.7140433192253113}, "car:5": {"box": [473, 184, 51, 44], "box_score": 0.9077698588371277}, "car:3": {"box": [756, 186, 101, 75], "box_score": 0.9486224055290222}, "car:6": {"box": [546, 179, 37, 23], "box_score": 0.8915871977806091}}}, "0000000260.png": {"car": {"car:2": {"box": [968, 231, 277, 146], "box_score": 0.9890809059143066}, "car:7": {"box": [592, 181, 37, 18], "box_score": 0.6190572381019592}, "car:1": {"box": [798, 191, 230, 125], "box_score": 0.99315345287323}, "car:4": {"box": [520, 186, 40, 34], "box_score": 0.8357712030410767}, "car:5": {"box": [696, 179, 43, 30], "box_score": 0.7088302969932556}, "car:3": {"box": [405, 184, 94, 70], "box_score": 0.9641875624656677}, "car:6": {"box": [477, 184, 48, 50], "box_score": 0.6801285147666931}}}, "0000000185.png": {"bicycle": {"bicycle:1": {"box": [864, 189, 70, 47], "box_score": 0.9835794568061829}}, "car": {"car:2": {"box": [0, 183, 72, 99], "box_score": 0.8781224489212036}, "car:1": {"box": [1006, 175, 218, 75], "box_score": 0.9692014455795288}, "car:3": {"box": [117, 184, 93, 48], "box_score": 0.8654491305351257}}}, "0000000286.png": {"car": {"car:2": {"box": [87, 189, 266, 171], "box_score": 0.9751542210578918}, "car:5": {"box": [717, 172, 51, 46], "box_score": 0.6754764914512634}, "car:1": {"box": [0, 240, 122, 136], "box_score": 0.9817143678665161}, "car:3": {"box": [733, 175, 54, 56], "box_score": 0.8625374436378479}, "car:4": {"box": [518, 173, 47, 33], "box_score": 0.8376556634902954}}}, "0000000031.png": {"car": {"car:2": {"box": [692, 178, 109, 77], "box_score": 0.9704581499099731}, "car:1": {"box": [169, 198, 181, 99], "box_score": 0.9857168197631836}, "car:3": {"box": [334, 195, 94, 62], "box_score": 0.9612715244293213}, "car:4": {"box": [418, 177, 68, 52], "box_score": 0.80470871925354}}}, "0000000440.png": {"traffic light": {"traffic light:2": {"box": [348, 14, 41, 98], "box_score": 0.7034421563148499}, "traffic light:3": {"box": [399, 47, 38, 63], "box_score": 0.6500977277755737}, "traffic light:1": {"box": [1047, 27, 32, 78], "box_score": 0.8137692213058472}}}, "0000000121.png": {"car": {"car:2": {"box": [0, 202, 273, 160], "box_score": 0.9932352900505066}, "car:7": {"box": [461, 177, 60, 36], "box_score": 0.7561582326889038}, "car:1": {"box": [744, 182, 155, 97], "box_score": 0.9950520396232605}, "car:4": {"box": [697, 180, 75, 65], "box_score": 0.9506382942199707}, "car:8": {"box": [43, 190, 95, 34], "box_score": 0.7200635075569153}, "car:5": {"box": [325, 188, 119, 67], "box_score": 0.9344533085823059}, "car:3": {"box": [1013, 241, 230, 134], "box_score": 0.9619333148002625}, "car:6": {"box": [665, 176, 55, 41], "box_score": 0.8859457969665527}}}, "0000000219.png": {"car": {"car:2": {"box": [361, 181, 81, 35], "box_score": 0.9390860795974731}, "car:7": {"box": [97, 186, 33, 24], "box_score": 0.6107562184333801}, "car:1": {"box": [283, 195, 127, 68], "box_score": 0.9674753546714783}, "car:4": {"box": [154, 192, 68, 41], "box_score": 0.8709341883659363}, "car:5": {"box": [748, 179, 97, 57], "box_score": 0.8158478736877441}, "car:3": {"box": [423, 167, 246, 138], "box_score": 0.9173599481582642}, "car:6": {"box": [667, 180, 65, 44], "box_score": 0.7973551154136658}}}, "0000000279.png": {"car": {"car:2": {"box": [377, 188, 93, 77], "box_score": 0.9552913308143616}, "car:5": {"box": [717, 178, 28, 44], "box_score": 0.635614812374115}, "car:1": {"box": [259, 199, 145, 110], "box_score": 0.964074969291687}, "car:3": {"box": [0, 190, 278, 184], "box_score": 0.9266766905784607}, "car:4": {"box": [547, 178, 40, 28], "box_score": 0.9007526636123657}}}, "0000000245.png": {"car": {"car:2": {"box": [715, 188, 98, 69], "box_score": 0.9519107937812805}, "car:7": {"box": [671, 176, 31, 25], "box_score": 0.6936980485916138}, "car:1": {"box": [1042, 165, 203, 75], "box_score": 0.9720721244812012}, "car:4": {"box": [691, 184, 63, 47], "box_score": 0.8550158143043518}, "car:5": {"box": [910, 177, 126, 41], "box_score": 0.8165148496627808}, "car:3": {"box": [484, 182, 63, 40], "box_score": 0.9256563782691956}, "car:6": {"box": [539, 182, 32, 26], "box_score": 0.7400617599487305}}}, "0000000091.png": {"car": {"car:2": {"box": [819, 157, 121, 47], "box_score": 0.956480860710144}, "car:7": {"box": [1085, 143, 65, 38], "box_score": 0.866087019443512}, "car:1": {"box": [180, 198, 185, 103], "box_score": 0.9713146090507507}, "car:4": {"box": [408, 192, 57, 50], "box_score": 0.9280679821968079}, "car:8": {"box": [1121, 143, 64, 37], "box_score": 0.7932462692260742}, "car:5": {"box": [450, 190, 45, 39], "box_score": 0.9077041745185852}, "car:3": {"box": [348, 198, 78, 62], "box_score": 0.9437596797943115}, "car:6": {"box": [483, 187, 39, 31], "box_score": 0.8929539918899536}}}, "0000000318.png": {"car": {"car:2": {"box": [807, 191, 341, 166], "box_score": 0.9655430316925049}, "car:7": {"box": [1098, 281, 145, 94], "box_score": 0.764133632183075}, "car:1": {"box": [2, 205, 306, 167], "box_score": 0.9890069961547852}, "car:4": {"box": [275, 194, 139, 88], "box_score": 0.9438961744308472}, "car:8": {"box": [695, 181, 44, 45], "box_score": 0.7291191816329956}, "car:5": {"box": [747, 188, 135, 88], "box_score": 0.9025362730026245}, "car:3": {"box": [467, 180, 67, 40], "box_score": 0.9476335048675537}, "car:6": {"box": [718, 180, 79, 62], "box_score": 0.8669848442077637}}}, "0000000118.png": {"car": {"car:2": {"box": [166, 195, 183, 105], "box_score": 0.9783132672309875}, "car:7": {"box": [685, 180, 62, 53], "box_score": 0.8799469470977783}, "car:1": {"box": [0, 214, 180, 157], "box_score": 0.995795488357544}, "car:4": {"box": [870, 178, 394, 193], "box_score": 0.9324159622192383}, "car:8": {"box": [475, 177, 54, 33], "box_score": 0.8769481778144836}, "car:5": {"box": [717, 181, 113, 75], "box_score": 0.9270647764205933}, "car:3": {"box": [376, 185, 92, 56], "box_score": 0.9601805806159973}, "car:6": {"box": [654, 176, 49, 38], "box_score": 0.8971196413040161}}}, "0000000162.png": {"car": {"car:2": {"box": [851, 165, 117, 49], "box_score": 0.9616567492485046}, "car:1": {"box": [1, 209, 59, 45], "box_score": 0.9901335835456848}, "car:4": {"box": [986, 163, 140, 54], "box_score": 0.7822654843330383}, "car:5": {"box": [299, 191, 41, 25], "box_score": 0.6991022825241089}, "car:3": {"box": [137, 181, 164, 65], "box_score": 0.8749586939811707}, "car:6": {"box": [71, 195, 66, 30], "box_score": 0.6304619908332825}}, "person": {"person:1": {"box": [1124, 133, 82, 212], "box_score": 0.619114339351654}}}, "0000000410.png": {"car": {"car:1": {"box": [251, 185, 183, 89], "box_score": 0.8936623930931091}}, "traffic light": {"traffic light:2": {"box": [348, 9, 40, 104], "box_score": 0.6468091607093811}, "traffic light:1": {"box": [1046, 28, 33, 78], "box_score": 0.8586576581001282}}}, "0000000176.png": {"bicycle": {"bicycle:1": {"box": [801, 189, 59, 36], "box_score": 0.9002830386161804}}, "car": {"car:2": {"box": [1091, 161, 151, 68], "box_score": 0.9889233112335205}, "car:1": {"box": [907, 171, 169, 63], "box_score": 0.9963125586509705}, "car:3": {"box": [133, 192, 92, 42], "box_score": 0.879879355430603}}}, "0000000422.png": {"car": {"car:1": {"box": [0, 212, 245, 163], "box_score": 0.982952356338501}}, "traffic light": {"traffic light:2": {"box": [349, 14, 40, 98], "box_score": 0.6946309804916382}, "traffic light:3": {"box": [401, 48, 36, 61], "box_score": 0.614611804485321}, "traffic light:1": {"box": [1047, 28, 32, 77], "box_score": 0.8412990570068359}}}, "0000000015.png": {"car": {"car:2": {"box": [1000, 221, 239, 152], "box_score": 0.9725140929222107}, "car:7": {"box": [473, 187, 35, 31], "box_score": 0.648189127445221}, "car:1": {"box": [0, 216, 190, 150], "box_score": 0.9850769639015198}, "car:9": {"box": [493, 178, 36, 32], "box_score": 0.6170602440834045}, "car:4": {"box": [432, 189, 58, 38], "box_score": 0.8644906282424927}, "car:8": {"box": [71, 203, 65, 22], "box_score": 0.622939944267273}, "car:5": {"box": [219, 198, 58, 30], "box_score": 0.859058141708374}, "car:3": {"box": [142, 198, 84, 32], "box_score": 0.8826071619987488}, "car:6": {"box": [619, 175, 41, 21], "box_score": 0.6920303702354431}}}, "0000000126.png": {"car": {"car:2": {"box": [170, 192, 205, 102], "box_score": 0.9717161655426025}, "car:1": {"box": [826, 182, 365, 186], "box_score": 0.9928585290908813}, "car:4": {"box": [688, 174, 66, 52], "box_score": 0.9494068622589111}, "car:5": {"box": [430, 176, 74, 44], "box_score": 0.9133498668670654}, "car:3": {"box": [733, 180, 124, 91], "box_score": 0.9616411328315735}, "car:6": {"box": [671, 173, 47, 46], "box_score": 0.6514826416969299}}}, "0000000076.png": {"car": {"car:2": {"box": [441, 182, 58, 38], "box_score": 0.9439566135406494}, "car:7": {"box": [329, 183, 106, 68], "box_score": 0.6117788553237915}, "car:1": {"box": [1, 213, 214, 158], "box_score": 0.9941775798797607}, "car:4": {"box": [1010, 125, 232, 144], "box_score": 0.8786491751670837}, "car:5": {"box": [879, 154, 204, 71], "box_score": 0.8623300790786743}, "car:3": {"box": [707, 176, 115, 84], "box_score": 0.9412603378295898}, "car:6": {"box": [483, 181, 31, 29], "box_score": 0.7619099617004395}}}, "0000000055.png": {"car": {"car:2": {"box": [265, 197, 116, 65], "box_score": 0.9700304269790649}, "car:7": {"box": [934, 145, 51, 29], "box_score": 0.6296318769454956}, "car:1": {"box": [0, 216, 106, 153], "box_score": 0.9918662905693054}, "car:4": {"box": [736, 163, 97, 40], "box_score": 0.9375759959220886}, "car:5": {"box": [482, 185, 47, 40], "box_score": 0.9000508189201355}, "car:3": {"box": [410, 188, 95, 63], "box_score": 0.9673212766647339}, "car:6": {"box": [628, 178, 44, 30], "box_score": 0.8568309545516968}}}, "0000000007.png": {"car": {"car:2": {"box": [879, 195, 384, 174], "box_score": 0.9366751909255981}, "car:7": {"box": [255, 195, 40, 28], "box_score": 0.6097596287727356}, "car:1": {"box": [740, 177, 131, 105], "box_score": 0.9973160624504089}, "car:4": {"box": [477, 185, 44, 29], "box_score": 0.7826281189918518}, "car:5": {"box": [584, 175, 39, 20], "box_score": 0.7797017097473145}, "car:3": {"box": [268, 196, 130, 80], "box_score": 0.9334776401519775}, "car:6": {"box": [512, 179, 36, 25], "box_score": 0.6537231802940369}}}, "0000000028.png": {"truck": {"truck:1": {"box": [1154, 133, 89, 61], "box_score": 0.8601068258285522}}, "car": {"car:2": {"box": [262, 197, 132, 75], "box_score": 0.985903263092041}, "car:1": {"box": [380, 194, 70, 52], "box_score": 0.992416262626648}, "car:3": {"box": [676, 176, 87, 63], "box_score": 0.8830649852752686}, "car:4": {"box": [438, 181, 56, 44], "box_score": 0.7729812860488892}}}, "0000000227.png": {"car": {"car:2": {"box": [27, 205, 132, 92], "box_score": 0.9782790541648865}, "car:10": {"box": [1078, 152, 61, 61], "box_score": 0.642815113067627}, "car:1": {"box": [0, 220, 101, 147], "box_score": 0.9841406345367432}, "car:9": {"box": [403, 179, 32, 33], "box_score": 0.7026432752609253}, "car:4": {"box": [515, 185, 135, 80], "box_score": 0.95107102394104}, "car:8": {"box": [1120, 156, 123, 76], "box_score": 0.7936041951179504}, "car:7": {"box": [413, 182, 59, 38], "box_score": 0.8877683877944946}, "car:5": {"box": [591, 166, 94, 39], "box_score": 0.9321403503417969}, "car:3": {"box": [703, 136, 429, 228], "box_score": 0.9667994976043701}, "car:6": {"box": [224, 183, 46, 33], "box_score": 0.9303341507911682}}}, "0000000353.png": {"truck": {"truck:1": {"box": [402, 154, 81, 49], "box_score": 0.7379288673400879}}, "car": {"car:2": {"box": [347, 181, 69, 37], "box_score": 0.7047153115272522}, "car:1": {"box": [626, 174, 75, 25], "box_score": 0.953044593334198}, "car:3": {"box": [401, 184, 75, 55], "box_score": 0.6513206362724304}, "car:4": {"box": [508, 173, 76, 31], "box_score": 0.6279450058937073}}, "person": {"person:1": {"box": [717, 171, 19, 47], "box_score": 0.7525338530540466}}}, "0000000043.png": {"car": {"car:2": {"box": [179, 179, 179, 108], "box_score": 0.9717671871185303}, "car:10": {"box": [628, 173, 31, 23], "box_score": 0.6578121185302734}, "car:1": {"box": [913, 195, 335, 174], "box_score": 0.9881687760353088}, "car:9": {"box": [1104, 149, 137, 39], "box_score": 0.7559416890144348}, "car:4": {"box": [346, 181, 83, 65], "box_score": 0.8679908514022827}, "car:8": {"box": [0, 253, 82, 119], "box_score": 0.7836236357688904}, "car:7": {"box": [492, 179, 31, 28], "box_score": 0.8194746375083923}, "car:5": {"box": [519, 178, 40, 29], "box_score": 0.8659312725067139}, "car:3": {"box": [690, 162, 86, 29], "box_score": 0.8999481201171875}, "car:6": {"box": [428, 182, 55, 40], "box_score": 0.8361213207244873}}}, "0000000102.png": {"car": {"car:2": {"box": [1041, 140, 196, 93], "box_score": 0.944757878780365}, "car:7": {"box": [970, 141, 141, 83], "box_score": 0.8469890356063843}, "car:1": {"box": [0, 232, 110, 142], "box_score": 0.9850018620491028}, "car:9": {"box": [680, 175, 51, 55], "box_score": 0.7746793031692505}, "car:5": {"box": [899, 152, 107, 66], "box_score": 0.9190413951873779}, "car:3": {"box": [402, 189, 71, 48], "box_score": 0.9355365037918091}, "car:6": {"box": [292, 198, 116, 73], "box_score": 0.8661022186279297}, "car:12": {"box": [493, 185, 36, 29], "box_score": 0.6283271312713623}, "car:10": {"box": [659, 177, 33, 35], "box_score": 0.7440066337585449}, "car:11": {"box": [453, 186, 44, 39], "box_score": 0.7029367089271545}, "car:4": {"box": [94, 208, 210, 123], "box_score": 0.9256389141082764}, "car:8": {"box": [701, 181, 82, 58], "box_score": 0.7905641198158264}}}, "0000000329.png": {"car": {"car:2": {"box": [348, 179, 102, 67], "box_score": 0.9908483028411865}, "car:7": {"box": [623, 170, 44, 18], "box_score": 0.6021182537078857}, "car:1": {"box": [828, 185, 329, 176], "box_score": 0.9933072924613953}, "car:4": {"box": [738, 183, 140, 90], "box_score": 0.8771267533302307}, "car:5": {"box": [514, 173, 37, 17], "box_score": 0.6941152811050415}, "car:3": {"box": [427, 176, 62, 52], "box_score": 0.9602691531181335}, "car:6": {"box": [728, 174, 61, 63], "box_score": 0.6893460750579834}}}, "0000000140.png": {"car": {"car:2": {"box": [196, 189, 170, 99], "box_score": 0.9454202651977539}, "car:5": {"box": [710, 180, 61, 60], "box_score": 0.7014132738113403}, "car:1": {"box": [800, 181, 351, 184], "box_score": 0.9955620765686035}, "car:3": {"box": [728, 180, 139, 102], "box_score": 0.930695116519928}, "car:4": {"box": [341, 188, 86, 67], "box_score": 0.7988629341125488}}}, "0000000266.png": {"car": {"car:2": {"box": [302, 189, 145, 95], "box_score": 0.987913191318512}, "car:7": {"box": [225, 183, 77, 34], "box_score": 0.81893390417099}, "car:1": {"box": [953, 212, 290, 156], "box_score": 0.9910147786140442}, "car:4": {"box": [493, 189, 47, 41], "box_score": 0.9137797951698303}, "car:5": {"box": [421, 187, 77, 65], "box_score": 0.8467267155647278}, "car:3": {"box": [0, 197, 100, 49], "box_score": 0.9578994512557983}, "car:6": {"box": [701, 178, 48, 39], "box_score": 0.8300041556358337}}}, "0000000106.png": {"car": {"car:2": {"box": [131, 202, 212, 104], "box_score": 0.984838604927063}, "car:7": {"box": [704, 177, 63, 67], "box_score": 0.8844744563102722}, "car:1": {"box": [0, 223, 121, 143], "box_score": 0.9918203353881836}, "car:9": {"box": [477, 183, 43, 33], "box_score": 0.8339710831642151}, "car:13": {"box": [965, 155, 105, 68], "box_score": 0.6970569491386414}, "car:5": {"box": [1008, 148, 160, 76], "box_score": 0.9242686629295349}, "car:3": {"box": [339, 190, 107, 62], "box_score": 0.9820512533187866}, "car:6": {"box": [730, 177, 126, 87], "box_score": 0.9194594025611877}, "car:12": {"box": [578, 172, 36, 21], "box_score": 0.6991442441940308}, "car:10": {"box": [672, 178, 38, 41], "box_score": 0.7873722910881042}, "car:11": {"box": [429, 186, 51, 46], "box_score": 0.749904990196228}, "car:4": {"box": [1128, 136, 114, 113], "box_score": 0.9638002514839172}, "car:8": {"box": [514, 179, 35, 24], "box_score": 0.8478850722312927}}}, "0000000320.png": {"car": {"car:2": {"box": [187, 197, 194, 116], "box_score": 0.9768624305725098}, "car:7": {"box": [700, 179, 46, 49], "box_score": 0.7946832180023193}, "car:1": {"box": [2, 212, 211, 156], "box_score": 0.9915651082992554}, "car:4": {"box": [773, 188, 167, 108], "box_score": 0.9519973993301392}, "car:8": {"box": [501, 180, 33, 34], "box_score": 0.7189674973487854}, "car:5": {"box": [730, 178, 91, 75], "box_score": 0.9215748310089111}, "car:3": {"box": [451, 181, 69, 42], "box_score": 0.955428957939148}, "car:6": {"box": [902, 203, 374, 167], "box_score": 0.8595050573348999}}}, "0000000409.png": {"car": {"car:2": {"box": [265, 184, 178, 84], "box_score": 0.8920577764511108}, "car:1": {"box": [0, 237, 60, 139], "box_score": 0.9915266633033752}}, "traffic light": {"traffic light:2": {"box": [350, 13, 39, 99], "box_score": 0.6629596948623657}, "traffic light:3": {"box": [406, 49, 31, 59], "box_score": 0.657349705696106}, "traffic light:1": {"box": [1046, 28, 33, 77], "box_score": 0.8817207217216492}}}, "0000000196.png": {"bicycle": {"bicycle:1": {"box": [1008, 201, 91, 52], "box_score": 0.9019119143486023}}, "car": {"car:2": {"box": [201, 183, 88, 47], "box_score": 0.9480160474777222}, "car:1": {"box": [0, 177, 141, 114], "box_score": 0.958274781703949}, "car:3": {"box": [1205, 219, 38, 56], "box_score": 0.9368812441825867}, "car:4": {"box": [122, 182, 70, 40], "box_score": 0.7635440230369568}}}, "0000000425.png": {"car": {"car:1": {"box": [2, 235, 145, 133], "box_score": 0.9934799671173096}}, "traffic light": {"traffic light:2": {"box": [350, 13, 39, 99], "box_score": 0.700237512588501}, "traffic light:3": {"box": [405, 49, 32, 59], "box_score": 0.6236019134521484}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.8359684348106384}}}, "0000000424.png": {"car": {"car:1": {"box": [0, 224, 182, 146], "box_score": 0.9933225512504578}}, "traffic light": {"traffic light:2": {"box": [349, 14, 40, 98], "box_score": 0.6546530723571777}, "traffic light:1": {"box": [1047, 28, 33, 78], "box_score": 0.8097615242004395}}}, "0000000394.png": {"car": {"car:2": {"box": [488, 178, 128, 49], "box_score": 0.9763680696487427}, "car:1": {"box": [179, 193, 178, 77], "box_score": 0.998565137386322}, "car:3": {"box": [1139, 158, 103, 73], "box_score": 0.9703219532966614}}, "traffic light": {"traffic light:1": {"box": [370, 23, 41, 88], "box_score": 0.7090003490447998}}}, "0000000389.png": {"car": {"car:2": {"box": [527, 178, 129, 44], "box_score": 0.9834966659545898}, "car:1": {"box": [261, 182, 142, 71], "box_score": 0.9921891689300537}, "car:3": {"box": [927, 161, 196, 71], "box_score": 0.9830815196037292}}, "traffic light": {"traffic light:1": {"box": [400, 33, 31, 80], "box_score": 0.7388616800308228}}}, "0000000417.png": {"car": {"car:1": {"box": [59, 194, 289, 133], "box_score": 0.9874317646026611}}, "traffic light": {"traffic light:2": {"box": [348, 9, 41, 104], "box_score": 0.6680038571357727}, "traffic light:3": {"box": [401, 48, 36, 62], "box_score": 0.6218007802963257}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.8403385281562805}}}, "0000000032.png": {"car": {"car:2": {"box": [699, 178, 119, 82], "box_score": 0.9494231343269348}, "car:5": {"box": [558, 176, 29, 22], "box_score": 0.6319510340690613}, "car:1": {"box": [119, 199, 206, 109], "box_score": 0.9842946529388428}, "car:3": {"box": [309, 197, 107, 65], "box_score": 0.9360628724098206}, "car:4": {"box": [412, 180, 68, 52], "box_score": 0.8119495511054993}}}, "0000000158.png": {"car": {"car:2": {"box": [1022, 280, 224, 91], "box_score": 0.8642368912696838}, "car:5": {"box": [0, 221, 49, 49], "box_score": 0.7968252301216125}, "car:1": {"box": [851, 172, 83, 37], "box_score": 0.9252031445503235}, "car:3": {"box": [16, 206, 104, 40], "box_score": 0.8492149114608765}, "car:4": {"box": [192, 179, 142, 61], "box_score": 0.8396052122116089}}, "person": {"person:2": {"box": [1055, 130, 63, 167], "box_score": 0.774465024471283}, "person:1": {"box": [991, 132, 62, 166], "box_score": 0.9308265447616577}}}, "0000000376.png": {"car": {"car:2": {"box": [439, 174, 180, 57], "box_score": 0.8992919325828552}, "car:1": {"box": [634, 177, 98, 36], "box_score": 0.9600980281829834}, "car:3": {"box": [0, 153, 48, 69], "box_score": 0.6693975925445557}}}, "0000000383.png": {"car": {"car:2": {"box": [348, 178, 130, 60], "box_score": 0.9572564959526062}, "car:1": {"box": [690, 166, 171, 67], "box_score": 0.9902287721633911}, "car:3": {"box": [576, 176, 115, 41], "box_score": 0.9219511151313782}}, "traffic light": {"traffic light:1": {"box": [429, 49, 34, 70], "box_score": 0.689161479473114}}}, "0000000013.png": {"car": {"car:2": {"box": [0, 210, 275, 149], "box_score": 0.9519956707954407}, "car:7": {"box": [102, 203, 56, 18], "box_score": 0.6089755892753601}, "car:1": {"box": [870, 190, 384, 177], "box_score": 0.9760077595710754}, "car:4": {"box": [242, 198, 50, 29], "box_score": 0.8606917262077332}, "car:5": {"box": [449, 189, 45, 37], "box_score": 0.8250716924667358}, "car:3": {"box": [609, 175, 44, 22], "box_score": 0.9234638214111328}, "car:6": {"box": [482, 187, 30, 30], "box_score": 0.6319758296012878}}}, "0000000134.png": {"car": {"car:2": {"box": [338, 187, 101, 68], "box_score": 0.9783318042755127}, "car:7": {"box": [0, 265, 53, 110], "box_score": 0.6495470404624939}, "car:1": {"box": [720, 177, 145, 93], "box_score": 0.9926424622535706}, "car:4": {"box": [689, 176, 64, 58], "box_score": 0.9226402044296265}, "car:8": {"box": [844, 165, 52, 18], "box_score": 0.6271743774414062}, "car:5": {"box": [422, 186, 51, 49], "box_score": 0.8611973524093628}, "car:3": {"box": [897, 188, 353, 179], "box_score": 0.9768805503845215}, "car:6": {"box": [23, 189, 129, 59], "box_score": 0.7442262768745422}}}, "0000000116.png": {"car": {"car:2": {"box": [3, 204, 265, 169], "box_score": 0.9796394109725952}, "car:7": {"box": [656, 178, 43, 36], "box_score": 0.807258665561676}, "car:1": {"box": [795, 181, 297, 166], "box_score": 0.9932004809379578}, "car:9": {"box": [681, 181, 53, 50], "box_score": 0.6921404600143433}, "car:4": {"box": [250, 193, 137, 87], "box_score": 0.919268786907196}, "car:8": {"box": [534, 174, 40, 25], "box_score": 0.7506629228591919}, "car:5": {"box": [706, 184, 89, 61], "box_score": 0.8489289879798889}, "car:3": {"box": [402, 187, 78, 50], "box_score": 0.9353994727134705}, "car:6": {"box": [485, 178, 48, 33], "box_score": 0.8413571119308472}}}, "0000000321.png": {"car": {"car:2": {"box": [445, 182, 68, 44], "box_score": 0.987633228302002}, "car:10": {"box": [7, 188, 108, 27], "box_score": 0.7276639938354492}, "car:1": {"box": [1, 223, 149, 145], "box_score": 0.9888195395469666}, "car:9": {"box": [661, 173, 38, 18], "box_score": 0.7413124442100525}, "car:4": {"box": [119, 199, 242, 132], "box_score": 0.9808370471000671}, "car:8": {"box": [702, 177, 54, 55], "box_score": 0.8169513940811157}, "car:7": {"box": [923, 203, 316, 154], "box_score": 0.8172450065612793}, "car:5": {"box": [734, 180, 95, 77], "box_score": 0.9453960657119751}, "car:3": {"box": [780, 188, 204, 122], "box_score": 0.9810633659362793}, "car:6": {"box": [493, 180, 37, 35], "box_score": 0.9354304075241089}}}, "0000000225.png": {"car": {"car:2": {"box": [601, 150, 350, 192], "box_score": 0.9598388075828552}, "car:10": {"box": [341, 182, 33, 32], "box_score": 0.7860305905342102}, "car:1": {"box": [456, 188, 126, 73], "box_score": 0.9692360162734985}, "car:11": {"box": [969, 162, 55, 49], "box_score": 0.7128943800926208}, "car:4": {"box": [2, 207, 95, 89], "box_score": 0.9441599249839783}, "car:9": {"box": [0, 225, 59, 110], "box_score": 0.7885492444038391}, "car:8": {"box": [151, 187, 47, 31], "box_score": 0.8653352856636047}, "car:7": {"box": [353, 188, 58, 35], "box_score": 0.872769296169281}, "car:5": {"box": [531, 170, 90, 35], "box_score": 0.9427307844161987}, "car:3": {"box": [1001, 162, 159, 73], "box_score": 0.9533398747444153}, "car:6": {"box": [916, 165, 66, 55], "box_score": 0.9138798117637634}}}, "0000000047.png": {"car": {"car:2": {"box": [0, 184, 251, 178], "box_score": 0.953885018825531}, "car:7": {"box": [1093, 152, 127, 35], "box_score": 0.7543883919715881}, "car:1": {"box": [238, 187, 135, 83], "box_score": 0.957843005657196}, "car:4": {"box": [699, 162, 91, 32], "box_score": 0.9434268474578857}, "car:5": {"box": [625, 175, 36, 24], "box_score": 0.8264124393463135}, "car:3": {"box": [398, 183, 59, 45], "box_score": 0.950686514377594}, "car:6": {"box": [494, 181, 49, 36], "box_score": 0.8054692149162292}}}, "0000000164.png": {"car": {"car:2": {"box": [1148, 161, 75, 74], "box_score": 0.8852551579475403}, "car:5": {"box": [1036, 163, 123, 47], "box_score": 0.7523602247238159}, "car:1": {"box": [858, 170, 122, 48], "box_score": 0.9756853580474854}, "car:3": {"box": [108, 185, 173, 67], "box_score": 0.8651581406593323}, "car:4": {"box": [0, 223, 25, 32], "box_score": 0.7556512355804443}}}, "0000000113.png": {"car": {"car:2": {"box": [746, 175, 175, 110], "box_score": 0.9672333598136902}, "car:10": {"box": [542, 170, 49, 25], "box_score": 0.7193232774734497}, "car:1": {"box": [116, 192, 241, 124], "box_score": 0.9834534525871277}, "car:9": {"box": [652, 178, 39, 32], "box_score": 0.7546131610870361}, "car:4": {"box": [691, 179, 72, 56], "box_score": 0.9387722611427307}, "car:8": {"box": [496, 178, 44, 29], "box_score": 0.7739646434783936}, "car:7": {"box": [0, 190, 68, 58], "box_score": 0.8976442813873291}, "car:5": {"box": [339, 192, 89, 67], "box_score": 0.9324242472648621}, "car:3": {"box": [433, 185, 64, 44], "box_score": 0.9414615631103516}, "car:6": {"box": [851, 190, 393, 181], "box_score": 0.9215216636657715}}}, "0000000188.png": {"bicycle": {"bicycle:1": {"box": [896, 193, 78, 49], "box_score": 0.9536385536193848}}, "car": {"car:2": {"box": [135, 185, 91, 48], "box_score": 0.908778190612793}, "car:1": {"box": [1054, 178, 190, 79], "box_score": 0.9838308095932007}, "car:3": {"box": [0, 180, 82, 101], "box_score": 0.8970090746879578}, "car:4": {"box": [67, 188, 52, 38], "box_score": 0.7102171778678894}}}, "0000000326.png": {"car": {"car:2": {"box": [778, 185, 186, 115], "box_score": 0.9684996008872986}, "car:7": {"box": [550, 175, 38, 16], "box_score": 0.849712073802948}, "car:1": {"box": [394, 180, 85, 57], "box_score": 0.9762669801712036}, "car:4": {"box": [0, 227, 178, 147], "box_score": 0.9605128169059753}, "car:5": {"box": [454, 178, 54, 45], "box_score": 0.9543125629425049}, "car:3": {"box": [890, 201, 356, 168], "box_score": 0.9649739265441895}, "car:6": {"box": [724, 184, 89, 69], "box_score": 0.9277952909469604}}}, "0000000081.png": {"truck": {"truck:1": {"box": [21, 233, 217, 98], "box_score": 0.6453291773796082}}, "car": {"car:2": {"box": [405, 186, 78, 46], "box_score": 0.9656996726989746}, "car:1": {"box": [771, 184, 244, 141], "box_score": 0.9911335110664368}, "car:4": {"box": [199, 191, 175, 96], "box_score": 0.9036746025085449}, "car:5": {"box": [1022, 145, 219, 106], "box_score": 0.9018858671188354}, "car:3": {"box": [463, 184, 42, 36], "box_score": 0.911139190196991}, "car:6": {"box": [503, 182, 29, 28], "box_score": 0.6684399843215942}}}, "0000000026.png": {"car": {"car:2": {"box": [402, 193, 60, 48], "box_score": 0.9367280602455139}, "car:1": {"box": [309, 194, 104, 66], "box_score": 0.973097026348114}, "car:4": {"box": [448, 181, 54, 43], "box_score": 0.8829041123390198}, "car:5": {"box": [1116, 135, 125, 56], "box_score": 0.7575211524963379}, "car:3": {"box": [668, 173, 79, 62], "box_score": 0.9027135968208313}, "car:6": {"box": [746, 162, 40, 21], "box_score": 0.6268060207366943}}}, "0000000339.png": {"truck": {"truck:1": {"box": [609, 151, 68, 42], "box_score": 0.8705434203147888}}, "car": {"car:2": {"box": [1, 199, 242, 157], "box_score": 0.9763338565826416}, "car:1": {"box": [770, 183, 227, 135], "box_score": 0.9800946116447449}, "car:4": {"box": [221, 184, 146, 98], "box_score": 0.9593288898468018}, "car:5": {"box": [476, 177, 52, 27], "box_score": 0.9084170460700989}, "car:3": {"box": [895, 199, 346, 169], "box_score": 0.9716702699661255}, "car:6": {"box": [684, 171, 47, 21], "box_score": 0.7733727097511292}}}, "0000000173.png": {"car": {"car:2": {"box": [1065, 157, 177, 63], "box_score": 0.9866985082626343}, "car:1": {"box": [888, 168, 159, 62], "box_score": 0.9968863129615784}, "car:3": {"box": [165, 192, 83, 39], "box_score": 0.8951213955879211}}}, "0000000378.png": {"car": {"car:2": {"box": [527, 174, 132, 62], "box_score": 0.8682135343551636}, "car:1": {"box": [409, 176, 106, 51], "box_score": 0.9391419291496277}, "car:3": {"box": [638, 177, 87, 36], "box_score": 0.8519754409790039}}, "traffic light": {"traffic light:1": {"box": [476, 69, 23, 59], "box_score": 0.6190178394317627}}}, "0000000258.png": {"car": {"car:2": {"box": [894, 214, 355, 155], "box_score": 0.9889005422592163}, "car:5": {"box": [513, 186, 37, 37], "box_score": 0.6058464646339417}, "car:1": {"box": [781, 188, 173, 97], "box_score": 0.9931479096412659}, "car:3": {"box": [425, 183, 93, 60], "box_score": 0.9809619784355164}, "car:4": {"box": [529, 184, 39, 31], "box_score": 0.8490380644798279}}}, "0000000143.png": {"car": {"car:2": {"box": [886, 207, 368, 166], "box_score": 0.9802598357200623}, "car:7": {"box": [355, 177, 88, 34], "box_score": 0.7161480188369751}, "car:1": {"box": [35, 197, 258, 133], "box_score": 0.9891129732131958}, "car:4": {"box": [282, 195, 109, 79], "box_score": 0.9069103598594666}, "car:5": {"box": [728, 185, 74, 76], "box_score": 0.903564989566803}, "car:3": {"box": [758, 188, 219, 131], "box_score": 0.9659268260002136}, "car:6": {"box": [904, 169, 51, 21], "box_score": 0.7253904342651367}}}, "0000000247.png": {"car": {"car:2": {"box": [483, 179, 68, 41], "box_score": 0.9483181238174438}, "car:7": {"box": [678, 171, 32, 27], "box_score": 0.7088176608085632}, "car:1": {"box": [735, 185, 110, 76], "box_score": 0.9766020178794861}, "car:4": {"box": [709, 178, 60, 57], "box_score": 0.8318003416061401}, "car:5": {"box": [943, 171, 162, 49], "box_score": 0.7882792353630066}, "car:3": {"box": [1100, 166, 142, 71], "box_score": 0.8960372805595398}, "car:6": {"box": [545, 180, 28, 26], "box_score": 0.710491955280304}}}, "0000000197.png": {"bicycle": {"bicycle:1": {"box": [1027, 199, 90, 56], "box_score": 0.9801116585731506}}, "car": {"car:2": {"box": [213, 182, 88, 47], "box_score": 0.9284549355506897}, "car:1": {"box": [0, 177, 147, 111], "box_score": 0.9817694425582886}, "car:3": {"box": [134, 184, 68, 40], "box_score": 0.9049394726753235}}}, "0000000338.png": {"truck": {"truck:1": {"box": [623, 151, 68, 47], "box_score": 0.8845731616020203}}, "car": {"car:2": {"box": [474, 177, 54, 28], "box_score": 0.9765124320983887}, "car:7": {"box": [686, 172, 46, 24], "box_score": 0.6732808351516724}, "car:1": {"box": [3, 195, 278, 147], "box_score": 0.980333149433136}, "car:4": {"box": [258, 187, 130, 88], "box_score": 0.9336426854133606}, "car:8": {"box": [242, 177, 55, 24], "box_score": 0.6145150065422058}, "car:5": {"box": [892, 191, 381, 179], "box_score": 0.9221729636192322}, "car:3": {"box": [763, 181, 198, 119], "box_score": 0.9735662341117859}, "car:6": {"box": [582, 174, 44, 21], "box_score": 0.6868625283241272}}}, "0000000017.png": {"bicycle": {"bicycle:1": {"box": [331, 206, 47, 43], "box_score": 0.6367072463035583}}, "car": {"car:2": {"box": [419, 188, 65, 43], "box_score": 0.94988614320755}, "car:7": {"box": [488, 179, 34, 31], "box_score": 0.702414333820343}, "car:1": {"box": [195, 199, 58, 33], "box_score": 0.9672338962554932}, "car:4": {"box": [36, 207, 71, 32], "box_score": 0.8526629209518433}, "car:5": {"box": [0, 256, 61, 119], "box_score": 0.840353786945343}, "car:3": {"box": [117, 200, 84, 34], "box_score": 0.8618670701980591}, "car:6": {"box": [465, 187, 37, 33], "box_score": 0.7763758301734924}}}, "0000000340.png": {"truck": {"truck:1": {"box": [605, 147, 59, 44], "box_score": 0.7107154726982117}}, "car": {"car:2": {"box": [0, 201, 198, 175], "box_score": 0.9802486300468445}, "car:7": {"box": [682, 170, 50, 21], "box_score": 0.7042397856712341}, "car:1": {"box": [780, 184, 264, 155], "box_score": 0.9814581274986267}, "car:4": {"box": [470, 176, 57, 29], "box_score": 0.8962748050689697}, "car:5": {"box": [374, 178, 39, 23], "box_score": 0.8064910769462585}, "car:3": {"box": [180, 181, 166, 110], "box_score": 0.9602937698364258}, "car:6": {"box": [952, 220, 292, 152], "box_score": 0.7464642524719238}}}, "0000000252.png": {"car": {"car:2": {"box": [732, 189, 95, 69], "box_score": 0.9777196645736694}, "car:1": {"box": [780, 194, 185, 108], "box_score": 0.997448205947876}, "car:4": {"box": [1033, 179, 208, 64], "box_score": 0.9545642733573914}, "car:5": {"box": [692, 181, 34, 28], "box_score": 0.7481004595756531}, "car:3": {"box": [470, 189, 75, 48], "box_score": 0.9651477932929993}, "car:6": {"box": [548, 189, 31, 28], "box_score": 0.7358536720275879}}}, "0000000117.png": {"car": {"car:2": {"box": [827, 179, 372, 187], "box_score": 0.9817798733711243}, "car:7": {"box": [660, 179, 42, 35], "box_score": 0.8079835176467896}, "car:1": {"box": [2, 212, 225, 159], "box_score": 0.9891706109046936}, "car:9": {"box": [528, 175, 39, 24], "box_score": 0.7257612943649292}, "car:4": {"box": [390, 187, 84, 52], "box_score": 0.9257237911224365}, "car:8": {"box": [482, 179, 48, 31], "box_score": 0.7908297777175903}, "car:5": {"box": [712, 182, 99, 70], "box_score": 0.8805702328681946}, "car:3": {"box": [217, 195, 151, 91], "box_score": 0.9518755674362183}, "car:6": {"box": [684, 180, 59, 51], "box_score": 0.8557705879211426}}}, "0000000382.png": {"car": {"car:2": {"box": [357, 178, 127, 57], "box_score": 0.9617976546287537}, "car:1": {"box": [657, 168, 165, 65], "box_score": 0.9947360157966614}, "car:3": {"box": [583, 176, 86, 40], "box_score": 0.9589580297470093}}}, "0000000103.png": {"car": {"car:2": {"box": [1056, 141, 180, 95], "box_score": 0.9669291377067566}, "car:7": {"box": [490, 183, 38, 31], "box_score": 0.8212094902992249}, "car:1": {"box": [10, 211, 260, 144], "box_score": 0.9708539247512817}, "car:9": {"box": [999, 141, 160, 84], "box_score": 0.8056172728538513}, "car:5": {"box": [263, 200, 132, 78], "box_score": 0.8936182260513306}, "car:3": {"box": [922, 152, 121, 69], "box_score": 0.9382278323173523}, "car:6": {"box": [709, 181, 86, 62], "box_score": 0.8928366899490356}, "car:12": {"box": [448, 186, 46, 40], "box_score": 0.6364218592643738}, "car:10": {"box": [685, 176, 54, 55], "box_score": 0.7964126467704773}, "car:11": {"box": [660, 178, 36, 35], "box_score": 0.7326381206512451}, "car:4": {"box": [390, 189, 77, 51], "box_score": 0.9232067465782166}, "car:8": {"box": [872, 154, 112, 61], "box_score": 0.8161279559135437}}}, "0000000363.png": {"car": {"car:2": {"box": [628, 177, 88, 30], "box_score": 0.9669601917266846}, "car:5": {"box": [488, 178, 90, 33], "box_score": 0.8887062668800354}, "car:1": {"box": [335, 189, 94, 71], "box_score": 0.99136883020401}, "car:3": {"box": [186, 181, 126, 49], "box_score": 0.9532698392868042}, "car:4": {"box": [0, 215, 261, 157], "box_score": 0.9143284559249878}}, "person": {"person:1": {"box": [823, 172, 28, 81], "box_score": 0.8580648303031921}}}, "0000000009.png": {"car": {"car:2": {"box": [940, 208, 304, 165], "box_score": 0.9870916604995728}, "car:1": {"box": [768, 178, 183, 131], "box_score": 0.9950998425483704}, "car:4": {"box": [220, 198, 61, 33], "box_score": 0.8654342293739319}, "car:5": {"box": [467, 187, 44, 32], "box_score": 0.7127817869186401}, "car:3": {"box": [208, 204, 162, 88], "box_score": 0.9582068920135498}, "car:6": {"box": [508, 180, 34, 26], "box_score": 0.6300076842308044}}}, "0000000319.png": {"car": {"car:2": {"box": [237, 193, 161, 108], "box_score": 0.9744757413864136}, "car:7": {"box": [698, 180, 42, 47], "box_score": 0.7894427180290222}, "car:1": {"box": [0, 209, 262, 162], "box_score": 0.9839878678321838}, "car:4": {"box": [726, 181, 78, 66], "box_score": 0.9278433918952942}, "car:5": {"box": [837, 197, 409, 171], "box_score": 0.9133800864219666}, "car:3": {"box": [460, 181, 75, 39], "box_score": 0.9724475741386414}, "car:6": {"box": [759, 189, 154, 96], "box_score": 0.905289888381958}}}, "0000000177.png": {"bicycle": {"bicycle:1": {"box": [806, 189, 59, 38], "box_score": 0.6457269787788391}}, "car": {"car:2": {"box": [1102, 161, 140, 69], "box_score": 0.9847381114959717}, "car:1": {"box": [915, 171, 174, 65], "box_score": 0.996421217918396}, "car:3": {"box": [127, 194, 91, 41], "box_score": 0.7121360898017883}}}, "0000000433.png": {"traffic light": {"traffic light:2": {"box": [348, 9, 41, 103], "box_score": 0.6684434413909912}, "traffic light:1": {"box": [1047, 28, 33, 79], "box_score": 0.7943635582923889}}}, "0000000246.png": {"car": {"car:2": {"box": [724, 187, 104, 71], "box_score": 0.938686728477478}, "car:1": {"box": [1073, 163, 168, 77], "box_score": 0.9894769191741943}, "car:4": {"box": [702, 180, 59, 55], "box_score": 0.8526023626327515}, "car:5": {"box": [926, 174, 152, 49], "box_score": 0.7247094511985779}, "car:3": {"box": [485, 181, 67, 40], "box_score": 0.9152758121490479}, "car:6": {"box": [542, 181, 30, 25], "box_score": 0.6952823400497437}}}, "0000000367.png": {"car": {"car:2": {"box": [631, 175, 96, 32], "box_score": 0.9786616563796997}, "car:1": {"box": [237, 185, 157, 119], "box_score": 0.9807696342468262}, "car:3": {"box": [253, 180, 102, 47], "box_score": 0.8398230671882629}, "car:4": {"box": [476, 177, 103, 35], "box_score": 0.6712839007377625}}, "person": {"person:1": {"box": [895, 162, 45, 110], "box_score": 0.931779146194458}}}, "0000000153.png": {"car": {"car:2": {"box": [814, 198, 407, 169], "box_score": 0.9586832523345947}, "car:7": {"box": [222, 186, 46, 25], "box_score": 0.6791126132011414}, "car:1": {"box": [1, 223, 118, 148], "box_score": 0.9876963496208191}, "car:4": {"box": [247, 178, 127, 51], "box_score": 0.8849632143974304}, "car:5": {"box": [77, 204, 82, 34], "box_score": 0.7367551922798157}, "car:3": {"box": [805, 171, 75, 34], "box_score": 0.9345800280570984}, "car:6": {"box": [106, 200, 77, 31], "box_score": 0.7100428342819214}}, "person": {"person:2": {"box": [926, 143, 41, 63], "box_score": 0.776982843875885}, "person:1": {"box": [876, 144, 43, 86], "box_score": 0.8890957832336426}}}, "0000000057.png": {"car": {"car:2": {"box": [205, 203, 144, 72], "box_score": 0.9678106307983398}, "car:5": {"box": [631, 178, 48, 31], "box_score": 0.843121349811554}, "car:1": {"box": [372, 190, 117, 74], "box_score": 0.9744958281517029}, "car:3": {"box": [462, 187, 58, 45], "box_score": 0.9339388608932495}, "car:4": {"box": [759, 163, 102, 41], "box_score": 0.8803681135177612}}}, "0000000156.png": {"car": {"car:2": {"box": [214, 176, 138, 57], "box_score": 0.9739691019058228}, "car:1": {"box": [913, 211, 330, 161], "box_score": 0.9777838587760925}, "car:3": {"box": [822, 168, 97, 37], "box_score": 0.9208269119262695}, "car:4": {"box": [4, 204, 132, 47], "box_score": 0.6413641571998596}}, "person": {"person:2": {"box": [997, 136, 51, 118], "box_score": 0.7733449339866638}, "person:1": {"box": [933, 137, 58, 140], "box_score": 0.9502657651901245}}}, "0000000421.png": {"car": {"car:1": {"box": [2, 210, 268, 163], "box_score": 0.9847821593284607}}, "traffic light": {"traffic light:2": {"box": [348, 10, 40, 102], "box_score": 0.6407935619354248}, "traffic light:3": {"box": [403, 49, 34, 59], "box_score": 0.6336992979049683}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.8220618963241577}}}, "0000000056.png": {"car": {"car:2": {"box": [238, 201, 126, 62], "box_score": 0.9484522938728333}, "car:5": {"box": [630, 179, 41, 30], "box_score": 0.8444415330886841}, "car:1": {"box": [390, 189, 107, 67], "box_score": 0.9760531783103943}, "car:3": {"box": [475, 186, 49, 43], "box_score": 0.9229504466056824}, "car:4": {"box": [744, 163, 98, 41], "box_score": 0.8646823763847351}}}, "0000000049.png": {"car": {"car:2": {"box": [0, 194, 157, 173], "box_score": 0.9786609411239624}, "car:7": {"box": [881, 150, 58, 28], "box_score": 0.7413184642791748}, "car:1": {"box": [374, 192, 68, 44], "box_score": 0.98753821849823}, "car:4": {"box": [706, 166, 92, 34], "box_score": 0.9579532742500305}, "car:8": {"box": [1130, 154, 113, 40], "box_score": 0.6494491100311279}, "car:5": {"box": [471, 185, 65, 41], "box_score": 0.9387693405151367}, "car:3": {"box": [152, 191, 188, 99], "box_score": 0.9759678840637207}, "car:6": {"box": [628, 178, 34, 25], "box_score": 0.8338125944137573}}}, "0000000239.png": {"car": {"car:2": {"box": [909, 167, 146, 56], "box_score": 0.9697999954223633}, "car:7": {"box": [647, 182, 48, 44], "box_score": 0.728493332862854}, "car:1": {"box": [1, 216, 239, 158], "box_score": 0.9818640947341919}, "car:4": {"box": [832, 210, 424, 161], "box_score": 0.9196445941925049}, "car:5": {"box": [819, 176, 104, 37], "box_score": 0.7949255704879761}, "car:3": {"box": [657, 185, 67, 51], "box_score": 0.9439502954483032}, "car:6": {"box": [462, 183, 52, 35], "box_score": 0.7763059139251709}}}, "0000000408.png": {"car": {"car:2": {"box": [285, 185, 167, 78], "box_score": 0.734846830368042}, "car:1": {"box": [0, 226, 99, 146], "box_score": 0.9793145656585693}}, "traffic light": {"traffic light:2": {"box": [349, 10, 39, 103], "box_score": 0.6888799071311951}, "traffic light:3": {"box": [404, 49, 33, 59], "box_score": 0.6535003781318665}, "traffic light:1": {"box": [1046, 28, 34, 79], "box_score": 0.8320263624191284}}}, "0000000163.png": {"car": {"car:2": {"box": [123, 183, 169, 67], "box_score": 0.901814877986908}, "car:1": {"box": [0, 209, 43, 45], "box_score": 0.9628339409828186}, "car:4": {"box": [1130, 161, 44, 64], "box_score": 0.747589111328125}, "car:5": {"box": [1005, 164, 138, 48], "box_score": 0.7059053778648376}, "car:3": {"box": [851, 166, 104, 49], "box_score": 0.8758783936500549}, "car:6": {"box": [286, 187, 51, 31], "box_score": 0.6893747448921204}}, "person": {"person:1": {"box": [1167, 117, 79, 241], "box_score": 0.9594149589538574}}}, "0000000045.png": {"car": {"car:2": {"box": [693, 163, 89, 32], "box_score": 0.959678590297699}, "car:7": {"box": [1066, 158, 105, 29], "box_score": 0.7496908903121948}, "car:1": {"box": [64, 180, 251, 137], "box_score": 0.9643741846084595}, "car:4": {"box": [298, 184, 105, 74], "box_score": 0.9156925082206726}, "car:5": {"box": [509, 180, 42, 33], "box_score": 0.8311142921447754}, "car:3": {"box": [418, 185, 53, 37], "box_score": 0.9351838231086731}, "car:6": {"box": [627, 175, 32, 24], "box_score": 0.7526190876960754}}}, "0000000022.png": {"car": {"car:2": {"box": [432, 190, 51, 40], "box_score": 0.901215136051178}, "car:5": {"box": [470, 181, 41, 36], "box_score": 0.7362368702888489}, "car:1": {"box": [373, 193, 75, 51], "box_score": 0.9770895838737488}, "car:3": {"box": [24, 206, 91, 39], "box_score": 0.8134620785713196}, "car:4": {"box": [1055, 134, 107, 47], "box_score": 0.7960762977600098}}}, "0000000115.png": {"car": {"car:2": {"box": [778, 184, 241, 139], "box_score": 0.9958042502403259}, "car:7": {"box": [489, 180, 41, 29], "box_score": 0.8809367418289185}, "car:1": {"box": [1, 199, 300, 157], "box_score": 0.9970802664756775}, "car:9": {"box": [540, 175, 40, 23], "box_score": 0.6351677179336548}, "car:4": {"box": [288, 192, 115, 78], "box_score": 0.9609196782112122}, "car:8": {"box": [657, 179, 38, 35], "box_score": 0.7276066541671753}, "car:5": {"box": [702, 184, 78, 58], "box_score": 0.9460240602493286}, "car:3": {"box": [940, 219, 300, 153], "box_score": 0.9740162491798401}, "car:6": {"box": [413, 188, 71, 49], "box_score": 0.937217652797699}}}, "0000000251.png": {"car": {"car:2": {"box": [477, 187, 77, 44], "box_score": 0.9824883341789246}, "car:7": {"box": [690, 179, 33, 28], "box_score": 0.7023592591285706}, "car:1": {"box": [772, 193, 164, 98], "box_score": 0.9950124621391296}, "car:4": {"box": [1028, 175, 203, 59], "box_score": 0.8643734455108643}, "car:5": {"box": [1170, 182, 74, 47], "box_score": 0.7704580426216125}, "car:3": {"box": [728, 187, 85, 64], "box_score": 0.9816864728927612}, "car:6": {"box": [548, 187, 30, 28], "box_score": 0.7700009942054749}}}, "0000000112.png": {"car": {"car:2": {"box": [165, 194, 209, 104], "box_score": 0.98479163646698}, "car:7": {"box": [357, 188, 81, 68], "box_score": 0.9204866290092468}, "car:1": {"box": [2, 229, 95, 148], "box_score": 0.9932277798652649}, "car:9": {"box": [685, 179, 67, 54], "box_score": 0.852620542049408}, "car:5": {"box": [743, 179, 141, 96], "box_score": 0.922497034072876}, "car:3": {"box": [828, 187, 377, 180], "box_score": 0.9603310823440552}, "car:6": {"box": [1124, 164, 120, 130], "box_score": 0.9216004014015198}, "car:12": {"box": [651, 179, 35, 30], "box_score": 0.7451121211051941}, "car:10": {"box": [499, 180, 39, 28], "box_score": 0.8016155958175659}, "car:11": {"box": [547, 173, 48, 23], "box_score": 0.7903664708137512}, "car:4": {"box": [441, 186, 60, 41], "box_score": 0.9229307174682617}, "car:8": {"box": [7, 187, 98, 53], "box_score": 0.9109017252922058}}}, "0000000243.png": {"car": {"car:2": {"box": [1018, 281, 226, 96], "box_score": 0.9388323426246643}, "car:7": {"box": [879, 179, 136, 45], "box_score": 0.7237521409988403}, "car:1": {"box": [990, 166, 207, 68], "box_score": 0.9753198623657227}, "car:4": {"box": [0, 270, 109, 102], "box_score": 0.8840529918670654}, "car:8": {"box": [661, 177, 29, 24], "box_score": 0.6611402630805969}, "car:5": {"box": [483, 183, 56, 39], "box_score": 0.8189510107040405}, "car:3": {"box": [700, 188, 88, 62], "box_score": 0.9248955249786377}, "car:6": {"box": [680, 185, 51, 43], "box_score": 0.811763346195221}}}, "0000000304.png": {"car": {"car:2": {"box": [783, 186, 163, 101], "box_score": 0.9744490385055542}, "car:7": {"box": [696, 179, 33, 42], "box_score": 0.6697477102279663}, "car:1": {"box": [346, 188, 119, 75], "box_score": 0.9974944591522217}, "car:4": {"box": [736, 184, 84, 66], "box_score": 0.9591119289398193}, "car:8": {"box": [536, 181, 34, 24], "box_score": 0.651559054851532}, "car:5": {"box": [929, 193, 343, 175], "box_score": 0.9485007524490356}, "car:3": {"box": [445, 185, 70, 49], "box_score": 0.9623985886573792}, "car:6": {"box": [712, 181, 44, 49], "box_score": 0.7690494060516357}}}, "0000000240.png": {"car": {"car:2": {"box": [927, 168, 161, 58], "box_score": 0.9820826053619385}, "car:7": {"box": [832, 177, 110, 33], "box_score": 0.755163848400116}, "car:1": {"box": [2, 224, 221, 153], "box_score": 0.99383544921875}, "car:4": {"box": [469, 184, 55, 34], "box_score": 0.9046653509140015}, "car:5": {"box": [670, 187, 74, 52], "box_score": 0.9016872048377991}, "car:3": {"box": [869, 214, 389, 159], "box_score": 0.972842276096344}, "car:6": {"box": [657, 184, 44, 43], "box_score": 0.793393611907959}}}, "0000000063.png": {"car": {"car:2": {"box": [57, 198, 345, 170], "box_score": 0.9594265818595886}, "car:7": {"box": [649, 178, 48, 42], "box_score": 0.7397027611732483}, "car:1": {"box": [368, 193, 107, 79], "box_score": 0.9655831456184387}, "car:4": {"box": [735, 164, 75, 43], "box_score": 0.8843060731887817}, "car:8": {"box": [943, 153, 57, 30], "box_score": 0.6431083083152771}, "car:5": {"box": [793, 160, 111, 57], "box_score": 0.7890979051589966}, "car:3": {"box": [2, 218, 165, 145], "box_score": 0.9052982926368713}, "car:6": {"box": [1041, 140, 78, 39], "box_score": 0.74612957239151}}}, "0000000092.png": {"car": {"car:2": {"box": [399, 196, 57, 52], "box_score": 0.9661416411399841}, "car:7": {"box": [1155, 140, 87, 41], "box_score": 0.8508511781692505}, "car:1": {"box": [830, 158, 127, 49], "box_score": 0.9813280701637268}, "car:9": {"box": [803, 161, 77, 45], "box_score": 0.6011900305747986}, "car:4": {"box": [323, 199, 91, 68], "box_score": 0.9199947714805603}, "car:8": {"box": [477, 188, 42, 32], "box_score": 0.77410489320755}, "car:5": {"box": [441, 192, 47, 39], "box_score": 0.9086779952049255}, "car:3": {"box": [126, 201, 214, 119], "box_score": 0.9644469618797302}, "car:6": {"box": [1097, 142, 71, 39], "box_score": 0.8532911539077759}}}, "0000000168.png": {"car": {"car:2": {"box": [1029, 160, 180, 57], "box_score": 0.9752677083015442}, "car:1": {"box": [871, 172, 137, 52], "box_score": 0.9910383224487305}, "car:3": {"box": [31, 190, 202, 75], "box_score": 0.8444945812225342}, "car:4": {"box": [229, 191, 63, 35], "box_score": 0.8086897134780884}}}, "0000000400.png": {"car": {"car:2": {"box": [425, 183, 132, 55], "box_score": 0.9047498106956482}, "car:1": {"box": [21, 196, 253, 127], "box_score": 0.9948076605796814}}, "traffic light": {"traffic light:2": {"box": [357, 15, 36, 93], "box_score": 0.7760236263275146}, "traffic light:3": {"box": [402, 45, 40, 61], "box_score": 0.6249387860298157}, "traffic light:1": {"box": [1042, 28, 35, 76], "box_score": 0.9299020171165466}}}, "0000000248.png": {"car": {"car:2": {"box": [482, 179, 65, 42], "box_score": 0.9622780680656433}, "car:1": {"box": [741, 185, 123, 80], "box_score": 0.9675722718238831}, "car:4": {"box": [712, 176, 67, 59], "box_score": 0.8785272836685181}, "car:5": {"box": [1097, 166, 145, 71], "box_score": 0.8345766067504883}, "car:3": {"box": [959, 165, 183, 54], "box_score": 0.9309424757957458}, "car:6": {"box": [548, 179, 29, 27], "box_score": 0.7139402627944946}}}, "0000000275.png": {"car": {"car:2": {"box": [0, 183, 223, 187], "box_score": 0.9683862328529358}, "car:1": {"box": [203, 182, 192, 140], "box_score": 0.982672929763794}, "car:4": {"box": [380, 191, 82, 77], "box_score": 0.9484028220176697}, "car:5": {"box": [717, 171, 71, 58], "box_score": 0.9429880976676941}, "car:3": {"box": [437, 183, 66, 60], "box_score": 0.9577857255935669}, "car:6": {"box": [561, 175, 41, 26], "box_score": 0.8701672554016113}}}, "0000000175.png": {"bicycle": {"bicycle:1": {"box": [798, 187, 58, 35], "box_score": 0.7760859727859497}}, "car": {"car:2": {"box": [1079, 156, 162, 67], "box_score": 0.98969566822052}, "car:1": {"box": [902, 169, 164, 63], "box_score": 0.9972468614578247}, "car:3": {"box": [142, 192, 93, 41], "box_score": 0.8815815448760986}}}, "0000000296.png": {"car": {"car:2": {"box": [832, 204, 234, 133], "box_score": 0.9552578330039978}, "car:7": {"box": [716, 185, 33, 42], "box_score": 0.6588466167449951}, "car:1": {"box": [454, 187, 74, 47], "box_score": 0.9730586409568787}, "car:4": {"box": [730, 184, 56, 57], "box_score": 0.8557841181755066}, "car:8": {"box": [693, 179, 27, 36], "box_score": 0.6456440687179565}, "car:5": {"box": [511, 186, 33, 33], "box_score": 0.840445876121521}, "car:3": {"box": [763, 187, 110, 81], "box_score": 0.9259355068206787}, "car:6": {"box": [562, 181, 34, 21], "box_score": 0.7161899209022522}}}, "0000000345.png": {"truck": {"truck:1": {"box": [515, 144, 90, 61], "box_score": 0.86540687084198}}, "car": {"car:2": {"box": [2, 201, 190, 170], "box_score": 0.989000141620636}, "car:5": {"box": [120, 184, 76, 51], "box_score": 0.7138729095458984}, "car:1": {"box": [461, 182, 53, 34], "box_score": 0.9944568872451782}, "car:3": {"box": [341, 184, 77, 29], "box_score": 0.9864802956581116}, "car:4": {"box": [881, 204, 364, 167], "box_score": 0.9654796719551086}}}, "0000000356.png": {"truck": {"truck:1": {"box": [337, 152, 101, 51], "box_score": 0.8465094566345215}}, "car": {"car:2": {"box": [626, 175, 75, 27], "box_score": 0.9291446805000305}, "car:1": {"box": [343, 184, 103, 78], "box_score": 0.9400557279586792}, "car:3": {"box": [501, 174, 79, 31], "box_score": 0.887010395526886}, "car:4": {"box": [173, 185, 46, 36], "box_score": 0.8062588572502136}}, "person": {"person:1": {"box": [737, 177, 24, 53], "box_score": 0.6968187093734741}}}, "0000000165.png": {"car": {"car:2": {"box": [91, 186, 179, 70], "box_score": 0.9294195175170898}, "car:5": {"box": [268, 193, 48, 27], "box_score": 0.6149722933769226}, "car:1": {"box": [861, 172, 126, 49], "box_score": 0.9581566452980042}, "car:3": {"box": [1169, 166, 75, 71], "box_score": 0.9127873778343201}, "car:4": {"box": [1086, 162, 90, 46], "box_score": 0.8905012607574463}}}, "0000000438.png": {"traffic light": {"traffic light:2": {"box": [399, 46, 38, 64], "box_score": 0.6643833518028259}, "traffic light:3": {"box": [348, 9, 40, 102], "box_score": 0.6600537896156311}, "traffic light:1": {"box": [1047, 27, 32, 79], "box_score": 0.8029645085334778}}}, "0000000430.png": {"traffic light": {"traffic light:2": {"box": [348, 13, 41, 99], "box_score": 0.7234288454055786}, "traffic light:3": {"box": [404, 49, 33, 59], "box_score": 0.6480507850646973}, "traffic light:1": {"box": [1047, 29, 32, 77], "box_score": 0.7467203140258789}}}, "0000000407.png": {"car": {"car:1": {"box": [0, 221, 136, 142], "box_score": 0.9927151799201965}}, "traffic light": {"traffic light:2": {"box": [349, 10, 39, 103], "box_score": 0.7169485092163086}, "traffic light:3": {"box": [402, 49, 35, 59], "box_score": 0.6505199074745178}, "traffic light:1": {"box": [1047, 28, 33, 79], "box_score": 0.807824969291687}}}, "0000000218.png": {"car": {"car:2": {"box": [394, 169, 241, 130], "box_score": 0.9225519299507141}, "car:7": {"box": [50, 187, 34, 24], "box_score": 0.7342497706413269}, "car:1": {"box": [250, 196, 126, 68], "box_score": 0.9727914333343506}, "car:4": {"box": [328, 180, 85, 40], "box_score": 0.9132421612739563}, "car:8": {"box": [94, 193, 44, 33], "box_score": 0.600936233997345}, "car:5": {"box": [632, 179, 71, 43], "box_score": 0.8595662117004395}, "car:3": {"box": [712, 184, 91, 49], "box_score": 0.9190890789031982}, "car:6": {"box": [113, 192, 69, 40], "box_score": 0.7655596733093262}}}, "0000000404.png": {"car": {"car:2": {"box": [403, 184, 107, 62], "box_score": 0.9150803089141846}, "car:1": {"box": [0, 206, 207, 163], "box_score": 0.9910905361175537}}, "traffic light": {"traffic light:2": {"box": [351, 14, 38, 93], "box_score": 0.7639333605766296}, "traffic light:3": {"box": [408, 47, 29, 55], "box_score": 0.6602334380149841}, "traffic light:1": {"box": [1046, 23, 35, 80], "box_score": 0.873327910900116}}}, "0000000336.png": {"car": {"car:2": {"box": [479, 176, 53, 25], "box_score": 0.9849779605865479}, "car:1": {"box": [135, 190, 202, 112], "box_score": 0.9865603446960449}, "car:4": {"box": [317, 184, 99, 76], "box_score": 0.9430399537086487}, "car:5": {"box": [844, 193, 402, 176], "box_score": 0.9419933557510376}, "car:3": {"box": [745, 182, 150, 97], "box_score": 0.9840828776359558}, "car:6": {"box": [588, 173, 49, 20], "box_score": 0.6917415261268616}}}, "0000000359.png": {"car": {"car:2": {"box": [623, 176, 80, 29], "box_score": 0.9716705679893494}, "car:5": {"box": [495, 178, 82, 31], "box_score": 0.9290412664413452}, "car:1": {"box": [231, 190, 181, 118], "box_score": 0.9830175638198853}, "car:3": {"box": [131, 183, 117, 42], "box_score": 0.9654316902160645}, "car:4": {"box": [360, 186, 77, 52], "box_score": 0.9334385991096497}}, "person": {"person:1": {"box": [765, 173, 27, 69], "box_score": 0.9560463428497314}}}, "0000000428.png": {"traffic light": {"traffic light:2": {"box": [348, 10, 40, 100], "box_score": 0.7042035460472107}, "traffic light:3": {"box": [401, 47, 36, 62], "box_score": 0.6415627598762512}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.8317627906799316}}}, "0000000042.png": {"car": {"car:2": {"box": [218, 176, 160, 105], "box_score": 0.9579134583473206}, "car:7": {"box": [362, 180, 74, 64], "box_score": 0.8597886562347412}, "car:1": {"box": [0, 227, 154, 140], "box_score": 0.9774398803710938}, "car:9": {"box": [629, 172, 31, 23], "box_score": 0.7461814880371094}, "car:4": {"box": [524, 178, 39, 28], "box_score": 0.925714910030365}, "car:8": {"box": [495, 179, 31, 27], "box_score": 0.8327491879463196}, "car:5": {"box": [690, 162, 83, 28], "box_score": 0.912418007850647}, "car:3": {"box": [859, 178, 404, 188], "box_score": 0.952353298664093}, "car:6": {"box": [433, 182, 56, 41], "box_score": 0.8624979853630066}}}, "0000000230.png": {"car": {"car:2": {"box": [594, 188, 150, 93], "box_score": 0.9853427410125732}, "car:7": {"box": [816, 136, 431, 234], "box_score": 0.7078906893730164}, "car:1": {"box": [0, 228, 137, 145], "box_score": 0.9913693070411682}, "car:4": {"box": [309, 187, 47, 31], "box_score": 0.9234012365341187}, "car:5": {"box": [681, 169, 97, 39], "box_score": 0.9058291912078857}, "car:3": {"box": [71, 208, 149, 103], "box_score": 0.9517291188240051}, "car:6": {"box": [492, 184, 57, 40], "box_score": 0.852076530456543}}}, "0000000195.png": {"bicycle": {"bicycle:1": {"box": [991, 198, 90, 56], "box_score": 0.955549418926239}}, "car": {"car:2": {"box": [190, 185, 89, 47], "box_score": 0.9592052698135376}, "car:1": {"box": [2, 174, 128, 110], "box_score": 0.9697085022926331}, "car:3": {"box": [1179, 213, 65, 64], "box_score": 0.9217953681945801}, "car:4": {"box": [120, 186, 57, 37], "box_score": 0.7685627341270447}}}, "0000000380.png": {"car": {"car:2": {"box": [383, 177, 118, 56], "box_score": 0.9733121991157532}, "car:1": {"box": [585, 170, 164, 64], "box_score": 0.9936378598213196}}, "traffic light": {"traffic light:1": {"box": [458, 62, 26, 62], "box_score": 0.8279416561126709}}}, "0000000211.png": {"car": {"car:2": {"box": [164, 173, 241, 117], "box_score": 0.9313123822212219}, "car:1": {"box": [1, 205, 133, 71], "box_score": 0.9600715637207031}, "car:3": {"box": [477, 183, 78, 48], "box_score": 0.9149706363677979}, "car:4": {"box": [406, 183, 61, 39], "box_score": 0.7719331383705139}}}, "0000000166.png": {"car": {"car:2": {"box": [1016, 164, 82, 52], "box_score": 0.915102481842041}, "car:5": {"box": [254, 192, 55, 32], "box_score": 0.8291995525360107}, "car:1": {"box": [864, 172, 130, 51], "box_score": 0.992155909538269}, "car:3": {"box": [1188, 164, 55, 77], "box_score": 0.9088473916053772}, "car:4": {"box": [70, 188, 188, 72], "box_score": 0.8460274338722229}}}, "0000000154.png": {"car": {"car:2": {"box": [815, 169, 80, 36], "box_score": 0.9531906843185425}, "car:7": {"box": [215, 186, 44, 24], "box_score": 0.6382117867469788}, "car:1": {"box": [1, 236, 68, 138], "box_score": 0.9749516844749451}, "car:4": {"box": [237, 177, 129, 53], "box_score": 0.9106975197792053}, "car:5": {"box": [87, 200, 66, 35], "box_score": 0.7672905921936035}, "car:3": {"box": [836, 196, 418, 172], "box_score": 0.9480616450309753}, "car:6": {"box": [46, 207, 86, 40], "box_score": 0.7318457961082458}}, "person": {"person:1": {"box": [895, 142, 43, 95], "box_score": 0.8936631083488464}}}, "0000000216.png": {"car": {"car:2": {"box": [640, 179, 85, 51], "box_score": 0.9543823003768921}, "car:7": {"box": [564, 180, 62, 42], "box_score": 0.7886683940887451}, "car:1": {"box": [178, 198, 132, 67], "box_score": 0.9749550819396973}, "car:4": {"box": [26, 196, 77, 40], "box_score": 0.8874981999397278}, "car:5": {"box": [253, 182, 86, 41], "box_score": 0.8133381009101868}, "car:3": {"box": [327, 170, 235, 125], "box_score": 0.8913628458976746}, "car:6": {"box": [0, 195, 54, 38], "box_score": 0.8015168309211731}}}, "0000000052.png": {"car": {"car:2": {"box": [330, 194, 87, 55], "box_score": 0.9628440141677856}, "car:1": {"box": [0, 200, 255, 141], "box_score": 0.9849104285240173}, "car:4": {"box": [720, 166, 95, 35], "box_score": 0.9513271450996399}, "car:5": {"box": [506, 183, 35, 34], "box_score": 0.8649643659591675}, "car:3": {"box": [447, 185, 75, 50], "box_score": 0.9586837291717529}, "car:6": {"box": [627, 178, 39, 28], "box_score": 0.7058629393577576}}}, "0000000214.png": {"car": {"car:2": {"box": [571, 182, 82, 49], "box_score": 0.9488794803619385}, "car:5": {"box": [174, 187, 93, 38], "box_score": 0.6052148342132568}, "car:1": {"box": [99, 201, 140, 68], "box_score": 0.9689548015594482}, "car:3": {"box": [262, 172, 236, 121], "box_score": 0.9162437915802002}, "car:4": {"box": [496, 182, 69, 42], "box_score": 0.8847327828407288}}}, "0000000385.png": {"car": {"car:2": {"box": [559, 177, 125, 41], "box_score": 0.9684800505638123}, "car:1": {"box": [768, 163, 179, 69], "box_score": 0.9982203841209412}, "car:3": {"box": [317, 180, 156, 63], "box_score": 0.9581671953201294}}, "traffic light": {"traffic light:1": {"box": [422, 42, 31, 76], "box_score": 0.7784990072250366}}}, "0000000403.png": {"car": {"car:2": {"box": [408, 182, 113, 59], "box_score": 0.8623533844947815}, "car:1": {"box": [0, 201, 228, 153], "box_score": 0.9869552254676819}}, "traffic light": {"traffic light:2": {"box": [351, 14, 38, 98], "box_score": 0.7597988843917847}, "traffic light:3": {"box": [409, 48, 28, 54], "box_score": 0.7300234436988831}, "traffic light:1": {"box": [1046, 24, 34, 79], "box_score": 0.9200390577316284}}}, "0000000136.png": {"car": {"car:2": {"box": [745, 180, 175, 112], "box_score": 0.9764651656150818}, "car:1": {"box": [302, 191, 121, 77], "box_score": 0.9905720353126526}, "car:4": {"box": [698, 181, 90, 66], "box_score": 0.8177272081375122}, "car:5": {"box": [1024, 261, 215, 111], "box_score": 0.7367819547653198}, "car:3": {"box": [403, 190, 57, 53], "box_score": 0.9049229025840759}, "car:6": {"box": [1, 192, 103, 61], "box_score": 0.6959551572799683}}}, "0000000167.png": {"car": {"car:2": {"box": [1024, 162, 150, 57], "box_score": 0.9487119913101196}, "car:5": {"box": [2, 204, 57, 33], "box_score": 0.7008553147315979}, "car:1": {"box": [864, 172, 137, 52], "box_score": 0.9931859970092773}, "car:3": {"box": [52, 187, 190, 73], "box_score": 0.906098484992981}, "car:4": {"box": [244, 194, 58, 32], "box_score": 0.8212275505065918}}}, "0000000313.png": {"car": {"car:2": {"box": [264, 194, 151, 93], "box_score": 0.9928383231163025}, "car:10": {"box": [590, 174, 43, 16], "box_score": 0.7625401616096497}, "car:1": {"box": [837, 189, 320, 171], "box_score": 0.9947000741958618}, "car:9": {"box": [710, 179, 47, 51], "box_score": 0.7698992490768433}, "car:4": {"box": [747, 185, 143, 89], "box_score": 0.9676896333694458}, "car:8": {"box": [1104, 175, 124, 50], "box_score": 0.8568838834762573}, "car:7": {"box": [720, 180, 65, 61], "box_score": 0.8675269484519958}, "car:5": {"box": [496, 179, 52, 35], "box_score": 0.9406078457832336}, "car:3": {"box": [1, 208, 288, 165], "box_score": 0.98583984375}, "car:6": {"box": [393, 191, 79, 62], "box_score": 0.9278247356414795}}}, "0000000101.png": {"car": {"car:2": {"box": [411, 189, 67, 46], "box_score": 0.961493730545044}, "car:7": {"box": [945, 143, 130, 76], "box_score": 0.7503964304924011}, "car:1": {"box": [1, 226, 179, 143], "box_score": 0.9768210649490356}, "car:9": {"box": [676, 175, 48, 46], "box_score": 0.6905889511108398}, "car:5": {"box": [969, 138, 260, 85], "box_score": 0.9207412004470825}, "car:3": {"box": [159, 204, 167, 112], "box_score": 0.9473445415496826}, "car:6": {"box": [694, 177, 74, 54], "box_score": 0.8304820656776428}, "car:12": {"box": [496, 184, 35, 29], "box_score": 0.6452792882919312}, "car:10": {"box": [657, 177, 31, 33], "box_score": 0.675413966178894}, "car:11": {"box": [884, 154, 96, 61], "box_score": 0.6623674631118774}, "car:4": {"box": [315, 196, 105, 66], "box_score": 0.9296782612800598}, "car:8": {"box": [464, 185, 40, 39], "box_score": 0.7470207810401917}}}, "0000000174.png": {"car": {"car:2": {"box": [1073, 156, 170, 65], "box_score": 0.9892963767051697}, "car:1": {"box": [898, 167, 157, 63], "box_score": 0.9959855675697327}, "car:3": {"box": [154, 191, 88, 41], "box_score": 0.8782378435134888}}}, "0000000061.png": {"car": {"car:2": {"box": [5, 210, 249, 117], "box_score": 0.9577653408050537}, "car:7": {"box": [774, 157, 139, 53], "box_score": 0.7171571850776672}, "car:1": {"box": [226, 192, 215, 126], "box_score": 0.9869536757469177}, "car:4": {"box": [643, 177, 54, 39], "box_score": 0.8891896605491638}, "car:5": {"box": [727, 162, 73, 44], "box_score": 0.8530136346817017}, "car:3": {"box": [404, 188, 91, 62], "box_score": 0.9371750354766846}, "car:6": {"box": [1009, 137, 71, 37], "box_score": 0.7772814631462097}}}, "0000000351.png": {"truck": {"truck:1": {"box": [439, 151, 73, 47], "box_score": 0.6531161665916443}}, "car": {"car:2": {"box": [627, 174, 73, 25], "box_score": 0.9068347811698914}, "car:1": {"box": [351, 182, 73, 33], "box_score": 0.9770514369010925}, "car:3": {"box": [420, 179, 65, 49], "box_score": 0.8506492972373962}, "car:4": {"box": [516, 174, 67, 26], "box_score": 0.6175535321235657}}, "person": {"person:1": {"box": [704, 173, 21, 47], "box_score": 0.686896800994873}}}, "0000000157.png": {"car": {"car:2": {"box": [835, 170, 92, 37], "box_score": 0.9907322525978088}, "car:1": {"box": [954, 228, 285, 143], "box_score": 0.9935064315795898}, "car:3": {"box": [201, 178, 140, 59], "box_score": 0.949191689491272}, "car:4": {"box": [37, 204, 98, 39], "box_score": 0.7645057439804077}}, "person": {"person:2": {"box": [1027, 136, 52, 152], "box_score": 0.8203330039978027}, "person:1": {"box": [964, 134, 57, 150], "box_score": 0.9440016150474548}}}, "0000000187.png": {"bicycle": {"bicycle:1": {"box": [886, 192, 74, 48], "box_score": 0.9757015705108643}}, "car": {"car:2": {"box": [126, 184, 94, 49], "box_score": 0.894829511642456}, "car:1": {"box": [1040, 174, 202, 81], "box_score": 0.9847612380981445}, "car:3": {"box": [-1, 177, 81, 106], "box_score": 0.8630589842796326}}}, "0000000276.png": {"car": {"car:2": {"box": [130, 184, 240, 153], "box_score": 0.9839150905609131}, "car:7": {"box": [11, 177, 129, 41], "box_score": 0.6752657294273376}, "car:1": {"box": [1, 206, 154, 165], "box_score": 0.9922155737876892}, "car:4": {"box": [355, 192, 93, 82], "box_score": 0.9570243954658508}, "car:5": {"box": [558, 175, 38, 26], "box_score": 0.8831207752227783}, "car:3": {"box": [423, 184, 73, 62], "box_score": 0.9714473485946655}, "car:6": {"box": [713, 170, 83, 58], "box_score": 0.845626175403595}}}, "0000000323.png": {"car": {"car:2": {"box": [426, 183, 75, 47], "box_score": 0.9818292856216431}, "car:7": {"box": [583, 176, 40, 16], "box_score": 0.8315643072128296}, "car:1": {"box": [1, 208, 307, 163], "box_score": 0.9821677207946777}, "car:9": {"box": [1169, 171, 71, 55], "box_score": 0.6098219156265259}, "car:4": {"box": [478, 180, 44, 38], "box_score": 0.9460781216621399}, "car:8": {"box": [714, 180, 56, 61], "box_score": 0.8288151621818542}, "car:5": {"box": [747, 184, 126, 87], "box_score": 0.9438378214836121}, "car:3": {"box": [810, 187, 308, 172], "box_score": 0.9645102620124817}, "car:6": {"box": [1012, 242, 231, 133], "box_score": 0.8540821671485901}}}, "0000000334.png": {"truck": {"truck:1": {"box": [665, 150, 65, 43], "box_score": 0.6555578708648682}}, "car": {"car:2": {"box": [221, 187, 161, 94], "box_score": 0.9848048686981201}, "car:1": {"box": [789, 186, 291, 157], "box_score": 0.9910345673561096}, "car:4": {"box": [1041, 249, 204, 127], "box_score": 0.9542122483253479}, "car:5": {"box": [358, 180, 88, 68], "box_score": 0.9407877326011658}, "car:3": {"box": [736, 180, 118, 81], "box_score": 0.9715216159820557}, "car:6": {"box": [483, 175, 49, 23], "box_score": 0.9405691623687744}}}, "0000000263.png": {"car": {"car:2": {"box": [852, 194, 394, 172], "box_score": 0.9816177487373352}, "car:7": {"box": [94, 192, 94, 39], "box_score": 0.6929686069488525}, "car:1": {"box": [363, 186, 115, 78], "box_score": 0.9859851598739624}, "car:4": {"box": [696, 176, 45, 36], "box_score": 0.8803278803825378}, "car:5": {"box": [459, 187, 58, 54], "box_score": 0.8481334447860718}, "car:3": {"box": [511, 184, 44, 36], "box_score": 0.9374797344207764}, "car:6": {"box": [586, 179, 40, 20], "box_score": 0.8298929929733276}}}, "0000000030.png": {"truck": {"truck:1": {"box": [1195, 134, 49, 60], "box_score": 0.9094624519348145}}, "car": {"car:2": {"box": [351, 193, 88, 59], "box_score": 0.944123387336731}, "car:1": {"box": [205, 198, 160, 88], "box_score": 0.9788459539413452}, "car:3": {"box": [683, 176, 106, 70], "box_score": 0.9221081733703613}, "car:4": {"box": [425, 178, 66, 49], "box_score": 0.7767382264137268}}}, "0000000402.png": {"car": {"car:2": {"box": [415, 182, 114, 56], "box_score": 0.9136374592781067}, "car:1": {"box": [1, 199, 244, 138], "box_score": 0.9819398522377014}}, "traffic light": {"traffic light:2": {"box": [405, 47, 33, 58], "box_score": 0.7227053642272949}, "traffic light:3": {"box": [349, 12, 40, 99], "box_score": 0.720648467540741}, "traffic light:1": {"box": [1046, 26, 33, 78], "box_score": 0.9038249254226685}}}, "0000000346.png": {"truck": {"truck:1": {"box": [501, 152, 94, 55], "box_score": 0.8841800689697266}}, "car": {"car:2": {"box": [340, 185, 79, 29], "box_score": 0.9629009366035461}, "car:1": {"box": [947, 223, 294, 148], "box_score": 0.9934023022651672}, "car:4": {"box": [458, 183, 52, 35], "box_score": 0.9424498081207275}, "car:5": {"box": [94, 185, 86, 54], "box_score": 0.9105323553085327}, "car:3": {"box": [1, 206, 146, 157], "box_score": 0.9582703709602356}, "car:6": {"box": [642, 176, 62, 24], "box_score": 0.7121559381484985}}}, "0000000365.png": {"car": {"car:2": {"box": [300, 190, 112, 86], "box_score": 0.9798490405082703}, "car:5": {"box": [156, 178, 65, 37], "box_score": 0.7780871391296387}, "car:1": {"box": [631, 175, 90, 31], "box_score": 0.9826220273971558}, "car:3": {"box": [215, 179, 113, 48], "box_score": 0.9616227149963379}, "car:4": {"box": [489, 177, 90, 34], "box_score": 0.8403427600860596}}, "person": {"person:1": {"box": [858, 166, 30, 97], "box_score": 0.8468474745750427}}}, "0000000183.png": {"bicycle": {"bicycle:1": {"box": [843, 192, 68, 42], "box_score": 0.9767503142356873}}, "car": {"car:2": {"box": [109, 188, 97, 46], "box_score": 0.8208545446395874}, "car:1": {"box": [979, 172, 205, 73], "box_score": 0.9761956334114075}, "car:3": {"box": [1191, 191, 53, 49], "box_score": 0.805435299873352}, "car:4": {"box": [-1, 183, 76, 100], "box_score": 0.8004701733589172}}}, "0000000229.png": {"car": {"car:2": {"box": [778, 138, 488, 230], "box_score": 0.963653564453125}, "car:7": {"box": [286, 183, 51, 31], "box_score": 0.8508654832839966}, "car:1": {"box": [0, 220, 131, 152], "box_score": 0.9892264008522034}, "car:4": {"box": [60, 205, 142, 99], "box_score": 0.9379441142082214}, "car:8": {"box": [459, 181, 31, 34], "box_score": 0.6741873025894165}, "car:5": {"box": [469, 182, 57, 40], "box_score": 0.9295737147331238}, "car:3": {"box": [572, 190, 142, 85], "box_score": 0.9603330492973328}, "car:6": {"box": [648, 168, 100, 43], "box_score": 0.9135627150535583}}}, "0000000201.png": {"bicycle": {"bicycle:1": {"box": [1110, 204, 105, 63], "box_score": 0.9665214419364929}}, "car": {"car:2": {"box": [2, 170, 188, 115], "box_score": 0.9069121479988098}, "car:1": {"box": [260, 181, 83, 47], "box_score": 0.953098714351654}, "car:3": {"box": [186, 182, 66, 41], "box_score": 0.8842735290527344}}}, "0000000244.png": {"car": {"car:2": {"box": [710, 188, 92, 67], "box_score": 0.9364846348762512}, "car:1": {"box": [1021, 165, 213, 72], "box_score": 0.9832859635353088}, "car:4": {"box": [687, 183, 54, 48], "box_score": 0.835688054561615}, "car:5": {"box": [894, 178, 135, 40], "box_score": 0.6680641174316406}, "car:3": {"box": [483, 183, 62, 40], "box_score": 0.9204826951026917}, "car:6": {"box": [668, 176, 28, 25], "box_score": 0.6542475819587708}}}, "0000000194.png": {"bicycle": {"bicycle:1": {"box": [975, 198, 87, 53], "box_score": 0.9254110455513}}, "car": {"car:2": {"box": [179, 185, 92, 48], "box_score": 0.9492315649986267}, "car:1": {"box": [1157, 206, 86, 72], "box_score": 0.9604842066764832}, "car:3": {"box": [4, 177, 118, 106], "box_score": 0.9179497957229614}, "car:4": {"box": [105, 185, 62, 42], "box_score": 0.7410865426063538}}}, "0000000342.png": {"truck": {"truck:1": {"box": [573, 145, 68, 46], "box_score": 0.681968629360199}}, "car": {"car:2": {"box": [810, 186, 388, 183], "box_score": 0.977523148059845}, "car:1": {"box": [467, 176, 56, 30], "box_score": 0.9944987893104553}, "car:4": {"box": [356, 176, 58, 28], "box_score": 0.9678938388824463}, "car:5": {"box": [0, 211, 80, 162], "box_score": 0.9664862751960754}, "car:3": {"box": [64, 186, 234, 137], "box_score": 0.973675549030304}, "car:6": {"box": [682, 170, 38, 22], "box_score": 0.6207343935966492}}}, "0000000352.png": {"truck": {"truck:1": {"box": [424, 150, 73, 50], "box_score": 0.652063250541687}}, "car": {"car:2": {"box": [626, 174, 75, 25], "box_score": 0.9420085549354553}, "car:1": {"box": [352, 180, 65, 38], "box_score": 0.9487681984901428}, "car:3": {"box": [413, 183, 67, 52], "box_score": 0.9086503386497498}, "car:4": {"box": [510, 173, 75, 30], "box_score": 0.6473504304885864}}, "person": {"person:1": {"box": [710, 175, 18, 42], "box_score": 0.7101636528968811}}}, "0000000104.png": {"car": {"car:2": {"box": [1, 214, 229, 154], "box_score": 0.9645618200302124}, "car:10": {"box": [884, 158, 105, 59], "box_score": 0.6738646626472473}, "car:1": {"box": [229, 197, 152, 86], "box_score": 0.9656519889831543}, "car:11": {"box": [444, 188, 45, 40], "box_score": 0.6292227506637573}, "car:4": {"box": [1048, 138, 175, 95], "box_score": 0.936674952507019}, "car:9": {"box": [688, 175, 61, 59], "box_score": 0.7114050388336182}, "car:8": {"box": [667, 178, 34, 36], "box_score": 0.7142031788825989}, "car:7": {"box": [487, 184, 40, 32], "box_score": 0.7445847988128662}, "car:5": {"box": [951, 152, 135, 73], "box_score": 0.9142849445343018}, "car:3": {"box": [376, 191, 87, 54], "box_score": 0.9632853865623474}, "car:6": {"box": [711, 178, 106, 70], "box_score": 0.9101556539535522}}}, "0000000079.png": {"truck": {"truck:1": {"box": [153, 221, 142, 79], "box_score": 0.7543933987617493}}, "car": {"car:2": {"box": [422, 184, 72, 44], "box_score": 0.9223426580429077}, "car:1": {"box": [744, 183, 167, 106], "box_score": 0.9759698510169983}, "car:4": {"box": [965, 153, 269, 83], "box_score": 0.7524409294128418}, "car:5": {"box": [265, 190, 140, 81], "box_score": 0.6859906911849976}, "car:3": {"box": [473, 183, 35, 34], "box_score": 0.8563855886459351}, "car:6": {"box": [509, 182, 26, 26], "box_score": 0.6358823776245117}}}, "0000000290.png": {"truck": {"truck:1": {"box": [810, 162, 321, 183], "box_score": 0.7327383160591125}}, "car": {"car:2": {"box": [498, 183, 60, 38], "box_score": 0.975786030292511}, "car:1": {"box": [-1, 219, 182, 155], "box_score": 0.9855983853340149}, "car:3": {"box": [758, 188, 83, 70], "box_score": 0.9506295323371887}, "car:4": {"box": [726, 182, 67, 53], "box_score": 0.915547788143158}}}, "0000000006.png": {"car": {"car:2": {"box": [812, 184, 388, 186], "box_score": 0.9815347194671631}, "car:5": {"box": [274, 193, 33, 29], "box_score": 0.6282444000244141}, "car:1": {"box": [293, 196, 121, 73], "box_score": 0.9849644303321838}, "car:3": {"box": [730, 179, 118, 91], "box_score": 0.937380313873291}, "car:4": {"box": [478, 185, 44, 26], "box_score": 0.8853045701980591}}}, "0000000372.png": {"traffic light": {"traffic light:1": {"box": [874, 89, 21, 44], "box_score": 0.7029725909233093}}, "car": {"car:2": {"box": [361, 175, 142, 57], "box_score": 0.9790686368942261}, "car:1": {"box": [-1, 218, 253, 156], "box_score": 0.981028139591217}, "car:3": {"box": [634, 175, 101, 34], "box_score": 0.9303577542304993}}, "person": {"person:1": {"box": [1050, 157, 76, 164], "box_score": 0.9249494671821594}}}, "0000000416.png": {"car": {"car:1": {"box": [95, 195, 255, 125], "box_score": 0.9865210056304932}}, "traffic light": {"traffic light:2": {"box": [349, 10, 39, 101], "box_score": 0.6901399493217468}, "traffic light:3": {"box": [399, 46, 38, 64], "box_score": 0.6250919699668884}, "traffic light:1": {"box": [1047, 28, 32, 79], "box_score": 0.7740589380264282}}}, "0000000050.png": {"fire hydrant": {"fire hydrant:1": {"box": [1154, 159, 33, 57], "box_score": 0.9422251582145691}}, "car": {"car:2": {"box": [358, 196, 76, 44], "box_score": 0.9716012477874756}, "car:7": {"box": [895, 151, 51, 29], "box_score": 0.6885434985160828}, "car:1": {"box": [95, 196, 216, 114], "box_score": 0.9784398674964905}, "car:9": {"box": [456, 190, 31, 29], "box_score": 0.612515926361084}, "car:4": {"box": [710, 170, 94, 33], "box_score": 0.9242193698883057}, "car:8": {"box": [1177, 155, 66, 50], "box_score": 0.6818838715553284}, "car:5": {"box": [469, 188, 64, 44], "box_score": 0.9119754433631897}, "car:3": {"box": [0, 206, 86, 173], "box_score": 0.9395838975906372}, "car:6": {"box": [626, 181, 37, 26], "box_score": 0.773968517780304}}}, "0000000068.png": {"truck": {"truck:1": {"box": [1149, 135, 90, 56], "box_score": 0.6243525147438049}}, "car": {"car:2": {"box": [861, 168, 215, 67], "box_score": 0.9498651623725891}, "car:7": {"box": [395, 196, 56, 40], "box_score": 0.646445095539093}, "car:1": {"box": [99, 199, 293, 167], "box_score": 0.9940686225891113}, "car:4": {"box": [477, 185, 42, 28], "box_score": 0.7794613242149353}, "car:8": {"box": [1104, 147, 46, 42], "box_score": 0.6107835173606873}, "car:5": {"box": [776, 165, 86, 44], "box_score": 0.7017605304718018}, "car:3": {"box": [666, 181, 61, 53], "box_score": 0.8361759185791016}, "car:6": {"box": [827, 157, 153, 69], "box_score": 0.689020037651062}}}, "0000000217.png": {"car": {"car:2": {"box": [295, 182, 80, 34], "box_score": 0.9392700791358948}, "car:7": {"box": [91, 194, 55, 39], "box_score": 0.6995158791542053}, "car:1": {"box": [214, 198, 130, 65], "box_score": 0.9851558804512024}, "car:4": {"box": [363, 170, 235, 128], "box_score": 0.9048758149147034}, "car:8": {"box": [1, 188, 35, 24], "box_score": 0.6977485418319702}, "car:5": {"box": [45, 193, 55, 37], "box_score": 0.8293296694755554}, "car:3": {"box": [676, 181, 89, 50], "box_score": 0.9311785101890564}, "car:6": {"box": [597, 181, 64, 39], "box_score": 0.8104304075241089}}}, "0000000077.png": {"car": {"car:2": {"box": [717, 178, 129, 85], "box_score": 0.9387356042861938}, "car:1": {"box": [-1, 222, 163, 143], "box_score": 0.9965519905090332}, "car:4": {"box": [911, 154, 214, 74], "box_score": 0.8788792490959167}, "car:5": {"box": [437, 183, 63, 39], "box_score": 0.8542520999908447}, "car:3": {"box": [1059, 137, 183, 138], "box_score": 0.9169971942901611}, "car:6": {"box": [476, 181, 36, 31], "box_score": 0.7356706261634827}}}, "0000000041.png": {"car": {"car:2": {"box": [379, 181, 67, 56], "box_score": 0.9253488183021545}, "car:7": {"box": [443, 183, 55, 38], "box_score": 0.8583285212516785}, "car:1": {"box": [0, 216, 208, 157], "box_score": 0.9899774789810181}, "car:9": {"box": [496, 178, 36, 27], "box_score": 0.7910667061805725}, "car:4": {"box": [856, 174, 409, 199], "box_score": 0.9143524765968323}, "car:8": {"box": [630, 174, 31, 23], "box_score": 0.803310751914978}, "car:5": {"box": [690, 163, 82, 29], "box_score": 0.9111682772636414}, "car:3": {"box": [254, 177, 144, 91], "box_score": 0.9237761497497559}, "car:6": {"box": [528, 178, 38, 27], "box_score": 0.89451664686203}}}, "0000000133.png": {"car": {"car:2": {"box": [353, 184, 95, 61], "box_score": 0.9735444188117981}, "car:7": {"box": [77, 204, 56, 35], "box_score": 0.625406801700592}, "car:1": {"box": [0, 226, 136, 142], "box_score": 0.9888709187507629}, "car:4": {"box": [715, 177, 129, 85], "box_score": 0.9380989074707031}, "car:5": {"box": [431, 184, 48, 45], "box_score": 0.8888022303581238}, "car:3": {"box": [861, 189, 394, 180], "box_score": 0.9565806984901428}, "car:6": {"box": [687, 175, 59, 55], "box_score": 0.822809100151062}}}, "0000000327.png": {"car": {"car:2": {"box": [793, 184, 223, 133], "box_score": 0.9803913831710815}, "car:7": {"box": [1, 274, 107, 98], "box_score": 0.689275324344635}, "car:1": {"box": [379, 182, 91, 58], "box_score": 0.9849652051925659}, "car:4": {"box": [933, 210, 308, 163], "box_score": 0.969708263874054}, "car:5": {"box": [735, 185, 98, 76], "box_score": 0.8786411881446838}, "car:3": {"box": [445, 178, 57, 46], "box_score": 0.9748115539550781}, "car:6": {"box": [538, 176, 39, 14], "box_score": 0.7903188467025757}}}, "0000000024.png": {"car": {"car:2": {"box": [419, 190, 55, 45], "box_score": 0.9270433187484741}, "car:1": {"box": [346, 192, 86, 59], "box_score": 0.9533599019050598}, "car:4": {"box": [17, 203, 76, 38], "box_score": 0.8481566905975342}, "car:5": {"box": [460, 179, 41, 39], "box_score": 0.7962413430213928}, "car:3": {"box": [667, 172, 70, 52], "box_score": 0.8579476475715637}, "car:6": {"box": [1082, 131, 119, 51], "box_score": 0.7374376058578491}}}, "0000000107.png": {"car": {"car:2": {"box": [65, 201, 253, 122], "box_score": 0.9845313429832458}, "car:7": {"box": [674, 179, 42, 40], "box_score": 0.8786596059799194}, "car:1": {"box": [739, 179, 151, 95], "box_score": 0.9856619238853455}, "car:9": {"box": [646, 178, 34, 30], "box_score": 0.7888169884681702}, "car:13": {"box": [1187, 165, 57, 88], "box_score": 0.6599748730659485}, "car:5": {"box": [703, 177, 75, 71], "box_score": 0.9428845643997192}, "car:3": {"box": [318, 192, 119, 65], "box_score": 0.9779611825942993}, "car:6": {"box": [474, 184, 46, 36], "box_score": 0.8825386762619019}, "car:12": {"box": [573, 175, 39, 18], "box_score": 0.6818003058433533}, "car:10": {"box": [513, 179, 35, 24], "box_score": 0.7335354685783386}, "car:11": {"box": [1028, 156, 74, 65], "box_score": 0.6938180923461914}, "car:4": {"box": [1044, 147, 194, 90], "box_score": 0.9664269089698792}, "car:8": {"box": [419, 186, 58, 50], "box_score": 0.8375282883644104}}}, "0000000335.png": {"truck": {"truck:1": {"box": [661, 150, 66, 43], "box_score": 0.7222543954849243}}, "car": {"car:2": {"box": [741, 181, 129, 91], "box_score": 0.9880443215370178}, "car:5": {"box": [343, 182, 88, 71], "box_score": 0.9295337796211243}, "car:1": {"box": [805, 187, 351, 172], "box_score": 0.9947425127029419}, "car:3": {"box": [180, 186, 180, 105], "box_score": 0.9780739545822144}, "car:4": {"box": [482, 176, 49, 23], "box_score": 0.9426699876785278}}}, "0000000147.png": {"car": {"car:2": {"box": [139, 193, 183, 111], "box_score": 0.9842914342880249}, "car:1": {"box": [1, 210, 144, 155], "box_score": 0.9927470088005066}, "car:4": {"box": [833, 187, 419, 182], "box_score": 0.9060097336769104}, "car:5": {"box": [314, 175, 100, 40], "box_score": 0.8114256262779236}, "car:3": {"box": [744, 183, 154, 101], "box_score": 0.9682357907295227}, "car:6": {"box": [273, 181, 55, 27], "box_score": 0.6739282011985779}}, "person": {"person:1": {"box": [811, 148, 30, 40], "box_score": 0.7383496761322021}}}, "0000000213.png": {"car": {"car:2": {"box": [539, 184, 82, 47], "box_score": 0.9245234727859497}, "car:5": {"box": [143, 188, 88, 33], "box_score": 0.7216968536376953}, "car:1": {"box": [59, 200, 150, 70], "box_score": 0.9405076503753662}, "car:3": {"box": [228, 173, 237, 120], "box_score": 0.9216077923774719}, "car:4": {"box": [464, 184, 66, 40], "box_score": 0.8061506152153015}}}, "0000000161.png": {"car": {"car:2": {"box": [845, 167, 113, 47], "box_score": 0.9633364081382751}, "car:5": {"box": [311, 184, 82, 31], "box_score": 0.6583002805709839}, "car:1": {"box": [0, 210, 76, 43], "box_score": 0.9865767955780029}, "car:3": {"box": [148, 181, 163, 65], "box_score": 0.947983980178833}, "car:4": {"box": [977, 163, 111, 45], "box_score": 0.7260393500328064}}, "person": {"person:2": {"box": [1160, 124, 83, 215], "box_score": 0.8196120262145996}, "person:1": {"box": [1091, 130, 80, 197], "box_score": 0.8963680267333984}}}, "0000000285.png": {"car": {"car:2": {"box": [1, 221, 193, 150], "box_score": 0.9883212447166443}, "car:5": {"box": [754, 159, 151, 104], "box_score": 0.6612304449081421}, "car:1": {"box": [162, 186, 212, 141], "box_score": 0.9911627769470215}, "car:3": {"box": [522, 172, 47, 32], "box_score": 0.8870566487312317}, "car:4": {"box": [730, 175, 48, 52], "box_score": 0.8625679016113281}}}, "0000000179.png": {"bicycle": {"bicycle:1": {"box": [815, 189, 62, 40], "box_score": 0.9581351280212402}}, "car": {"car:2": {"box": [1128, 163, 114, 70], "box_score": 0.9832806587219238}, "car:1": {"box": [932, 171, 183, 67], "box_score": 0.9920571446418762}, "car:3": {"box": [114, 190, 96, 46], "box_score": 0.8806917071342468}}}, "0000000431.png": {"traffic light": {"traffic light:2": {"box": [348, 9, 41, 102], "box_score": 0.7097687125205994}, "traffic light:1": {"box": [1048, 29, 31, 77], "box_score": 0.8019014000892639}}}, "0000000436.png": {"traffic light": {"traffic light:2": {"box": [347, 13, 42, 99], "box_score": 0.6767739653587341}, "traffic light:3": {"box": [400, 46, 37, 64], "box_score": 0.6370341181755066}, "traffic light:1": {"box": [1047, 28, 32, 77], "box_score": 0.7826669812202454}}}, "0000000269.png": {"car": {"car:2": {"box": [169, 179, 90, 40], "box_score": 0.9547172784805298}, "car:7": {"box": [575, 179, 41, 21], "box_score": 0.7220657467842102}, "car:1": {"box": [201, 189, 204, 130], "box_score": 0.9939737915992737}, "car:4": {"box": [381, 185, 92, 78], "box_score": 0.9267059564590454}, "car:5": {"box": [462, 190, 47, 52], "box_score": 0.9082847237586975}, "car:3": {"box": [479, 189, 48, 44], "box_score": 0.9507473111152649}, "car:6": {"box": [704, 177, 53, 43], "box_score": 0.7653023600578308}}}, "0000000131.png": {"truck": {"truck:1": {"box": [679, 134, 71, 65], "box_score": 0.6443389058113098}}, "car": {"car:2": {"box": [1, 202, 242, 165], "box_score": 0.992003858089447}, "car:7": {"box": [681, 172, 50, 46], "box_score": 0.6114112138748169}, "car:1": {"box": [803, 178, 343, 169], "box_score": 0.9975684285163879}, "car:4": {"box": [705, 172, 103, 77], "box_score": 0.9454317688941956}, "car:5": {"box": [1152, 267, 93, 105], "box_score": 0.7665324807167053}, "car:3": {"box": [384, 176, 83, 57], "box_score": 0.963697612285614}, "car:6": {"box": [444, 176, 44, 41], "box_score": 0.7184305787086487}}}, "0000000370.png": {"car": {"car:2": {"box": [7, 202, 331, 168], "box_score": 0.9670151472091675}, "car:1": {"box": [317, 175, 136, 55], "box_score": 0.9874629378318787}, "car:3": {"box": [633, 175, 99, 33], "box_score": 0.9331894516944885}, "car:4": {"box": [476, 176, 93, 38], "box_score": 0.8092749118804932}}, "person": {"person:1": {"box": [974, 162, 63, 136], "box_score": 0.9145528674125671}}}, "0000000264.png": {"car": {"car:2": {"box": [875, 194, 380, 177], "box_score": 0.9667336344718933}, "car:7": {"box": [695, 175, 49, 39], "box_score": 0.8126072287559509}, "car:1": {"box": [346, 189, 125, 83], "box_score": 0.9917367100715637}, "car:4": {"box": [250, 178, 75, 35], "box_score": 0.9008260369300842}, "car:8": {"box": [585, 180, 40, 20], "box_score": 0.6411543488502502}, "car:5": {"box": [446, 186, 64, 59], "box_score": 0.8931897878646851}, "car:3": {"box": [507, 187, 41, 36], "box_score": 0.9050348401069641}, "car:6": {"box": [0, 193, 158, 59], "box_score": 0.8833243250846863}}}, "0000000000.png": {"car": {"car:2": {"box": [688, 182, 62, 60], "box_score": 0.9527430534362793}, "car:1": {"box": [386, 195, 76, 51], "box_score": 0.9872051477432251}, "car:4": {"box": [795, 189, 271, 180], "box_score": 0.8275532126426697}, "car:5": {"box": [496, 188, 36, 23], "box_score": 0.7766715884208679}, "car:3": {"box": [724, 183, 119, 89], "box_score": 0.9336661100387573}, "car:6": {"box": [887, 181, 330, 165], "box_score": 0.6676373481750488}}}, "0000000343.png": {"truck": {"truck:1": {"box": [542, 144, 85, 53], "box_score": 0.8903258442878723}}, "car": {"car:2": {"box": [2, 190, 265, 152], "box_score": 0.9714995622634888}, "car:1": {"box": [466, 178, 53, 31], "box_score": 0.9846159815788269}, "car:3": {"box": [344, 179, 71, 28], "box_score": 0.9558891654014587}, "car:4": {"box": [872, 191, 394, 176], "box_score": 0.8936951756477356}}}, "0000000149.png": {"bus": {"bus:1": {"box": [1149, 3, 93, 190], "box_score": 0.7342215180397034}}, "car": {"car:2": {"box": [10, 199, 265, 142], "box_score": 0.9654787182807922}, "car:1": {"box": [756, 183, 213, 124], "box_score": 0.9800962805747986}, "car:3": {"box": [891, 199, 358, 171], "box_score": 0.9609839916229248}, "car:4": {"box": [305, 177, 93, 43], "box_score": 0.8206578493118286}}, "person": {"person:2": {"box": [870, 149, 28, 42], "box_score": 0.7027267217636108}, "person:1": {"box": [810, 148, 52, 47], "box_score": 0.8746609091758728}}}, "0000000442.png": {"traffic light": {"traffic light:2": {"box": [348, 9, 41, 102], "box_score": 0.6969681978225708}, "traffic light:3": {"box": [398, 47, 39, 63], "box_score": 0.6656519174575806}, "traffic light:1": {"box": [1047, 28, 32, 77], "box_score": 0.8073378801345825}}}, "0000000087.png": {"car": {"car:2": {"box": [313, 190, 116, 69], "box_score": 0.9884682297706604}, "car:10": {"box": [763, 155, 74, 37], "box_score": 0.615106999874115}, "car:1": {"box": [0, 214, 168, 152], "box_score": 0.9956603646278381}, "car:9": {"box": [484, 184, 32, 30], "box_score": 0.7398611903190613}, "car:4": {"box": [1073, 140, 61, 35], "box_score": 0.8545588850975037}, "car:8": {"box": [508, 180, 32, 27], "box_score": 0.7540217638015747}, "car:7": {"box": [1071, 296, 172, 76], "box_score": 0.8068455457687378}, "car:5": {"box": [790, 155, 96, 38], "box_score": 0.8337056636810303}, "car:3": {"box": [409, 188, 61, 48], "box_score": 0.9258280992507935}, "car:6": {"box": [1131, 135, 101, 40], "box_score": 0.8244071006774902}}}, "0000000080.png": {"truck": {"truck:1": {"box": [99, 223, 175, 90], "box_score": 0.6828206181526184}}, "car": {"car:2": {"box": [413, 184, 74, 47], "box_score": 0.9502519965171814}, "car:1": {"box": [758, 182, 205, 120], "box_score": 0.9944038391113281}, "car:4": {"box": [230, 190, 160, 88], "box_score": 0.8568550944328308}, "car:5": {"box": [981, 149, 257, 94], "box_score": 0.8055675625801086}, "car:3": {"box": [469, 183, 35, 35], "box_score": 0.8654401898384094}, "car:6": {"box": [767, 161, 71, 31], "box_score": 0.6293526887893677}}}, "0000000129.png": {"truck": {"truck:1": {"box": [676, 134, 71, 76], "box_score": 0.665448009967804}}, "car": {"car:2": {"box": [0, 191, 313, 158], "box_score": 0.9747110605239868}, "car:1": {"box": [766, 176, 228, 126], "box_score": 0.9953587651252747}, "car:4": {"box": [701, 171, 84, 65], "box_score": 0.9426046013832092}, "car:5": {"box": [405, 174, 62, 50], "box_score": 0.9182727336883545}, "car:3": {"box": [951, 186, 294, 188], "box_score": 0.9604173898696899}, "car:6": {"box": [455, 177, 42, 37], "box_score": 0.6334694623947144}}}, "0000000105.png": {"car": {"car:2": {"box": [179, 201, 185, 93], "box_score": 0.973629891872406}, "car:7": {"box": [668, 178, 38, 37], "box_score": 0.8686409592628479}, "car:1": {"box": [-1, 218, 183, 145], "box_score": 0.9873215556144714}, "car:9": {"box": [695, 175, 66, 63], "box_score": 0.7892000675201416}, "car:13": {"box": [517, 178, 32, 24], "box_score": 0.6355434656143188}, "car:5": {"box": [1083, 135, 157, 99], "box_score": 0.944384753704071}, "car:3": {"box": [360, 190, 94, 60], "box_score": 0.9500066637992859}, "car:6": {"box": [723, 179, 109, 78], "box_score": 0.9150424003601074}, "car:12": {"box": [1148, 163, 95, 92], "box_score": 0.7246973514556885}, "car:10": {"box": [916, 156, 102, 62], "box_score": 0.7613582611083984}, "car:11": {"box": [438, 186, 47, 43], "box_score": 0.7295439839363098}, "car:4": {"box": [975, 149, 153, 80], "box_score": 0.9455476999282837}, "car:8": {"box": [483, 184, 42, 32], "box_score": 0.8057742714881897}}}, "0000000128.png": {"car": {"car:2": {"box": [894, 181, 348, 192], "box_score": 0.9851266741752625}, "car:7": {"box": [463, 178, 40, 36], "box_score": 0.6292956471443176}, "car:1": {"box": [751, 175, 190, 115], "box_score": 0.9888026118278503}, "car:4": {"box": [413, 176, 68, 46], "box_score": 0.941588819026947}, "car:5": {"box": [695, 173, 77, 63], "box_score": 0.9398945569992065}, "car:3": {"box": [53, 190, 285, 142], "box_score": 0.9775823950767517}, "car:6": {"box": [675, 172, 50, 46], "box_score": 0.7332578897476196}}}, "0000000144.png": {"car": {"car:2": {"box": [934, 217, 316, 155], "box_score": 0.977641761302948}, "car:7": {"box": [343, 178, 89, 36], "box_score": 0.615692675113678}, "car:1": {"box": [2, 199, 267, 157], "box_score": 0.9944975972175598}, "car:4": {"box": [729, 184, 89, 83], "box_score": 0.9502037763595581}, "car:5": {"box": [258, 191, 119, 87], "box_score": 0.8463226556777954}, "car:3": {"box": [772, 188, 259, 150], "box_score": 0.9749075770378113}, "car:6": {"box": [917, 168, 52, 25], "box_score": 0.6873891949653625}}, "person": {"person:1": {"box": [790, 160, 28, 35], "box_score": 0.6150185465812683}}}, "0000000200.png": {"bicycle": {"bicycle:1": {"box": [1086, 200, 103, 62], "box_score": 0.987373411655426}}, "car": {"car:2": {"box": [0, 169, 182, 115], "box_score": 0.9051299095153809}, "car:1": {"box": [248, 182, 84, 45], "box_score": 0.9592108726501465}, "car:3": {"box": [171, 181, 64, 43], "box_score": 0.8606294989585876}}}, "0000000360.png": {"motorcycle": {"motorcycle:1": {"box": [84, 210, 32, 44], "box_score": 0.7183235883712769}}, "car": {"car:2": {"box": [146, 183, 108, 43], "box_score": 0.9846567511558533}, "car:5": {"box": [491, 178, 85, 30], "box_score": 0.7229877710342407}, "car:1": {"box": [352, 187, 85, 55], "box_score": 0.989677906036377}, "car:3": {"box": [159, 193, 229, 146], "box_score": 0.9659695625305176}, "car:4": {"box": [623, 177, 85, 29], "box_score": 0.9406658411026001}}, "person": {"person:1": {"box": [776, 171, 34, 73], "box_score": 0.9771436452865601}}}, "0000000255.png": {"car": {"car:2": {"box": [1091, 179, 149, 67], "box_score": 0.9960303902626038}, "car:7": {"box": [493, 187, 51, 44], "box_score": 0.661157488822937}, "car:1": {"box": [820, 203, 278, 150], "box_score": 0.9994555115699768}, "car:4": {"box": [752, 191, 125, 80], "box_score": 0.9634064435958862}, "car:5": {"box": [692, 180, 37, 29], "box_score": 0.9462299942970276}, "car:3": {"box": [451, 188, 83, 52], "box_score": 0.9793686866760254}, "car:6": {"box": [541, 188, 32, 29], "box_score": 0.8515013456344604}}}, "0000000231.png": {"car": {"car:2": {"box": [620, 189, 158, 101], "box_score": 0.9574428796768188}, "car:7": {"box": [854, 133, 391, 239], "box_score": 0.6417050957679749}, "car:1": {"box": [0, 238, 137, 131], "box_score": 0.9655107259750366}, "car:4": {"box": [709, 170, 97, 49], "box_score": 0.9128730893135071}, "car:8": {"box": [501, 187, 32, 32], "box_score": 0.6033660769462585}, "car:5": {"box": [510, 189, 61, 40], "box_score": 0.9096778631210327}, "car:3": {"box": [72, 210, 158, 111], "box_score": 0.9281956553459167}, "car:6": {"box": [331, 188, 53, 34], "box_score": 0.8037174344062805}}}, "0000000122.png": {"car": {"car:2": {"box": [294, 190, 140, 72], "box_score": 0.9745688438415527}, "car:7": {"box": [1138, 335, 107, 39], "box_score": 0.7948606610298157}, "car:1": {"box": [757, 179, 178, 114], "box_score": 0.9921838641166687}, "car:4": {"box": [700, 180, 83, 68], "box_score": 0.9543208479881287}, "car:5": {"box": [456, 177, 63, 38], "box_score": 0.9165182113647461}, "car:3": {"box": [0, 196, 228, 176], "box_score": 0.9731921553611755}, "car:6": {"box": [669, 176, 55, 47], "box_score": 0.8676751852035522}}}, "0000000401.png": {"car": {"car:2": {"box": [425, 182, 121, 54], "box_score": 0.8511609435081482}, "car:1": {"box": [0, 199, 261, 129], "box_score": 0.9936339855194092}}, "traffic light": {"traffic light:2": {"box": [353, 14, 38, 95], "box_score": 0.7378902435302734}, "traffic light:3": {"box": [406, 46, 33, 58], "box_score": 0.6433923840522766}, "traffic light:1": {"box": [1044, 28, 34, 76], "box_score": 0.9095763564109802}}}, "0000000142.png": {"car": {"car:2": {"box": [747, 184, 182, 119], "box_score": 0.9477487802505493}, "car:7": {"box": [363, 177, 83, 32], "box_score": 0.7753469944000244}, "car:1": {"box": [98, 197, 221, 121], "box_score": 0.9929034113883972}, "car:4": {"box": [309, 194, 92, 74], "box_score": 0.932368278503418}, "car:5": {"box": [723, 185, 64, 65], "box_score": 0.9036219120025635}, "car:3": {"box": [860, 193, 392, 178], "box_score": 0.9364742636680603}, "car:6": {"box": [892, 168, 51, 21], "box_score": 0.8347299098968506}}}, "0000000391.png": {"car": {"car:2": {"box": [508, 178, 133, 46], "box_score": 0.9847091436386108}, "car:1": {"box": [231, 186, 155, 74], "box_score": 0.9983933568000793}, "car:3": {"box": [1018, 160, 199, 70], "box_score": 0.9624266624450684}}, "traffic light": {"traffic light:2": {"box": [1012, 35, 32, 75], "box_score": 0.6718971729278564}, "traffic light:1": {"box": [386, 28, 35, 83], "box_score": 0.8703531622886658}}}, "0000000291.png": {"truck": {"truck:1": {"box": [877, 157, 380, 205], "box_score": 0.6143296957015991}}, "car": {"car:2": {"box": [491, 188, 68, 38], "box_score": 0.9645638465881348}, "car:7": {"box": [697, 182, 33, 38], "box_score": 0.6875805258750916}, "car:1": {"box": [1, 234, 89, 140], "box_score": 0.968011200428009}, "car:4": {"box": [729, 186, 73, 62], "box_score": 0.9225449562072754}, "car:8": {"box": [687, 181, 31, 32], "box_score": 0.6337985396385193}, "car:5": {"box": [574, 184, 35, 19], "box_score": 0.8179264664649963}, "car:3": {"box": [768, 196, 104, 76], "box_score": 0.9454033374786377}, "car:6": {"box": [709, 185, 36, 42], "box_score": 0.7337507009506226}}}, "0000000199.png": {"bicycle": {"bicycle:1": {"box": [1065, 200, 95, 61], "box_score": 0.9897566437721252}}, "car": {"car:2": {"box": [235, 183, 86, 46], "box_score": 0.916080117225647}, "car:1": {"box": [0, 173, 171, 111], "box_score": 0.9221389889717102}, "car:3": {"box": [157, 181, 70, 43], "box_score": 0.897179901599884}}}, "0000000254.png": {"car": {"car:2": {"box": [1062, 182, 182, 63], "box_score": 0.9961340427398682}, "car:1": {"box": [804, 201, 237, 136], "box_score": 0.9977394342422485}, "car:4": {"box": [459, 190, 78, 51], "box_score": 0.9677709937095642}, "car:5": {"box": [693, 182, 38, 29], "box_score": 0.9097188115119934}, "car:3": {"box": [748, 192, 109, 73], "box_score": 0.9693342447280884}, "car:6": {"box": [541, 191, 31, 30], "box_score": 0.8300966620445251}}}, "0000000287.png": {"car": {"car:2": {"box": [512, 176, 55, 34], "box_score": 0.949999213218689}, "car:5": {"box": [775, 160, 190, 125], "box_score": 0.6783374547958374}, "car:1": {"box": [4, 192, 326, 183], "box_score": 0.9688721895217896}, "car:3": {"box": [740, 180, 60, 59], "box_score": 0.890446662902832}, "car:4": {"box": [720, 173, 54, 56], "box_score": 0.7431417107582092}}}, "0000000202.png": {"bicycle": {"bicycle:1": {"box": [1136, 206, 106, 64], "box_score": 0.8905847072601318}}, "car": {"car:2": {"box": [2, 172, 205, 115], "box_score": 0.9418270587921143}, "car:1": {"box": [274, 184, 82, 46], "box_score": 0.954417884349823}, "car:3": {"box": [200, 184, 61, 41], "box_score": 0.8806092739105225}}}, "0000000274.png": {"car": {"car:2": {"box": [249, 181, 163, 124], "box_score": 0.9715291261672974}, "car:1": {"box": [448, 183, 62, 56], "box_score": 0.9805377125740051}, "car:4": {"box": [400, 191, 72, 70], "box_score": 0.9487136006355286}, "car:5": {"box": [714, 170, 69, 56], "box_score": 0.8155855536460876}, "car:3": {"box": [-1, 189, 273, 182], "box_score": 0.956153154373169}, "car:6": {"box": [565, 175, 37, 26], "box_score": 0.7420944571495056}}}, "0000000330.png": {"car": {"car:2": {"box": [416, 176, 65, 54], "box_score": 0.919117271900177}, "car:5": {"box": [729, 175, 70, 67], "box_score": 0.7409910559654236}, "car:1": {"box": [329, 180, 111, 72], "box_score": 0.9863597750663757}, "car:3": {"box": [880, 181, 391, 185], "box_score": 0.9173880219459534}, "car:4": {"box": [749, 182, 142, 94], "box_score": 0.8945502042770386}}}, "0000000025.png": {"car": {"car:2": {"box": [411, 191, 58, 46], "box_score": 0.9401543736457825}, "car:7": {"box": [1186, 117, 59, 64], "box_score": 0.6131166219711304}, "car:1": {"box": [326, 192, 99, 64], "box_score": 0.9424676895141602}, "car:4": {"box": [11, 204, 60, 41], "box_score": 0.9278398752212524}, "car:5": {"box": [454, 178, 46, 43], "box_score": 0.8011265397071838}, "car:3": {"box": [670, 172, 70, 53], "box_score": 0.9307437539100647}, "car:6": {"box": [1105, 132, 119, 54], "box_score": 0.7302596569061279}}}, "0000000223.png": {"car": {"car:2": {"box": [474, 174, 87, 36], "box_score": 0.9611513614654541}, "car:7": {"box": [904, 171, 126, 65], "box_score": 0.8006043434143066}, "car:1": {"box": [399, 193, 124, 68], "box_score": 0.9674851298332214}, "car:9": {"box": [275, 187, 36, 31], "box_score": 0.6435819268226624}, "car:4": {"box": [815, 171, 70, 53], "box_score": 0.9091388583183289}, "car:8": {"box": [0, 208, 38, 86], "box_score": 0.737500011920929}, "car:5": {"box": [286, 187, 62, 38], "box_score": 0.8293749690055847}, "car:3": {"box": [535, 161, 297, 162], "box_score": 0.959693968296051}, "car:6": {"box": [73, 189, 49, 34], "box_score": 0.8036249876022339}}}, "0000000191.png": {"bicycle": {"bicycle:1": {"box": [934, 197, 80, 49], "box_score": 0.9850794076919556}}, "car": {"car:2": {"box": [152, 180, 93, 51], "box_score": 0.958579957485199}, "car:1": {"box": [1100, 184, 144, 83], "box_score": 0.9754519462585449}, "car:3": {"box": [0, 181, 97, 98], "box_score": 0.9076456427574158}, "car:4": {"box": [81, 186, 59, 37], "box_score": 0.7426407933235168}}}, "0000000396.png": {"car": {"car:2": {"box": [136, 193, 199, 93], "box_score": 0.9863722920417786}, "car:1": {"box": [484, 180, 114, 49], "box_score": 0.9917113780975342}}, "traffic light": {"traffic light:1": {"box": [366, 19, 38, 91], "box_score": 0.777204692363739}}}, "0000000328.png": {"car": {"car:2": {"box": [808, 184, 270, 162], "box_score": 0.9648956656455994}, "car:7": {"box": [729, 177, 65, 67], "box_score": 0.6632435917854309}, "car:1": {"box": [364, 180, 97, 62], "box_score": 0.9922559261322021}, "car:4": {"box": [744, 183, 110, 79], "box_score": 0.8992967009544373}, "car:5": {"box": [1002, 229, 239, 143], "box_score": 0.8815402984619141}, "car:3": {"box": [437, 177, 59, 49], "box_score": 0.9589734673500061}, "car:6": {"box": [526, 174, 37, 16], "box_score": 0.678523063659668}}}, "0000000395.png": {"car": {"car:2": {"box": [484, 179, 123, 48], "box_score": 0.9773622155189514}, "car:1": {"box": [159, 193, 187, 87], "box_score": 0.9918414354324341}, "car:3": {"box": [1183, 158, 60, 69], "box_score": 0.9384389519691467}}, "traffic light": {"traffic light:1": {"box": [368, 17, 38, 92], "box_score": 0.805779755115509}}}, "0000000377.png": {"car": {"car:2": {"box": [424, 177, 96, 49], "box_score": 0.8238409161567688}, "car:1": {"box": [635, 178, 94, 35], "box_score": 0.979698657989502}, "car:3": {"box": [510, 173, 138, 60], "box_score": 0.6750120520591736}}, "traffic light": {"traffic light:1": {"box": [925, 75, 25, 57], "box_score": 0.6115337014198303}}}, "0000000373.png": {"traffic light": {"traffic light:1": {"box": [885, 85, 26, 47], "box_score": 0.6129673719406128}}, "car": {"car:2": {"box": [387, 175, 133, 55], "box_score": 0.9662652015686035}, "car:1": {"box": [0, 242, 176, 131], "box_score": 0.9880822896957397}, "car:3": {"box": [631, 174, 106, 36], "box_score": 0.912341833114624}}, "person": {"person:1": {"box": [1093, 158, 79, 175], "box_score": 0.9239374995231628}}}, "0000000108.png": {"car": {"car:2": {"box": [752, 179, 174, 108], "box_score": 0.9760948419570923}, "car:7": {"box": [511, 180, 29, 25], "box_score": 0.8804919719696045}, "car:1": {"box": [3, 205, 290, 139], "box_score": 0.9924126267433167}, "car:9": {"box": [570, 175, 36, 20], "box_score": 0.7823376059532166}, "car:5": {"box": [291, 192, 135, 73], "box_score": 0.9396166205406189}, "car:3": {"box": [466, 184, 50, 37], "box_score": 0.9488354921340942}, "car:6": {"box": [1126, 147, 117, 105], "box_score": 0.9091705083847046}, "car:12": {"box": [647, 178, 33, 30], "box_score": 0.6298945546150208}, "car:10": {"box": [410, 186, 60, 53], "box_score": 0.7550884485244751}, "car:11": {"box": [948, 156, 272, 94], "box_score": 0.6654122471809387}, "car:4": {"box": [706, 179, 85, 69], "box_score": 0.9462259411811829}, "car:8": {"box": [676, 180, 45, 43], "box_score": 0.8605964779853821}}}, "0000000228.png": {"car": {"car:2": {"box": [542, 186, 137, 82], "box_score": 0.9766432642936707}, "car:10": {"box": [432, 179, 32, 34], "box_score": 0.6130275726318359}, "car:1": {"box": [1, 221, 116, 149], "box_score": 0.9823285937309265}, "car:9": {"box": [1169, 152, 48, 56], "box_score": 0.6785534620285034}, "car:4": {"box": [50, 205, 132, 94], "box_score": 0.9590693116188049}, "car:8": {"box": [1191, 157, 52, 83], "box_score": 0.7401116490364075}, "car:7": {"box": [444, 182, 56, 39], "box_score": 0.8639380931854248}, "car:5": {"box": [619, 167, 96, 41], "box_score": 0.9447060227394104}, "car:3": {"box": [746, 138, 486, 232], "box_score": 0.9745768904685974}, "car:6": {"box": [256, 182, 50, 33], "box_score": 0.9006390571594238}}}, "0000000341.png": {"truck": {"truck:1": {"box": [590, 146, 63, 45], "box_score": 0.7309602499008179}}, "car": {"car:2": {"box": [1, 207, 143, 156], "box_score": 0.992233395576477}, "car:1": {"box": [796, 183, 314, 175], "box_score": 0.9955229759216309}, "car:4": {"box": [470, 175, 54, 29], "box_score": 0.9365281462669373}, "car:5": {"box": [366, 175, 49, 27], "box_score": 0.7882540822029114}, "car:3": {"box": [126, 181, 197, 124], "box_score": 0.9670609831809998}, "car:6": {"box": [681, 170, 47, 20], "box_score": 0.6918953061103821}}}, "0000000237.png": {"car": {"car:2": {"box": [0, 218, 259, 155], "box_score": 0.9803617000579834}, "car:1": {"box": [774, 205, 305, 158], "box_score": 0.9881883263587952}, "car:4": {"box": [864, 169, 122, 48], "box_score": 0.8817922472953796}, "car:5": {"box": [437, 187, 47, 33], "box_score": 0.8522816896438599}, "car:3": {"box": [625, 185, 65, 50], "box_score": 0.9062297344207764}, "car:6": {"box": [790, 175, 85, 31], "box_score": 0.7339741587638855}}}, "0000000008.png": {"car": {"car:2": {"box": [242, 198, 143, 88], "box_score": 0.9478534460067749}, "car:7": {"box": [588, 176, 40, 20], "box_score": 0.6666243076324463}, "car:1": {"box": [754, 177, 150, 118], "box_score": 0.9895291924476624}, "car:4": {"box": [469, 187, 42, 30], "box_score": 0.8327281475067139}, "car:5": {"box": [642, 174, 40, 27], "box_score": 0.772642195224762}, "car:3": {"box": [883, 189, 374, 183], "box_score": 0.9408341646194458}, "car:6": {"box": [238, 197, 53, 28], "box_score": 0.7172660827636719}}}, "0000000308.png": {"car": {"car:2": {"box": [853, 193, 374, 174], "box_score": 0.9897657036781311}, "car:7": {"box": [457, 188, 52, 44], "box_score": 0.80108642578125}, "car:1": {"box": [233, 196, 179, 99], "box_score": 0.9922560453414917}, "car:9": {"box": [698, 178, 38, 44], "box_score": 0.7390971779823303}, "car:4": {"box": [722, 183, 65, 62], "box_score": 0.9289559721946716}, "car:8": {"box": [520, 180, 44, 28], "box_score": 0.7611994743347168}, "car:5": {"box": [386, 188, 91, 64], "box_score": 0.8761155009269714}, "car:3": {"box": [762, 185, 138, 91], "box_score": 0.9794986844062805}, "car:6": {"box": [710, 179, 47, 48], "box_score": 0.8194370269775391}}}, "0000000289.png": {"truck": {"truck:1": {"box": [811, 162, 252, 160], "box_score": 0.7053809762001038}}, "car": {"car:2": {"box": [-2, 209, 236, 162], "box_score": 0.9503011107444763}, "car:1": {"box": [502, 180, 54, 35], "box_score": 0.985592782497406}, "car:3": {"box": [749, 185, 78, 65], "box_score": 0.8864814043045044}, "car:4": {"box": [726, 177, 63, 57], "box_score": 0.7218843698501587}}}, "0000000002.png": {"car": {"car:2": {"box": [365, 194, 84, 58], "box_score": 0.9839418530464172}, "car:5": {"box": [893, 204, 376, 164], "box_score": 0.8931097984313965}, "car:1": {"box": [701, 184, 68, 61], "box_score": 0.9891161322593689}, "car:3": {"box": [749, 182, 156, 112], "box_score": 0.9703866243362427}, "car:4": {"box": [491, 188, 38, 25], "box_score": 0.9313976764678955}}}, "0000000109.png": {"car": {"car:2": {"box": [262, 195, 154, 76], "box_score": 0.9862660765647888}, "car:10": {"box": [566, 176, 40, 20], "box_score": 0.8293913006782532}, "car:1": {"box": [4, 206, 261, 159], "box_score": 0.9903281331062317}, "car:11": {"box": [647, 179, 35, 31], "box_score": 0.6995550394058228}, "car:4": {"box": [462, 185, 51, 38], "box_score": 0.9475462436676025}, "car:9": {"box": [508, 180, 34, 27], "box_score": 0.8553003668785095}, "car:8": {"box": [679, 182, 50, 44], "box_score": 0.8588221669197083}, "car:7": {"box": [713, 179, 96, 78], "box_score": 0.8976340889930725}, "car:5": {"box": [982, 158, 207, 85], "box_score": 0.9342359304428101}, "car:3": {"box": [766, 185, 205, 122], "box_score": 0.9788001775741577}, "car:6": {"box": [397, 188, 67, 54], "box_score": 0.9256226420402527}}}, "0000000171.png": {"car": {"car:2": {"box": [1049, 159, 192, 60], "box_score": 0.9735903143882751}, "car:1": {"box": [883, 170, 148, 59], "box_score": 0.9972701668739319}, "car:3": {"box": [190, 191, 75, 38], "box_score": 0.8415442109107971}, "car:4": {"box": [4, 187, 187, 85], "box_score": 0.713742733001709}}}, "0000000040.png": {"car": {"car:2": {"box": [1, 210, 256, 156], "box_score": 0.9532991051673889}, "car:7": {"box": [396, 184, 59, 49], "box_score": 0.843645453453064}, "car:1": {"box": [799, 184, 392, 182], "box_score": 0.9814141392707825}, "car:9": {"box": [998, 158, 97, 26], "box_score": 0.6565350890159607}, "car:4": {"box": [533, 178, 36, 27], "box_score": 0.9115864634513855}, "car:8": {"box": [627, 175, 35, 21], "box_score": 0.7007920145988464}, "car:5": {"box": [281, 178, 130, 86], "box_score": 0.8721565008163452}, "car:3": {"box": [691, 165, 78, 27], "box_score": 0.9488703608512878}, "car:6": {"box": [502, 178, 34, 27], "box_score": 0.8651111125946045}}}, "0000000186.png": {"bicycle": {"bicycle:1": {"box": [874, 193, 72, 45], "box_score": 0.9734592437744141}}, "car": {"car:2": {"box": [120, 184, 94, 49], "box_score": 0.838171124458313}, "car:1": {"box": [1024, 175, 216, 77], "box_score": 0.9593486785888672}, "car:3": {"box": [-1, 182, 75, 100], "box_score": 0.7142969369888306}}}, "0000000146.png": {"car": {"car:2": {"box": [802, 186, 377, 184], "box_score": 0.983799934387207}, "car:5": {"box": [337, 176, 82, 40], "box_score": 0.7877405881881714}, "car:1": {"box": [0, 207, 193, 163], "box_score": 0.9939504861831665}, "car:3": {"box": [737, 184, 128, 96], "box_score": 0.9778087735176086}, "car:4": {"box": [187, 193, 153, 100], "box_score": 0.957180380821228}}}, "0000000362.png": {"truck": {"truck:1": {"box": [247, 157, 94, 56], "box_score": 0.6706559658050537}}, "car": {"car:2": {"box": [626, 177, 88, 30], "box_score": 0.9759348630905151}, "car:5": {"box": [173, 185, 91, 33], "box_score": 0.7471404075622559}, "car:1": {"box": [343, 188, 89, 69], "box_score": 0.9918455481529236}, "car:3": {"box": [2, 208, 322, 163], "box_score": 0.9568554162979126}, "car:4": {"box": [490, 180, 86, 32], "box_score": 0.924518346786499}}, "person": {"person:1": {"box": [807, 175, 30, 70], "box_score": 0.697240948677063}}}, "0000000344.png": {"truck": {"truck:1": {"box": [543, 148, 71, 51], "box_score": 0.7345405220985413}}, "car": {"car:2": {"box": [339, 183, 73, 27], "box_score": 0.9748533368110657}, "car:5": {"box": [647, 174, 66, 23], "box_score": 0.6382225751876831}, "car:1": {"box": [464, 180, 52, 33], "box_score": 0.9872875213623047}, "car:3": {"box": [1, 195, 232, 167], "box_score": 0.966151237487793}, "car:4": {"box": [858, 192, 408, 174], "box_score": 0.9561615586280823}}}, "0000000207.png": {"car": {"car:2": {"box": [369, 186, 83, 46], "box_score": 0.943828284740448}, "car:1": {"box": [42, 175, 261, 118], "box_score": 0.9667302966117859}, "car:3": {"box": [298, 186, 63, 41], "box_score": 0.8049578070640564}, "car:4": {"box": [1020, 183, 75, 32], "box_score": 0.6152008175849915}}}, "0000000347.png": {"truck": {"truck:1": {"box": [494, 159, 96, 47], "box_score": 0.6491647362709045}}, "car": {"car:2": {"box": [0, 208, 89, 158], "box_score": 0.9546614289283752}, "car:1": {"box": [455, 182, 50, 38], "box_score": 0.9831669926643372}, "car:4": {"box": [638, 176, 57, 23], "box_score": 0.8845657706260681}, "car:5": {"box": [61, 184, 90, 55], "box_score": 0.8569512367248535}, "car:3": {"box": [342, 183, 78, 31], "box_score": 0.9384704232215881}, "car:6": {"box": [0, 186, 82, 50], "box_score": 0.7623516917228699}}}, "0000000354.png": {"car": {"car:2": {"box": [626, 174, 75, 26], "box_score": 0.9549858570098877}, "car:1": {"box": [385, 186, 83, 58], "box_score": 0.9725471138954163}, "car:3": {"box": [508, 174, 72, 29], "box_score": 0.7337833046913147}, "car:4": {"box": [349, 179, 65, 40], "box_score": 0.707528293132782}}, "person": {"person:1": {"box": [725, 169, 19, 53], "box_score": 0.6682517528533936}}}, "0000000423.png": {"car": {"car:1": {"box": [1, 219, 215, 152], "box_score": 0.9907005429267883}}, "traffic light": {"traffic light:2": {"box": [349, 13, 40, 98], "box_score": 0.6803398728370667}, "traffic light:3": {"box": [404, 49, 33, 59], "box_score": 0.6277970671653748}, "traffic light:1": {"box": [1047, 28, 32, 78], "box_score": 0.8321627378463745}}}, "0000000065.png": {"car": {"car:2": {"box": [2, 212, 322, 162], "box_score": 0.9837204217910767}, "car:7": {"box": [433, 186, 50, 42], "box_score": 0.6657336354255676}, "car:1": {"box": [310, 194, 142, 104], "box_score": 0.9867472648620605}, "car:4": {"box": [484, 185, 33, 26], "box_score": 0.8185862302780151}, "car:5": {"box": [748, 166, 82, 43], "box_score": 0.7978307604789734}, "car:3": {"box": [811, 162, 183, 63], "box_score": 0.9755208492279053}, "car:6": {"box": [945, 157, 70, 31], "box_score": 0.6712794899940491}}}, "0000000437.png": {"traffic light": {"traffic light:2": {"box": [349, 10, 39, 103], "box_score": 0.6806934475898743}, "traffic light:3": {"box": [399, 47, 38, 63], "box_score": 0.6038501858711243}, "traffic light:1": {"box": [1047, 28, 32, 77], "box_score": 0.7723974585533142}}}, "0000000303.png": {"car": {"car:2": {"box": [858, 182, 337, 184], "box_score": 0.9757345914840698}, "car:7": {"box": [710, 181, 44, 47], "box_score": 0.835680365562439}, "car:1": {"box": [365, 186, 110, 70], "box_score": 0.9960902333259583}, "car:9": {"box": [697, 179, 32, 42], "box_score": 0.6872503161430359}, "car:4": {"box": [734, 184, 71, 61], "box_score": 0.942773699760437}, "car:8": {"box": [502, 185, 31, 35], "box_score": 0.7152519822120667}, "car:5": {"box": [538, 180, 39, 23], "box_score": 0.9066241383552551}, "car:3": {"box": [774, 188, 139, 89], "box_score": 0.9475584626197815}, "car:6": {"box": [455, 184, 59, 48], "box_score": 0.9029967784881592}}}, "0000000358.png": {"truck": {"truck:1": {"box": [304, 154, 99, 54], "box_score": 0.8410404324531555}}, "car": {"car:2": {"box": [140, 186, 92, 37], "box_score": 0.955161988735199}, "car:5": {"box": [400, 188, 39, 45], "box_score": 0.702966570854187}, "car:1": {"box": [282, 188, 146, 99], "box_score": 0.9774787425994873}, "car:3": {"box": [622, 176, 82, 28], "box_score": 0.9502100348472595}, "car:4": {"box": [494, 176, 85, 31], "box_score": 0.8906225562095642}}}, "0000000280.png": {"car": {"car:2": {"box": [0, 198, 235, 175], "box_score": 0.9336113333702087}, "car:1": {"box": [212, 207, 169, 124], "box_score": 0.9532944560050964}, "car:4": {"box": [542, 182, 41, 29], "box_score": 0.9123556017875671}, "car:5": {"box": [715, 183, 31, 43], "box_score": 0.7496926784515381}, "car:3": {"box": [354, 193, 106, 80], "box_score": 0.9330620765686035}, "car:6": {"box": [733, 177, 97, 72], "box_score": 0.6164487600326538}}}, "0000000375.png": {"traffic light": {"traffic light:1": {"box": [907, 80, 24, 51], "box_score": 0.7799198627471924}}, "car": {"car:2": {"box": [441, 175, 142, 57], "box_score": 0.8024097084999084}, "car:1": {"box": [633, 176, 102, 36], "box_score": 0.9303010106086731}, "car:3": {"box": [0, 157, 58, 63], "box_score": 0.7396066188812256}}, "person": {"person:1": {"box": [1180, 172, 66, 186], "box_score": 0.6871007084846497}}}, "0000000288.png": {"truck": {"truck:1": {"box": [791, 158, 219, 145], "box_score": 0.6351765990257263}}, "car": {"car:2": {"box": [744, 184, 70, 59], "box_score": 0.9345678091049194}, "car:1": {"box": [508, 177, 56, 35], "box_score": 0.9553018808364868}, "car:3": {"box": [-1, 201, 282, 172], "box_score": 0.8810140490531921}, "car:4": {"box": [728, 176, 59, 57], "box_score": 0.7778781652450562}}}, "0000000446.png": {"traffic light": {"traffic light:2": {"box": [347, 9, 41, 103], "box_score": 0.7046733498573303}, "traffic light:1": {"box": [1047, 28, 32, 79], "box_score": 0.7592803239822388}}}, "0000000014.png": {"car": {"car:2": {"box": [927, 201, 315, 170], "box_score": 0.9894792437553406}, "car:7": {"box": [497, 179, 35, 30], "box_score": 0.6929203867912292}, "car:1": {"box": [1, 216, 233, 154], "box_score": 0.9937586784362793}, "car:9": {"box": [87, 203, 60, 18], "box_score": 0.6347618103027344}, "car:4": {"box": [231, 198, 53, 29], "box_score": 0.8909830451011658}, "car:8": {"box": [478, 187, 32, 30], "box_score": 0.6361638307571411}, "car:5": {"box": [164, 199, 71, 28], "box_score": 0.8355186581611633}, "car:3": {"box": [613, 175, 45, 22], "box_score": 0.8968015313148499}, "car:6": {"box": [441, 189, 51, 38], "box_score": 0.8302094340324402}}}, "0000000208.png": {"car": {"car:2": {"box": [396, 186, 81, 46], "box_score": 0.9419499635696411}, "car:1": {"box": [72, 175, 250, 116], "box_score": 0.9592326879501343}, "car:3": {"box": [324, 184, 67, 41], "box_score": 0.8479225635528564}, "car:4": {"box": [0, 195, 39, 76], "box_score": 0.8215895891189575}}}, "0000000004.png": {"car": {"car:2": {"box": [713, 179, 87, 75], "box_score": 0.9759979844093323}, "car:5": {"box": [320, 192, 38, 25], "box_score": 0.67329341173172}, "car:1": {"box": [767, 182, 238, 144], "box_score": 0.996548593044281}, "car:3": {"box": [331, 193, 99, 65], "box_score": 0.9725985527038574}, "car:4": {"box": [486, 184, 37, 26], "box_score": 0.9091295003890991}}}, "0000000309.png": {"car": {"car:2": {"box": [777, 188, 152, 93], "box_score": 0.9721404910087585}, "car:7": {"box": [703, 179, 45, 49], "box_score": 0.8298583030700684}, "car:1": {"box": [188, 196, 208, 115], "box_score": 0.9897704124450684}, "car:9": {"box": [720, 181, 53, 54], "box_score": 0.6525911092758179}, "car:4": {"box": [731, 184, 73, 64], "box_score": 0.9284899830818176}, "car:8": {"box": [515, 180, 46, 29], "box_score": 0.8290570378303528}, "car:5": {"box": [369, 190, 97, 65], "box_score": 0.9147428274154663}, "car:3": {"box": [886, 196, 374, 176], "box_score": 0.9712730050086975}, "car:6": {"box": [449, 189, 53, 46], "box_score": 0.8765226006507874}}}, "0000000306.png": {"car": {"car:2": {"box": [297, 192, 147, 85], "box_score": 0.9910237789154053}, "car:7": {"box": [526, 180, 44, 27], "box_score": 0.7852158546447754}, "car:1": {"box": [811, 190, 234, 135], "box_score": 0.9921411275863647}, "car:4": {"box": [977, 195, 260, 176], "box_score": 0.9726088047027588}, "car:8": {"box": [696, 180, 29, 42], "box_score": 0.6428775191307068}, "car:5": {"box": [716, 181, 54, 54], "box_score": 0.8416562676429749}, "car:3": {"box": [745, 185, 109, 75], "box_score": 0.9773579835891724}, "car:6": {"box": [423, 188, 73, 54], "box_score": 0.8302068114280701}}}, "0000000220.png": {"car": {"car:2": {"box": [392, 179, 81, 37], "box_score": 0.9442669749259949}, "car:7": {"box": [136, 185, 34, 23], "box_score": 0.6406489014625549}, "car:1": {"box": [316, 195, 121, 68], "box_score": 0.976426362991333}, "car:4": {"box": [702, 178, 67, 46], "box_score": 0.8598580956459045}, "car:5": {"box": [187, 192, 67, 38], "box_score": 0.8138926029205322}, "car:3": {"box": [453, 165, 254, 144], "box_score": 0.921421229839325}, "car:6": {"box": [785, 178, 102, 56], "box_score": 0.8009197115898132}}}, "0000000209.png": {"car": {"car:2": {"box": [420, 184, 82, 47], "box_score": 0.9408003687858582}, "car:5": {"box": [2, 191, 75, 51], "box_score": 0.7011060118675232}, "car:1": {"box": [103, 176, 247, 115], "box_score": 0.9720078706741333}, "car:3": {"box": [0, 206, 66, 63], "box_score": 0.8860876560211182}, "car:4": {"box": [350, 185, 59, 38], "box_score": 0.8234326243400574}}}, "0000000406.png": {"car": {"car:1": {"box": [0, 214, 162, 156], "box_score": 0.9904916882514954}}, "traffic light": {"traffic light:2": {"box": [348, 10, 41, 101], "box_score": 0.7771068215370178}, "traffic light:3": {"box": [407, 48, 31, 57], "box_score": 0.7168889045715332}, "traffic light:1": {"box": [1047, 26, 32, 79], "box_score": 0.8707415461540222}}}, "0000000364.png": {"car": {"car:2": {"box": [1, 244, 166, 126], "box_score": 0.9781226515769958}, "car:5": {"box": [488, 177, 94, 34], "box_score": 0.7434577941894531}, "car:1": {"box": [320, 190, 101, 79], "box_score": 0.9924914240837097}, "car:3": {"box": [631, 176, 88, 30], "box_score": 0.9741186499595642}, "car:4": {"box": [193, 181, 133, 47], "box_score": 0.9614098072052002}}, "person": {"person:1": {"box": [837, 171, 32, 87], "box_score": 0.9551299214363098}}}, "0000000119.png": {"car": {"car:2": {"box": [96, 195, 225, 124], "box_score": 0.9815722703933716}, "car:7": {"box": [361, 183, 98, 61], "box_score": 0.8791567087173462}, "car:1": {"box": [0, 228, 108, 147], "box_score": 0.9866344928741455}, "car:9": {"box": [119, 187, 71, 34], "box_score": 0.7454417943954468}, "car:4": {"box": [883, 182, 369, 185], "box_score": 0.9601657390594482}, "car:8": {"box": [658, 174, 52, 39], "box_score": 0.8044224977493286}, "car:5": {"box": [689, 179, 69, 55], "box_score": 0.9231739044189453}, "car:3": {"box": [726, 180, 126, 81], "box_score": 0.9670994281768799}, "car:6": {"box": [472, 175, 56, 34], "box_score": 0.8899617791175842}}}, "0000000062.png": {"car": {"car:2": {"box": [391, 189, 96, 70], "box_score": 0.9559258818626404}, "car:7": {"box": [1016, 138, 77, 38], "box_score": 0.6652944087982178}, "car:1": {"box": [159, 195, 263, 145], "box_score": 0.9806751608848572}, "car:9": {"box": [490, 182, 32, 23], "box_score": 0.6557080149650574}, "car:4": {"box": [731, 163, 71, 42], "box_score": 0.8208099007606506}, "car:8": {"box": [774, 158, 65, 52], "box_score": 0.6625556945800781}, "car:5": {"box": [647, 178, 52, 39], "box_score": 0.7847456336021423}, "car:3": {"box": [-1, 211, 228, 142], "box_score": 0.9440116286277771}, "car:6": {"box": [790, 157, 139, 54], "box_score": 0.7418822050094604}}}, "0000000182.png": {"bicycle": {"bicycle:1": {"box": [835, 192, 67, 41], "box_score": 0.9102532267570496}}, "car": {"car:2": {"box": [965, 173, 198, 72], "box_score": 0.9838982224464417}, "car:1": {"box": [1172, 181, 73, 57], "box_score": 0.9839717149734497}, "car:3": {"box": [-1, 186, 77, 98], "box_score": 0.8108798265457153}, "car:4": {"box": [106, 187, 98, 48], "box_score": 0.6990378499031067}}}, "0000000060.png": {"car": {"car:2": {"box": [60, 209, 230, 104], "box_score": 0.9622044563293457}, "car:1": {"box": [281, 195, 177, 102], "box_score": 0.9813060164451599}, "car:4": {"box": [639, 179, 54, 37], "box_score": 0.8476829528808594}, "car:5": {"box": [776, 161, 122, 48], "box_score": 0.7933500409126282}, "car:3": {"box": [429, 188, 74, 56], "box_score": 0.9595460891723633}, "car:6": {"box": [720, 165, 63, 38], "box_score": 0.7671739459037781}}}, "0000000053.png": {"car": {"car:2": {"box": [0, 200, 223, 166], "box_score": 0.9713107943534851}, "car:1": {"box": [438, 185, 77, 54], "box_score": 0.9787763953208923}, "car:4": {"box": [722, 163, 98, 39], "box_score": 0.9486553072929382}, "car:5": {"box": [498, 184, 38, 34], "box_score": 0.8761308193206787}, "car:3": {"box": [312, 194, 94, 57], "box_score": 0.9614003300666809}, "car:6": {"box": [627, 178, 40, 28], "box_score": 0.7250189781188965}}}, "0000000181.png": {"bicycle": {"bicycle:1": {"box": [826, 193, 66, 40], "box_score": 0.9549676775932312}}, "car": {"car:2": {"box": [1156, 173, 89, 64], "box_score": 0.9815913438796997}, "car:1": {"box": [952, 172, 195, 71], "box_score": 0.9829534292221069}, "car:3": {"box": [109, 191, 94, 45], "box_score": 0.8799864649772644}, "car:4": {"box": [0, 189, 84, 93], "box_score": 0.8645619750022888}}}, "0000000003.png": {"car": {"car:2": {"box": [348, 194, 96, 61], "box_score": 0.9847407937049866}, "car:5": {"box": [488, 186, 38, 24], "box_score": 0.9111561179161072}, "car:1": {"box": [759, 181, 195, 123], "box_score": 0.9877864122390747}, "car:3": {"box": [905, 206, 333, 166], "box_score": 0.974290132522583}, "car:4": {"box": [707, 181, 76, 69], "box_score": 0.966191291809082}}}}
        #pred_labels = "Files/documents/predicted_BB.json"

    else: #polygon is enabled
        #get list of images uploaded on the bucket of GCS
        image_list = get_bucket_of_images(private_key_location, bucket_name, image_folder)

        for f in image_list:
            if(f.endswith(".jpg") or f.endswith(".png")):
                all_files.append(f.encode("utf8"))
        all_files.sort(key=natural_keys)

    slice_of_masks = []
    slice_of_masks.insert(0, starting_mask_file)
    """if(instance_mask_path != ""):
        for ins in glob.glob(instance_mask_path + "/*.json"):
            all_mask.append(basename(ins))

        all_mask.sort(key=natural_keys)
        starting_mask_index = all_mask.index(starting_mask_file)
        slice_of_masks = all_mask[starting_mask_index: starting_mask_index + count]

    slice_of_files = []
    if(len(all_files) > 0):
        starting_file_index = all_files.index(starting_img)
        slice_of_files = all_files[starting_file_index: starting_file_index + count]"""
    slice_of_files = []
    return slice_of_files, slice_of_masks

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]