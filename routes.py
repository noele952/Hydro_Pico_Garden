from microdot_asyncio import send_file, redirect
from microdot_utemplate import render_template
from data.garden_data import plant_data
import urequests


def get_garden_pic(garden):
    garden_pic = f"http://hydropi.s3.amazonaws.com/{garden.machine_id}/garden_pic.jpeg"
    coming_soon = "http://hydropi.s3.amazonaws.com/images/coming_soon.jpeg"
    response = urequests.head(garden_pic)
    print(response)
    print(response.status_code)
    if response.status_code == 200:
        picture_url = garden_pic
    else:
        picture_url = coming_soon
    return picture_url


def setup_routes(app, garden):
    @app.route('/', methods=['GET', 'POST'])
    async def index(request):
        print("in index")
        garden_pic = get_garden_pic(garden)
        if request.method == 'POST':
            # Check if a dynamic button is clicked
            selected_plant = request.form.get('selected-plant')
            if selected_plant:
                garden.plant_type = selected_plant
                garden.save_config()
            elif 'reset_garden' in request.form:
                garden.reset()
            return redirect('/')
        return render_template('garden_template.html',
                               garden_pic=garden_pic,
                               plant_options=list(plant_data.keys()),
                               plant_type=garden.plant_type,
                               days_planted=garden.days_planted(),
                               temperature=garden.temperature()[1],  # [1] for F [0] for C
                               humidity=garden.humidity(),
                               barometric_pressure=garden.pressure(),
                               pico_internal_temp=garden.internal_temp()[1],
                               thermistor_temp=garden.thermistor_temp()[1])
    
    @app.route("/data")
    async def index(request):
        return render_template("data.html")

    @app.route("/sensorReadings")
    async def get_sensor_readings(request):
        print("sensor readings")
        temperature = garden.temp
        pressure = garden.pres
        humidity = garden.hum
        water_temp = garden.temp_therm
        sensor_readings = {"status": "OK", "temperature": temperature, "pressure": pressure, "humidity": humidity, "water_temp": water_temp}
        return sensor_readings

    @app.route("/gardenReadings")
    async def get_garden_readings(request):
        print("in garden readings")
        heater_on = 0
        if garden.temp_internal:
            heater_on = 1
        airpump_status = garden.airpump_status
        waterpump_status = garden.waterpump_status
        garden_readings = {"status": "OK", "airpump_on": airpump_status,"waterpump_on": waterpump_status, "heater_on": heater_on}
        print(garden_readings)
        return garden_readings

    @app.route('/static/<path:path>')
    async def static(request, path):
        if '..' in path:
            # directory traversal is not allowed
            return 'Not found', 404
        return send_file('static/' + path, max_age=86400)
    

    @app.get('/shutdown')
    def shutdown(request):
        request.app.shutdown()
        return 'The server is shutting down...'
