1. Install deps
```
pip install -r requirements.txt
```

2. Install redis-server and run it on your machine

3. Run migrations:
   
```
python manage.py migrate
```

4. Run celery workers:

```
celery -A core worker -l info
```

5. Run django

```
python manage.py runserver
```

6. Open frontend:

```
cd frontend
open test_sse.html
```
