import os
import importlib

# Get environment (defaults to development)
ENV = os.environ.get('ENVIRONMENT', 'dev')

# Import appropriate settings module based on environment
config = importlib.import_module(f'configs.{ENV}')

