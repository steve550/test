from mongoengine import Document, StringField, MapField, EmbeddedDocument, EmbeddedDocumentField, ListField, IntField
import json
import time
from app.google_cloud import storage
from app.model.file import FileModel
import sys
import traceback


class StatusModel(EmbeddedDocument):
    total = IntField()
    labelling_in_progress = IntField()
    qa_in_progress = IntField()
    finished = IntField()


class DatasetModel(EmbeddedDocument):
    gcs_bucket = StringField()
    gcs_files_root_path = StringField()
    status = EmbeddedDocumentField(StatusModel)
    meta = {'strict': False}


class ProjectModel(EmbeddedDocument):
    datasets = MapField(EmbeddedDocumentField(DatasetModel))


class ClientFeature(EmbeddedDocument):
    label_category_ids = ListField(StringField())

class ClientModel(Document):
    client_id = StringField(primary_key=True)
    label_category_ids = ListField(StringField())
    features = ListField(StringField())
    features_new = MapField(EmbeddedDocumentField(ClientFeature))
    projects = MapField(EmbeddedDocumentField(ProjectModel))
    meta = {'db_alias': 'deepen', 'collection': "client", 'strict': False}


def get_dataset_summary(client_id, project_id, dataset_id,
        gcs_bucket, gcs_files_root_path):
    if gcs_bucket is None or gcs_files_root_path is None:
        return {
            "total": 0,
            "labelling_in_progress": 0,
            "qa_in_progress": 0,
            "finished": 0
        }

    all_file_ids = [file_dict["file_id"] for file_dict in
        storage.get_files(gcs_bucket, gcs_files_root_path)]
    total_file_ids = len(all_file_ids)
    labelling_in_progress = 0
    qa_in_progress = 0
    finished = 0
    for file_id in all_file_ids:
        file_data = FileModel.objects(client_id=client_id, project_id=project_id,
            dataset_id=dataset_id, file_id=file_id)
        if len(file_data) == 0:
            labelling_in_progress += 1
        elif file_data[0].get("status") == "label_finished":
            qa_in_progress += 1
        elif file_data[0].get("status") == "qa_finished":
            finished += 1
        else:
            labelling_in_progress += 1

    return {
        "total": total_file_ids,
        "labelling_in_progress": labelling_in_progress,
        "qa_in_progress": qa_in_progress,
        "finished": finished
    }


def update_summary():
    start_time = time.time()
    try:
        clients = ClientModel.objects()
        for client in clients:
            client_json = json.loads(client.to_json())
            if client_json.get("projects") is None:
                continue
            projects = client_json["projects"]
            for project_id in projects.keys():
                if projects[project_id].get("datasets") is None:
                    continue
                datasets = projects[project_id]["datasets"]
                for dataset_id in datasets.keys():
                    dataset = datasets[dataset_id]
                    summary = get_dataset_summary(client_json["_id"], project_id, dataset_id,
                        dataset.get("gcs_bucket"), dataset.get("gcs_files_root_path"))

                    set_prefix = "set__projects__{}__datasets__{}__status__".format(
                        project_id, dataset_id)
                    set_dict = {
                        set_prefix + "total": summary["total"],
                        set_prefix + "labelling_in_progress": summary["labelling_in_progress"],
                        set_prefix + "qa_in_progress": summary["qa_in_progress"],
                        set_prefix + "finished": summary["finished"],
                    }
                    ClientModel.objects(client_id=client_json["_id"]).update_one(
                        **set_dict
                    )
    except:
        print("Unexpected error:", sys.exc_info())
        traceback.print_tb(sys.exc_info()[2])
    print("Total time for summary update {} seconds".format(time.time() - start_time))