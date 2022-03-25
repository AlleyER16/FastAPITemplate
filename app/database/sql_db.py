from time import sleep
import psycopg2
from psycopg2.extras import RealDictCursor

from app.settings import settings

try:
    db = psycopg2.connect(
        database=settings.DB, 
        user=settings.USER, 
        password=settings.PASSWORD, 
        host=settings.HOST, 
        cursor_factory=RealDictCursor
        )
    cursor = db.cursor()
except Exception as ex:
    print(ex)
    sleep(5)