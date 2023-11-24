
# Plant data dictionary that holds timing and temperature settings for a hydroponic garden

# Explanation of Parameters:
# - water_temp: Ideal water temperature for the plant (in degrees Fahrenheit)
# - waterpump_duration: Duration to run the water pump for the plant (in seconds)
# - waterpump_interval: Interval between water pump cycles for the plant (in seconds)
# - airpump_duration: Duration to run the air pump for the plant (in seconds)
# - airpump_interval: Interval between air pump cycles for the plant (in seconds)
plant_data = {
    "lettuce": {
        'waterpump_duration': 60,
        'waterpump_interval': 3540,
        'airpump_duration': 600,
        'airpump_interval': 1200,
        'image': 'lettuce.jpg'
    },
    "tomato": {
        'waterpump_duration': 60,
        'waterpump_interval': 3540,
        'airpump_duration': 600,
        'airpump_interval': 1200,
        'image': 'tomato.jpg'

    },
    "basil": {
        'waterpump_duration': 60,
        'waterpump_interval': 3540,
        'airpump_duration': 600,
        'airpump_interval': 1200,
        'image': 'basil.jpg'
    }
}