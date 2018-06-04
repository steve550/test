from django.contrib.auth.models import AnonymousUser
from google.oauth2 import id_token
from rest_framework.decorators import api_view, authentication_classes
from rest_framework import status
from rest_framework.response import Response
from google.auth.transport import requests as googlerequests
from app.model.session import SessionModel
from app.model.user import UserModel
import jwt
from datetime import datetime
from datetime import timedelta
import traceback
import sys
from app.auth.jwt_token import JwtTokenAuthentication
import json


def create_jwt_token(user_id, email, profile_image_url=None, full_name=None):
    current_time = datetime.now()
    UserModel.objects(user_id=user_id,
        email=email).update_one(upsert=True, last_logged_in_date_time=current_time)
    if email.endswith("deepenai.com"):
        UserModel.objects(user_id=user_id, email=email).update_one(set__user_role__role="labeller")
    elif email.endswith("deepen.ai"):
        UserModel.objects(user_id=user_id, email=email).update_one(set__user_role__role="superadmin")
    if profile_image_url is not None:
        UserModel.objects(user_id=user_id, email=email).update_one(set__profile_image_url=profile_image_url)
    if full_name is not None:
        UserModel.objects(user_id=user_id, email=email).update_one(set__full_name=full_name)
    user = UserModel.objects(user_id=user_id, email=email)
    if len(user) == 0:
        return Response(status=status.HTTP_401_UNAUTHORIZED,
            data='Unauthorized user {}'.format(email))
    user_data = json.loads(user[0].to_json())
    role = user_data.get("user_role", {}).get("role", "")
    full_name = user_data.get("full_name", "")
    profile_image_url = user_data.get("profile_image_url")
    authorized_client_ids = user_data.get("user_role", {}).get("authorized_client_ids", [])

    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'authorized_client_ids': authorized_client_ids,
        'expires_at_date_time': (current_time + timedelta(days=1)).isoformat()
    }

    jwt_token = jwt.encode(payload, "SECRET_KEY")

    SessionModel(
        jwt_token=jwt_token,
        user_id=user_id,
        email=email,
    ).save()

    data = {
        "jwt_token": jwt_token,
        "role": role,
        "authorized_client_ids": authorized_client_ids,
        "full_name": full_name
    }
    if profile_image_url is not None:
        data["profile_image_url"] = profile_image_url
    return Response(data=data)


@api_view(['POST'])
def login(request):
    if request.data.get("google_id_token") is not None:
        auth_method = "google"
        google_id_token = request.data["google_id_token"]
    elif request.data.get("email") is not None and request.data.get("password") is not None:
        auth_method = "email"
        email = request.data.get("email")
        password = request.data.get("password")
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        full_name = ""
        profile_image_url = None
        if auth_method == "google":
            try:
                id_info = id_token.verify_oauth2_token(
                    google_id_token, googlerequests.Request(),
                    "3890518873-9igg3o5c5c45a3cnq3fku68jrvc5ricj.apps.googleusercontent.com")
            except ValueError as value_error:
                print(value_error)
                return Response(data=str(value_error), status=status.HTTP_401_UNAUTHORIZED)
            print(id_info)

            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return Response(status=status.HTTP_403_FORBIDDEN, data='Wrong issuer {}'.format(id_info['iss']))

            if id_info.get('hd') != "deepen.ai" and id_info.get('hd') != "deepenai.com" \
                    and id_info["email"] != "anilmuthineni@gmail.com" \
                    and id_info["email"] != "swarnasama75@gmail.com":
                return Response(status=status.HTTP_403_FORBIDDEN, data='Unauthorized user {}'.format(id_info))
            user_id = id_info["sub"]
            email = id_info["email"]
            full_name = id_info["name"]
            profile_image_url = id_info["picture"]

        else:
            user = UserModel.objects(email=email, password=password)
            if len(user) == 0:
                return Response(status=status.HTTP_403_FORBIDDEN, data='Unauthorized user {}'.format(email))
            user_id = user[0]["user_id"]
            email = user[0]["email"]

        return create_jwt_token(user_id, email, full_name=full_name, profile_image_url=profile_image_url)
    except:
        print "Unexpected error:", sys.exc_info()
        traceback.print_tb(sys.exc_info()[2])
        return Response(data=str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JwtTokenAuthentication])
def logout(request):
    SessionModel.objects(jwt_token=request.auth).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JwtTokenAuthentication])
def check_login(request):
    try:
        sessions = SessionModel.objects(jwt_token=request.auth)

        if len(sessions) == 0:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return create_jwt_token(sessions[0]["user_id"], sessions[0]["email"])
    except:
        print "Unexpected error:", sys.exc_info()
        traceback.print_tb(sys.exc_info()[2])
        return Response(data=str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([JwtTokenAuthentication])
def test(request):
    try:
        return Response("All ok")

    except:
        print "Unexpected error:", sys.exc_info()
        traceback.print_tb(sys.exc_info()[2])
        return Response(data=str(sys.exc_info()), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
