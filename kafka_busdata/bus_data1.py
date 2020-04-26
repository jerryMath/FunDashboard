from pykafka import KafkaClient
import time
import json
from datetime import datetime
import uuid


def generate_uuid():
    return uuid.uuid4()


input_file = open('./bus1.json')
json_array = json.load(input_file)

coordinates = json_array['features'][0]['geometry']['coordinates']

client = KafkaClient(hosts='localhost:9092')

topic = client.topics['busData']

producer = topic.get_sync_producer()

data = {}
data['busline'] = '00001'


def generate_checkpoint(coordinates):
    i = 0
    while i < len(coordinates):
        data['key'] = data['busline'] + '_' + str(generate_uuid())
        data['timestamp'] = str(datetime.utcnow())
        data['latitude'] = coordinates[i][1]
        data['longitude'] = coordinates[i][0]

        message = json.dumps(data)
        producer.produce(message.encode('ascii'))
        print(message)

        if i == len(coordinates) - 1:
            i = 0
        i += 1
        time.sleep(1)


generate_checkpoint(coordinates)
