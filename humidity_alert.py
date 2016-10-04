# coding=utf-8
import RPi.GPIO as GPIO
import Adafruit_DHT
from threading import Timer
import os, time
import json
from rpi_rf import RFDevice

# Set up pins for water level detection switches
def setup_level_pins():
	#set up GPIO using BCM numbering
	GPIO.setmode(GPIO.BCM)

	# Set the pins working as electrodes switched by water if its level increases
	# set pin 22, 23, 24 to use internal pull up resitor
	GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Get continuous sensor data (temperature and humidity) and show/store them
# pin 4 will be used to get DHT sensor data
sensor = Adafruit_DHT.AM2302
pin = 4
# set corrct timezone
os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

# set the file directory to absolute path
dirpath = os.path.dirname(os.path.abspath(__file__))

# set up the 433Mhz sender
rfdevice = RFDevice(17)
rfdevice.enable_tx()
pulselength = 350
protocol = 1

def process_sensor_values():
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
	setup_level_pins()
	level1 = not GPIO.input(22)
	level2 = not GPIO.input(23)
	level3 = not GPIO.input(24)

	if (humidity and temperature and level1 and level2 and level3) is not None:
		# write data to csv file
		stringtowrite = ''
		timestring = time.strftime('%Y-%m-%d %H:%M:%S')
		if os.path.exists(dirpath + '/tdh-data.csv'):
			stringtowrite = '{0};{1:0.1f};{2:0.1f};{3};{4};{5}\n'.format(timestring, temperature, humidity, level1, level2, level3)
		else:
			stringtowrite = 'time;Temperature[°C];Humidity[%];Level1;Level2;Level3\n{0};{1:0.1f};{2:0.1f};{3};{4};{5}\n'.format(timestring, temperature, humidity, level1, level2, level3)
		with open(dirpath + '/tdh-data.csv', 'a') as csvfile:
			csvfile.write(stringtowrite)

		# write current values into json
		with open(dirpath + '/tdh_current_values.json', 'w') as jsonfile:
			jsonstring = json.dumps({'time': timestring, 'temperature': temperature, 'humidity': humidity, 'level1': level1, 'level2': level2, 'level3': level3});
			jsonfile.write(jsonstring);

		# check if dehumidifier has to be switched on
		if (humidity > 50):
			rfdevice.tx_code(5242961, protocol, pulselength)
			print('Switch on')
		else:
			rfdevice.tx_code(5242964, protocol, pulselength)
			print('Switch off')

	else:
	    print('Failed to get reading. Try again!')

	Timer(1, process_sensor_values).start()

Timer(0, process_sensor_values).start()
