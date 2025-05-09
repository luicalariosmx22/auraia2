web: pip cache purge && pip install --upgrade pip && pip install -r requirements.txt && gunicorn -w 4 -b 0.0.0.0:$PORT app:app --worker-class gevent
