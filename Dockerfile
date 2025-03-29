FROM ubuntu:latest
LABEL authors="sarim"

ENTRYPOINT ["top", "-b"]
# Use an official lightweight Python image.
FROM python:3.9-slim

# Set the working directory inside the container.
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose port 8000 for the FastAPI server.
EXPOSE 8000

# Start the server using uvicorn.
CMD ["uvicorn", "rover_server:app", "--host", "0.0.0.0", "--port", "8000"]
