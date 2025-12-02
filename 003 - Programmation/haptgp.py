# Code provonant d'exemples, formation des fonctions 100% Humain
# Code global 90% Humain

# Bibliothèques standards
import math
import random
import time
import json
import requests

# Bibliothèques tierces
import RPi.GPIO as GPIO
from smbus2 import SMBus
import paho.mqtt.client as mqtt
import numpy as np

# Modules Adafruit / spécifiques au matériel
import adafruit_drv2605
import adafruit_ds3231
import adafruit_veml7700
import board
import busio
import cst816
import displayio
import neopixel
import pwmio
import terminalio
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_display_text.bitmap_label import Label
from adafruit_gc9a01a import GC9A01A
from fourwire import FourWire

client = None
THINGSBOARD_HOST = None
pixels = None
bme280 = None
veml7700 = None
display = None
drv = None
touch = None
buzzer = None
CENTER_X = 0
CENTER_Y = 0

#équation mathématique représentant la courbe de correction du luxmètre du HapTGP
#code correctLux() par Gemini 3.0 Pro
def correctLux(y):
    """
    Calculates the inverse x for the given y based on the cubic equation:
    y = 1E-09x^3 - 7E-05x^2 + 2.4252x + 81.592
    """
    # Constants derived from the original coefficients
    shift = 23333.33333333333
    p = 791866666.6666667
    
    # The 'q' term depends on y
    # q = q_base - 1e9 * y
    q_base = 31262184592592.586
    q_y_factor = -1000000000.0
    
    q = q_base + q_y_factor * y
    
    # Discriminant term: sqrt((q/2)^2 + (p/3)^3)
    inner_sqrt = np.sqrt((q / 2)**2 + (p / 3)**3)
    
    # Calculate the two terms for the cubic root
    term1 = -q / 2 + inner_sqrt
    term2 = -q / 2 - inner_sqrt
    
    # Compute cube roots (using np.cbrt handles negative numbers correctly)
    x = np.cbrt(term1) + np.cbrt(term2) + shift
    
    return x

def setupDRV():
    global drv
    i2c = busio.I2C(board.SCL, board.SDA)  # uses board.SCL and board.SDA
    drv = adafruit_drv2605.DRV2605(i2c)
    
def setupTouch():
    global touch
    # Pin Definitons:
    touch_rst_n = 17 # Touch Screen reset pin

    # Pin Setup:
    GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
    GPIO.setup(touch_rst_n, GPIO.OUT) # touch reset pin set as output

    # Initial state for touch screen reset pin
    GPIO.output(touch_rst_n, GPIO.HIGH)

    # Initialize I2C
    i2c = board.I2C()  # uses board.SCL and board.SDA
    touch = cst816.CST816(i2c)

    # Check if the touch controller is detected
    if touch.who_am_i():
        print("CST816 detected.")
    else:
        print("CST816 not detected.")
    
def setupMagneto():
    # Define I2C bus number (e.g., 1 for Raspberry Pi 2/3/4)
    global I2C_BUS_NUMBER
    global DEVICE_ADDRESS
    global REGISTER_DIR
    global REGISTER_ANGLE_MSB
    global REGISTER_ANGLE_LSB
    
    I2C_BUS_NUMBER = 1
    # Define the I2C address of your slave device (e.g., from i2cdetect)
    DEVICE_ADDRESS = 0x06   # Example: MT6701 address
    # Define the register address within the device to read/write
    REGISTER_DIR = 0x29 #DIR = 1 for CW (bit 1)
    REGISTER_ANGLE_MSB = 0x03   # Angle<13:6>
    REGISTER_ANGLE_LSB = 0x04   # Angle<5:0>


    #Ce type de filtre ne fonctionne pas avec les angles (passage de 360 à 0 !!!!)
    filtered_angle = 0
    alpha = 0.1 # must be between 0 and 1 inclusive
    
