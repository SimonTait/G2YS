#!/usr/bin/env python3

# Author: Simon Tait

# GPIO 2 Yamaha SCP
# Module to command Yamaha console via SCP (Simple Control Protocol) in response to GPIO activity

#TODO: Use some GPIO output pins to drive LED's to indicate operational status (eg: PWR, OS OK, Online)

# Importz
import sys
import os
import socket
import fcntl
import struct
import uuid
from time import sleep
from datetime import datetime
import threading, queue
from RPi import GPIO
import board
import busio
import digitalio
from adafruit_mcp230xx.mcp23017 import MCP23017 # MCP23017 is the i2c <-> GPIO silicon
import mysql.connector
from mysql.connector import Error


# Thread lockers
caLock = threading.Lock()
outLock = threading.Lock()

# Queue for network commands   
q = queue.Queue()

# To quit
quittingTime = False 

# To control loop
loopTime = False
loopIsGoing = False

# If no i2c GPIO expanders are found, revert to inbuilt pins
usingInbuilt = False

# Debug level
debug = True
debugVerbose = False

# Console attributes
console = {"IP":None,               # To be found via YSDP
           "port": 49280,           # Must be 49280 by default
           "beGentleTime": 0.01,    # Don't smash the port too frequently. Sleep time in seconds.
           #"startChannel": 1,       # Which channel is the first of the group to be controlled?
           }

# Dict to hold base console command strings
#TODO: This dict will eventually be populated by a function that grabs data from the SQL
cmdz = {"setFader":"set MIXER:Current/InCh/Fader/Level ",
        "getFader":"get MIXER:Current/InCh/Fader/Level ",
        "getOnOff":"get MIXER:Current/InCh/Fader/On ",
        "setOnOff":"set MIXER:Current/InCh/Fader/On ",
        "Audio Follows Picture":"set MIXER:Current/InCh/Fader/Level "
        # Insert more here as needed
        }

# Reflects the current state of the 'controller_assignments' sql table, updated every 2sec by checkAss() thread
ca = []

# GPIO pins objects
pins = []

# prior pins state to detect changes
pinStatePrior =[]

# For AudioFollowsPicture behaviour, we need to store the state of the fader before sending the change command
prevFaderVal = {}

# Where are our expander boards on the i2c bus? The number of addresses must == qty of boards
mcpi2cAddresses = [0x21, 0x22]



def slog(msg):
    
    """ sane logger """
    
    with outLock: print(str(datetime.now()) + msg, file=sys.stderr)
    sys.stderr.flush() 

def sqlConnection(host_name, user_name, user_password, db_name):
    
    """ Plug in baby ... """
    
    connection = None
    
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        slog("Connection to MySQL DB " + db_name + " successful")
    
    except Error as e:
        slog("Error...Failed to connect to mySQL database" + str(e))

    return connection

def sqlQuery(connection, query, reportBack = False):
    
    """ Execute an SQL query """
    cursor = connection.cursor(buffered=True)        
    
    try:
        cursor.execute(query)
        
        if reportBack:
            result = cursor.fetchall()
            return result
        
        else:
            # No return has been requested, just write the cursor
            connection.commit()
        
        if debug:
            slog("Query executed successfully ::" + query)
    
    except Error as e:
        slog("Query errror ::" + str(e))
    

def getIpAddress():
    """
    Only works from Debian Stretch onwards, where Ethernet interface would be en[mac_address]
    Otherwise interface would be 'en0' or 'enX'
    """
    try:
        if debugVerbose:
            slog("uuid.getnode() returns :: " + str(uuid.getnode()))
            slog("hex(uuid.getnode()) returns :: " + str(hex(uuid.getnode())))
            slog("os.listdir(""/sys/class/net"") returns :: " + str(os.listdir("/sys/class/net")))
        
        # enInterface = 'en' + (hex(uuid.getnode()))[1:] # Not reliable - sometimes returns a random UUID instead of MAC
        
        for i in os.listdir("/sys/class/net"):
            if i[0:2] == "en":
                enInterface = str(i)
        
        if debugVerbose:
            slog("enInterface :: " + str(enInterface))
        
        t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        ip = socket.inet_ntoa(fcntl.ioctl(
            t.fileno(),
            0x8915, # SIOCGIFADDR
            struct.pack('256s', bytes(enInterface, 'utf-8'))
            )[20:24])
        
        if debugVerbose:
            slog("In getIpAddress(), ip is :: " + str(ip))
                
        return ip
    
    except Exception as e:
        print(e)
        if debug:
            slog("getIpAddress failed because :: " + str(e))

