from rest_framework.decorators import api_view, authentication_classes, parser_classes
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
import os
import zipfile
import shutil
from app.google_cloud import storage

from app.model.client import ClientModel
import traceback
import sys
import json
from app.auth.jwt_token import JwtTokenAuthentication
from app.model.file import FileModel
from app.model.user import is_super_admin, user_access_level
import os


@api_view(['GET', 'POST', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def client(request, client_id=None):
    try:
        if request.method == 'OPTIONS':
            return Response(status=status.HTTP_200_OK)
        elif request.method == 'POST':
            if not is_super_admin(request.user):
                return Response(status=status.HTTP_403_FORBIDDEN)

            if client_id is None:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                    data="client id cannot be empty")
            ClientModel.objects(client_id=client_id).update_one(upsert=True, **request.data)
            return Response()
        elif request.method == 'DELETE':
            if not is_super_admin(request.user):
                return Response(status=status.HTTP_403_FORBIDDEN)
            ClientModel.objects(client_id=client_id).delete()
            return Response()
        elif request.method == 'GET':
            if client_id is None:
                all_clients = ClientModel.objects()
                return Response(
                    dict([(client["client_id"], json.loads(client.to_json())) for client in all_clients
                        if user_access_level(request.user, client["client_id"]) is not None ]))
            else:
                if user_access_level(request.user, client_id) is None:
                    return Response(status=status.HTTP_403_FORBIDDEN)
                client_data = ClientModel.objects(client_id=client_id)
                if len(client_data) == 0:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(data=json.loads(client_data[0].to_json()))
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def project(request, client_id, project_id=None):
    try:
        if request.method == 'OPTIONS':
            return Response(status=status.HTTP_200_OK)
        elif request.method == 'POST':
            if user_access_level(request.user, client_id) != "edit":
                return Response(status=status.HTTP_403_FORBIDDEN)
            if project_id is None:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                    data="project_id cannot be empty")
            ClientModel.objects(client_id=client_id).update_one(
                upsert=True,
                **{
                    "set__projects__{}".format(
                        project_id): request.data
                })
            return Response()
        if request.method == 'DELETE':
            if user_access_level(request.user, client_id) != "edit":
                return Response(status=status.HTTP_403_FORBIDDEN)
            if project_id is None:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                    data="project_id cannot be empty")
            ClientModel.objects(client_id=client_id).update_one(
                upsert=True,
                **{
                    "unset__projects__{}".format(
                        project_id): "true"
                })
            return Response()
        elif request.method == 'GET':
            if user_access_level(request.user, client_id) is None:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if project_id is None:
                client_data = ClientModel.objects(client_id=client_id)

                if len(client_data) == 0:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(data=json.loads(client_data[0].to_json()).get("projects", {}))
            else:
                client_data = ClientModel.objects.filter(
                    client_id=client_id,
                    **{
                        "projects__{}__exists".format(project_id): "true"
                    })

                if len(client_data) == 0:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(json.loads(client_data[0]["projects"][project_id].to_json()))
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def dataset(request, client_id=None, project_id=None, dataset_id=None, file_size=None):
    try:
        if request.method == 'OPTIONS':
            return Response()
        elif request.method == 'POST':
            if user_access_level(request.user, client_id) != "edit":
                return Response(status=status.HTTP_403_FORBIDDEN)
            if dataset_id is None:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                    data="dataset_id cannot be empty")

            json_data =json.loads(request.body)
            origin = json_data['origin']
            dataset_data = json.loads(request.body)
            gcs_upload_bucket = "deepenai-rannotateclientdata"
            gcs_files_bucket = "deepenai-rannotateservingdata"
            gcs_upload_zip_path = "{}/{}/{}/data.zip".format(client_id, project_id, dataset_id)
            gcs_post_url = "https://www.googleapis.com/upload/storage/v1/b/{}/o?" \
                            "uploadType=resumable&name={}".format(gcs_upload_bucket, gcs_upload_zip_path)
            dataset_data["gcs_bucket"] = gcs_files_bucket
            dataset_data["gcs_files_root_path"] = "{}/{}/{}".format(client_id, project_id,
                dataset_id)

            ClientModel.objects(client_id=client_id).update_one(
                upsert=True,
                **{
                    "set__projects__{}__datasets__{}".format(
                        project_id, dataset_id): dataset_data,
                })

            return Response({"resumable_upload_url": storage.get_resumable_upload_url(
                gcs_post_url, file_size, origin)})
        elif request.method == 'DELETE':
            if user_access_level(request.user, client_id) != "edit":
                return Response(status=status.HTTP_403_FORBIDDEN)
            if dataset_id is None:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                    data="dataset_id cannot be empty")
            ClientModel.objects(client_id=client_id).update_one(
                upsert=True,
                **{
                    "unset__projects__{}__datasets__{}".format(
                        project_id, dataset_id): "true"
                })
            return Response()
        elif request.method == 'GET':
            if user_access_level(request.user, client_id) is None:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if client_id is None:
                clients = ClientModel.objects().all()

                if len(clients) == 0:
                    return Response({})
                datasets = {}
                for client in clients:
                    client_data = json.loads(client.to_json())
                    if client_data.get("projects") is None:
                        continue
                    client_id = client_data["_id"]
                    for project_id in client_data.get("projects").keys():
                        if client_data["projects"][project_id].get("datasets") is None:
                            continue
                        for dataset_id in client_data["projects"][project_id]["datasets"].keys():
                            if datasets.get(client_id) is None:
                                datasets[client_id] = {}
                            if datasets[client_id].get(project_id) is None:
                                datasets[client_id][project_id] = {}
                            datasets[client_id][project_id][dataset_id] = client_data["projects"][
                                project_id]["datasets"][dataset_id]
                return Response(datasets)
            elif client_id is not None and project_id is None:
                client_data = ClientModel.objects(client_id=client_id)

                if len(client_data) == 0:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                client_data = json.loads(client_data[0].to_json())
                if client_data.get("projects") is None:
                    return Response({})
                datasets = {}
                for project_id in client_data.get("projects").keys():
                    if client_data["projects"][project_id].get("datasets") is None:
                        continue
                    for dataset_id in client_data["projects"][project_id]["datasets"].keys():
                        if datasets.get(project_id) is None:
                            datasets[project_id] = {}
                        datasets[project_id][dataset_id] = client_data["projects"][
                            project_id]["datasets"][dataset_id]
                return Response(datasets)
            elif client_id is not None and project_id is not None and dataset_id is None:
                client_data = ClientModel.objects(
                    client_id=client_id)

                if len(client_data) == 0:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                client_data = json.loads(client_data[0].to_json())
                if client_data.get("projects") is None or\
                                client_data["projects"].get(project_id) is None or\
                                client_data["projects"][project_id].get("datasets") is None:
                    return Response({})
                return Response(client_data["projects"][project_id]["datasets"])
            elif client_id is not None and project_id is not None and dataset_id is not None:
                client_data = ClientModel.objects(
                    client_id=client_id,
                    **{
                        "projects__{}__datasets__{}__exists".format(project_id, dataset_id): "true"
                    })

                if len(client_data) == 0:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(json.loads(
                        client_data[0]["projects"][project_id]["datasets"][dataset_id].to_json()))
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', 'OPTIONS'])
@parser_classes([FileUploadParser])
@authentication_classes([JwtTokenAuthentication])
def upload_dataset(request, client_id, project_id, dataset_id):
    #user = authenticate_request(request)
    #if user is None:
    #    return HttpResponseForbidden("Unauthorized user")
    try:
        if request.method == 'OPTIONS':
            return Response()
        elif request.method == 'POST':
            if user_access_level(request.user, client_id) != "edit":
                return Response(status=status.HTTP_403_FORBIDDEN)
            temp_directory = "deependata-{}-{}-{}".format(client_id, project_id, dataset_id)
            if os.path.exists(temp_directory):
                shutil.rmtree(temp_directory)
            os.makedirs(temp_directory)
            with zipfile.ZipFile(request.FILES['file'], "r") as zip_ref:
                zip_ref.extractall(temp_directory)
            gcs_bucket, gcs_files_root_path = storage.upload_directory(
                client_id, project_id, dataset_id, temp_directory)
            shutil.rmtree(temp_directory)

            set_prefix = "set__projects__{}__datasets__{}".format(
                        project_id, dataset_id)

            ClientModel.objects(client_id=client_id).update_one(
                upsert=True,
                **{
                    "{}__gcs_bucket".format(set_prefix): gcs_bucket,
                    "{}__gcs_files_root_path".format(set_prefix): gcs_files_root_path,
                })
            return Response()
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def boundingboxes(request, client_id, project_id, dataset_id, file_id):
    try:
        if request.method == 'OPTIONS':
            return Response()
        elif request.method == 'GET':
            if client_id is not None and project_id is not None and dataset_id is not None:
                client_data = ClientModel.objects(
                    client_id=client_id,
                    **{
                        "projects__{}__datasets__{}__exists".format(project_id, dataset_id): "true"
                    })
                gcs_bucket = client_data[0]["projects"][project_id]["datasets"][dataset_id]['gcs_bucket']
                gcs_file_root_path = client_data[0]["projects"][project_id]["datasets"][dataset_id]['gcs_files_root_path'] + "/" + file_id
                print str (gcs_bucket + gcs_file_root_path)

                return Response(storage.get_bounding_boxes(gcs_bucket, gcs_file_root_path))

    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)