from microdot_asyncio import send_file, redirect
from microdot_utemplate import render_template
from garden_data import plant_data
import urequests
import uos


# AWS Lambda endpoint for garden pictures
app_config = ConfigManager(filename='config.bin')

lambda_endpoint_gardenpic = app_config.LAMBDA_ENDPOINT_GARDENPIC

def setup_routes(app, garden):
    @app.route('/', methods=['GET', 'POST'])
    async def index(request):
        # Handle form submissions on the index page
        if request.method == 'POST':
            selected_plant = request.form.get('selected-plant')
            if selected_plant:
                # Update the selected plant type in the garden and save the configuration
                garden.plant_type = selected_plant
                garden.save_config()
            elif 'reset_garden' in request.form:
                # Reset the garden
                garden.reset()
            return redirect('/')
        
        try:
            # Check if the garden picture file exists
            uos.stat("/static/images/image.jpg")
            garden_pic = '/static/images/image.jpg'
        except:
            # Use a placeholder image if the file doesn't exist
            garden_pic = "https://hydropi.s3.us-east-2.amazonaws.com/images/coming_soon.jpeg"
            
        # Render the main template with garden data   
        return render_template('garden_template.html',
                               garden_pic=garden_pic,
                               plant_options=list(plant_data.keys()),
                               plant_type=garden.plant_type,
                               days_planted=garden.days_planted(),
                               temperature=garden.temperature()[1],  # [1] for F [0] for C
                               humidity=garden.humidity(),
                               pressure=garden.pressure(),
                               pico_temp=garden.internal_temp()[1],
                               water_temp=garden.thermistor_temp()[1],
                               light_percentage=garden.photoresistor_percent())
                               
    
    # Additional routes for data retrieval
    @app.route("/data")
    async def index(request):
        return render_template("data.html")


    @app.route("/sensorReadings")
    async def get_sensor_readings(request):
        # Retrieve sensor readings from the garden
        temperature = garden.temp
        pressure = garden.pres
        humidity = garden.hum
        water_temp = garden.temp_therm
        pico_temp = garden.internal_temp()[1]
        light_percentage = garden.photoresistor_percent()
        sensor_readings = {"status": "OK", "temperature": temperature, "pressure": pressure, "humidity": humidity,
                           "water_temp": water_temp, "pico_temp": pico_temp, "light_percentage": light_percentage}
    
        return sensor_readings


    @app.route("/gardenReadings")
    async def get_garden_readings(request):
        # Retrieve garden-related readings
        heater_on = 0
        if garden.temp_internal:
            heater_on = 0
        airpump_status = garden.airpump_status
        waterpump_status = garden.waterpump_status
        garden_readings = {"status": "OK", "airpump_on": airpump_status,"waterpump_on": waterpump_status, "heater_on": heater_on}
        return garden_readings

    # Route for serving static files
    @app.route('/static/<path:path>')
    async def static(request, path):
        if '..' in path:
            # directory traversal is not allowed
            return 'Not found', 404
        return send_file('static/' + path, max_age=86400)
    
    # Shutdown route
    @app.get('/shutdown')
    def shutdown(request):
        # Shutdown the server
        request.app.shutdown()
        return 'The server is shutting down...'
