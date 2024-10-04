from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Save the map as an HTML file
    if request.method == 'POST':
        # Get the user input from the form
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')

        result = __get_next_acquisition_date(longitude, latitude)

        return render_template('index.html', result=result)
    return render_template('index.html', result=None)

def __request_landsat_cycle(satellite):
    url = "https://landsat.usgs.giv/sites/default/files/landsat_acq/assets/json/cycles_full.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
    else:
        return None

def __get_next_acquisition_date(longitude, latitude):
    url = "https://landsat.usgs.gov/sites/default/files/landsat_acq/assets/json/cycles_full.json"

    # Send the GET request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
    # Parse the response as JSON
        data = response.json()
        print("Successfully retrieved data!")
        print(data['landsat_9'])  # Replace 'key' with the specific key you want to access
        data = data['landsat_9']
    else:
        print(f"Error: {response.status_code}")

    return """
    <tr>
        <td>Landsat 8</td>
        <td>2023-03-15</td>
        <td><input type="checkbox"></td>
    </tr>
    <tr>
        <td>MODIS</td>
        <td>2023-03-20</td>
        <td><input type="checkbox"></td>
    </tr>
    <tr>
        <td>VIIRS</td>
        <td>2023-03-25</td>
        <td><input type="checkbox"></td>
    </tr> """

if __name__ == '__main__':
    app.run()
