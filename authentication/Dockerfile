FROM docker.io/python:3.12-rc-slim-buster

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY app.py app.py

EXPOSE 5001

CMD [ "python3", "-u", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5001"]
