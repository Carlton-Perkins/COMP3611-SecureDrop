FROM python:latest

COPY *.py /SecureDrop/
COPY *.txt /SecureDrop/
COPY testConfigs/ /SecureDrop/testConfigs

RUN pip3 install -r /SecureDrop/requirements.txt

CMD bash