def discoverConsoles():
    
    """
    Locate Yamaha Consoles on the network using Yamaha Simple Discovery Protocol
    Send the YSDP request packet to the YSDP multicast address
    TODO: Recieve multiple responses
    """
    
    multicastGroup = '239.192.0.64'
    multicastPort = 54330
    multicastTimeToLive = 2 # Don't stray too far Baby
    
    ysdp = [0x59, 0x53, 0x44, 0x50] #"YSDP"
    data_size = [0x00, 0x23]
    type_ver_status = [0x00]
    ip_type = [0x04] #ipv4
    
    addr = []
    
    try:
        ip = getIpAddress().split('.')
    
    except Exception as e:
        if debug:
            slog("I don't have an IP address...can't help you sorry :: " + str(e))
        return []
    
    for i in ip:
        addr.append(int(i))
    
    # Paddington... these last digits would be for for ipv6
    for i in range(0,12):
        addr.append(0x00)
    
    mac = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00] # I'm Wicked and I'm lazy
    size_service_name = [0x08]
    service_name = [0x5f, 0x79, 0x70, 0x61, 0x2d, 0x73, 0x63, 0x70] # _ypa-scp
    size_ext_info = [0x00, 0x00]
    
    ysdp_list = ysdp + data_size + type_ver_status + ip_type + addr + mac + size_service_name + service_name + size_ext_info
    
    # Now transmit it 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, multicastTimeToLive)
    sock.settimeout(2)
    
    try:
        sock.sendto(bytes(ysdp_list), (multicastGroup, multicastPort))
    
    except Exception as e:
        slog("Couldn't send discovery packets:: " + str(e))
        sock.close ()
    
    # Now deal with the family!
    # TODO: ONLY HANDLES A SINGLE RESPONSE RIGHT NOW!!!!
    try:
        resp = sock.recv(256)
    
    except Exception as e:
        if debugVerbose:
            slog("Didn't recieve any YSDP response:: " + str(e))
        sock.close ()
        return []
    
    if debugVerbose:
        slog(str(resp))
    
    sock.close ()
    
    if len(resp) > 16: #16 is arbitrary
        
        # Work out the position of everything
        man_pos = 42
        man_size = resp[41]
        model_pos = man_pos + man_size + 1
        model_size = resp[(man_pos + man_size)]
        host_pos = model_pos + model_size + 1
        host_size = resp[(model_pos + model_size)]
        unit_pos = host_pos + host_size + 1
        unit_size = resp[(host_pos + host_size)]
        
        # Extract the characters and return a list
        ip = resp[8:12]
        manufacturer = resp[man_pos:(man_pos + man_size)].decode()
        model = resp[model_pos:(model_pos + model_size)].decode()
        host = resp[host_pos:(host_pos + host_size)].decode()
        unit = resp[unit_pos:(unit_pos + unit_size)].decode()
                
        return [manufacturer, model, host, unit, ip]
    
    else:
        return []

