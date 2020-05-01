import sys
import time
import datetime
from w1thermsensor import W1ThermSensor
import logging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

print(firebase_admin)


# Use a service account
cred = credentials.Certificate('./serviceAccountKey.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


sensores = W1ThermSensor.get_available_sensors()

print("Inicio")


if len(sensores) <= 0:
    print("No hay sensores")
    sys.exit()

# Intenta ejecutar las siguientes instrucciones, si falla va a la instruccion except
try:
    # Ciclo principal infinito
    while True:
	batch = db.batch()
	count = 1

        for sensor in sensores:

	    sensor_name = ('sensor' + str(count))

	    readings = {
 	 	u'timestamp': time.time(),
                u'temperatureInCelsius': sensor.get_temperature(),
                u'temperatureInFahrenheit': sensor.get_temperature(W1ThermSensor.DEGREES_F)
	    }

	    data = {
		u'id': sensor.id,
		u'name': sensor_name,
		u'lastReading': readings
            }

	    sensor_ref = db.collection(u'sensors').document(sensor.id)
	    batch.update(sensor_ref, data)

	    reads_ref = db.collection(u'readings').document(sensor.id)
	    batch.update(reads_ref, { u'temperatures':firestore.ArrayUnion(readings) } )

            print('Sensor: '+ id + ' Temperatura: ' + str(temperature))
	    count = count + 1

	# Realiza la escritura en la base de datos
	batch.commit()
        # Duerme 5 minutos
        print('Wait 300 seconds...')
        time.sleep(300)


# Se ejecuta en caso de que falle alguna instruccion dentro del try
except Exception as e:
    logger.exception(e)
