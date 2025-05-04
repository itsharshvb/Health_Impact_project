from typing import List
import random
from bs4 import BeautifulSoup
import requests
from fastapi import HTTPException
import re
from urllib.parse import quote
import logging
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load cities from CSV
CITY_URL_MAP = {}
with open('city_name.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        city_key = row['city_name'].lower().strip()
        state_path = row['state_name'].lower().replace(' ', '-')
        city_path = row['city_name'].lower().replace(' ', '-')
        CITY_URL_MAP[city_key] = (state_path, city_path)

# Manual corrections for special cases
CITY_URL_MAP.update({
    "chandigarh": ("chandigarh", "chandigarh"),
    "bangalore": ("karnataka", "bengaluru"),
    "puducherry": ("puducherry", "pondicherry"),
    "noida": ("uttar-pradesh", "noida"),
    "gurgaon": ("haryana", "gurugram")
})


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


def load_cities(filename: str = 'city_name.csv') -> List[str]:
    """Load city names from CSV file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return [row['city_name'] for row in reader]
    except FileNotFoundError:
        raise RuntimeError(f"City data file {filename} not found")
    except KeyError:
        raise RuntimeError("Invalid CSV format - missing 'city_name' column")


def generate_test_cases(num_cases: int = 15) -> List[str]:
    """Generate random test cases from city data"""
    cities = load_cities()
    return random.sample(cities, min(num_cases, len(cities)))


# Add to your existing __main__ block:
if __name__ == "__main__":
    # Generate 15 random test cases
    test_cities = generate_test_cases(15)

    print(f"Testing {len(test_cities)} random cities:")
    for city in test_cities:
        try:
            print(f"\nFetching data for {city}:")
            result = get_air_quality_data(city)
            print(f"Result: {result}")
        except HTTPException as e:
            print(f"Error: {e.detail}")
