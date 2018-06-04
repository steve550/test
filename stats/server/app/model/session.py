from mongoengine import Document, StringField, DateTimeField
import datetime


class SessionModel(Document):
    jwt_token = StringField(max_length=1000, required=True, unique=True)
    create_date_time = DateTimeField(max_length=120, default=datetime.datetime.now)
    auth_method = StringField(max_length=120, default="google")
    user_id = StringField(max_length=120, required=True)
    email = StringField(max_length=120, required=True)

    meta = {'db_alias': 'deepen', 'collection': "session",
        'indexes': [
            {'fields': ('jwt_token', 'user_id'), 'unique': True},
            {'fields': ('jwt_token', 'user_id', 'email'), 'unique': True}
        ]}
