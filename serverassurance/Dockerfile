FROM python:3.12

WORKDIR /app

COPY . .

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV PYTHONPATH=/app

CMD ["sh", "-c", "python manage.py makemigrations && \
                  python manage.py migrate && \
                  python manage.py create_default_company && \
                  python manage.py runserver 0.0.0.0:8002"]
