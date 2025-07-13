from confluent_kafka import Producer, Consumer
import requests
import json
import time
from datetime import datetime,timedelta,timezone


def read_config():
  # reads the client configuration from client.properties
  # and returns it as a key-value map
  config = {}
  with open("client.properties") as fh:
    for line in fh:
      line = line.strip()
      if len(line) != 0 and line[0] != "#":
        parameter, value = line.strip().split('=', 1)
        config[parameter] = value.strip()
  return config

def produce(topic, config):
  # creates a new producer instance
  producer = Producer(config)
  today = None
  read = 0
  while(True):
   utc_today = datetime.now(timezone.utc)
   day = utc_today.date()
   print(day)
   if(today!=day):
     today=day
     read=0
  
   tomorrow = today + timedelta(days=1)

# Format the date as YYYY-MM-DD
   today_date = today.strftime("%Y-%m-%d")
   tom_date = tomorrow.strftime("%Y-%m-%d")

   print(today_date,tom_date)
 
   response = requests.get(f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={today_date}&endtime={tom_date}")
   res=json.loads(response.text)
   to_read=res['metadata']['count']-read
   sorted_res = sorted(res['features'], key=lambda eth: eth['properties']['time'], reverse=True)
   
  # produces a sample message
   for i in range(to_read):
    key=sorted_res[i]['id']
    dt=datetime.fromtimestamp(sorted_res[i]['properties']['time']/1000)
    eq_time=dt.time()
    val=f"{sorted_res[i]['properties']['place']}|{sorted_res[i]['properties']['mag']}|{sorted_res[i]['geometry']['coordinates'][0]}|{sorted_res[i]['geometry']['coordinates'][1]}|{today}|{eq_time}"
    print(key,val)
    producer.produce(topic, key=sorted_res[i]['id'], value=val)
    print(f"Produced message to topic {topic}: key = {key} value = {val}")
    producer.flush()
   read = res['metadata']['count']
   time.sleep(3*60)
  # send any outstanding or buffered messages to the Kafka broker
  

def consume(topic, config):
  # sets the consumer group ID and offset
  config["group.id"] = "python-group-1"
  config["auto.offset.reset"] = "earliest"

  # creates a new consumer instance
  consumer = Consumer(config)

  # subscribes to the specified topic
  consumer.subscribe([topic])

  try:
    while True:
      # consumer polls the topic and prints any incoming messages
      msg = consumer.poll(1.0)
      if msg is not None and msg.error() is None:
        key = msg.key().decode("utf-8")
        value = msg.value().decode("utf-8")
        print(f"Consumed message from topic {topic}: key = {key:12} value = {value:12}")
  except KeyboardInterrupt:
    pass
  finally:
    # closes the consumer connection
    consumer.close()

def main():
  config = read_config()
  topic = "Earthquakes"

  produce(topic, config)
  #consume(topic, config)


main()