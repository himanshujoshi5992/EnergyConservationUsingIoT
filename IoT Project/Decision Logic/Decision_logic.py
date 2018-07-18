#!/usr/bin/python

import datetime
import json
import urllib.request
import MySQLdb
import time as t
import datetime
import requests
#from temp_API import API

#tempapi = API()

# State variables
mintemp_in = 0

maxtemp_in = 0
mote1_light = 0
mote2_light = 0

# Open database connection


# prepare a cursor object using cursor() method

ts = t.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
#st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
#print (st)
#print (st1)
message ='NA'
AC_status = 'NA'
provalue = 'NA'
message = 'NA'
wifi_select = "SELECT max(Temperature), min(Temperature) from wifimote where DATE = CURDATE() AND TIME > DATE_ADD(CURTIME(), INTERVAL -10 MINUTE)"
#rpi_select = "SELECT Sound,Pir,Door_status FROM rpi where DATE >= st"
rpi_delete = "DELETE FROM rpi"
rpi_sumselect = "SELECT sum(door_status) from rpi"
mote1 = "SELECT Ambientlight from wifimote where IP LIKE '172.%' AND DATE >= CURDATE() ORDER BY TIME DESC limit 1"
mote2 = "SELECT Ambientlight from wifimote where IP LIKE '10.%' AND DATE >= CURDATE() ORDER BY TIME DESC limit 1"

def callserver(acvalue,doorvalue,provalue,timestamp):
	hit="https://smartclassroom.herokuapp.com/api/v1/sensordata/"+acvalue+"/"+doorvalue+"/"+provalue+"/"+timestamp
	r = requests.get(url = hit, params = "PARAMS")
	print(r)


def time_converter(time):
    converted_time = datetime.datetime.fromtimestamp(
        int(time)
    ).strftime('%I:%M %p')
    return converted_time


def url_builder(city_id):
    user_api = 'bfc33ad91247a3daeac7bf4cebc3c3cb'  # Obtain yours form: http://openweathermap.org/
    unit = 'metric'  # For Fahrenheit use imperial, for Celsius use metric, and the default is Kelvin.
    api = 'http://api.openweathermap.org/data/2.5/weather?id='     # Search for your city ID here: http://bulk.openweathermap.org/sample/city.list.json.gz

    full_api_url = api + str(city_id) + '&mode=json&units=' + unit + '&APPID=' + user_api
    return full_api_url


def data_fetch(full_api_url):
    url = urllib.request.urlopen(full_api_url)
    output = url.read().decode('utf-8')
    raw_api_dict = json.loads(output)
    url.close()
    return raw_api_dict


def data_organizer(raw_api_dict):
    data = dict(
        city=raw_api_dict.get('name'),
        country=raw_api_dict.get('sys').get('country'),
        temp=raw_api_dict.get('main').get('temp'),
        temp_max=raw_api_dict.get('main').get('temp_max'),
        temp_min=raw_api_dict.get('main').get('temp_min'),
        humidity=raw_api_dict.get('main').get('humidity'),
        pressure=raw_api_dict.get('main').get('pressure'),
        sky=raw_api_dict['weather'][0]['main'],
        sunrise=time_converter(raw_api_dict.get('sys').get('sunrise')),
        sunset=time_converter(raw_api_dict.get('sys').get('sunset')),
        wind=raw_api_dict.get('wind').get('speed'),
        wind_deg=raw_api_dict.get('deg'),
        dt=time_converter(raw_api_dict.get('dt')),
        cloudiness=raw_api_dict.get('clouds').get('all')
    )
    return data


def data_output(data):
    return data['temp']



