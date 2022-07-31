import pymysql.cursors
import pymysql

import CAMERA
import config
import shutil
try:
    configuration = config.read()
    host = configuration.get("DB", "HOST")
    user = configuration.get("DB", "USER")
    password = configuration.get("DB", "PASSWORD")
    db = configuration.get("DB", "DB")



    # Connect to the database
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 db=db,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

except:
    pass

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


def insert(targa):
    probabile_targa = CAMERA.getTarga(targa)
    try:

        with connection.cursor() as cursor:
            # Create a new record
            sql = "SELECT id FROM `targhe` WHERE targa = %s "
            cursor.execute(sql, probabile_targa)




            id_targa = cursor.fetchone()
            if id_targa == None:
                sql = "INSERT INTO `targhe` (`targa`) VALUES ( %s)"
                cursor.execute(sql, (probabile_targa))
                sql = "SELECT LAST_INSERT_ID() AS id "
                cursor.execute(sql)
                id_targa = cursor.fetchone()
            id = int(id_targa['id'])
            # Create a new record
            sql = "INSERT INTO `pesate` (`pesata`, `path_immagine`, `id_targa`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (150,targa , id))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
    finally:
        connection.close()