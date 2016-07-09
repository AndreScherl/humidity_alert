# coding=utf-8
import RPi.GPIO as GPIO
import Adafruit_DHT
from threading import Timer
import os, time
import json
#please read tutorial at http://home-automation-community.com/temperature-and-humidity-from-am2302-dht22-sensor-displayed-as-chart/

#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

# Set the pins working as electrodes switched by water if its level increases
# set pin 24 to use internal pull up resitor
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# the callback of electrodes short-circuit event
def water_alert(channel):
    print "The water level increased!"

# set the callback to pin event
GPIO.add_event_detect(24, GPIO.RISING, callback=water_alert)

# Get continuous sensor data (temperature and humidity) and show/store them
# pin 4 will be used to get DHT sensor data
sensor = Adafruit_DHT.AM2302
pin = 4
# set corrct timezone
os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

def process_sensor_values():
	# Try to grab a sensor reading.  Use the read_retry method which will retry up
	# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
	if humidity is not None and temperature is not None:
		# write data to csv file
		stringtowrite = ''
		timestring = time.strftime('%Y-%m-%d %H:%M:%S')
		if os.path.exists('tdh-data.csv'):
			stringtowrite = '{0};{1:0.1f};{2:0.1f}\n'.format(timestring, temperature, humidity)
		else:
			stringtowrite = 'time;Temperature[°C];Humidity[%]\n{0};{1:0.1f};{2:0.1f}\n'.format(timestring, temperature, humidity)
		with open('tdh-data.csv', 'a') as csvfile:
			csvfile.write(stringtowrite)

		# write current values into json
		with open('tdh_current_values.json', 'w') as jsonfile:
			# jsonstring = '\'time\': {0}, \'temperature\': {1:0.1f}, \'humidity\': {2:0.1f}'.format(timestring, temperature, humidity)
			jsonstring = json.dumps({'time': timestring, 'temperature': temperature, 'humidity': humidity});
			jsonfile.write(jsonstring);
	else:
	    print('Failed to get reading. Try again!')

	Timer(1*60.0, process_sensor_values).start()

Timer(0, process_sensor_values).start()

GPIO.cleanup()
