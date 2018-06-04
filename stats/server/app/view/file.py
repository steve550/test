from rest_framework.decorators import api_view, authentication_classes
from rest_framework import status
from rest_framework.response import Response

from app.model.client import ClientModel
from app.model.file import FileModel, FeedbackModel
from app.model.label import LabelModel
import traceback
import sys
import json
from app.auth.jwt_token import JwtTokenAuthentication
from app.model.user import user_access_level


@api_view(['GET', 'POST', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def status(request,
        client_id, project_id, dataset_id,
        file_id):

    if file_id is not None:
        file_id = file_id.replace("_____", "/")
    if user_access_level(request.user, client_id) is None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        if request.method == 'OPTIONS':
            return Response(status=status.HTTP_200_OK)
        elif request.method == 'POST':
            FileModel.objects(client_id=client_id, project_id=project_id, dataset_id=dataset_id,
                file_id=file_id).update_one(upsert=True, status=request.data["status"])
            return Response()
        elif request.method == 'GET':
            file_data = FileModel.objects(client_id=client_id, project_id=project_id, dataset_id=dataset_id,
                file_id=file_id)
            if len(file_data) == 0:
                return Response({})
            return Response(json.loads(file_data[0].to_json()))
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def get_file_summary(request, client_id, project_id, dataset_id, file_id):

    if file_id is not None:
        file_id = file_id.replace("_____", "/")
    if user_access_level(request.user, client_id) is None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        if request.method == 'OPTIONS':
            return Response(status=status.HTTP_200_OK)
        elif request.method == 'GET':
            summary = {
                "client_id": client_id,
                "project_id": project_id,
                "dataset_id": dataset_id,
                "file_id": file_id
            }
            file_data = FileModel.objects(client_id=client_id, project_id=project_id, file_id=file_id)
            if len(file_data) == 0:
                return Response(status.HTTP_404_NOT_FOUND)
            elif file_data[0].get("status") is None:
                summary["status"] = "not_started"
            elif file_data[0].get("status") is not None:
                summary["status"] = file_data[0].get("status")

            return Response(summary)
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def feedback(request,
        client_id, project_id, dataset_id,
        file_id):

    if file_id is not None:
        file_id = file_id.replace("_____", "/")
    if user_access_level(request.user, client_id) is None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        if request.method == 'OPTIONS':
            return Response(status=status.HTTP_200_OK)
        elif request.method == 'POST':
            feedback_author = "Placeholder"
            feedback = FeedbackModel(author_name=feedback_author,
                author_email="placeholder@deepen.ai", text=request.data["text"])
            FileModel.objects(client_id=client_id, project_id=project_id, dataset_id=dataset_id,
                file_id=file_id).update(upsert=True, push__feedback=feedback)
            return Response()
        elif request.method == 'GET':
            file_data = FileModel.objects(client_id=client_id, project_id=project_id, dataset_id=dataset_id,
                file_id=file_id)
            if len(file_data) == 0:
                return Response({})
            return Response(json.loads(file_data[0].to_json()))
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def file_id(request,
        client_id, project_id, dataset_id):
    if user_access_level(request.user, client_id) is None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        if request.method == 'GET':
            from app.google_cloud import storage

            clients = ClientModel.objects(client_id=client_id,
                **{"projects__{}__datasets__{}__gcs_bucket__exists".format(project_id, dataset_id):"true"})
            if len(clients) == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)
            client_data = json.loads(clients[0].to_json())

            gcs_bucket = client_data["projects"][project_id]["datasets"][dataset_id]["gcs_bucket"]
            gcs_files_root_path = client_data["projects"][project_id][
                "datasets"][dataset_id]["gcs_files_root_path"]

            all_files = storage.get_files(gcs_bucket=gcs_bucket,
                gcs_files_root_path=gcs_files_root_path)
            return Response(all_files)
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

