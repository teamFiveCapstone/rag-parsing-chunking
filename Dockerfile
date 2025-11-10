FROM python:3.9

RUN apt-get update 
RUN apt-get install -y libgl1 libglib2.0-0

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src /src
WORKDIR /src

CMD [ "python", "main.py"]