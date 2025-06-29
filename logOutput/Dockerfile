# Use official Python image
FROM python:3.11-slim

WORKDIR /app

COPY logOutput.py ./
COPY requirements.txt ./

# No dependencies to install, but keep the step for extensibility
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "logOutput.py"]