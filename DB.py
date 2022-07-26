import pymysql.cursors
import pymysql
import config

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

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


def prova():
    try:
        targa = "C:\\Users\\andre\\Desktop\\TARGHE\\FX231TM.png"

        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `targhe` (`PESO`, `TARGA`) VALUES (%s, %s)"
            cursor.execute(sql, ('150.5', targa))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
        """
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
            cursor.execute(sql, ('webmaster@python.org',))
            result = cursor.fetchone()
            print(result)
        """
    finally:
        connection.close()