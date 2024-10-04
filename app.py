from flask import Flask, render_template, request
import requests
import time
from src.utils import WRS2

app = Flask(__name__)
time_last_acq_date_request = 0
landsat_cycles = {}
wrs2 = WRS2()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')

        result = __get_next_acquisition_date(longitude, latitude)

        return render_template('index.html', result=result)
    return render_template('index.html', result=None)

def __request_landsat_cycle(satellite):
    if int(time.time()-time_last_acq_date_request) > 86400:
        url = "https://landsat.usgs.gov/sites/default/files/landsat_acq/assets/json/cycles_full.json"
        response = requests.get(url)
        if response.status_code == 200:
            landsat_cycles = response.json()

    return landsat_cycles[satellite]

def __get_next_acquisition_date(longitude, latitude):
    landsat8_schedules = __request_landsat_cycle('landsat_8')
    landsat9_schedules = __request_landsat_cycle('landsat_9')
    path, row = wrs2.get_path_row(longitude, latitude)

    next_acq_dates = {}

    for date, details in landsat8_schedules.items():
        if str(path) in details['path']:
            next_acq_dates[date].append('Landsat 8')

    for date, details in landsat9_schedules.items():
        if str(path) in details['path']:
            next_acq_dates[date].append('Landsat 9')

    html = ''

    for date, sat in next_acq_dates.items():
        html += '<tr>\n'
        html += f"<td>{date}</td>\n"
        html += f"<td>{sat}</td>\n"
        html += '</tr>\n'

    return html

if __name__ == '__main__':
    app.run(debug=True)
