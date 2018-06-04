from mongoengine import Document, StringField, ListField, LongField


class PredictedLabelModel(Document):
    client_id = StringField(max_length=100, required=True)
    project_id = StringField(max_length=100, required=True)
    dataset_id = StringField(max_length=100, required=True)
    file_id = StringField(max_length=100, required=True)
    label_type = StringField(max_length=100, required=True)
    label_category_id = StringField(max_length=100, required=True)
    label_id = StringField(max_length=100, required=True)
    polygons = ListField(ListField(ListField(LongField())))
    box = ListField(LongField())

    meta = {
        'db_alias': 'deepen',
        'collection': "predicted_label",
        'indexes': [
            {'fields': ('client_id', 'project_id', 'dataset_id', 'file_id', 'label_type', 'label_category_id',
                        'label_id'), 'unique': True}
        ]
    }