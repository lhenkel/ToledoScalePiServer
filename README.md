# README #

This is a lightweight weight server intended to run on a Raspberry Pi.  It will sit next to a Toledo scale and serve a webpage that displays the weight from the scale. 

You need to connect a serial to USB cable to the Raspberry PI, then connect the serial to the RS232 port on the scale.  We made out own serial to RS232, but you can also buy them from vendors (they're stupidly expensive though).

I am obviously not the greatest Pythoner, but it's worked in our office for about a year so far.  I use Python 2.7 if that matters.

You can call it like this:

http://[some IP]:6875/getWeight

It will display a float if successful.

You can also call http://[some IP]:6875/debug  which will show which baud rate, USB port etc it's using.  My scales will sometimes myseriously change their baud settings (or people in the warehouse are messing with me) so this script will try to redetect those settings if it doesn't work.  

I install in the /jobs/piscale directory, but it doesn't really matter.  I wrote some scripts to check if it's runnind and restart 
them periodically which seems to help w/ reliability

*/5 * * * * /jobs/piscale/checkForProcess.sh > /var/log/checkProcess.log
22 2 * * * /jobs/piscale/checkForUpdatesAndReload.sh > /var/log/reload.log   

