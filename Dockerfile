FROM python:3.6.2
RUN mkdir -p /code
WORKDIR /code
ADD ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt