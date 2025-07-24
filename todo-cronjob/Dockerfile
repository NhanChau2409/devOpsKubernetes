FROM python:3.9-alpine

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY main.py .

# Make script executable
RUN chmod +x main.py

# Run the script
CMD ["python", "main.py"] 