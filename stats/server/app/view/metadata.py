from rest_framework.decorators import api_view, authentication_classes
from rest_framework import status
from rest_framework.response import Response

from app.model.client import ClientModel
from app.model.metadata import LabelCategoryMetadataModel
import traceback
import sys
import json
from app.auth.jwt_token import JwtTokenAuthentication
import temp_labels
from app.model.user import user_access_level


@api_view(['GET', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def features(request, client_id):
    if user_access_level(request.user, client_id) is None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        if request.method == 'OPTIONS':
            return Response()
        elif request.method == 'GET':
            client_data = ClientModel.objects(client_id=client_id)
            if len(client_data) == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(json.loads(client_data[0].to_json()).get("features", []))
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response()

@api_view(['GET', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def features_new(request, client_id):
    if user_access_level(request.user, client_id) is None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        if request.method == 'OPTIONS':
            return Response()
        elif request.method == 'GET':
            client_data = ClientModel.objects(client_id=client_id)
            if len(client_data) == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)
            a = json.loads(client_data[0].to_json())
            return Response(json.loads(client_data[0].to_json()).get("features_new", {}))
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response()

@api_view(['GET', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def label_categories(request, client_id):
    if user_access_level(request.user, client_id) is None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        if request.method == 'OPTIONS':
            return Response()
        elif request.method == 'GET':
            client_data = ClientModel.objects(client_id=client_id)
            if len(client_data) == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)
            label_category_ids = json.loads(client_data[0].to_json()).get("label_category_ids")
            label_categories = {}
            if label_category_ids is not None:
                for label_category_id in label_category_ids:
                    label_category_data = LabelCategoryMetadataModel.objects(
                            label_category_id=label_category_id)
                    if len(label_category_data) > 0:
                        label_category = json.loads(label_category_data[0].to_json())
                        label_categories[label_category_id] = label_category
            return Response(label_categories)
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response()
