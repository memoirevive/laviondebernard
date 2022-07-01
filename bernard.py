#!/usr/bin/python3
import os
import sys
import re
import random
import requests
import time
import datetime
import locale
import csv
import folium
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import geopy.distance
import smtplib, ssl

#########################################################################################
# Script params
scriptPath = '/absolute/path/to/script/' # the '/' at the end is needed
ask = False # ask before running
openskynetwork = True # check flights on openskynetwork (alternative: own json)
instagram = True # upload to instagram
sendEmail = True # send recap email
headlessInstagram = True  # hide Instagram browsing
headlessFolium = True # hide map creation
logFile = True # write console output to log file
test = False  # test mode

if (test):
	openskynetwork = False # test mode fecth yourwebsite.com/aircraft.json
	headlessInstagram = False
	headlessFolium = False
	logFile = False

# Fligths params
aircraft = "000000" #icao24 code, this is important
aircraftName = "F-XXXX" # only for display
tonPerKm = 0.00460220930232558 # ton of CO2 per km for this aircraft
startDaysAgo = 7 # fetch flights from XX days ago
endDaysAgo = 0 # up until XX days ago

# Browser params
browserPath = '/path/to/geckodriver'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
options = Options() # first instance of browser -> Instagram
options.add_argument("-profile")
options.add_argument(r'/path/to/firefox/profile/.mozilla/firefox/regatzrxsd.default') # use a profile to avoid logging in to Instagram each time
if headlessInstagram: options.add_argument("--headless")
options2 = Options() # second instance of browser -> creates maps
if headlessFolium: options2.add_argument("--headless")

# Instagram
login = 'instaAccount'
pwd = 'instaPassword'
instagramPost = "{day} | {departure} -> {arrival} | {duration} | ~ {co2} t CO2\n.\n{hashtags}\n.\nLes émissions de CO2 sont des estimations.\nLa trajectoire de vol représentée est illustrative."
nbHashtags = random.randint(4,8)
hashtags = [
	'justiceclimatique',
	'climat',
	'co2',
	'changementclimatique',
	'rechauffementclimatique',
	'criseecologique',
	'environnement',
	'ecologie',
	'planete',
	'petrole',
	'tourdumonde',
	'inégalités',
	'pollution',
	'jetprive'
	]

# Email (sender and receiver) to send logs
smtp = "your.SMTP.server.com"
port = 465
email = "email@address.com"
password = "emailPassword"

# Others
locale.setlocale(locale.LC_TIME,'') # For French date format
#########################################################################################
# Ask before running
if ask:
	run = input("Run Bernard? y/n : ")
	if run == "n":
		quit()
else:
	print("Bernard is running")
		
# Write in log or print in console
if logFile: 
	sys.stdout = open('bernard.log', 'w')
else: 
	open('bernard.log', 'w').close()

startTime = time.time()

# Open Sky API request
apiURL = "https://opensky-network.org/api/flights/aircraft"
begin = int(startTime - startDaysAgo*24*60*60)
end = int(startTime - endDaysAgo*24*60*60)
if openskynetwork: requestURL = apiURL + '?icao24=' + aircraft + '&begin=' + str(begin) + '&end=' + str(end) 
else: requestURL = "http://yourwebsite.com/aircraft.json"
	
# Requesting API
for i in range(20):
	try:
		print('Requesting OpenSky Network API')
		print(requestURL)
		r = requests.get(requestURL, headers=headers,timeout=10)
	except:
		print('Cannot access OpenSky Network API, sleep for 1min')
		r = None
		time.sleep(60)
	else:
		break

if r is None :
	print('Cannot reach OpenSky API - just re-run the script')
	flights = []
else:
	flights = r.json()
	
nbFlightsFoundAPI = len(flights)

flightList = []

