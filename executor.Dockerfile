FROM python:3.10-bookworm

# Set the working directory
WORKDIR /app

# Install common data science and utility packages
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    matplotlib \
    scikit-learn \
    requests \
    beautifulsoup4 \
    wikipedia \
    fastapi \
    uvicorn \
    python-gitlab \
    python-dotenv \
    paramiko \
    autopep8

# Create directories for code execution
RUN mkdir -p /app/data /app/code

# Copy the modules directory
COPY ./modules ./modules

# Install additional requirements from the modules directory
RUN pip install --no-cache-dir -r ./modules/requirements.txt

RUN for dir in /app/modules/*/; do \
    echo "Installing module in $dir"; \
    pip install "$dir"; \
    if [ $? -eq 0 ]; then \
        echo "Successfully installed $dir"; \
    else \
        echo "Failed to install $dir" >&2; \
    fi; \
done

# Copy the .env file
COPY ./executor/.env .env

# Copy the executor service
COPY ./executor/executor_service.py .

# Expose the port for the executor service
EXPOSE 5000

# Run the executor service
CMD ["python", "executor_service.py"]