from mongoengine import Document, StringField, ListField, IntField


class LabelCategoryMetadataModel(Document):
    label_category_id = StringField(primary_key=True)
    depth_type = StringField()
    color = ListField()
    category = ListField()

    meta = {
        'db_alias': 'deepen',
        'collection': "label_category_metadata",
        'strict': False
    }