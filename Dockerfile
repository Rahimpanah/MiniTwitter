FROM python:3.11-slim

# set the environment variables
    #prevents creation of .pyc files 
ENV PYTHONDONTWRITEBYTECODE 1
    #ensures logs are shown in real time
ENV PYTHONUNBUFFERED 1
# set the work directorty
WORKDIR /app/

COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copies everything from your local project into the container’s /app directory 
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI Uvicorn
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]

