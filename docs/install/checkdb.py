import mysql.connector
import sys

if __name__ == '__main__':
    host_port = sys.argv[1].split(':')
    host = host_port[0]
    port = host_port[1]
    user = sys.argv[2]
    password = sys.argv[3]
    database = sys.argv[4]
    conn = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)