class scanForConsoles(threading.Thread):
    """
    Scan for consoles on the network every 3 seconds
    Populate the mySQL consoles database
    
    """
    
    def __init__(self): 
        threading.Thread.__init__(self, name="scanForConsoles")
        
        self.cnxn = sqlConnection("localhost", "root", "allenallen", "console_controller")
        self.sleepyTime = 3 # Seconds to wait between scans
        self.prevDc = [] # Results of previous scan
        
        # Initialise the controller-consoles table ... make everything 'offline' at startup
        msg = "UPDATE `controller-consoles` SET `consoleIsOnline`='False'"
        sqlQuery(self.cnxn, msg)
        
    def run(self):
        
        global quittingTime
        
        while not quittingTime:
            
            try:
                self.goHunting()
                
            except Exception as e:
                slog("Oops...goHunting() accident :: " + str(e))
                slog("Trying again in 3 seconds")
                sleep(self.sleepyTime)
                
    def goHunting(self):
        
        global quittingTime, loopTime  
        
        try:
            while not quittingTime:
                
                self.dc = discoverConsoles() # CAUTION: ONLY FINDS A SINGLE CONSOLE AT THE MOMENT
                
                if self.dc == self.prevDc: # Nothing has changed
                    sleep(self.sleepyTime)
                    continue
                 
                """
                We only reach here if a new console has been found, or one has disappeared.
                TODO :: Handle multiple consoles
                TODO :: Handle 'consoleIsSelected' attribute
                """
                
                if debug:
                    if len(self.dc) == 0:
                        slog("A console was disconnected...")
                    else:
                        slog("A new console was connected...")
                                
                if len(self.dc) > 0:
                    
                    # What's on the network?
                    self.returnedIp = '.'.join([str(b) for b in self.dc[4]])
                    slog("Found " + self.dc[0] + " " + self.dc[1] + " with ID:" + self.dc[2] + " at " + self.returnedIp)
                    
                    # Maybe later this will come from sql...
                    console["IP"] = self.returnedIp
                    
                    # What's in sql?                     
                    cmd = "SELECT * from `controller-consoles`"
                    consolesInDb = sqlQuery(self.cnxn, cmd, True)
                    
                    """
                    consolesInDb[i] return is ::        [model, ID, IP, Online, Selected, Virtual] 
                    discoverConsoles() return is ::     [manufacturer, model, ID, unit, ip (bytes)]
                    
                    """
                    
                    if len(consolesInDb) == 0: # Database in empty, so just add the online console to it
                        
                        if debug:
                            slog("No consoles found in sql database :: adding this console..." + str(self.dc[1]) + " :: " + str(self.dc[2]) )
                        cmd = "INSERT INTO `controller-consoles` (`consoleModel`, `consoleID`, `consoleIPv4`, `consoleIsOnline`, `consoleIsSelected`, `consoleIsVirtual`) VALUES ('" + str(self.dc[1]) + "', '" + str(self.dc[2]) + "', '" + str(self.returnedIp) +  "', 'True', 'False', 'False')"
                        sqlQuery(self.cnxn, cmd)
                        
                        loopTime = True
                        
                        continue
                    
                    # Check if the online console is found in the database...
                    if any((self.dc[1] in i and self.dc[2] in i for i in consolesInDb)):
                        #Console was found
                        if debug:
                            slog("This " + str(self.dc[1]) + "::" + str(self.dc[2]) + " console already exists in the database :: Updating dB etry")
                        # Set consoleIsOnline to 'True', update its IP and set consoleIsVirtual to 'False'
                        cmd = "UPDATE `controller-consoles` SET `consoleIsOnline`='True', `consoleIsVirtual`='False', `consoleIPv4`='" + str(self.returnedIp) +  "' WHERE `consoleModel`='"+ str(self.dc[1]) + "' AND `consoleID`='" + str(self.dc[2]) + "'"
                        sqlQuery(self.cnxn, cmd)
                           
                    else:
                        # Then we have a new console to add
                        if debug:
                            slog("New console! Adding to db :: " + str(self.dc[1]) + "::" + str(self.dc[2]))
                            
                        cmd = "INSERT INTO `controller-consoles` (`consoleModel`, `consoleID`, `consoleIPv4`, `consoleIsOnline`, `consoleIsSelected`, `consoleIsVirtual`) VALUES ('" + str(self.dc[1]) + "', '" + str(self.dc[2]) + "', '" + str(self.returnedIp) +  "', 'True', 'False', 'False')"
                        sqlQuery(self.cnxn, cmd)
                        
                    # Take all other consoles offline
                    cmd = "UPDATE `controller-consoles` SET `consoleIsOnline`='False', `consoleIsVirtual`='True' WHERE `consoleModel`!='"+ str(self.dc[1]) + "' OR `consoleID`!='" + str(self.dc[2]) + "'"
                    sqlQuery(self.cnxn, cmd)
                
                    loopTime = True
                
                else:
                    # Take the previous console offline
                    cmd = "UPDATE `controller-consoles` SET `consoleIsOnline`='False', `consoleIsVirtual`='True' WHERE `consoleIPv4`= '"+ str(console["IP"]) + "'"
                    sqlQuery(self.cnxn, cmd)
                    
                    console["IP"] = None
                    loopTime = False
                    slog("Couldn't find any consoles.")
                    slog("Please check that the console's control port is on the same subnet as this controller.")
                    slog("No subscribers to multicast address 239.192.0.64 port 54330")
                    slog("Trying again in 3 seconds...")
                    sleep(3) 
                
                # Update the previous scan results to compare next time around
                self.prevDc = self.dc
                
                # Pause for a bit
                sleep(self.sleepyTime)
            
            # It's quittin' time ... console is no longer online!!
            cmd = "UPDATE `controller-consoles` SET `consoleIsOnline`='False', `consoleIsVirtual`='True' WHERE `consoleIPv4`='" + str(self.returnedIp) +  "'"
            sqlQuery(self.cnxn, cmd)
                
        except Exception as e:
            slog("Sorry...Console discovery failed. Check yr network for lumps.")
            slog(str(e))

        

