from db.models import AirQuality
from utils.city_map import load_city_url_map

CITY_URL_MAP = load_city_url_map()


def save_air_quality_to_db(db, air_data: dict):
    db_air_quality = AirQuality(**air_data)
    db.add(db_air_quality)
    db.commit()
    db.refresh(db_air_quality)
    return db_air_quality
