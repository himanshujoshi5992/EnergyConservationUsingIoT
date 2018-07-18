from flask import Flask, request, json
from time import gmtime, strftime
import MySQLdb
import random
import time
from datetime import datetime

app = Flask(__name__)
@app.route("/homecontrol/api/v1.0/temperature", methods=['POST'])

def api_temperature():
    # Open database connection
    db = MySQLdb.connect("127.0.0.1","root","IIITB@123.","iotproject" )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    read_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if request.headers['Content-Type'] == 'text/plain':
        print (request.data)
        return 'OK', 200
    elif request.headers['Content-Type'] == 'application/json':
        d = request.json
        read_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sound= d['Sound']
        pir = d['Pir']
        doorStatus = d['door_status']
        print(sound,pir,read_time)
        cursor.execute("INSERT INTO rpi VALUES (%s, %s, %s, %s)", (sound,pir,read_time,doorStatus))
        db.commit()
        return "OK", 200
    else:
        return "Unsupported Media Type", 415

if __name__ == '__main__':
    app.run(threaded=True,host='0.0.0.0',port=5000,debug = False)
