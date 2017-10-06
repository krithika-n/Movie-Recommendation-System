import psycopg2
import csv
from sys import stdout
def getOpenConnection(user, password, dbname):
    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='localhost' password='" + password + "'")

def createDB(user, password, dbname):
    """
    We create a DB by connecting to the default user and database of Postgres
    The function first checks if an existing database exists for a given name, else creates it.
    :return:None
    """
    # Connect to the default database
    con = getOpenConnection(user, password,'postgres')
    con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    # Check if an existing database with the same name exists
    cur.execute('SELECT COUNT(*) FROM pg_catalog.pg_database WHERE datname=\'%s\'' % (dbname,))
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute('CREATE DATABASE %s' % (dbname,))  # Create the database
    else:
        print 'A database named {0} already exists'.format(dbname)

    # Clean up
    cur.close()
    con.commit()
    con.close()

def loadtable(tablename, filepath, openconnection,createTableSubQuery,columns,values):
    data=csv.reader(file(filepath))
    data=list(data)
    data=data[1:]
    filelen=open(filepath)
    fraction=100/float(len(filelen.readlines()));
    length=0
    cur = openconnection.cursor()
    cur.execute("DROP TABLE IF EXISTS " + tablename)

    cur.execute(
        "CREATE TABLE " + tablename + createTableSubQuery)
    for i,row in enumerate(data):
        cur.execute("INSERT INTO "+tablename+" "+columns+" VALUES "+values,row)
        stdout.write("\r//-----%f percent loaded-----//" % length)
        stdout.flush()
        length+=fraction
    stdout.write("\r//-----100 percent loaded-----//\n")
    cur.close()
    openconnection.commit()

def queryActioner(openconnection,query):
    cur=openconnection.cursor()
    cur.execute(query)
    result=cur.fetchall();
    return result
