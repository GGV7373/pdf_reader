FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Only copy the code, so PDFs in this folder never end up inside the image
COPY main.py app.py index.html ./

ENV HOST=0.0.0.0 PYTHONUNBUFFERED=1
EXPOSE 5000
USER nobody
CMD ["python", "app.py"]