# Getting flights
for flight in flights:
	if (flight['estDepartureAirport'] is None or flight['estArrivalAirport'] is None or flight['firstSeen'] is None or flight['estDepartureAirport'] == flight['estArrivalAirport']):
		continue
	# Getting airport municipalities and day of travel
	with open("airports.csv") as f:
		airports = csv.DictReader(f)
		for airport in airports:
			if(airport['ident'] == flight['estDepartureAirport']):
				departure = airport['municipality']
				departureCoord = [airport['latitude_deg'],airport['longitude_deg']]
			if(airport['ident'] == flight['estArrivalAirport']):
				arrival = airport['municipality']
				arrivalCoord = [airport['latitude_deg'],airport['longitude_deg']]
	departureTime = str(datetime.date.fromtimestamp(flight['firstSeen']).strftime("%d.%m.%Y"))
	duration = flight['lastSeen'] - flight['firstSeen']
	# Removing flights already fetched
	with open("flights.csv", "r") as f:
		oldFlights = csv.DictReader(f)
		old = False
		for oldFlight in oldFlights:
			if (oldFlight['departure'] == departure and oldFlight['arrival'] == arrival and oldFlight['day'] == departureTime):
				old = True
				break
		if not old:
			distance = geopy.distance.geodesic(departureCoord, arrivalCoord).km
			co2 = round(distance * tonPerKm, 1)
			flightList.insert(0, [departure, arrival, departureTime, departureCoord, arrivalCoord, co2, duration])

# Print flight list
for (index,flight) in enumerate(flightList): print(str(index) + " | " + flight[0] + " -> " + flight[1] + " | " + flight[2])

nbFlightsNew = len(flightList)
nbFlightsUploaded = 0

