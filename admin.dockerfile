FROM python:3

RUN mkdir -p /opt/src/applications/admin
WORKDIR /opt/src/applications/admin

COPY applications/admin/application.py ./application.py
COPY applications/admin/configuration.py ./configuration.py
COPY applications/admin/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt
COPY ./checkRole.py ./checkRole.py

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]
