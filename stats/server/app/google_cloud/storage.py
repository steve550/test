from google.oauth2 import service_account
from google.cloud import storage
from google.cloud.storage import Bucket, Blob
from server.settings import PROJECT_ROOT
import os
import datetime
import base64
import json

from google.auth.transport.requests import Request
import requests


CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(PROJECT_ROOT, 'DeepenAIMain-59b958e27d2b.json'))


CREDENTIALS_DOWNLOAD_SIGNER = service_account.Credentials.from_service_account_file(
    os.path.join(PROJECT_ROOT, 'DeepenAIMain-96594d5bb829.json'))


CREDENTIALS_UPLOAD_SIGNER = service_account.Credentials.from_service_account_file(
    os.path.join(PROJECT_ROOT, 'DeepenAIMain-056dd4968645.json')).with_scopes(
    ["https://www.googleapis.com/auth/cloud-platform"])


STORAGE_CLIENT = storage.Client.from_service_account_json(
    os.path.join(PROJECT_ROOT, 'DeepenAIMain-59b958e27d2b.json'))

def create_bucket_if_not_exists(bucket_name):
    if STORAGE_CLIENT.lookup_bucket(bucket_name) is None:
        STORAGE_CLIENT.create_bucket(bucket_name)


def get_gcs_location(client_id, project_id, dataset_id):
    return "deependata-{}-{}-{}".format(client_id, project_id, dataset_id), "deependata"


def upload_directory(client_id, project_id, dataset_id, directory):
    gcs_bucket, gcs_files_root_path = get_gcs_location(client_id, project_id, dataset_id)
    create_bucket_if_not_exists(gcs_bucket)
    #STORAGE_CLIENT = storage.Client()
    bucket = STORAGE_CLIENT.get_bucket(bucket_name=gcs_bucket)
    for dir_path, dirs, files in os.walk(directory):
        for filename in files:
            local_file_path = os.path.join(dir_path, filename)
            if local_file_path.lower().endswith("jpg") or local_file_path.lower().endswith("png"):
                gcs_file_path = gcs_files_root_path + "/" + local_file_path[len(directory)+1:]
                blob = bucket.blob(gcs_file_path)
                blob.upload_from_filename(local_file_path)
    return gcs_bucket, gcs_files_root_path

def get_files(gcs_bucket, gcs_files_root_path, expiration_date_time=(
        datetime.datetime.now() + datetime.timedelta(days=2))):
    #STORAGE_CLIENT = storage.Client()
    if STORAGE_CLIENT.lookup_bucket(gcs_bucket) is None:
        return []

    blobs = STORAGE_CLIENT.get_bucket(bucket_name=gcs_bucket).list_blobs(prefix=gcs_files_root_path)
    files = []
    for blob in blobs:
        file_id = blob.name[len(gcs_files_root_path) + 1:]
        if file_id.lower().endswith("png") or file_id.lower().endswith("jpg"):
            files.append({
                "file_id": file_id,
                "media_link": blob.media_link,
                "signed_media_link": blob.generate_signed_url(expiration=expiration_date_time,
                    credentials=CREDENTIALS_DOWNLOAD_SIGNER)
            })
    return files

def get_signed_upload_url(gcs_bucket, gcs_file_path):
    bucket = STORAGE_CLIENT.get_bucket(bucket_name=gcs_bucket)
    blob = bucket.blob(gcs_file_path)
    return blob.generate_signed_url(credentials=CREDENTIALS_UPLOAD_SIGNER,
        expiration=datetime.datetime.now() +
                   datetime.timedelta(hours=4))

def get_resumable_upload_url(gcs_post_url, file_size, origin):
    CREDENTIALS_UPLOAD_SIGNER.refresh(Request())
    token = CREDENTIALS_UPLOAD_SIGNER.token;

    post_response = requests.post(
        gcs_post_url,
        headers={
            "Authorization": "Bearer {}".format(token),
            "X-Upload-Content-Type": "application/zip",
            "X-Upload-Content-Length": str(file_size),
            "Origin": origin
        })
    if post_response.status_code != 200:
        return False
    else:
        return post_response.headers["Location"];

def get_bounding_boxes(gcs_bucket, gcs_file_root_path):
    url = "http://35.197.77.238:8000/bbox?image_path=" + gcs_file_root_path + "&bucket_name=" + gcs_bucket
    post_response = requests.post(url)
    if post_response.status_code != 200:
        return False
    else:
        return json.loads(post_response.content)