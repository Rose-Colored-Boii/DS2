FROM python:3.12-rc-slim-buster

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY app.py app.py

EXPOSE 5001

CMD [ "python", "app.py" ]
