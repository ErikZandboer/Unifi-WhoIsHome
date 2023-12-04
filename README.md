# Unifi-WhoIsHome

This Python code is meant to run on a Raspberry Pi connected to a network where a Unifi Controller is also connected. Using a connected 20x4 LCD the code will connect to the Unifi API, draw out any WiFi clients that have the "notes" section filled out, match that device to the airport used, and display that to the LCD.

This way every known device (phone) that enters the Unifi WiFi range will be reported on the LCD together with the AP it is connected to. Using the strength of the signal to that specific IP you may be able to pinpoint the location of the device even more precisely. This is atm all embedded inside the code, no fancy web GUI or anything to configure those. 
