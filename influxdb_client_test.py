from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import random
# You can generate a Token from the "Tokens Tab" in the UI
token = "6GqhhbHug0P1ewJLlvyXwkRXwc9pgxGiRNz-T__7rkYgm4Ya771qCHdC7HhNTltLmon2U7YIQzP50yXK0wXNTQ=="
org = "tpdp"
bucket = "db"

client = InfluxDBClient(url="http://192.168.4.23:8086", token=token)

write_api = client.write_api(write_options=SYNCHRONOUS)


# for n in range(300):
#     num = random.randint(0, 100) * 1.0
#     data = "mem,host=host1 used_percent="+str(num)
#     write_api.write(bucket, org, data)

dbs = client.get_list_database()

#for better format
list = []
for db in dbs:
    list.append(db.get('name'))
