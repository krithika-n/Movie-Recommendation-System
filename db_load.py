import MySQLdb
import csv

conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")

#Load genome-tags.csv into genome table
f=open("../phase2_dataset/genome-tags.csv","rb")
r=csv.reader(f)

conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mydb")

cur=conn.cursor()
try:
	for row in r:
		print row[0]+" "+row[1]
		cur.execute("INSERT INTO genome VALUES(%s, %s);",(row))
		conn.commit()
except:
	print "Error"
	conn.rollback()

f.close()

#Load imdb-actor-info.csv into imdb_actor_info table
f=open("../phase2_dataset/imdb-actor-info.csv","rb")
r=csv.reader(f)

cur=conn.cursor()
try:
	for row in r:
		print row[0]+" "+row[1]+" "+row[2]
		cur.execute("INSERT INTO imdb_actor_info VALUES(%s, %s, %s);",(row))
		conn.commit()
except:
	print "Error"
	conn.rollback()

f.close()
'''
#Load mlmovies.csv into mlmovies table
f=open("../phase2_dataset/mlmovies.csv","rb")
r=csv.reader(f)

cur=conn.cursor()
try:
	for row in r:
		print row[0]+" "+row[1]+" "+row[2]+" "+row[3]
		cur.execute("INSERT INTO mlmovies VALUES(%s, %s, %s, %s);",(row))
		conn.commit()
except:
	print "Error"
	conn.rollback()

f.close()
'''
#Load mltags.csv into mltags table
f=open("../phase2_dataset/mltags.csv","rb")
r=csv.reader(f)

cur=conn.cursor()
try:
	for row in r:
		print row[0]+" "+row[1]+" "+row[2]+" "+row[3]
		cur.execute("INSERT INTO mltags VALUES(%s, %s, %s, %s);",(row))
		conn.commit()
except:
	print "Error"
	conn.rollback()

f.close()

#Load mlusers.csv into mlusers table
f=open("../phase2_dataset/mlusers.csv","rb")
r=csv.reader(f)

cur=conn.cursor()
try:
	for row in r:
		print row[0]
		cur.execute("INSERT INTO mlusers VALUES(%s);",(row))
		conn.commit()
except:
	print "Error"
	conn.rollback()

#Load movie-actor.csv into movie_actor table
f=open("../phase2_dataset/movie-actor.csv","rb")
r=csv.reader(f)

cur=conn.cursor()
try:
	for row in r:
		print row[0]+" "+row[1]+" "+row[2]
		cur.execute("INSERT INTO movie_actor VALUES(%s, %s, %s);",(row))
		conn.commit()
except:
	print "Error"
	conn.rollback()

f.close()

#Load mlratings.csv into mlratings table
f=open("../phase2_dataset/mlratings.csv","rb")
r=csv.reader(f)

cur=conn.cursor()
try:
	for row in r:
		print row[0]+" "+row[1]+" "+row[2]+" "+row[3]+" "+row[4]
		cur.execute("INSERT INTO mlratings VALUES(%s, %s, %s, %s, %s);",(row))
		conn.commit()
except:
	print "Error"
	conn.rollback()

f.close()
