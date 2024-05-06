FROM python:3.12-bullseye

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR /app/src

CMD ["streamlit", "run", "main.py"]
