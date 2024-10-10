FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ocrmypdf \
    tesseract-ocr \
    tesseract-ocr-spa \
    mupdf-tools \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mortage_analyzer.py .

EXPOSE 8501

CMD ["streamlit", "run", "mortage_analyzer.py"]
