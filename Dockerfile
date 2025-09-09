# Example Dockerfile for a Hugging Face application
FROM python:3.12-slim

WORKDIR /app
RUN mkdir uploads
RUN chmod 777 uploads


COPY src/ ./src/
COPY requirements.txt .
COPY pyproject.toml .
RUN pip install  -e .
RUN pip install -r requirements.txt


COPY . .

# Or your chosen port
EXPOSE 7860 


CMD ["python3", "app.py"] 
