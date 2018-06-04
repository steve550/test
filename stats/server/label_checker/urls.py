from django.conf.urls import url
from . import views
from .views import WrongIdListView, MissingObjectListView, MissingPolygonListView, \
    LabeledCorrectlyListView, FileUploadView

from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'label_checker'

urlpatterns = [
    #/dataset/
    url(r'^$', views.index, name='index'),

    #/dataset/<dataset_id>
    url(r'^(?P<dataset>[0-9]+)/$', views.detail, name='detail'),
    url(r'^home/$', views.home, name='home'),
    #url(r'^list/$', views.list, name='list'),

    #get images
    #url(r'^get_images/$', views.getImages, name='get_images'),

    # view results
    url(r'^wrong_id/$', WrongIdListView.as_view(), name='wrong_id'),
    url(r'^missing_polygon/$', MissingPolygonListView.as_view(), name='missing_polygon'),
    url(r'^missing_object/$', MissingObjectListView.as_view(), name='missing_object'),
    url(r'^labeled_correctly/$', LabeledCorrectlyListView.as_view(), name='labeled_correctly'),

]
