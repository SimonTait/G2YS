# G2YS
**Not tested since 2020 ... YMMV**
GPIO to Yamaha SCP

Automatically finds a single Yamaha QL/CL console on the same subnet as the R.Pi and issues remote control commands via SCP in response to GPIO actions.

Configured using web interface - point your browser to the R.Pi3's IP address.

Compatible with MCP23017-based Adafruit GPIO expander bonnet. Multiple bonnets can be connected to provide extra GPIO in multiples of 16.

If no Adafruit bonnet is found on the i2c bus, then it will revert back to the on-board R.Pi3 GPIO header using BCM-format pin numbering.
In this case, GPIO numbering follows the orange labels found here:
https://docs.microsoft.com/en-us/windows/iot-core/learn-about-hardware/pinmappings/pinmappingsrpi

This BCM-format pin numbering results in GPIO 4 being the 'first' pin in the web interface, because the i2c bus occupies pins 3 & 5 on the header (corresponding to GPIO 2 and 3) - thus GPIO 2 and 3 cannot be used.

REQUIREMENTS:
 - DHCP server
 - A Yamaha CL/QL mixing console
 - Adafruit 4132 GPIO Expander bonnet (optional, qty = up to 3)

DEPENDENCIES:
 - Tested using Raspberry Pi 3B+ with R.Pi OS Lite
 - a mySQL server (tested using MariaDb - see Web_G2YS for details of each mySQL database)
 - a web server (tested using Apache2 - use contents of Web_G2YS copied to /var/www/html for example)
 - php
 - python3
 - Various Adafruit dependencies (see imports section of G2YS.py and also follow: https://learn.adafruit.com/gpio-expander-bonnet/overview)
 - G2YS.py should be loaded automatically using systemd

KNOWN ISSUES:
 - Only handles a single console using YSDP discovery. Multiple consoles are not supported yet.
