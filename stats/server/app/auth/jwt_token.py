from rest_framework import exceptions
from django.http import HttpResponse
from rest_framework.authentication import get_authorization_header, BaseAuthentication
import jwt
import json
import sys
import traceback

from app.model.session import SessionModel
from app.model.user import UserModel


class JwtTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].upper() != b'JWT':
            raise exceptions.AuthenticationFailed("Invalid authorization header {}".format(str(auth)))

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided {}.'.format(get_authorization_header(request))
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header {}'.format(get_authorization_header(request))
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1]
            if token == "null":
                msg = 'Null token not allowed'
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        try:
            payload = jwt.decode(token, "SECRET_KEY")
            SessionModel.objects(jwt_token=token)
            email = payload['email']
            user_id = payload['user_id']
            sessions = SessionModel.objects(jwt_token=token, user_id=user_id, email=email)
            if len(sessions) == 0:
                raise exceptions.AuthenticationFailed({'Error': "Token mismatch", 'status': "401"})
            else:
                user = UserModel.objects(user_id=sessions[0]["user_id"], email=sessions[0]["email"])
                user_data = json.loads(user[0].to_json())

                return (user_data, token)
        except jwt.exceptions.InvalidTokenError:
            raise exceptions.AuthenticationFailed()
        except:
            print "Unexpected error:", sys.exc_info()
            traceback.print_tb(sys.exc_info()[2])
            raise exceptions.AuthenticationFailed(str(sys.exc_info()))

    def authenticate_header(self, request):
        return 'JWT'