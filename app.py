from flask import Flask, render_template, request
import requests
import time

app = Flask(__name__)
time_last_acq_date_request = 0
landsat_cycles = {}

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
    if int(time.time()-time_last_acq_date_request) > 86400:
        url = "https://landsat.usgs.giv/sites/default/files/landsat_acq/assets/json/cycles_full.json"
        response = requests.get(url)
        if response.status_code == 200:
            landsat_cycles = data.response.json()

    dates = []

    for date, details in data.items():
        # Check if '116' is in the path list
        if '115' in details['path']:
            dates.append(date)
            latest_date = date

    return landsat_cycles[satellite]

def __get_next_acquisition_date(longitude, latitude):
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
