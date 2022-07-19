FROM python:3

RUN mkdir -p /opt/src/applications/daemon
WORKDIR /opt/src/applications/daemon

COPY applications/daemon/application.py ./application.py
COPY applications/daemon/configuration.py ./configuration.py
COPY applications/daemon/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]
