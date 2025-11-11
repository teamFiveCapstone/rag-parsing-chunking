FROM python:3.9-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./src /src
WORKDIR /src

CMD ["python", "main.py"]