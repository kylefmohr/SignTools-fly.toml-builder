FROM python:3.11-slim-bullseye

RUN apt update && apt install python3-flask -y

RUN pip install flask

COPY . /app

WORKDIR /app

EXPOSE 8080

CMD ["python3", "app.py"]