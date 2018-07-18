import datetime
import json
import urllib.request

class API:

    def time_converter(time):
        converted_time = datetime.datetime.fromtimestamp(
            int(time)
        ).strftime('%I:%M %p')
        return converted_time


    def url_builder(city_id):
        user_api = 'bfc33ad91247a3daeac7bf4cebc3c3cb'  # Obtain yours form: http://openweathermap.org/
        unit = 'metric'  # For Fahrenheit use imperial, for Celsius use metric, and the default is Kelvin.
        api = 'http://api.openweathermap.org/data/2.5/weather?id='     # Search for your city ID here: http://bulk.openweathermap.org/sample/city.list.json.gz

        full_api_url = api + str(city_id) + '&mode=json&units=' + unit + '&APPID=' + user_api
        return full_api_url


    def data_fetch(full_api_url):
        url = urllib.request.urlopen(full_api_url)
        output = url.read().decode('utf-8')
        raw_api_dict = json.loads(output)
        url.close()
        return raw_api_dict


    def data_organizer(raw_api_dict):
        data = dict(
            city=raw_api_dict.get('name'),
            country=raw_api_dict.get('sys').get('country'),
            temp=raw_api_dict.get('main').get('temp'),
            temp_max=raw_api_dict.get('main').get('temp_max'),
            temp_min=raw_api_dict.get('main').get('temp_min'),
            humidity=raw_api_dict.get('main').get('humidity'),
            pressure=raw_api_dict.get('main').get('pressure'),
            sky=raw_api_dict['weather'][0]['main'],
            sunrise=time_converter(raw_api_dict.get('sys').get('sunrise')),
            sunset=time_converter(raw_api_dict.get('sys').get('sunset')),
            wind=raw_api_dict.get('wind').get('speed'),
            wind_deg=raw_api_dict.get('deg'),
            dt=time_converter(raw_api_dict.get('dt')),
            cloudiness=raw_api_dict.get('clouds').get('all')
        )
        return data


    def data_output(data):
        return data['temp']

"""
if __name__ == '__main__':
    try:
        temp = data_output(data_organizer(data_fetch(url_builder(1277333))))
        print(temp)
    except IOError:
        print('no internet')
"""