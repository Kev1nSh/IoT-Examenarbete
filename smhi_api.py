import requests
import json
import time 
from datetime import datetime, timedelta


SMHI_API_URL = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/18.063240/lat/59.334591/data.json'

# Preceptetation category, min fråga är om vi behöver denna då vi har wsymb2 som visar vad det är för väder
pcat_meanings = {
    0: 'none',
    1: 'snow',
    2: 'snow and rain',
    3: 'rain',
    4: 'drizzle',
    5: 'freezing rain',
    6: 'freezing drizzle'
}
# Weather symbol category
wsymb2_meanings = {
    1: 'clear sky',
    2: 'nearly clear sky',
    3: 'variable cloudiness',
    4: 'halfclear sky',
    5: 'cloudy sky',
    6: 'overcast',
    7: 'fog',
    8: 'light rain showers',
    9: 'moderate rain showers',
    10: 'heavy rain showers',
    11: 'thunderstorm',
    12: 'light sleet showers',
    13: 'moderate sleet showers',
    14: 'heavy sleet showers',
    15: 'light snow showers',
    16: 'moderate snow showers',
    17: 'heavy snow showers',
    18: 'light rain',
    19: 'moderate rain',
    20: 'heavy rain',
    21: 'thunder',
    22: 'light sleet',
    23: 'moderate sleet',
    24: 'heavy sleet',
    25: 'light snowfall',
    26: 'moderate snowfall',
    27: 'heavy snowfall'
}



def fetch_data():
    """Hämtar väderdata från SMHI:s API."""
    
    response = requests.get(SMHI_API_URL)
    
    if response.status_code != 200:
        print(f'Failed to get data: {response.status_code}')
        return None
    else:
        data = response.json()
        return data
    

def filter_data(data):
    """Filtrerar data och returnerar en lista med relevanta uppgifter."""

#Fokus är att om det ska regna då ska vi få en notis om det
#Fokus också på temperaturen då vi vill veta om det är kallt eller varmt och om vi ska ha på oss en stor jacka eller en tunn jacka

    desired_wysimb2_rain = {8, 9, 10, 18, 19, 20}
    desired_pcat_rain = {2, 3, 4, 6} # Kanske inte behövs
    
    desired_wysimb2_snow = {15, 16, 17, 25, 26, 27}
    desired_pcat_snow = {1, 2} # Kanske inte behövs

    checked_parameters = [] # Kanske tas bort då jag vet inte om jag ska implementera ett extra funktion

    #Parameter för temperatur är t 
    
    going_to_rain = False
    going_to_snow = False
    temperature = None

    current_time = datetime.now()
    one_hour_later = current_time + timedelta(hours=1)

    nearest_rain_time = None
    nearest_snow_time = None
    

    for time_series in data.get('timeSeries', []):
        forecast_time = datetime.strptime(time_series['validTime'], '%Y-%m-%dT%H:%M:%SZ')
        
        if forecast_time <= current_time or forecast_time > one_hour_later: # Kollar bara på prognoser som är inom en timme eller som händer nu
            continue
        
        for parameter in time_series.get('parameters', []):
            if parameter.get('name') in ['t', 'pcat', 'Wsymb2']:
                checked_parameters.append(parameter) # Sparar alla parametrar som vi är intresserade av # Kanske inte behövs då jag vet inte om jag ska implementera ett extra funktion 

                if parameter.get('name') == 'pcat' and parameter['values'][0] in desired_pcat_rain:
                    if nearest_rain_time is None or forecast_time < nearest_rain_time:
                        nearest_rain_time = forecast_time
                        #break # Detta rad kanske inte behövs 

                elif parameter.get('name') == 'Wsymb2' and parameter['values'][0] in desired_wysimb2_rain:    
                    if nearest_rain_time is None or forecast_time < nearest_rain_time:
                        nearest_rain_time = forecast_time
                        #break # Detta rad kanske inte behövs 

                elif parameter.get('name') == 'pcat' and parameter['values'][0] in desired_pcat_snow:
                    if nearest_rain_time is None or forecast_time < nearest_rain_time:
                        nearest_rain_time = forecast_time
                        #break # Detta rad kanske inte behövs 

                elif parameter.get('name') == 'Wsymb2' and parameter['values'][0] in desired_wysimb2_snow:    
                    if nearest_snow_time is None or forecast_time < nearest_snow_time:
                        nearest_snow_time = forecast_time
                        #break # Detta rad kanske inte behövs 
                elif parameter.get('name') == 't':
                    temperature = parameter['values'][0]

    if nearest_rain_time and current_time <= nearest_rain_time <= one_hour_later:
        going_to_rain = True
    
    if nearest_snow_time and current_time <= nearest_snow_time <= one_hour_later:
        going_to_snow = True

    return going_to_rain, going_to_snow, temperature
    """ # Vet inte om jag ska returnera en dictionary eller separata variabler
        return {
        'going_to_rain': going_to_rain,
        'going_to_snow': going_to_snow,
        'temperature': temperature
       }
    """


def test_filter_data():
    mock_data = {
        "timeSeries": [
            {
                "validTime": (datetime.now() + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "parameters": [
                    {"name": "t", "values": [12]},
                    {"name": "pcat", "values": [0]},
                    {"name": "Wsymb2", "values": [1]}
                ]
            },
            {
                "validTime": (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "parameters": [
                    {"name": "t", "values": [10]},
                    {"name": "pcat", "values": [3]},
                    {"name": "Wsymb2", "values": [9]}
                ]
            }
        ]
    }

    going_to_rain, going_to_snow, temperature = filter_data(mock_data)
    print(f"Going to rain: {going_to_rain}")
    print(f"Going to snow: {going_to_snow}")
    print(f"Temperature: {temperature}°C")

if __name__ == "__main__":
    test_filter_data()

    

      

    