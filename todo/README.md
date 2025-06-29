# Todo App

A simple web server that outputs "Server started in port NNNN" when started and can be deployed to Kubernetes.

## Features

- Flask-based web server
- Configurable port via PORT environment variable
- Health check endpoint at `/health`
- Kubernetes deployment ready
- Docker containerization

## Quick Start

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python app.py
   ```
   Or with a custom port:
   ```bash
   PORT=3000 python app.py
   ```

### Docker

1. Build the image:
   ```bash
   ./build.sh
   ```

2. Run locally:
   ```bash
   docker run -p 8080:8080 -e PORT=8080 todo-app:latest
   ```

### Kubernetes Deployment

1. Build the Docker image:
   ```bash
   ./build.sh
   ```

2. Deploy to Kubernetes:
   ```bash
   ./deploy.sh
   ```

3. Check deployment status:
   ```bash
   kubectl get pods -l app=todo-app
   kubectl logs -l app=todo-app
   ```

## Environment Variables

- `PORT`: The port number to run the server on (default: 8080)

## Endpoints

- `GET /`: Main page showing "Todo App - Server is running!"
- `GET /health`: Health check endpoint returning "OK"

## Next Steps

This is the foundation for a todo application. Future features will include:
- Todo CRUD operations
- Database integration
- User authentication
- API endpoints for todo management 