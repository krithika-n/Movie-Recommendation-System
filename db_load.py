import MySQLdb
import csv

conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")

#Load genome-tags.csv into genome table
f=open("./phase2_dataset/genome-tags.csv","rb")
r=csv.reader(f)
r=list(r)[1:]
conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")

cur=conn.cursor()
try:
	for row in r:
		cur.execute("INSERT INTO genome VALUES(%s, %s);",(row))
		conn.commit()
	print 'genome tags database loaded'
except Exception as e:
	print e
	conn.rollback()

f.close()

#Load imdb-actor-info.csv into imdb_actor_info table
f=open("./phase2_dataset/imdb-actor-info.csv","rb")
r=csv.reader(f)
r=list(r)[1:]
cur=conn.cursor()
try:
	for row in r:
		cur.execute("INSERT INTO imdb_actor_info VALUES(%s, %s, %s);",(row))
		conn.commit()
	print 'imdb actor info tags database loaded'
except:
	print "Error"
	conn.rollback()

f.close()

#Load mlmovies.csv into mlmovies table
f=open("./phase2_dataset/mlmovies.csv","rb")
r=csv.reader(f)
r=list(r)[1:]
cur=conn.cursor()
try:
	for row in r:
		cur.execute("INSERT INTO mlmovies VALUES(%s, %s, %s, %s);",(row))
		conn.commit()
	print 'mlmovies database loaded'
except:
	print "Error"
	conn.rollback()

f.close()

#Load mltags.csv into mltags table
f=open("./phase2_dataset/mltags.csv","rb")
r=csv.reader(f)
r=list(r)[1:]
cur=conn.cursor()
try:
	for row in r:
		cur.execute("INSERT INTO mltags VALUES(%s, %s, %s, %s);",(row))
		conn.commit()
	print 'mltags database loaded'
except:
	print "Error"
	conn.rollback()

f.close()

#Load mlusers.csv into mlusers table
f=open("./phase2_dataset/mlusers.csv","rb")
r=csv.reader(f)
r=list(r)[1:]
cur=conn.cursor()
try:
	for row in r:
		cur.execute("INSERT INTO mlusers VALUES(%s);",(row))
		conn.commit()
	print 'mlusers database loaded'
except:
	print "Error"
	conn.rollback()

#Load movie-actor.csv into movie_actor table
f=open("./phase2_dataset/movie-actor.csv","rb")
r=csv.reader(f)
r=list(r)[1:]
cur=conn.cursor()
try:
	for row in r:
		cur.execute("INSERT INTO movie_actor VALUES(%s, %s, %s);",(row))
		conn.commit()
	print 'movie actor database loaded'
except:
	print "Error"
	conn.rollback()

f.close()

#Load mlratings.csv into mlratings table
f=open("./phase2_dataset/mlratings.csv","rb")
r=csv.reader(f)
r=list(r)[1:]
cur=conn.cursor()
try:
	for row in r:
		cur.execute("INSERT INTO mlratings VALUES(%s, %s, %s, %s, %s);",(row))
		conn.commit()
	print 'mlratings database loaded'
except:
	print "Error"
	conn.rollback()

f.close()
