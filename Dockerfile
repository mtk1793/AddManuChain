FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false 

# Expose port for Streamlit
EXPOSE 8501

# Command to run the application
CMD ["bash", "-c", "python init_db.py && streamlit run app.py --server.port=${STREAMLIT_SERVER_PORT} --server.address=0.0.0.0 --server.enableCORS=${STREAMLIT_SERVER_ENABLE_CORS}"]