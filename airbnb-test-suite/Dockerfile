
FROM mcr.microsoft.com/playwright/python:latest
LABEL authors="razsa"
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create temp directory for logs
RUN mkdir -p temp

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTEST_ADDOPTS="--html=temp/report.html"

# Command to run tests when container starts
CMD ["./run_tests.sh"]