if nbFlightsNew != 0:
	if instagram:
		# Go to Instagram
		print("Go to Instagram")
		driver = webdriver.Firefox(service=Service(browserPath), options=options)
		driver.get('https://instagram.com')
		time.sleep(5)
		
		# Log in only if sessionId did not work (looking for publish button)
		try:
			driver.find_element(By.XPATH, '//*[@class="_abl- _abm2"]')
		except:
			again = 0
			while (again < 10):
				print("Not logged, get instagram")
				if (re.search("Allow the use of cookies", driver.page_source) or re.search("utilisation des cookies", driver.page_source)):
					allowCookiesButton = driver.find_element(By.XPATH, '//*[@class="aOOlW  bIiDR  "]').click()
					time.sleep(5)
					print("Closed cookie pop-up")
				usernameInput = driver.find_element(By.XPATH, '//*[@name="username"]').send_keys(login)
				passwordInput = driver.find_element(By.XPATH, '//*[@name="password"]').send_keys(pwd)
				loginButton = driver.find_element(By.XPATH, '//*[@type="submit"]').click()
				print("Sent login details")
				time.sleep(5)
				if (re.search("Forgot password", driver.page_source)):
					print('Cannot log in, sleep for 2min')
					time.sleep(120)
					driver.get('https://google.com') #reload by changing page
					driver.get('https://instagram.com')
					again += 1
				else:
					again = 99
					print("Logged in Instagram")
		else:	
			again = 99
			print("Logged in Instagram")
			if (re.search("Not Now", driver.page_source) or re.search("Plus tard", driver.page_source)):
				notNowCookieButton = driver.find_element(By.XPATH, '//*[@class="aOOlW   HoLwm "]').click()
	else:
		again = 99

	if (again == 10):
		print("Could not log into Instagram - just re-run script later")
	else:
		i = 0
		for flight in flightList:
			# gather flight infos
			departure = flight[0]
			arrival = flight[1]
			day = flight[2]
			departureCoord = flight[3]
			arrivalCoord = flight[4]
			co2 = str(flight[5])
			duration = time.strftime("%-Hh%Mmin", time.gmtime(flight[6]))
			print("[Flight " + str(i) + " - " + departure + " -> " + arrival + "]")

			# convert GPS coordinates to numbers
			departureCoord[0] = float(departureCoord[0])
			departureCoord[1] = float(departureCoord[1])
			arrivalCoord[0] = float(arrivalCoord[0])
			arrivalCoord[1] = float(arrivalCoord[1])
			
			# Turn the globe to keep distance < 180°
			if abs(arrivalCoord[1]-departureCoord[1])>180:
				if (arrivalCoord[1] < departureCoord[1]):
					departureCoord[1] -= 360
				else:
					arrivalCoord[1] -= 360
				
			# Create the map
			map = folium.Map(zoom_control=False)
			map.fit_bounds([departureCoord, arrivalCoord], padding=[120,120]);

			# Add plane and city names
			if (departureCoord[1] < arrivalCoord[1]): # position the plane towards arrival
				planeSide = "toright"
			else: 
				planeSide = "toleft"

			if (departureCoord[0] < arrivalCoord[0]): # write arrival city name above or below coordinate (not to cross plane path)
				cityMarginTop = "-50"
			else:
				cityMarginTop = "10"
			
			# Add cities and plane
			folium.Marker(
					departureCoord,
					icon=folium.DivIcon(html=f"""<div style='transform: scale(0.45) translate(-90px, -210px)'><img src="icons/plane""" + planeSide + """.png"></div>""")
				 ).add_to(map)
			folium.CircleMarker(
					arrivalCoord,
					color="black",
					fill_color='black', 
					radius=3
					).add_to(map)
			
			folium.Marker(
					departureCoord,
					icon=folium.DivIcon(html=f"""<div style='font-family: Arial; margin-top: 40px; font-size: 3.1em; font-weight: 600; color:black; width: max-content; transform: translate(-50%)'>""" + flight[0] + """</div>""")
				 ).add_to(map)
			folium.Marker(
					arrivalCoord,
					icon=folium.DivIcon(html=f"""<div style='font-family: Arial; margin-top: """ + cityMarginTop + """px; font-size: 3.1em; font-weight: 600; color: black; width: max-content; transform: translate(-50%);'>""" + flight[1] + """</div>""")
				 ).add_to(map)

			# Add curve between airports
			curve = []
			slope = abs(arrivalCoord[1]-departureCoord[1])/500
			for t in range(101):
				curve.append([
					departureCoord[0] + slope*t + (arrivalCoord[0]-departureCoord[0]-slope*100)/10000*t*t,
					departureCoord[1] + t*(arrivalCoord[1]-departureCoord[1])/100
					])

			folium.PolyLine(
				curve,
				weight=3,
				color='black'
				).add_to(map)

			# Export the map to HTML
			print("Creating map")
			outputFile = "map.html"
			map.save(outputFile)
			mapURL = 'file://{0}/{1}'.format(os.getcwd(), outputFile)

			# Add 'absolute position' content to HTML
			# Folium does not allow for it, so use a direct solution
			with open(outputFile, 'a') as mapHTML:
				mapHTML.write(
				"""
				<div style='position: absolute; z-index: 9999; font-family: Arial; font-size: 2.4em; padding-top:5px; font-weight: 600; color: black; left: 20px; top: 20px;'>""" 
				+ aircraftName +
				"""</div>
				<div style='position: absolute; z-index: 9999; font-family: Arial; font-size: 2.7em; font-weight: 600; color: black; right: 20px; top: 20px;'>"""
				+ day +
				"""
				</div>
				<div style='position: absolute; z-index: 9999; font-family: Arial; font-size: 2.7em; font-weight: 600; color: black; left: 20px; bottom: 20px;'>"""
				+ duration +
				"""</div>
				<div style='position: absolute; z-index: 9999; font-family: Arial; font-size: 2.7em; font-weight: 600; color: black; right: 20px; bottom: 20px;'>~ """
				+ co2 +
				""" t CO2</div>""")
			
			# Open it with webdriver
			driver2 = webdriver.Firefox(service=Service(browserPath), options=options2)
			driver2.set_window_size(1080, 1165)

			# Save screenshot (png)
			driver2.get(mapURL)
			time.sleep(6)
			output = 'output/output'+str(i)+'.png'
			print("Taking screenshot")
			driver2.save_screenshot(output)
			driver2.quit()
			
			# Convert to jpg
			im = Image.open(output)
			output = 'output/output'+str(i)+'.jpg'
			rgb_im = im.convert('RGB')
			rgb_im.save(output)

			time.sleep(5)
			
			# Add flight to Instagram
			if instagram:
				again = 0
				while (again < 10):
					#Randomly choose hashtags
					sample = random.sample(range(0, len(hashtags)), nbHashtags)
					hashtagSample = ""
					for i in sample:
						hashtagSample += "#" + hashtags[i] + " "

					# Publish image
					try:
						print("Adding map to Instagram")
						newPostButton = driver.find_element(By.XPATH, '//*[@aria-label="Nouvelle publication"]').click()
						
						print("New post window opened")
						time.sleep(5)
						dropZone = driver.find_element(By.XPATH, "//div[contains(@class,'_ac2r')]//input[contains(@type,'file')]").send_keys(scriptPath + output)
						print("Map dropped in drop zone")
						time.sleep(8)
						submitButton = driver.find_element(By.XPATH, "//div[contains(@class,'_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9p  _ab9- _abaa')]//button[contains(@type,'button')]").click()
						print("Map submitted")
						time.sleep(8)
						noFilterButton = driver.find_element(By.XPATH, "//div[contains(@class,'_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9p  _ab9- _abaa')]//button[contains(@type,'button')]").click()
						print("Next no filter clicked")
						time.sleep(5)
							
						captionArea = driver.find_element(By.XPATH, '//*[@class="_ablz _aaeg"]')
						captionArea.send_keys(instagramPost.format(day=day,departure=departure,arrival=arrival,duration=duration,co2=co2, hashtags=hashtagSample))
						
						# Test mode prevent from posting
						if (test):
							post = input("Post flight? (y/n)")
							if (post != "y"):
								quit()
						
						print("Caption sent")						
						publishButton = driver.find_element(By.XPATH, "//div[contains(@class,'_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9p  _ab9- _abaa')]//button[contains(@type,'button')]").click()
						print("Post published")
						time.sleep(8)
						confirmPopUpCloseButton = driver.find_element(By.XPATH, '//*[@class="fg7vo5n6 lrzqjn8y"]').click()
						time.sleep(5)

						# Record flight into .csv file
						with open("flights.csv", "a") as f:
							oldFlightsWriter = csv.writer(f)
							oldFlightsWriter.writerow(flight)
					except:
						print("Could not add flight. Trying again.")
						driver.get('https://instagram.com')
						time.sleep(5)
						again += 1
					else:
						again = 99
						nbFlightsUploaded += 1
					
				if (again == 10):
					print('Could not add flight to Instagram. Ignore the flight : ' + day + ' | ' + departure + ' -> ' + arrival)
			
			i+=1
			

if 'driver' in locals():
	driver.quit()

endTime = time.time()

# print general results
print("API : " + str(nbFlightsFoundAPI))
print("New : " + str(nbFlightsNew))
print("Uploaded : " + str(nbFlightsUploaded))

# stop logging and send logs via email
sys.stdout.close()
with open('bernard.log', "r") as f:
	log = f.read()

message = """\
Subject: Avion

""" + str(nbFlightsUploaded) + """/""" + str(nbFlightsNew) + """ nouveaux vols


Debut: """ + str(datetime.datetime.fromtimestamp(startTime).strftime("%H.%M:%S")) + """
Fin: """ + str(datetime.datetime.fromtimestamp(endTime).strftime("%H.%M:%S")) + """


Log:

""" + log

if sendEmail:
	# Create a secure SSL context
	context = ssl.create_default_context()
	# Send email
	with smtplib.SMTP_SSL(smtp, port, context=context) as server:
		server.login(email, password)
		server.sendmail(email, email, message)

