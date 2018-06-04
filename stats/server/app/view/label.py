from rest_framework.decorators import api_view, authentication_classes
from rest_framework import status
from rest_framework.response import Response

from app.model.label import LabelModel
import traceback
import sys
import json
from app.auth.jwt_token import JwtTokenAuthentication
from app.model.user import user_access_level


@api_view(['GET', 'POST', 'OPTIONS'])
@authentication_classes([JwtTokenAuthentication])
def label(request,
          client_id, project_id, dataset_id,
          file_id=None, label_type=None,
          label_category_id=None, label_id=None):
    if file_id is not None:
        file_id = file_id.replace("_____", "/")
    if user_access_level(request.user, client_id) is None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        if request.method == 'OPTIONS':
            return Response(status=status.HTTP_200_OK)
        elif request.method == 'POST':
            if label_type is None:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                    data="Label type cannot be empty")
            elif label_category_id is None:
                for label_category_id in request.data.keys():
                    for label_id in request.data[label_category_id].keys():
                        LabelModel.objects(
                            client_id=client_id,
                            project_id=project_id,
                            dataset_id=dataset_id,
                            file_id=file_id,
                            label_type=label_type,
                            label_category_id=label_category_id,
                            label_id=label_id).update_one(upsert=True,
                            **request.data[label_category_id][label_id])

                    if request.query_params.get("keeponly") != "true":
                        LabelModel.objects(
                            client_id=client_id,
                            project_id=project_id,
                            dataset_id=dataset_id,
                            file_id=file_id,
                            label_type=label_type,
                            label_category_id=label_category_id,
                            label_id__nin=request.data[label_category_id].keys()).delete()

                if request.query_params.get("keeponly") != "true":
                    LabelModel.objects(
                        client_id=client_id,
                        project_id=project_id,
                        dataset_id=dataset_id,
                        file_id=file_id,
                        label_type=label_type,
                        label_category_id__nin=request.data.keys()).delete()
            elif label_id is None:
                for label_id in request.data.keys():
                    LabelModel.objects(
                        client_id=client_id,
                        project_id=project_id,
                        dataset_id=dataset_id,
                        file_id=file_id,
                        label_type=label_type,
                        label_category_id=label_category_id,
                        label_id=label_id).update_one(upsert=True, **request.data[label_id])
                if request.query_params.get("keeponly") != "true":
                    LabelModel.objects(
                        client_id=client_id,
                        project_id=project_id,
                        dataset_id=dataset_id,
                        file_id=file_id,
                        label_type=label_type,
                        label_category_id=label_category_id,
                        label_id__nin=request.data.keys()).delete()

            else:
                LabelModel.objects(
                    client_id=client_id,
                    project_id=project_id,
                    dataset_id=dataset_id,
                    file_id=file_id,
                    label_type=label_type,
                    label_category_id=label_category_id,
                    label_id=label_id).update_one(upsert=True, **request.data)
            return Response()
        elif request.method == 'GET':
            if file_id is None:
                all_labels = LabelModel.objects(
                    client_id = client_id,
                    project_id = project_id,
                    dataset_id = dataset_id)
                labels_dict = {}
                for label in all_labels:
                    if labels_dict.get(label["file_id"]) is None:
                        labels_dict[label["file_id"]] = {}
                    if labels_dict[label["file_id"]].get(label["label_type"]) is None:
                        labels_dict[label["file_id"]][label["label_type"]] = {}
                    if labels_dict[label["file_id"]][label["label_type"]].get(label["label_category_id"]) is None:
                        labels_dict[label["file_id"]][label["label_type"]][label["label_category_id"]] = {}
                    labels_dict[label["file_id"]][label["label_type"]][label["label_category_id"]][label_id] =\
                        json.loads(label.to_json())
                return Response(data=labels_dict)
            elif label_type is None:
                all_labels = LabelModel.objects(
                    client_id = client_id,
                    project_id = project_id,
                    dataset_id = dataset_id,
                    file_id = file_id,
                )
                labels_dict = {}
                for label in all_labels:
                    if labels_dict.get(label["label_type"]) is None:
                        labels_dict[label["label_type"]] = {}
                    if labels_dict[label["label_type"]].get(label["label_category_id"]) is None:
                        labels_dict[label["label_type"]][label["label_category_id"]] = {}
                    labels_dict[label["label_type"]][label["label_category_id"]][label["label_id"]] =\
                        json.loads(label.to_json())
                return Response(data=labels_dict)
            elif label_category_id is None:
                all_labels = LabelModel.objects(
                    client_id = client_id,
                    project_id = project_id,
                    dataset_id = dataset_id,
                    file_id = file_id,
                    label_type = label_type
                )
                labels_dict = {}
                for label in all_labels:
                    if labels_dict.get(label["label_category_id"]) is None:
                        labels_dict[label["label_category_id"]] = {}
                    labels_dict[label["label_category_id"]][label["label_id"]] = json.loads(label.to_json())
                return Response(data=labels_dict)
            elif label_id is None:
                all_labels = LabelModel.objects(
                    client_id = client_id,
                    project_id = project_id,
                    dataset_id = dataset_id,
                    file_id = file_id,
                    label_type = label_type,
                    label_category_id = label_category_id
                )
                labels_dict = {}
                for label in all_labels:
                    labels_dict[label["label_id"]] = json.loads(label.to_json())

                return Response(data=labels_dict)
            else:
                all_labels = LabelModel.objects(
                    client_id = client_id,
                    project_id = project_id,
                    dataset_id = dataset_id,
                    file_id = file_id,
                    label_type = label_type,
                    label_category_id = label_category_id,
                    label_id = label_id
                )

                if len(all_labels) == 0:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                return Response(data=json.loads(all_labels[0].to_json()))
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
        return Response(str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response()

