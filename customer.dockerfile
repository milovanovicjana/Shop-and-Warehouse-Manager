FROM python:3

RUN mkdir -p /opt/src/applications/customer
WORKDIR /opt/src/applications/customer

COPY applications/customer/application.py ./application.py
COPY applications/customer/configuration.py ./configuration.py
COPY applications/customer/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt
COPY ./checkRole.py ./checkRole.py

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]
