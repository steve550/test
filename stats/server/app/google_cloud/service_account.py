from google.oauth2 import service_account
from google.cloud import storage
from google.cloud.storage import Bucket, Blob
from server.settings import PROJECT_ROOT
import os
import requests
from google.auth.transport.requests import Request

PROJECT_ID = "deepen-161721"

CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(PROJECT_ROOT, 'DeepenAIMain-6f3c4b6a03a6.json')).with_scopes(
    ["https://www.googleapis.com/auth/cloud-platform"])


def grant_roles(service_account_id):
    pass


def create_service_account(account_id, email):
    CREDENTIALS.refresh(Request())
    a = get_service_account(account_id)
    post_url = "https://iam.googleapis.com/v1/projects/{}/serviceAccounts".format(PROJECT_ID)
    post_body = {
        "accountId": account_id,
        "serviceAccount": {
            "displayName": "Rannotate user service account for {}".format(email),
        }
    }


    post_response = requests.post(post_url, json=post_body,
        headers={"Authorization": "Bearer {}".format(CREDENTIALS.token)})
    if post_response.status_code != 409 and post_response.status_code != 200:
        print("Failed to create service account {}".format(post_response))
        return False
    pass
