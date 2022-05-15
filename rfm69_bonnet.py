import time
import datetime
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_ssd1306
import adafruit_rfm69
import requests
import pyrebase


def weather_api_data(locale, open_weather_map_api_key, isTest):
    
    weather_response = ''
    
    if isTest:
        weather_response = 'locale=Ontario,CA,"pressure":1020'
        
    else:
        # Open Weather Map API data
        response = requests.get("https://api.openweathermap.org/data/2.5/weather?q=" + locale + "&appid=" + open_weather_map_api_key)
        
        weather_response = response.text
    
    # Putting the response into a list, where the first item is text before pressure and the second item is after pressure
    weather_list = weather_response.split('"pressure":')
    
    # Removing first item from list
    weather_list.pop(0)
    
    # Converting list to string
    weather_text_string = ''.join(weather_list)
    
    # Dividing string by comma, which converts the string to list
    text_split = weather_text_string.split(",", 1)
    
    # Printing the pressure, the first item in the list
    sea_level_pressure = text_split[0]
    
    # Returning sea level pressure for use in altitude calculation
    return sea_level_pressure
    

# Using this formula: 44,300 * [1-(local_pressure/sea_level_pressure)^(1/5.255)] altitude is received from pressure
def pressure_to_altitude(local_pressure, sea_level_pressure):

    # Dividing the sea level pressure
    pressure_divided = int(local_pressure) / int(sea_level_pressure)
    
    # Bringing in power
    power = 1 / 5.255

    # Setting pressure to the power
    pressure_to_the_power = pressure_divided**power

    # Minus pressure from one
    minus_from_one = 1 - pressure_to_the_power

    # Multiplying by constant
    altitude = 44330 * minus_from_one
    
    altitude = round(altitude, 0)
    
    # Converting altitude int to string
    altitude = str(altitude)
    
    # Returning altitude to use in database
    return altitude


def token_refresh(data: dict, user, node_id, epoch_time):
        
    # The token expires every hour, it will fail to write. Once refreshed it will work again 
    try:
        # sasgPRBqdwQdgr9jCXIF82qFYjA2 is the account id and a cell, which is used for Firebase authentication
        db.child("BaseCamps").child("sasgPRBqdwQdgr9jCXIF82qFYjA2").child(node_id).child(epoch_time).set(data, user['idToken'])
    except:
        user = auth.refresh(user['refreshToken'])
        db.child("BaseCamps").child("sasgPRBqdwQdgr9jCXIF82qFYjA2").child(node_id).child(epoch_time).set(data, user['idToken'])
       
       
def run():
    while True:
        packet = None
        # draw a box to clear the image
        display.fill(0)
        display.text('Emanate Radio', 35, 0, 1)

        # check for packet rx (receive)
        packet = rfm69.receive()
        if packet is None:
            display.show()
            display.text('Waiting for packet..', 1, 20, 1)
        else:
            # Display the packet text and rssi
            display.fill(0)
            prev_packet = packet
            packet_text = str(prev_packet, "utf-8")
            packet_array = packet_text.split(",")
            
            # Packet Data
            temperature = packet_array[0]
            local_pressure = packet_array[1]
            gas = packet_array[2]
            humidity = packet_array[3]
            node_id = packet_array[4]
            
            sea_level_pressure = weather_api_data(locale, open_weather_map_api_key, isTest)
        
            altitude = pressure_to_altitude(local_pressure, sea_level_pressure)
            
            packet_received = bytes("Packet received from node " + node_id, "utf-8")
            print(packet_received)
            rfm69.send(packet_received)
            
            print("—————————————-")
            print("Data is being sent to Firebase with the master radio")
            print("—————————————-")
           
            # This is the data that is being written to Firebase
            data = {
                "locale": locale,
                "altitude": altitude,
                "temperature": temperature,
                "localPressure": local_pressure,
                "gas": gas,
                "humidity": humidity,
                "nodeId": node_id
            }
            
            # This will be the time of the packet event. It is a timestamp to be set as a cell in the database
            epoch_time = int(time.time())
            date_time = datetime.datetime.fromtimestamp(epoch_time)
            
            # These are metrics that I think are important from the sensor, it may be subjective
            important_metrics = altitude + " " + temperature + " " + humidity  
            
            token_refresh(data, user, node_id, epoch_time)
            
            # Display the important metrics on the master radio display when they are recieved
            display.text("NODE ID " + node_id + " METRICS", 0, 0, 1)
            display.text(important_metrics, 1, 20, 1)
            print(important_metrics)
            time.sleep(0.5)

        display.show()
        time.sleep(0.1)
    
if __name__ == "__main__":
    
    # Variable for testing purposes
    isTest = False
    
    print("Running")
    
    config = {
      "apiKey": "FILL",
      "authDomain": "FILL",
      "databaseURL": "FILL",
      "storageBucket": "FILL"
    }

    # Reference to database service
    firebase = pyrebase.initialize_app(config)

    # Reference to authentication service
    auth = firebase.auth()
    
    # Credentials
    email = "FILL"
    password = "FILL"
    
    # Applying credentials to Firebase
    user = auth.sign_in_with_email_and_password(email, password)

    db = firebase.database()
    
    # Current Locale of Expedition. Must be in format "City,Country code"
    locale = "Dublin,IE"
    
    # Open Weather Map API key
    open_weather_map_api_key = "FILL"

    # Creating the I2C interface
    i2c = busio.I2C(board.SCL, board.SDA)

    # OLED display
    reset_pin = DigitalInOut(board.D4)
    display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)

    # Clearing the display.
    display.fill(0)
    display.show()
    width = display.width
    height = display.height

    # Configure the packet radio (Frequency 433MHz)
    CS = DigitalInOut(board.CE1)
    RESET = DigitalInOut(board.D25)
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, 433.0)
    prev_packet = None
    
    run()