from anilmuthinenideepenai/ubuntu1604-googlecloud-python-opencv-pcl
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/docker
WORKDIR /opt/docker
RUN apt-get update
ADD requirements.txt /opt/docker/
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt
ADD . /opt/docker/
CMD python manage.py runserver 0.0.0.0:8000