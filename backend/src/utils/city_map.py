import csv


def load_city_url_map(filename: str = '../data_files/city_name.csv') -> dict:
    city_url_map = {}
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            city_key = row['city_name'].lower().strip()
            state_path = row['state_name'].lower().replace(' ', '-')
            city_path = row['city_name'].lower().replace(' ', '-')
            city_url_map[city_key] = (state_path, city_path)

    # Manual corrections
    city_url_map.update({
        "chandigarh": ("chandigarh", "chandigarh"),
        "bangalore": ("karnataka", "bengaluru"),
        "puducherry": ("puducherry", "pondicherry"),
        "noida": ("uttar-pradesh", "noida"),
        "gurgaon": ("haryana", "gurugram")
    })

    return city_url_map
