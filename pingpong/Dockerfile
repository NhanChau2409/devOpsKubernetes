FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pingpong.py ./

EXPOSE 8080

CMD ["python", "pingpong.py"]