def setupNeoPixel():
    global pixels
    pixels = neopixel.NeoPixel(board.D21, 12, auto_write=False)
    
def setupBME():
    global bme280 # <-- Ajouté: Rend l'objet bme280 accessible globalement
    i2c = board.I2C()   # uses board.SCL and board.SDA
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
    
def setupVEML():
    global veml7700
    i2c = board.I2C()  # uses board.SCL and board.SDA
    veml7700 = adafruit_veml7700.VEML7700(i2c,0x10)

def setupEcran():
    global display
    global i2c # <-- La variable i2c était globale au début
    # --- Configuration SPI et Écran ---
    spi = board.SPI()
    tft_cs = board.D8
    tft_dc = board.D25
    tft_reset = board.D27

    displayio.release_displays()

    display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset, baudrate=62500000)
    
    display = GC9A01A(display_bus, width=240, height=240)

    # --- Constantes pour centrer ---
    global CENTER_X
    global CENTER_Y
    CENTER_X = display.width // 2
    CENTER_Y = display.height // 2

def setupBuzz():
    global buzzer
    buzzer = pwmio.PWMOut(board.D12, duty_cycle=0, frequency=1000)  # 1 kHz tone

def check_wifi(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False
    except requests.Timeout:
        return False

def setupMQTT():
    global client
    global THINGSBOARD_HOST
    if(check_wifi):
        THINGSBOARD_HOST = "tb-io.claurendeau.qc.ca"
        DEVICE_TOKEN = "0wwg0wfbjtw6038m4rqp"
        client = mqtt.Client()
        client.username_pw_set(username=DEVICE_TOKEN)
    else:
        print("Connexion WiFi non fonctionnel")

def setupAll():
    setupNeoPixel()
    print("NeoPixel Setupé")
    setupBME()
    print("BME Setupé")
    setupVEML()
    print("VEML Setupé")
    setupMagneto()
    print("Magneto Setupé")
    setupTouch()
    print("Touch Setupé")
    setupDRV()
    print("DRV Setupé")
    setupBuzz()
    print("Buzzer Setupé")
    setupEcran()
    print("Ecran Setupé")
    time.sleep(2)
    setupMQTT()
    print("MQTT Setupé")

def buzz(duration,type,typeB=None):
    for times in range(type):
        if typeB==None:
            multiplier = times+1
        else:
            multiplier = (times+1)*typeB
        buzzer.frequency = 1000*multiplier
        buzzer.duty_cycle = 65536 // 2  # 50% duty cycle
        time.sleep(duration*(multiplier/2))
        buzzer.duty_cycle = 0  # Turn off the buzzer

def playHaptic(effect_id=24):
    drv.stop()
    drv.sequence[0] = adafruit_drv2605.Effect(effect_id)  # Set the effect on slot 0.
    drv.play()

def getAngle():
    with SMBus(I2C_BUS_NUMBER) as bus:
        
        # Read DIR REGISTER
        bytes1 = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_DIR)
        #Set direction clockwise
        bytes1 = bytes1 |  0b00000010   #DIR = 1 for CW (bit 1)
        # Write DIR REGISTER
        bus.write_byte_data(DEVICE_ADDRESS, REGISTER_DIR, bytes1)
                
        #Read Angle MSB Register (Angle<13:6>) ... Bit7 to Bit0
        bytes1 = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_ANGLE_MSB)
        #print(f"Read byte from register {hex(REGISTER_ADDRESS_MSB)}: {hex(bytes1)}")
    
        #Read Angle LSB Register (Angle<5:0>) ... Bit7 to Bit2
        bytes2 = bus.read_byte_data(DEVICE_ADDRESS, REGISTER_ANGLE_LSB)
        #print(f"Read byte from register {hex(REGISTER_ADDRESS_LSB)}: {hex(bytes2)}")
    
        # Concatenate bytes2 with bytes1
        angle_int = bytes2 >> 2
        angle_int = (bytes1 << 6) | angle_int 
    
        # Compute angle in degrees (14 bits)
        return angle_int * (360.0/16384.0)


