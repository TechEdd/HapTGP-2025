# Bibliothèques standards
import math
import random
import time

# Bibliothèques tierces
import RPi.GPIO as GPIO
from smbus2 import SMBus

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

global i2c
global bme280
global veml7700
global touch

def setupDRV():
    i2c = busio.I2C(board.SCL, board.SDA)  # uses board.SCL and board.SDA
    drv = adafruit_drv2605.DRV2605(i2c)
    
def setupTouch():
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
    pixels = neopixel.NeoPixel(board.D21, 12, auto_write=False)
    
def setupBME():
    global i2c # <-- Ajouté: Pour utiliser ou modifier la variable globale i2c si besoin
    global bme280 # <-- Ajouté: Rend l'objet bme280 accessible globalement
    i2c = board.I2C()   # uses board.SCL and board.SDA
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
    
def setupVEML():
    i2c = board.I2C()  # uses board.SCL and board.SDA
    veml7700 = adafruit_veml7700.VEML7700(i2c,0x10)

def setupEcran():
    
    # --- Configuration SPI et Écran ---
    spi = board.SPI()
    tft_cs = board.D8
    tft_dc = board.D25
    tft_reset = board.D27

    displayio.release_displays()

    display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
    display = GC9A01A(display_bus, width=240, height=240)
    
    # --- Configuration Capteur ---
    global i2c # <-- La variable i2c était globale au début
    i2c = board.I2C()
    global bme280 # <-- Déjà présent, mais assure l'accès global
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
    bme280.sea_level_pressure = 1013.25

    # --- Constantes pour centrer ---
    CENTER_X = display.width // 2
    CENTER_Y = display.height // 2

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
