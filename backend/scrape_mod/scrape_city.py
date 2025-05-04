import requests
from bs4 import BeautifulSoup
import csv

url = "https://en.wikipedia.org/wiki/List_of_cities_in_India_by_population"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

with open('indian_cities.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['City_Name', 'State_Name',
                    'IQAir_State_Path', 'IQAir_City_Path'])

    table = soup.find('table', {'class': 'wikitable'})
    for row in table.find_all('tr')[1:301]:  # First 300 cities
        cols = row.find_all('td')
        city = cols[1].text.strip()
        state = cols[2].text.strip()
        writer.writerow([
            city,
            state,
            state.lower().replace(' ', '-').replace('&', 'and'),
            city.lower().replace(' ', '-').replace('&', 'and')
        ])