prev_mintemp = 0
cur_mintemp = 0
while True:

		db = MySQLdb.connect("localhost","root","IIITB@123.","iotproject" )
		cursor = db.cursor()
		cursor1 = db.cursor()
		cursor2 = db.cursor()
		cursor3 = db.cursor()

		while True:
		    cursor.execute(wifi_select)

		    # Fetch all the rows in a list of lists.
		    results = cursor.fetchall()
		    #print (results[0])
		    if results[0][0]== None:
		    	print ('Value is none')
		    	t.sleep(3)
		    	continue
		    else:
		    	break

		maxtemp_in = results[0][0]
		mintemp_in = results[0][1]
		

		cur_mintemp = float(mintemp_in)

		minutes = 0
		temp_out = data_output(data_organizer(data_fetch(url_builder(1277333))))
		print ("=========================================================================")
		print("Max temperature: ",maxtemp_in,"   Min temperature: ",mintemp_in)
		print ("Api temperature: ",temp_out)
		print("Current temp: ",cur_mintemp)
		print("Previous temp: ",prev_mintemp)

		if cur_mintemp - prev_mintemp >= 0:
			if temp_out - float(mintemp_in) > 1:
				
				if mintemp_in == maxtemp_in:
					AC_status = 'ON and temperature set at ' + str(mintemp_in)
				elif mintemp_in < maxtemp_in:
					AC_status = 'ON and cooling in effect...'
					print ('AC status: ON and cooling in effect...')
				while minutes < 10:


					# Projector status
					while True:
					    cursor2.execute(mote1)

					    # Fetch all the rows in a list of lists.
					    results2 = cursor2.fetchall()
					    #print (results2)
					    if results2[0][0]== None:
					    	print ('Value is none')
					    	t.sleep(3)
					    	continue
					    else:
					    	break

					mote1_light = results2[0][0]
					print('Mote 1 light level: '+ str(mote1_light))


					while True:
					    cursor3.execute(mote2)

					    # Fetch all the rows in a list of lists.
					    results3 = cursor3.fetchall()
					    #print (results[0])
					    if results3[0][0]== None:
					    	print ('Value is none')
					    	t.sleep(3)
					    	continue
					    else:
					    	break

					mote2_light = results3[0][0]
					print('Mote 2 light level: '+ str(mote2_light))


					if (mote1_light > mote2_light): 
			   			provalue="ON"
			   			print ('Projector status: ON')
						
					else:
						provalue="OFF"
						print ('Projector status: OFF')

					#print (AC_status, message, provalue)	
					callserver(AC_status, message,provalue,datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S'))

					# Door status
					while True:

						cursor1.execute(rpi_sumselect)
						results1 = cursor1.fetchall()
						if results1[0][0] == None:
							print ('Value is none')
							t.sleep(3)
							continue
						else:
							break
					door_status = results1[0][0]
					cursor1.execute(rpi_delete)
					db.commit()
					if door_status == 0:
						message = 'Open'
					else:
						message = 'Closed'

					#print (AC_status, message, provalue)		
					callserver(AC_status, message,provalue,datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S'))
					print ('Door status: ',message)
					minutes += 2.5
					#cursor1.close()
					print ('---------------------------------------------------')
					t.sleep(151)
			else:
				AC_status ="OFF"
				print('AC status: OFF')

				#print (AC_status, message, provalue)
				callserver(AC_status, message,provalue,datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S'))

				while minutes < 10:
					# Projector status
					while True:
					    cursor2.execute(mote1)

					    # Fetch all the rows in a list of lists.
					    results2 = cursor2.fetchall()
					    #print (results2)
					    if results2[0][0]== None:
					    	print ('Value is none')
					    	t.sleep(3)
					    	continue
					    else:
					    	break

					mote1_light = results2[0][0]
					print('Mote 1 light level: '+ str(mote1_light))


					while True:
					    cursor3.execute(mote2)

					    # Fetch all the rows in a list of lists.
					    results3 = cursor3.fetchall()
					    #print (results[0])
					    if results3[0][0]== None:
					    	print ('Value is none')
					    	t.sleep(3)
					    	continue
					    else:
					    	break

					mote2_light = results3[0][0]
					print('Mote 2 light level: '+ str(mote2_light))


					if (mote1_light > mote2_light): 
			   			provalue="ON"
			   			print ('Projector status: ON')
						
					else:
						provalue="OFF"
						print ('Projector status: OFF')

					#print (AC_status, message, provalue)	
					callserver(AC_status, message,provalue,datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S'))

					minutes += 2.5
					#cursor1.close()
					print ('---------------------------------------------------')
					t.sleep(151)


				#t.sleep(601)

		else:
			AC_status ="ON"
			print ("AC status: ON")
			while minutes < 10:

				while True:
					cursor1.execute(rpi_sumselect)
					results1 = cursor1.fetchall()
					if results1[0][0] == None:
						print ('Value is none')
						t.sleep(3)
						continue
					else:
						break

				door_status = results1[0][0]
				cursor1.execute(rpi_delete)
				db.commit()
				if door_status == 0:
					message = 'Open.'
				else:
					message = 'Closed.'	

				#print (AC_status, message, provalue)	
				callserver(AC_status, message,provalue,datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S'))
				print ('Door status: ',message)


				# Projector status
				while True:
				    cursor2.execute(mote1)

				    # Fetch all the rows in a list of lists.
				    results2 = cursor2.fetchall()
				    #print (results2)
				    if results2[0][0]== None:
				    	print ('Value is none')
				    	t.sleep(3)
				    	continue
				    else:
				    	break

				mote1_light = results2[0][0]
				print('Mote 1 light level: '+ str(mote1_light))


				while True:
				    cursor3.execute(mote2)

				    # Fetch all the rows in a list of lists.
				    results3 = cursor3.fetchall()
				    #print (results[0])
				    if results3[0][0]== None:
				    	print ('Value is none')
				    	t.sleep(3)
				    	continue
				    else:
				    	break

				mote2_light = results3[0][0]
				print('Mote 2 light level: '+ str(mote2_light))


				if (mote1_light > mote2_light): 
		   			provalue="ON"
		   			print ('Projector status: ON')
					
				else:
					provalue="OFF"
					print ('Projector status: OFF')

				#print (AC_status, message, provalue)	
				callserver(AC_status, message,provalue,datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S'))


				minutes += 2.5
				print ('---------------------------------------------------')
				t.sleep(151)

		prev_mintemp = cur_mintemp
		print ("=========================================================================")
		db.close()
		#t.sleep(1)	
		
  	
# disconnect from server

