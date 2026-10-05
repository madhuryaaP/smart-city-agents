FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Install CPU-only torch first to keep image ~800 MB instead of ~3 GB
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# Pre-bake embedding model into image — eliminates 40s cold-start download
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
