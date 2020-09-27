#!/usr/bin/env python3

import requests
import re

token = 'dbccac2b303dc8ed21da417f693f9f63'
city = 'Dnipro'
url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={token}'
response = requests.get(url).json()

response['weather'] = response['weather'][0]

# weather id, main, description
# name
# main temp feels_like

weather_dict = {
    'weather_icon': response['weather']['icon'],
    'weather_descr': response['weather']['description'],
    'city': response['name'],
    'temp': response['main']['temp'],
}

print(weather_dict)

# with open('weather_data.txt', 'w+') as data:
#     for key in response.keys():

#         data.write(f'{key} >> {response[key]} \n')
    


