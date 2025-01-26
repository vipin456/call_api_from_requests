# Select the base image
FROM python:3.9-slim

# Install Git (if it's not already installed)
RUN apt-get update && apt-get install -y git

# Clone the project from GitHub
RUN git clone https://github.com/vipin456/call_api_from_requests.git /app

# Set the working directory
WORKDIR /app

# Install the virtual environment and dependencies
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

# Set the entry point to run in the container
ENTRYPOINT ["venv/bin/python", "main.py"]

# CMD for arguments passed when running the container
CMD ["--input_file", "inputs/in.csv", "--manifest", "resources/manifest.xml", "--script", "scripts/extract.py", "--dev_mode", "true", "--settings", "settings/settings.json"]
