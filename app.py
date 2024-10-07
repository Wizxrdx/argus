from flask import Flask, render_template, request, send_file, jsonify
from src.utils import WRS2, LandsatAcquisition
from src.sentinel_api import SentinelDataRetriever, display_image_from_list
import io
import matplotlib.pyplot as plt
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

client_id = 'sh-64233615-ff7d-48cb-837f-18b46b07e4ca'
client_secret = 'a8Su2H9C36qa3oaEXGDEe6MQLrGMuzgV'
token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
base_url = "https://sh.dataspace.copernicus.eu"

# Initialize the SentinelDataRetriever
sentinel_data_retriever = SentinelDataRetriever(client_id, client_secret, token_url, base_url)
schedule = LandsatAcquisition()
wrs2 = WRS2()

@app.route('/plot.png')
def plot():
    longitude = request.args.get('long', default=0, type=float)
    latitude = request.args.get('lat', default=0, type=float)
    band = request.args.get('band', default=0, type=int)

    band_data = sentinel_data_retriever.retrieve_band_data(longitude, latitude, time_interval=("2024-09-20", "2024-10-01"))
    image = display_image_from_list(band_data[band-1]['values'], brightness_factor=3.5/10000)

    img = io.BytesIO()
    image.save(img, format='PNG')  # You can specify the format (e.g., 'JPEG', 'PNG')
    img.seek(0)  # Go back to the beginning of the BytesIO ob

    return send_file(img, mimetype='image/png')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()

        longitude = data.get('longitude')
        latitude = data.get('latitude')
        
        result = __get_next_acquisition_date(longitude, latitude)
        band_data = sentinel_data_retriever.retrieve_band_data(longitude, latitude, time_interval=("2024-09-20", "2024-10-01"))

        header = ''
        values = ''
        for x in band_data:
            band = x['band']
            header += f'<th>{band}</th>'
            value = x['values'][1][1]
            values += f'<td>{value}</td>'

        band_data_html = '<table><tr>'
        band_data_html += f'{header}</tr>'
        band_data_html += f'<tr>{values}'
        band_data_html += '</tr></table>'

        img = render_template('radiobox.html', image=f'<img id="img-grid" src="/plot.png?long={longitude}&lat={latitude}&band=1" alt="Generated Plot">')
        rendered_table = render_template('table.html', result=result)

        return jsonify({'html': rendered_table, 'img':img, 'values': band_data_html})

    return render_template('index.html', result=None, img=None)

@app.route('/set_notification', methods=['POST'])
def set_notification():
    data = request.get_json()

    days = data.get('days')
    date = data.get('date')
    satellite = data.get('satellite')
    latitude = data.get('latitude')
    longitude = data.get('longitude')


    # Here, implement your logic to save the notification.
    if save_notification(days, date, satellite, latitude, longitude):
        return jsonify({'message': 'Notification set successfully!'}), 200
    else:
        return jsonify({'message': 'Failed to set notification!'}), 500

def save_notification(days, date, satellite, latitude, longitude):
    return True

def __get_next_acquisition_date(longitude, latitude):
    global wrs2, schedule

    path, row = wrs2.get_path_row(longitude, latitude)
    landsat8_schedules = schedule.get_next_acquisition_dates('landsat_8', path)
    landsat9_schedules = schedule.get_next_acquisition_dates('landsat_9', path)
    future_dates = sentinel_data_retriever.get_future_dates(longitude, latitude, 3)  # Get future dates for 1 month

    next_acq_dates = {}

    for date in future_dates:
        next_acq_dates[date] = 'Sentinel 2'

    for date in landsat8_schedules:
        next_acq_dates[date] = 'Landsat 8'

    for date in landsat9_schedules:
        next_acq_dates[date] = 'Landsat 9'

    html = ''

    for date, sat in next_acq_dates.items():
        html += '<tr>\n'
        html += f"<td style=\"text-align: left;\">{date}</td>\n"
        html += f"<td>{sat}</td>\n"
        html += f"<td><a href='#' data-date=\"{date}\"\
        data-satellite=\"{sat}\" class=\"popupButton\">Notify Me!</a></td>\n"
        html += '</tr>\n'

    return html

if __name__ == '__main__':
    app.run(debug=True)
