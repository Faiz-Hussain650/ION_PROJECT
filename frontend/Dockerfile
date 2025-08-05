FROM python:3.9-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
CMD ["python", "app.py"]