old_angle = 0
angle = None
def doClickIfRotated(millis):
    global old_angle
    hasClicked=False
    angle = getAngle()
    #Évite le noise en mettant un range de 20deg
    if (angle<(old_angle-5) or angle>(old_angle+5)):
        hasClicked = True
        #Éviter d'y donner trop de click pour éviter un buzz
        if ((time.time()-millis)>0.05):
            #Si on bouge rapide, le faire moins fort, et vice-versa
            if ((time.time()-millis)>0.2):
                old_angle = angle
                playHaptic(17)
            else:
                old_angle = angle
                playHaptic(24)

            millis = time.time()
    return millis, hasClicked

def getTemperature():
    """Retourne la température en °C."""
    return bme280.temperature

def getHumidity():
    """Retourne l'humidité relative en %."""
    return bme280.relative_humidity

def getPressure():
    """Retourne la pression en hPa."""
    return bme280.pressure
    
def getLux():
    return veml7700.light

def hasSwiped():
    if touch.get_touch():
        gesture = touch.get_gesture()
        new_page_index = -1
        direction = 0
        if touch.get_touch():
            if gesture == 3: # Balayage de droite à gauche
                return True, 1 # Glisser vers la gauche
            elif gesture == 4: # Balayage de gauche à droite
                return True, -1 # Glisser vers la droite
            elif gesture == 2:
                return True, "up"
            elif gesture == 0x0C:
                return True, "long"
            elif gesture == 0:
                return False, 0 # Ne rien faire
    return False, 0

def lightStatus(V, pattern = 0):
    R = 0
    G = 0
    B = 0

    if V <= 85: # Blue to Green
        factor = V * (255.0 / 85.0)
        G = factor
        B = 255 - factor
        R = 0

    elif V <= 170: # Green to Yellow
        V_prime = V - 86
        factor = V_prime * (255.0 / 84.0)
        R = factor 
        G = 255
        B = 0

    else: # Yellow to Red (V <= 255)
        V_prime = V - 171
        factor = V_prime * (255.0 / 84.0)
        R = 255
        G = 255 - factor # G goes from 255 to 0
        B = 0

    if (pattern == 0):
        R, G, B = round(R), round(G), round(B)
        for i in range(len(pixels)):
            pixels[i] = R, G, B
            pixels.show()
        pixels.show()
        return
    else:
        #plus fort à moins fort
        for _ in range(pattern):
            for step in range(10, 0, -1):
                R_n, G_n, B_n = round((R/10)*step), round((G/10)*step), round((B/10)*step)
                for i in range(len(pixels)):
                    pixels[i] = R_n, G_n, B_n
                    pixels.show()
        #reset à zéro les dels
        clearLEDS()

def clearLEDS():
    for i in range(len(pixels)):
        pixels[i] = 0,0,0
        pixels.show()

def sendThingsBoard(title,data):
    try:
        
        telemetry_data = {"ts": int(round(time.time() * 1000)), title: int(data)}
        print(f"Envoie de: {json.dumps(telemetry_data, ensure_ascii=False)}")
        client.connect(THINGSBOARD_HOST, 1883, 60)
        client.loop_start()
        time.sleep(1)
        status = client.publish("v1/devices/me/telemetry", json.dumps(telemetry_data), qos=1)
        status.wait_for_publish()
        client.loop_stop()
        client.disconnect()
        return True
    except Exception as e:
        print("Erreur: " + str(e))
        return False

def changeRange(x, old_range, new_range = [0, 255]):
    try: 
        old_min, old_max = float(old_range[0]), float(old_range[1])
        new_min, new_max = float(new_range[0]), float(new_range[1])
        x = float(x)
        new_value = (((x - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min
        #clampe
        new_value = max(new_min, min(new_max, new_value))
        return new_value
    except Exception as e:
        print(e)
        time.sleep(0.1)
        return 0
