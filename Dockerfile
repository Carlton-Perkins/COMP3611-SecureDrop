FROM python:latest

WORKDIR /SecureDrop/

COPY *.py ./
COPY *.txt ./
COPY testConfigs/ ./testConfigs

RUN pip3 install -r ./requirements.txt

CMD bash