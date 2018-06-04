from mongoengine import Document, StringField, DateTimeField, BooleanField, ListField, EmbeddedDocument, \
    EmbeddedDocumentField
import datetime


class UserRoleModel(EmbeddedDocument):
    role = StringField()
    authorized_client_ids = ListField(StringField())


class UserModel(Document):
    user_id = StringField(required=True, unique=True)
    email = StringField(required=True)
    full_name = StringField(default="")
    profile_image_url = StringField()
    password = StringField()
    create_date_time = DateTimeField(max_length=120, default=datetime.datetime.now)
    last_logged_in_date_time = DateTimeField()
    auth_method = StringField(required=True)
    user_role = EmbeddedDocumentField(UserRoleModel)

    meta = {'db_alias': 'deepen', 'collection': "user",
        'indexes': [
            {'fields': ('email', 'user_id'), 'unique': True},
            {'fields': ('email', 'password'), 'unique': True}
        ]
    }


def is_super_admin(user):
    return user is not None and user.get("user_role") is not None\
           and user["user_role"].get("role") == "superadmin"

def is_admin(user):
    return user is not None and user.get("user_role") is not None\
           and user["user_role"].get("role") == "admin"

def is_labeller(user):
    return user is not None and user.get("user_role") is not None\
           and user["user_role"].get("role") == "labeller"

def authorized_client_ids(user):
    if user is not None and user.get("user_role") is not None:
        return user["user_role"].get("authorized_client_ids", [])
    return []

def user_access_level(user, client_id):
    if is_super_admin(user):
        return "edit"
    elif is_admin(user) and client_id in authorized_client_ids(user):
        return "edit"
    elif is_labeller(user) and client_id in authorized_client_ids(user):
        return "view"
    return None
