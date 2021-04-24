FROM python:3.6.9
MAINTAINER Christian Heusel <christian@heusel.eu>

COPY requirements.txt config.json ./
RUN pip3 install -r requirements.txt
COPY fshelper.py ./
CMD ["python3", "fshelper.py"]
