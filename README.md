# MITACS-Dashboard

## 3D Printing and Supply Chain Management Dashboard

This application provides a comprehensive dashboard for managing 3D printing operations and supply chain logistics.

## Setup and Installation

### Local Development

1. Clone the repository
2. Create a virtual environment: python -m venv venv`n3. Activate the virtual environment: source venv/bin/activate (or env\\Scripts\\activate on Windows)
4. Install dependencies: pip install -r requirements.txt`n5. Run the application: streamlit run app.py`n
### Docker

`ash
docker-compose up
``n
## Project Structure

The project follows a modular structure designed to support scalability and maintainability.

- pp.py: Main application entry point
- pages/: Streamlit pages for different modules
- src/: Core application code
  - components/: Reusable UI components
  - db/: Database models and connection management
  - services/: Business logic and services
  - utils/: Helper utilities
- static/: Static assets like images and CSS
- 	ests/: Test suite
- configs/: Configuration management
- data/: Sample and development data
- scripts/: Utility scripts

## Features

- User Management
- Device Tracking
- Materials Inventory
- Product Management
- Quality Assurance
- Certifications
- Subscription Management
- and more...

## Testing

Run the test suite with:

`ash
pytest
``n
