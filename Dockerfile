FROM python:3.9
MAINTAINER Christian Heusel <christian@heusel.eu>

COPY requirements.txt fshelper.py config.json ./
RUN pip3 install -r requirements.txt
CMD ["python3", "fshelper.py"]
