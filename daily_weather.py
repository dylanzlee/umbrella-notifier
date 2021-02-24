import os
from twilio.rest import Client
import requests
import datetime
import pytz

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
source = os.getenv("TWILIO_TRIAL_NUMBER_1")
recipient = os.getenv("US_NUMBER")
client = Client(account_sid, auth_token)

weather_api_key = os.getenv("OPENWEATHER_API_KEY")

city_name, city_id = "Nashville", "4644585"
city_lon, city_lat = "-86.784439", "36.16589"

unit_type = "metric"
temp_type = {"metric": "°C", "imperial": "°F", "kelvin": "K"}

api_call = f"https://api.openweathermap.org/data/2.5/onecall?lat={city_lat}&lon={city_lon}&units={unit_type}" \
           f"&exclude=minutely,current&appid={weather_api_key}"


def convertToReadableTime(unix_time):
    if type(unix_time) is not int:
        unix_time = int(unix_time)
    return datetime.datetime.fromtimestamp(unix_time).strftime("%I:%M%p")


# Make API call
status_code = requests.get(api_call)
c = status_code.json()

# Extract the data

# Times for sunrise and sunset
sunrise_time = convertToReadableTime(c["daily"][0]["sunrise"])
sunset_time = convertToReadableTime(c["daily"][0]["sunset"])
if sunrise_time[0] == '0':
    sunrise_time = sunrise_time[1:]
if sunset_time[0] == '0':
    sunset_time = sunset_time[1:]

# Max and Min temps
max_temp = c["daily"][0]["temp"]["max"]
min_temp = c["daily"][0]["temp"]["min"]

tz = pytz.timezone('America/Chicago')
hour = int(datetime.datetime.now(tz=tz).strftime("%H"))
if hour < 12:
    greeting_time = 'morning'
elif hour >= 12 and hour < 18:
    greeting_time = 'afternoon'
else:
    greeting_time = 'evening'

# Determine whether there will be rain or not
weather_today = {i: c['hourly'][i]['weather']
                 [0]['description'] for i in range(48)}
some_rain = []
for j in range(len(weather_today)):
    if 'rain' in weather_today[j] or 'RAIN' in weather_today[j]:
        some_rain.append(j)        # j = 30-minute block where it will rain

# Rain/No rain messages
if len(some_rain) > 0:
    rain_message = "You can expect some rainfall today, so check the weather app for specific times to bring your umbrella out!"
else:
    rain_message = "The forecast indicates that there will be no rain today"


weather_update = f"""Good {greeting_time} in {city_name}! Here is your daily weather update for {datetime.date.today().strftime('%A')}, {datetime.datetime.today().strftime("%B %d")}:
\nThe sun will rise at {sunrise_time} and will set at {sunset_time}.
\nThe coldest it will be today is {min_temp}{temp_type[unit_type]} while temperatures will cap at {max_temp}{temp_type[unit_type]}.
\n{rain_message}
\nThat is all for now. Have a great day and see you tomorrow!
"""

message = client.messages.create(
    to=recipient,
    from_=source,
    body=weather_update)

print(message.sid)
