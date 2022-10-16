import sys
import time
import requests
import RPi.GPIO as GPIO

# Connection settings
# SERVER_PROTOCOL - Server protocol (either 'http' or 'https')
# SERVER_HOST - Octoprint host (usually 'localhost' if you're running this script on the same machine as octoprint) - Can be a FQDN or hostname or IP address
# SERVER_PORT - Octoprint server port if different than standard http or https ports. Leave 0 if using standard http/https port otherwise change it (e.g. 5000).
# OCTOPRINT_PATH - Octoprint path from webserver root (e.g. /octoprint/). If octoprint is installed on the webserver root directory set this as '/'
# API_PATH - Path to the required API (printer) and query string. DO NOT EDIT.
# API_KEY - Api key used to access the Octoprint server without logging in. DO NOT SHARE - WHOEVER HAS THIS KEY CAN CONTROL YOUR WHOLE OCTOPRINT SERVER.
SERVER_PROTOCOL = 'http' # <--- CHANGE THIS IF NEEDED
SERVER_HOST = 'localhost' # <--- CHANGE THIS IF NEEDED
SERVER_PORT = 0 # <--- CHANGE THIS IF NEEDED
OCTOPRINT_PATH = '/' # <--- CHANGE THIS IF NEEDED
API_PATH = 'api/printer?apikey=' # <--- DO NOT EDIT
API_KEY = 'SET_THIS' # <--- WRITE YOURS HERE AND DO NOT SHARE

# Constants
# GPIO
# Relay signal pin
PIN_IMP = 7 

# Interval between status requests (in seconds) - Default: 10 seconds
STATUS_READ_INTERVAL = 10

def main():
	try:
		# Variables
		retries = 1 # Loop retries (used to handle request timeout)
		gpio_setup = False # Whether GPIO pins have been set up (used to handle finally scenario in case of exceptions)

		# Build complete URL
		# Check if protocol is valid
		if SERVER_PROTOCOL == 'http' or SERVER_PROTOCOL == 'https':
			# Check if using standard port
			if SERVER_PORT == 0:
				COMPLETE_URL = SERVER_PROTOCOL + '://' + SERVER_HOST + OCTOPRINT_PATH + API_PATH + API_KEY
			# Check if using custom port
			elif SERVER_PORT > 0 and SERVER_PORT < 65536:
				COMPLETE_URL = SERVER_PROTOCOL + '://' + SERVER_HOST + ':' + SERVER_PORT + OCTOPRINT_PATH + API_PATH + API_KEY
			# Otherwise invalid port - print error verbose and exit with error
			else:
				sys.exit("Invalid port Error.\nPlease check your connection settings in this script then try again.\nTerminating.")
		# Invalid protocol - print error verbose and exit with error
		else:
			sys.exit("Invalid protocol Error.\nPlease check your connection settings in this script then try again.\nTerminating.")

		# Verbose
		print(str("Using URL: " + COMPLETE_URL))

		# GPIO Initialization	
		GPIO.setmode(GPIO.BOARD) # Set GPIO mode to BOARD
		GPIO.setup(PIN_IMP, GPIO.OUT) # Sets relay as output
		gpio_setup = True; # GPIO Pins have been set up - set true

		# Verbose
		print("GPIO pins have been set up.")

		# Infinite loop
		while True:
			unix_time = int(time.time())
		
			# HTTP Request
			try:
				# Send GET Request to Octoprint Server API
				print("Sending request to Octoprint server...")
				response = requests.get(COMPLETE_URL)

				# HTTP Error Handling - response code other than 200 - Print error then exit with error (http status string)
				if response.status_code != 200:
						print(str("HTTP error: " + response.json()['error'] + "\nHTTP error status code: " + str(response.status_code)))				
						sys.exit("Please check your connection settings in this script and the octoprint server status, then try again.\nTerminating.");
				# No error (get status)
				else:
					status = response.json()['state']['flags']['printing']

			# HTTP Request Exceptions
			# Request timeout - retry three times, then exit
			except requests.exceptions.Timeout:
				if retries < 3:
					retries += 1

					# Wait for selected time
					# Verbose
					print("Waiting before sending a new request...")
					time_diff = int(time.time()) - unix_time
					if time_diff < STATUS_READ_INTERVAL:
						time.sleep((STATUS_READ_INTERVAL - time_diff))
					
					# Then continue
					continue
				else:
					sys.exit("Connection timed out error obtained after three retries.\nPlease check your connection settings in this script, network status and octoprint server status, then try again.\nTerminating.")
			
			# Connection Error - quit
			except requests.exceptions.ConnectionError:
				sys.exit("Connection error.\nPlease check your connection settings in this script, network status and octoprint server status, then try again.\nTerminating.")
			
			# Fatal error - quit
			except requests.exceptions.RequestException as e:
				print("Generic fatal error.\nPlease check your connection settings in this script, network status and octoprint server status, then try again.\nException stack trace:")
				sys.exit(str(e + "\nTerminating."))

			# Check status then turn pin ON or OFF
			if status == True:
				print("Printer printing. Relay on.")
				GPIO.output(PIN_IMP, GPIO.HIGH) # Relay on
			else:
				print("Printer not printing. Relay off.")
				GPIO.output(PIN_IMP, GPIO.LOW) # Relay off

			# Wait for selected time before requesting again
			# Verbose
			print("Waiting before sending a new request...")
			time_diff = int(time.time()) - unix_time
			if time_diff < STATUS_READ_INTERVAL:
				time.sleep((STATUS_READ_INTERVAL - time_diff))

	finally:
		# If GPIO pins have been setup, free them
		if gpio_setup == True:
			GPIO.cleanup() # Frees GPIO pins
		
if __name__ == "__main__":
	main()