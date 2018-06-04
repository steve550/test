from mongoengine import Document, StringField, ListField, LongField, DateTimeField, EmbeddedDocument, \
    EmbeddedDocumentListField
from datetime import datetime

class FeedbackModel(EmbeddedDocument):
    author_name = StringField()
    author_email = StringField()
    timestamp = DateTimeField(default=datetime.now())
    text = StringField()

class FileModel(Document):
    client_id = StringField(required=True)
    project_id = StringField(required=True)
    dataset_id = StringField(required=True)
    file_id = StringField(required=True)
    status = StringField()
    feedback = EmbeddedDocumentListField(FeedbackModel)

    meta = {
        'db_alias': 'deepen',
        'collection': "file",
        'indexes': [
            {'fields': ('client_id', 'project_id', 'dataset_id', 'file_id'), 'unique': True}
        ]
    }