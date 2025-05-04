import requests
from bs4 import BeautifulSoup
import re
from fastapi import HTTPException
import logging
from urllib.parse import quote
from core.city_loader import load_city_map


def search_city_details(city: str):
    """Improved city search with result selection from list"""
    search_url = f"https://www.iqair.com/in-en/india/search?query={quote(city.lower())}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.iqair.com/",
        }

        response = requests.get(
            search_url, headers=headers, allow_redirects=True)
        logging.info(f"Search URL: {response.url}")

        if response.status_code == 200:
            if "/india/" in response.url:
                path = response.url.split("/india/")[1].split("/")[0:2]
                return tuple(path)

            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('a', class_='search-result')

            if results:
                for result in results:
                    href = result.get('href', '')
                    if '/india/' in href:
                        path = href.split("/india/")[-1].split("/")
                        if len(path) >= 2:
                            return (path[0], path[1])
        return None

    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return None


def get_air_quality_data(city: str):
    formatted_city = city.lower().strip()
    CITY_URL_MAP = load_city_map()

    if formatted_city in CITY_URL_MAP:
        state, city_path = CITY_URL_MAP[formatted_city]
    else:
        result = search_city_details(city)
        if not result:
            raise HTTPException(
                status_code=404, detail="City not found on IQAir")
        state, city_path = result

    url = f"https://www.iqair.com/in-en/india/{state}/{city_path}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.iqair.com/"
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code,
                                detail="Failed to fetch data")

        soup = BeautifulSoup(response.content, 'html.parser')

        def extract_aqi(soup):
            # Try multiple AQI locations
            selectors = [
                ('p', {'class': 'aqi-value__estimated'}),
                ('div', {'class': 'aqi-value__value'}),
                ('meta', {'property': 'og:title'})
            ]

            for tag, attrs in selectors:
                element = soup.find(tag, attrs)
                if element:
                    try:
                        if tag == 'meta':
                            match = re.search(
                                r'AQI: (\d+)', element.get('content', ''))
                            return int(match.group(1)) if match else None
                        return int(element.get_text(strip=True))
                    except (ValueError, AttributeError):
                        continue
            return None

        data = {
            "city": city,
            "aqi": extract_aqi(soup),
            "pm2_5": None,
            "pm10": None,
            "co": None,
            "so2": None,
            "no2": None,
            "o3": None
        }

        # Pollutant extraction
        for card in soup.find_all('air-pollutant-card'):
            try:
                title = card.find(
                    'div', class_='card-wrapper-info__title').get_text(strip=True)
                value_str = card.find(
                    'span', class_='measurement-wrapper__value').get_text(strip=True)
                value = float(value_str.split()[0])

                mapping = {
                    'PM2.5': 'pm2_5',
                    'PM10': 'pm10',
                    'CO': 'co',
                    'SO₂': 'so2',
                    'NO₂': 'no2',
                    'O₃': 'o3'
                }
                if title in mapping:
                    data[mapping[title]] = value
            except Exception as e:
                logging.warning(f"Error parsing pollutant: {str(e)}")
                continue

        return data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Scraping failed: {str(e)}")
