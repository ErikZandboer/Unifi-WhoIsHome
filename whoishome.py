#!/usr/bin/python3

# ----------------- Version control -------------------------
# Version 1.20 - Removed the need for "iPhone" to be part of the device name - Just any device which has the "notes" section set to a value gets tracked
#                and gets reported by that same value in the "notes" section.
# Version 1.21 - Moved IP and login details to variables, added a R/W pin to the LCD


# ** GENERAL USE **
# -----------------

# Please adjust the code to reflect the correct data for the uiController (IP, credentials etc).
# Also check and adjust the different airports you have in the code below. The if...elif waterfall should contain all airports. Locations are 3 characters,
# names should be a maximum of 5 characters to fit a 20x4 LCD (up to five devices can be displayed).
# For more users you'll have to say goodbye to the clock or the "WhoIsHome" header line, simply adjust the cursor positioning logic to make that happen.

# Remember the names of the persons get stored in the Unifi Controllers "notes" section. Any device with notes added will be displayed on the LCD (clipped to 5 characters).

# If the code stays at "trying to connect" you probably put the wrong information into the uiControllerXxxx vars (like a wrong password);
# there are no checks for that in the code atm.

from unificontrol import UnifiClient
import ssl
import time
import sys
from datetime import datetime
from RPLCD import CharLCD
from RPi import GPIO

GPIO.setwarnings(False)

updateCounter = 0

updateFreq = 3   # Screen refreshes every 1 second, but new values are only fetched this often (3 = once every 3 seconds) to relax the UI controller a bit.
uiControllerIP="192.168.1.100"
uiControllerPort = 8443
uiControllerUser = "your.ui@account.com"
uiControllerPass = "YourPassword"

lcd = CharLCD(cols=20, rows=4, pin_rs=37, pin_e=35, pin_rw= 13, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)
time.sleep(1)
lcd.clear()
lcd.write_string(" --- WhoIsHome? ---")

try:
  cert = ssl.get_server_certificate((uiControllerIP, uiControllerPort))
  client = UnifiClient(host=uiControllerIP, port=uiControllerPort, username=uiControllerUser, password=uiControllerPass, cert=cert)
except:
  lcd.clear()
  lcd.write_string("No conn 2 Unifi")
  delay(5)
  pass
  try:
    cert = ssl.get_server_certificate((uiControllerIP, uiControllerPort))
    client = UnifiClient(host=uiControllerIP, port=uiControllerPort, username=uiControllerUser, password=uiControllerPass, cert=cert)
  except:
    lcd.clear()
    lcd.write_string("2nd conn fail- Exit")
    sys.exit()

timedot = 0

lcd.cursor_pos = (0, 0)
lcd.write_string(" --- WhoIsHome? ---")
lcd.cursor_pos = (3, 8)
lcd.write_string("            ")

clients = ""
devices = ""

while(1):

  updateCounter = updateCounter + 1
  if (updateCounter >= updateFreq):
    updateCounter = 0
    try:
      clients = client.list_clients(client_mac=None)
      devices = client.list_devices_basic()
    except:
      clients = ""
      devices = ""

  cnt=0
  lines = []
  powers = []

  for guest in clients:
    try:
      if (guest['note']):    # This will include ANY device who has something in the notes section as a device to be tracked
        for device in devices:
          if guest['ap_mac'] in device['mac']:
            airport = device['name']
            signal = int(guest['signal'])
            if (airport == "U6-Lite-Living"):
              if (signal > -61):
                location = "LIV" #Living Room
#              elif (signal > -76):
#                location = "TUI" #Garden
              else:
                location = "MAN" #Mancave

            elif (airport == "U6-Lite-SCA"):
              if (signal > -63):
                location = "SCA" # Studio
              elif (signal < -63) and (signal > -68):
                location = "WC" #Toilet downstairs
              else:
                location = "DOR" #Front door of the house
            elif (airport == "U6-Lite-Up"):
              if (signal > -51):
                location = "DOU" #Bathroom
              else:
                location = "UP" #Upstairs
            elif (airport == "AC-Lite-Space"):
              if (signal > -55):
                location = "WAS" #WashingRoom
              else:
                location = "MBD" #Master Bedroom
            else:
              location = "???"  #unknown AP

        lines.append(guest['note'][:5] + "-" + location)
        powers.append(guest['signal'])
        cnt = cnt + 1

    except:
#      print("unknown guest with MAC",guest['ap_mac'],"at airport",device['mac'])
      pass

  lcd.cursor_pos = (1, 0)

  if (len(lines) == 0):
    if (len(clients) == 0):
      lcd.write_string("No connection.      ")
      lcd.write_string("->Trying to connect.")
      lcd.write_string("            ")
    else:
      lcd.write_string("Nobody is home.     ")
      lcd.write_string("                    ")
      lcd.write_string("            ")

#    print("Nobody is home.")
  else:
#    for i in range(0,len(lines),1):
#      print (lines[i])

    for i in range(0,len(lines),1):
      if (i<3):
        lcd.cursor_pos = (i+1,0)
      else:
        lcd.cursor_pos = (i-2, 10)
      lcd.write_string(lines[i].ljust(10,' '))

    for i in range(cnt,5,1):
      if (i<3):
        lcd.cursor_pos = (i+1,0)
      else:
        lcd.cursor_pos = (i-2, 10)
      lcd.write_string("          ")

  time.sleep(0.2)
  if (len(lines)<6):
    if (timedot == 0):
      lcd.cursor_pos = (3,10)
      lcd.write_string('  ' + datetime.now().strftime('%H %M %S'))
    else:
      lcd.cursor_pos = (3,10)
      lcd.write_string('  ' + datetime.now().strftime('%H:%M:%S'))
  else:
    if (timedot == 0):
      lcd.cursor_pos = (3,19)
      lcd.write_string(' ')
    else:
      lcd.cursor_pos = (3,19)
      lcd.write_string('.')


  timedot = timedot + 1
  if (timedot >1): timedot = 0

  #time.sleep(1)

  while (round(time.time()*1000) % 1000):
    i=0
#  print("")

