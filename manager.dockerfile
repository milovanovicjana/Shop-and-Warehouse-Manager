FROM python:3

RUN mkdir -p /opt/src/applications/manager
WORKDIR /opt/src/applications/manager

COPY applications/manager/application.py ./application.py
COPY applications/manager/configuration.py ./configuration.py
COPY applications/manager/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt
COPY ./checkRole.py ./checkRole.py

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]
