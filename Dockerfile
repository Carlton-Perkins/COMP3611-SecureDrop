FROM python:latest

WORKDIR /SecureDrop/

COPY *.txt ./
RUN pip3 install -r ./requirements.txt

COPY *.py ./
COPY testConfigs/ ./testConfigs


CMD bash