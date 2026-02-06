# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY backend/requirements.txt ./requirements.txt

# Install any exact package versions specified in requirements.txt
# Using --no-cache-dir to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Metadata indicating that the container listens on port 8000
# (Useful for documentation, though Render/Railway inject PORT env var)

# Command to run the application
# We use uvicorn directly, but for high load gunicorn is recommended
# CMD exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
