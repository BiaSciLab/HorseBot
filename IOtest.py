"""
'HorseBot'

Author(s): BiaSciLab, based on Analog In from Adafruit

Dependencies:
    - Adafruit_Blinka
        (https://github.com/adafruit/Adafruit_Blinka)
    - Adafruit_CircuitPython_MCP3xxx
        (https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx)
"""
# Import standard python modules
import time

# import Adafruit Blinka
import board
import digitalio
import busio

# import Adafruit IO REST client
from Adafruit_IO import Client, Feed, RequestError

# import Adafruit CircuitPython MCP3xxx library
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = '0ca65ae2145c4d1a9cf55393fe513685'

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = 'BiaSciLab'
# Create an instance of the REST client
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

try: # if we have a 'analog' feed
    analog = aio.feeds('waterlevel')
except RequestError: # create a analog feed
    feed = Feed(name='waterlevel')
    analog = aio.create_feed(feed)

# Create an instance of the `busio.spi` class
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D22)

# create a mcp3008 object
mcp = MCP.MCP3008(spi, cs)

# create an an adc (single-ended) on pin 0
chan = AnalogIn(mcp, MCP.P0)

def remap_range(value, low_min, low_max, high_min, high_max):
    # this remaps a value from original (low) range to new (high) range
    # Figure out how 'wide' each range is
    low_span = low_max - low_min
    high_span = high_max - high_min

    # Convert the low range into a 0-1 range (int)
    valueScaled = int(value - low_min) / int(low_span)

    # Convert the 0-1 range into a value in the high range.
    return int(high_min + (valueScaled * high_span))

while True:
    sensor_data = chan.value

    water_volume = remap_range(sensor_data, 0, 65535, 0, 100)

    print('Analog Data -> ', sensor_data)
    aio.send(analog.key, sensor_data)

    # avoid timeout from adafruit io
    time.sleep(10)
