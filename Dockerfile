FROM node:18-alpine
WORKDIR /app
COPY . .
RUN cd frontend && npm install && npm run build
RUN cd /app && pip install -r backend/requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "cp -r /app/frontend/build/* /app/static/ && cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000"]
