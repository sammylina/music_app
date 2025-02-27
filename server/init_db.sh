
#!/bin/bash
cd "$(dirname "$0")"
export FLASK_APP=wsgi.py
export FLASK_ENV=development
python3 -c "from db_init import init_db; init_db()"
echo "Database initialization complete."

