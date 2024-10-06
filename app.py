from flask import Flask, render_template, request, send_file, jsonify
from src.utils import WRS2, LandsatAcquisition
import io
import matplotlib.pyplot as plt
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

schedule = LandsatAcquisition()
wrs2 = WRS2()

@app.route('/plot.png')
def plot():
    longitude = request.args.get('long', default=0, type=float)
    latitude = request.args.get('lat', default=0, type=float)

    # Generate the plot
    fig, ax = plt.subplots()
    ax.plot([longitude, longitude, longitude], [latitude, latitude, latitude], [4, 2, 3])
    ax.set_title('Sample Plot')

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()

        longitude = data.get('longitude')
        latitude = data.get('latitude')
        
        result = __get_next_acquisition_date(longitude, latitude)
        img = f'<img id="img-grid" src="/plot.png?long={longitude}&lat={latitude}" alt="Generated Plot">'

        rendered_table = render_template('table.html', result=result, img=img)
        return jsonify({'html': rendered_table, 'img':img})

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

    next_acq_dates = {}

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
