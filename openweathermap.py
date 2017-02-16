import configparser
import requests
import json
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
from requests.exceptions import ConnectionError

config = configparser.ConfigParser()
config.read('config.ini')

delay = config['GENERAL']['Delay']
output = config['GENERAL'].get('Output', fallback=True)

influxAddress = config['INFLUXDB']['Address']
influxPort = config['INFLUXDB']['Port']
influxDatabase = config['INFLUXDB']['Database']
influxUser = config['INFLUXDB'].get('Username', fallback='')
influxPassword = config['INFLUXDB'].get('Password', fallback='')

cityid = config['OPENWEATHERMAP']['Location']
weatherapikey = config['OPENWEATHERMAP']['APIKey']

influx_client = InfluxDBClient(influxAddress, influxPort, influxUser, influxPassword, influxDatabase)

def getWeatherData(cityid):
    
    requestURL = 'http://api.openweathermap.org/data/2.5/weather?id=' + str(cityid) + '&APPID=' + weatherapikey
    
    response = requests.get(requestURL)
    
    return response.json()
    
def sendInfluxData(json_data):
        
        if output:
            print(json_data)
            
        try:
            influx_client.write_points(json_data)
        except (InfluxDBClientError, ConnectionError, InfluxDBServerError) as e:
            if hasattr(e, 'code') and e.code == 404:

                print('Database {} Does Not Exist.  Attempting To Create'.format(influxDatabase))

                influx_client.create_database(influxDatabase)
                influx_client.write_points(json_data)

                return

            print('ERROR: Failed To Write To InfluxDB')
            print(e)

        if output:
            print('Written To Influx: {}'.format(json_data))
            
            
def main():
    sendInfluxData(getWeatherData(cityid))
    
if __name__ == '__main__':
    main()