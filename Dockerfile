FROM python:3.13

WORKDIR /app

COPY requirements.txt .

RUN  pip install -r requirements.txt 

COPY . .

CMD sleep 10 && python manage.py migrate && uvicorn schedule_app.asgi:application --host 0.0.0.0 --port 8000 --reload
