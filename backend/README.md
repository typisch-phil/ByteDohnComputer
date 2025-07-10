# Backend Structure

This directory contains all Python backend code for the ByteDohm PC Configurator application.

## Structure

```
backend/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── models.py          # Database models (AdminUser, Customer, Order, etc.)
├── routes/
│   ├── __init__.py
│   ├── routes.py          # Main application routes
│   ├── admin_routes.py    # Admin panel routes
│   └── dhl_routes.py      # DHL shipping routes
├── services/
│   ├── __init__.py
│   ├── email_service.py   # Email sending service
│   ├── dhl_integration.py # DHL API integration
│   └── dhl_alternatives.py # Alternative DHL tracking
├── utils/
│   ├── __init__.py
│   └── test_email.py      # Email testing utilities
└── config/
    ├── __init__.py
    ├── mysql_config.py    # MySQL configuration
    └── setup_mysql.py     # MySQL setup utilities
```

## Key Files

- **models/models.py**: Contains all SQLAlchemy database models
- **routes/routes.py**: Main application routes for frontend
- **routes/admin_routes.py**: Admin panel functionality
- **services/email_service.py**: Email sending service for notifications
- **services/dhl_integration.py**: DHL shipping API integration

## Import Structure

All imports from the backend should use the full path:
```python
from backend.models.models import Customer, Order
from backend.services.email_service import send_registration_email
from backend.services.dhl_integration import create_shipping_label_for_order
```

## Notes

- All Python files are organized in this backend/ directory for better code management
- The main app.py file in the root directory imports from these modules
- Database configuration is handled in config/mysql_config.py
- Email and DHL services are separated into their own service modules