"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from app import views
import app.view.session
import app.view.label
import app.view.predicted_label
import app.view.client
import app.view.file
import app.view.metadata

urlpatterns = [
url(r'^api/client/bounding_boxes/(.+)/(.+)/(.+)/(.+)$', app.view.client.boundingboxes),

    url(r'^api/metadata/label_category/client/(.+)$', app.view.metadata.label_categories),
    url(r'^api/metadata/features/client/(.+)$', app.view.metadata.features),
    url(r'^api/metadata/features_new/client/(.+)$', app.view.metadata.features_new),

    url(r'^api/label/(.+)/(.+)/(.+)/(.+)/(.+)/(.+)/(.+)$', app.view.label.label),
    url(r'^api/label/(.+)/(.+)/(.+)/(.+)/(.+)/(.+)$', app.view.label.label),
    url(r'^api/label/(.+)/(.+)/(.+)/(.+)/(.+)$', app.view.label.label),
    url(r'^api/label/(.+)/(.+)/(.+)/(.+)$', app.view.label.label),
    url(r'^api/label/(.+)/(.+)/(.+)$', app.view.label.label),

    url(r'^api/predicted_label/(.+)/(.+)/(.+)/(.+)/(.+)/(.+)/(.+)$', app.view.predicted_label.predicted_label),
    url(r'^api/predicted_label/(.+)/(.+)/(.+)/(.+)/(.+)/(.+)$', app.view.predicted_label.predicted_label),
    url(r'^api/predicted_label/(.+)/(.+)/(.+)/(.+)/(.+)$', app.view.predicted_label.predicted_label),
    url(r'^api/predicted_label/(.+)/(.+)/(.+)/(.+)$', app.view.predicted_label.predicted_label),
    url(r'^api/predicted_label/(.+)/(.+)/(.+)$', app.view.predicted_label.predicted_label),

    url(r'^api/file/status/(.+)/(.+)/(.+)/(.+)$', app.view.file.status),
    url(r'^api/file/feedback/(.+)/(.+)/(.+)/(.+)$', app.view.file.feedback),
    url(r'^api/file/file_id/(.+)/(.+)/(.+)$', app.view.file.file_id),

    url(r'^api/summary/(.+)/(.+)/(.+)/(.+)$', app.view.file.get_file_summary),

    url(r'^api/client/(.+)$', app.view.client.client),
    url(r'^api/client$', app.view.client.client),

    url(r'^api/project/(.+)/(.+)$', app.view.client.project),
    url(r'^api/project/(.+)$', app.view.client.project),
    url(r'^api/dataset/(.+)/(.+)/(.+)/(.+)$', app.view.client.dataset),
    url(r'^api/dataset/(.+)/(.+)$', app.view.client.dataset),
    url(r'^api/dataset/(.+)$', app.view.client.dataset),
    url(r'^api/dataset$', app.view.client.dataset),
    url(r'^api/upload_dataset/(.+)/(.+)/(.+)$', app.view.client.upload_dataset),
    url(r'^api/springcloudtest$', app.view.predicted_label.predicted_test),

    url(r'^api/login', app.view.session.login),
    url(r'^api/logout', app.view.session.logout),
    url(r'^api/check_login', app.view.session.check_login),
    url(r'^api/test', app.view.session.test),


    # app -> label_checker
    url(r'^api/label_checker/', include('label_checker.urls')),

]#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
