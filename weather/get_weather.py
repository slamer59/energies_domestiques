from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
import time
import requests
import logging

from decouple import config
from urllib.parse import urlparse
import influxdb_client

logging.basicConfig(level=logging.INFO)
# from influxdb_client.client.write_api import SYNCHRONOUS
API_KEY = config("API_KEY")
CITY = config("CITY")
INFLUXDB_URL = config("INFLUXDB_URL")
parsed_uri = urlparse(INFLUXDB_URL)
# host = '{uri.scheme}://{uri.hostname}'.format(uri=parsed_uri)
host = '{uri.hostname}'.format(uri=parsed_uri)
port = parsed_uri.port
INFLUXDB_ADMIN_USER = config("INFLUXDB_ADMIN_USER")
INFLUXDB_ADMIN_PASSWORD = config("INFLUXDB_ADMIN_PASSWORD")
INFLUXDB_DB = config("INFLUXDB_DB")

# from influxdb_client.client.write_api import SYNCHRONOUS
# bucket = "energie"
# org = "tpdp"
# token = "CUYsq3pBdRXG5XEui8ljOtW-__Wg2Sb7QpoU-P_rVNxZLR7RkyPWsTa92x_ntPmjVMt_1wMP_0q_BWX8b_k1KA=="

# Store the URL of your InfluxDB instance
# url=INFLUXDB_URL

# client = influxdb_client.InfluxDBClient(
#    url=url,
#    token=token,
#    org=org
# )
# write_api = client.write_api(write_options=SYNCHRONOUS)
client = InfluxDBClient(
    host, int(port), INFLUXDB_ADMIN_USER, INFLUXDB_ADMIN_PASSWORD, INFLUXDB_DB
)
client.switch_database(INFLUXDB_DB)
# logging.info(host, int(port), INFLUXDB_ADMIN_USER, INFLUXDB_ADMIN_PASSWORD, INFLUXDB_DB)
# https://public.opendatasoft.com/api/records/1.0/search/?dataset=donnees-synop-essentielles-omm&q=&sort=date&facet=date&facet=nom&facet=temps_present&facet=libgeo&facet=nom_epci&facet=nom_dept&facet=nom_reg&refine.nom_reg=Occitanie&refine.libgeo=Blagnac
while 1:
    response = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=%s" % (CITY, API_KEY)
    )
    
    timenow = time.asctime(time.localtime(time.time()))
    logging.info(timenow)
    logging.info("Status: %s" % response.status_code)
    jsonobj = response.json()
    # logging.info(jsonobj)
    t_city = jsonobj["name"]
    t_country = jsonobj["sys"]["country"]
    t_type = jsonobj["weather"][0]
    t_type = t_type["main"]
    t_temp = jsonobj["main"]["temp"] - 273.15
    t_temp = round(t_temp)
    t_humidity = jsonobj["main"]["humidity"]
    t_wind = jsonobj["wind"]["speed"]
    t_wind = round(t_wind)
    speed_deg = jsonobj["wind"]["deg"]
    pressure = jsonobj["main"]["pressure"]
    
    bjson_body = [
        {
            "measurement": "weather",
            "tags": {"city": t_city, "country": t_country},
            "fields": {
                "type": t_type,
                "temp": t_temp,
                "humidity": t_humidity,
                "pressure": pressure,
                "wind": t_wind,
                "wind_dir": speed_deg
            },
        }
    ]
    
    
    client.write_points(bjson_body)
    logging.info("Write done")
    time.sleep(600)
