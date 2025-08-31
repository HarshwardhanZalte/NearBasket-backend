#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell << EOF
from users.models import User
import os

mobile = os.environ.get('SUPERUSER_MOBILE', '1234567890')
name = os.environ.get('SUPERUSER_NAME', 'Admin')
password = os.environ.get('SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(mobile_number=mobile).exists():
    User.objects.create_superuser(
        mobile_number=mobile,
        name=name,
        password=password
    )
    print(f"Superuser created: {name} ({mobile})")
else:
    print("Superuser already exists")
EOF