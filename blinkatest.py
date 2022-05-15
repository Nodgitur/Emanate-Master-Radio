import board
import digitalio
import busio

print("Hello blinka!")

# Trying to get digital input
pin = digitalio.DigitalInOut(board.D4)
print("Digital IO ok!")

# Trying to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print("I2C ok!")

# Trying to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("SPI ok!")

print("Done!")