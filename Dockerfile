# 1) pick a small Python image
FROM python:3.11-slim

# 2) set working dir
WORKDIR /app

# 3) copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) copy rest of the app
COPY . .

# 5) tell Docker which port we'll serve on
EXPOSE 8080

# 6) run via Gunicorn (production-ready WSGI)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
