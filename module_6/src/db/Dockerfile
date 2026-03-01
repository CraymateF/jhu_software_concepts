FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir psycopg2-binary==2.9.9 python-dotenv==1.2.1
COPY load_data.py .
CMD ["python", "load_data.py"]
