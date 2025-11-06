FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    JWT_SECRET=change_me_in_env \
    SQLALCHEMY_DATABASE_URI=sqlite:////app/girvi.db

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