class getCa(threading.Thread):
    
    """ Get the controller_assignments every 2 seconds """
    
    def __init__(self): 
        threading.Thread.__init__(self, name="getCa")
        
        self.connection = sqlConnection("localhost", "root", "allenallen", "console_controller")
        self.prevCa = []
        self.c = "SELECT * from controller_assignments"
        
    def run(self):
        
        global quittingTime, ca
        
        while not quittingTime:
            
            try:
                with caLock:
                    
                    ca = sqlQuery(self.connection, self.c, True)
                    
                    if ca != self.prevCa:
                        slog("New controller_assignments :: " + str(ca))
                        
                    self.prevCa = ca
                
                # Update
                self.connection.commit()
                
                #slog("Current :: " + str(ca))
                #slog("Previous :: " + str(self.prevCa))
                    
                sleep(2)
                
            except Exception as e:
                slog("Couldn't get the sql stuff..." + str(e))
     

def setupPins():
    """ Does what it says..."""
    
    global loopTime, loopIsGoing, usingInbuilt
    global pins
    
    """
    Probe for devices on the i2c bus
    If devices are not found, revert to standard R.Pi GPIO pins
    """
    
    # Re-initialise stuff so we only populate it once!
    pins.clear()
    
    try:
    
        # Initialize the I2C bus:
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # First 16 GPIO's
        mcp1 = MCP23017(i2c, mcpi2cAddresses[0])
        
        # 17 -> 32 GPIO's
        if len(mcpi2cAddresses) >= 2:
            mcp2 = MCP23017(i2c, mcpi2cAddresses[1])
        
        # 33 -> 48 GPIO's
        if len(mcpi2cAddresses) >= 3:
            mcp3 = MCP23017(i2c, mcpi2cAddresses[2])
        
        # Let any current loop finish
        while loopIsGoing: 
            sleep(0.5)
        
        # Populate ze pins[] list first ... 16 pins per mcp board
        for i in range(0, (len(mcpi2cAddresses) * 16), 1):
            if i <= 15:
                mcp = mcp1
                offset = 0
            elif 16 <= i <= 31:
                mcp = mcp2
                offset = 16
            elif 32 <= i <= 47:
                mcp = mcp3
                offset = 32
            
            pins.append(mcp.get_pin(i - offset))
        
        # Now setup the pin direction & pullup
        for pin in pins:
            pin.direction = digitalio.Direction.INPUT
            pin.pull = digitalio.Pull.UP 
    
    except Exception as e:
        
        slog(" Couldn't find Adafruit GPIO extenders on the i2c bus ... Revert to built-in GPIO ::")
        slog(" " + str(e))
        
        usingInbuilt = True
        
        GPIO.setmode(GPIO.BCM)
        #pins = [7,11,12,13,15,16,18,19,21,22,23,24,26,29,31,32,33,35,36,37,38,40]
        pins = [4,5,6,7,8,9,10,11,12,13,16,17,18,19,20,21,22,23,24,25,26,27]
        
        if debugVerbose:
            slog("pins list as populated by Exception handler :: " + str(pins))
        
        GPIO.setup(pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def setupConsole():
    """
    Old helper function for python3 console when __name__ != 'main'
    Discover console on the network, get its IP
    """
    global quittingTime
    
    try:
        while not quittingTime:
            
            dc = discoverConsoles()
            
            if len(dc) > 4:
                returnedIp = '.'.join([str(b) for b in dc[4]])
                slog("Found " + dc[0] + " " + dc[1] + " with ID:" + dc[2] + " at " + returnedIp)
                console["IP"] = returnedIp
                break
            
            else:
                slog("Couldn't find any consoles.")
                slog("Please check that the console's control port is on the same subnet as this controller.")
                slog("No subscribers to multicast address 239.192.0.64 port 54330")
                slog("Trying again in 3 seconds...")
                sleep(3)
            
    except Exception as e:
        slog("Sorry...Console discovery failed. Check yr network for lumps.")
        slog(str(e))

def sendCommand(cmd, reportBack = False):
    """
    Hey Man, Are you the DJ?
    Can I borrow some gaffer?
    Can I charge my phone from yr console?
    Can you look after my jacket?
    """
    
    # append newline to command
    cmd += '\n'
    
    # connect socket
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((console["IP"],console["port"]))
    
        # send command
        s.sendall(cmd.encode())
    
        # receive a message before closing socket
        response = s.recv(1500)
    
        if debugVerbose:
            slog("Received: " + str(response))
        
        # close socket
        s.close ()
        
        if reportBack:
            result = str(response)
            return result
    
    except Exception as e:
        slog("SOCKET CONNECTION TO " + str(console["IP"]) + ":" + str(console["port"]) + " FAILED!!!")
        slog("Attempted to send: " + str(cmd))
        slog(str(e))


def getParam(channel, param):
        # Get the current param of a channel
        if param == 'fader':
            cmd = cmdz["getFader"] + str(channel) + " 0"
            
            try:
                faderPos = sendCommand(cmd, True).split()[-1].split('\\n')[0]
                return faderPos
                
            except Exception as e:
                slog("Couldn't get Fader Position, returning -Inf as default :: " + str(e))
                return '-32768'
        
        elif param == 'onOff':
            cmd = cmdz["getOnOff"] + str(channel) + " 0"
            
            try:
                onOffState = sendCommand(cmd, True).split()[-1].split('\\n')[0]
                return onOffState
                
            except Exception as e:
                slog("Couldn't get OnOff State, returning ON as default :: " + str(e))
                return '1'

class iLikeToMooveIt(threading.Thread):   #(func, channel, newVal)
    
    """ Consume the queue of commands produced by loopityLoop """
    
    def __init__(self): 
        threading.Thread.__init__(self, name="iLikeToMooveIt")
    
    def run(self): #func, channel, val
        """Get jobs from the queue"""
        
        global quittingTime, q
        
        while not quittingTime:
            
            try:
                job = q.get(timeout=2) # Infinite timeout would block forever
            
            except queue.Empty:
                continue
            
            # get steveAlbini to produce the string
            tcpString = self.steveAlbini(job)
            
            if debugVerbose:
                slog("Sending: " + tcpString)
            
            # Send the command
            if tcpString:
                sendCommand(tcpString)
            
            sleep(console["beGentleTime"])   
            q.task_done()
    
    def steveAlbini(self, job):
        """ Assemble the command string """
        
        pin, active, latch, norm, function, chan = job[0]
        pinStatePrior = job[1]
        pinState = job[2]
        
        channel = str(int(chan) - 1) # Zero indexed 
        
        # Catch any glitchiness..
        if pinStatePrior == pinState:
            return 0 # Something has gone wrong
        
        # Logic graph to compare norm state against !norm
        if pinStatePrior > pinState:
            transition = 'falling'
        else:
            transition = 'rising'
        
        if norm == "N/O": # Normally open 
            if transition == 'rising':
                normal = True
            else:
                normal = False
        
        elif norm == "N/C": # Normally closed
            if transition == 'falling':
                normal = True
            else:
                normal = False
        
        else: # Assume default state
            normal = True
        
        if function == 'Audio Follows Picture': # Audio Follow Picture
            
            command = cmdz["setFader"]
            
            if not normal:    
                # Get the fader value from the console and store it
                currentFaderVal = getParam(channel, 'fader')
                
                if debugVerbose:
                    slog("Storing Fader Value for channel " + str(channel) + " which is :: " + str(currentFaderVal))
                
                prevFaderVal[channel] = currentFaderVal
                
                newVal = 0 # Unity
                
            else: 
                # Pin has normalled, so go back to the previous value
                if channel in prevFaderVal:
                    newVal = prevFaderVal[channel]
                    
                    if debugVerbose:
                        slog("Retrieved previous fader position for ch " + str(channel) + " :: " + str(newVal))
                
                else:
                    newVal = -32768
                    
                    if debug:
                        slog("No stored previous fader position for ch " + str(channel) + " :: ")
                        
            
        if function == 'Mute':
            
            command = cmdz["setOnOff"]
            
            if not normal:# Turn it OFF
                newVal = '0'
            
            else: # Turn it ON
                newVal = '1'
        
        if function == 'Panic':
            # Not yet implemented
            return 0
        
        if function == 'Q-Lab Backup':
            # Not yet implemented
            return 0
        
        return command + str(channel) + " 0 " + str(newVal)        
        
        
#Looptiy Loop
def loopityLoop():
    
    slog("We'll fix it in POOOOOSST!")
    
    global quittingTime, loopTime, loopIsGoing, usingInbuilt, q
    
    firstRun = True
    
    if debug:
        slog("Number of pins installed :: " + str(len(pins)))
    
    while not quittingTime:
        
        # pin.value will be False if held low
        # pin.value will be True if let go, and pullup
        # if usingInbuilt, GPIO.input(pin) = 0 if held low
        # if usingInbuilt, GPIO.input(pin) = 1 if let go, and pullup
        
        if firstRun:
            # Populate the 'pinStatePrior' list with current states
            
            pinStatePrior = []
            
            for pin in range (0, len(pins)):
                if usingInbuilt:
                    pinStatePrior.append(GPIO.input(pins[pin]))
                
                else:
                    pinStatePrior.append(pins[pin].value)
            
            if debugVerbose:
                slog("pinStatePrior :: " + str(pinStatePrior))
                slog(str(ca))
            
            firstRun = False
        
        try:
            # How to pause the loop
            if not loopTime:
                sleep(0.5)
                continue
            
            loopIsGoing = True
            
            # Loop thru the controller assignments given by the webinterface ( ca[] )
            # Check if any pins have changed and put the job into the queue if they have
            with caLock:
                for i in range(0, len(ca)):
                    
                    active = ca[i][1]              
                    if not active: # Move on, nothing to see here
                        continue
                    
                    chan = ca[i][5]
                    if chan == 0: # Input Channel is not assigned
                        continue
                    
                    # 'pin' variable comes from web interface. Convert it to zero-index
                    pin = ca[i][0] -1
                    
                    if usingInbuilt:
                        pinState = GPIO.input(pins[pin])
                    
                    else:
                        pinState = pins[pin].value
                    
                    # Compare pin to its previous state
                    if pinState == pinStatePrior[pin]: # Nothing has changed
                        continue   
                    
                    """We only reach here if something has changed"""
                    
                    if debugVerbose:
                        slog("Something has changed...")
                        slog("Pin :: " + str(pin) + " went " + str(pinState))
                        slog(" ")
                    
                    job = [ca[i], pinStatePrior[pin], pinState]
                    
                    # Put the job into the queue
                    q.put(job)
                    
                    # Pin state has changed, so update it's pinStatePrior...
                    pinStatePrior[pin] = pinState
                    
                    loopIsGoing = False
            
            #Slow down the loop to prevent bouncing
            sleep(0.02)
            
        except KeyboardInterrupt:
            quittingTime = True
            slog("It's quittin' Time")
    
    # Tidying up on the way out...
    if usingInbuilt:
        GPIO.cleanup()

   
if __name__ == '__main__':
    setupPins()
    scanForConsoles().start()
    iLikeToMooveIt().start()
    getCa().start()
    loopityLoop()
