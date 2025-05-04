import json
import csv

json_file_path = 'city_name.json'
csv_file_path = 'city_name.csv'


def json_to_csv(json_file_path, csv_file_path):
    """
    Convert a JSON file containing city data to a CSV file with specific formatting.

    Args:
        json_file_path (str): Path to the input JSON file
        csv_file_path (str): Path to the output CSV file

    The function will:
    - Read the JSON file
    - Convert it to CSV with columns 'city_name' and 'state_name'
    - Convert all names to lowercase
    - Replace spaces with hyphens in names
    """

    try:
        # Read the JSON file
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        # Process the data and prepare rows for CSV
        csv_rows = []
        for item in data:
            city_name = item['name'].lower().replace(' ', '-')
            state_name = item['state'].lower().replace(' ', '-')
            csv_rows.append({'city_name': city_name, 'state_name': state_name})

        # Write to CSV file
        with open(csv_file_path, 'w', newline='') as csv_file:
            fieldnames = ['city_name', 'state_name']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(csv_rows)

        print(f"Successfully converted {json_file_path} to {csv_file_path}")

    except FileNotFoundError:
        print(f"Error: The file {json_file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {json_file_path} contains invalid JSON.")
    except KeyError as e:
        print(f"Error: Missing expected key in JSON data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Example usage:
if __name__ == "__main__":
    json_to_csv(json_file_path, csv_file_path)
    # You can call the function with different file paths if needed
    # json_to_csv('path/to/your/input.json', 'path/to/your/output.csv')
