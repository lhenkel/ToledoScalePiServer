from serial import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import re
import subprocess
import socket
import urllib2
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import  glob
import  os

PORT_NUMBER = 8675

def find_usb_tty(vendor_id = None, product_id = None) :
    tty_devs    = []

    for dn in glob.glob('/sys/bus/usb/devices/*') :
        try     :
            vid = int(open(os.path.join(dn, "idVendor" )).read().strip(), 16)
            pid = int(open(os.path.join(dn, "idProduct")).read().strip(), 16)
            if  ((vendor_id is None) or (vid == vendor_id)) and ((product_id is None) or (pid == product_id)) :
                dns = glob.glob(os.path.join(dn, os.path.basename(dn) + "*"))
                for sdn in dns :
                    for fn in glob.glob(os.path.join(sdn, "*")) :
                        if  re.search(r"\/ttyUSB[0-9]+$", fn) :
                            #tty_devs.append("/dev" + os.path.basename(fn))
                            tty_devs.append(os.path.join("/dev", os.path.basename(fn)))
                        pass
                    pass
                pass
            pass
        except ( ValueError, TypeError, AttributeError, OSError, IOError ) :
            pass
        pass

    return tty_devs

        
def detect_USB_serial():
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)
    #print devices
    for device in devices:
        #print device
        if "Serial Port" in device['tag']:
            print "Got Serial USB"
            return True

    return False

def redetect_settings():
    # Because scales like to randomly get new baud rates, because of course they do
    possible_usb_ports = find_usb_tty()
    possible_baud_rates = [9600, 4800, 115200,  57600, 1200, 2400, 19200, 38400]
    possible_bytesizes = [7,5,6,8]
    possible_parity = [PARITY_ODD,'N',  PARITY_EVEN]
    possible_stopbits = [2,1]

    if (len(possible_usb_ports) == 0):
        print "No USB/tty detected"
        return False
    else:
        print "Detecting Baud Rate.."
        
        for usb_port in possible_usb_ports:
            for baud in possible_baud_rates:
                for parity in possible_parity:
                    for stopbit in possible_stopbits:
                        for bytesize in possible_bytesizes:
                            print "Attempting: " + str(baud) + ' - ' + str(parity) + ' - ' + str(baud) + ' - ' + str(bytesize) + ' - ' + str(stopbit) 
                            serial = Serial(port = usb_port, baudrate = baud , bytesize = bytesize, parity  = parity, stopbits =stopbit, timeout = .2)
                            serial.write("W\r")         #S D       6.35 g
                            s = serial.readline()
                            serial.close()
                            if "lb" in s:
                                print "Detected" + str(usb_port) + ' - ' + str(baud) + ' - ' + str(parity) + ' - ' + str(baud) + ' - ' + str(bytesize) + ' - ' + str(stopbit) 
                                
                                return {'usb_port':usb_port, 'baud':baud, 'parity':parity, 'bytesize':bytesize, 'stopbits':stopbit}
        print "No Port detected"
        return False                
                    
def get_weight(serial):

    try:
        serial.write("W\r")         #S D       6.35 g
    except SerialException:
        print "Serial Exception.. Nuts"
        return False
    count = 0
    while count < 5:
        try:
            s = serial.readline()
        except SerialException:
            print "Serial Exception.. Nuts"
            return False            
        count = count + 1
        #print(s)

        if (len(s.strip()) > 1):
            floats_arr = re.findall("\d+\.\d+", s[0:7])
            if len(floats_arr) > 0:
                return floats_arr[0]
            else: 
                return False

        count = count + 1    

    return False

    
class MyHandler(BaseHTTPRequestHandler):    
    def __init__(self, context, *args):
        self.context = context
        BaseHTTPRequestHandler.__init__(self, *args)    
        
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        if self.path.endswith("debug"):
            self.wfile.write( context )
        else:    
            if self.path.endswith("getWeight"):
                serial = context['serial_obj']
                got_weight =  get_weight(serial) 
                if (got_weight == False):
                    print "Got Error, troubleshooting.."
                    if detect_USB_serial() == False:
                        print "Did not find Serial on USB"     
                    else:
                        settings = redetect_settings() 
                        if settings == False:
                            print "Could not detect Baud Rate etc during Call"
                            message = "Could not detect Baud Rate etc,"
                            print message
                            alert('lee.henkel@kng.com', 'Problem with PI scale' + my_ip, message)                                
                        else:
                            print "Got settings (maybe they changed)"
                            serial = Serial(port =  settings['usb_port'], baudrate = settings['baud'] , bytesize = settings['bytesize'], parity  = settings['parity'], stopbits = settings['stopbits'], timeout = 1)    
                            context['serial_obj'] = serial
                            self.context = context
                            got_weight =  get_weight(serial) 
                            self.wfile.write( got_weight )
                else:
                    self.wfile.write( got_weight )
            else:
                self.wfile.write( "Hello" )
        return        

print find_usb_tty()
   
if detect_USB_serial() == False:
    message = "Did not find Serial on USB, Bailing"
    print message
    
else:
    settings = redetect_settings() 
    if settings == False:
        message = "Could not detect Baud Rate etc,"
        print message
        
    else:
        serial = Serial(port = settings['usb_port'], baudrate = settings['baud'] , bytesize = settings['bytesize'], parity  = settings['parity'], stopbits = settings['stopbits'], timeout = 1)    

        try:
            #Create a web server and define the handler to manage the
            #incoming request
            context = {
                'serial_obj' : serial
            }
            def handler(*args):
                MyHandler(context, *args)
                
            server = HTTPServer(('', PORT_NUMBER), handler)
            print 'Started httpserver on port ' , PORT_NUMBER

            #Wait forever for incoming htto requests
            server.serve_forever()

        except KeyboardInterrupt:
            print '^C received, shutting down the web server'
            server.socket.close()        
