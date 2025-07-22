# Use official Python image
FROM python:3.11-slim

WORKDIR /app

COPY logOutput.py ./
COPY reader.py ./
COPY requirements.txt ./
COPY config/information.txt ./config/information.txt

RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to run the log writer
CMD ["python", "-u", "logOutput.py"]