FROM python:3.11-slim
WORKDIR /app
RUN mkdir -p /app/static
COPY frontend/build /app/static
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ ./
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
