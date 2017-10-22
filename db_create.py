import MySQLdb
conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")

print("GENOME")
cur=conn.cursor()
try:
	cur.execute("CREATE TABLE IF NOT EXISTS genome( tagid INT, tag VARCHAR(400) );")
	conn.commit()
except:
	conn.rollback()

print("IMDB ACTOR INFO")
cur=conn.cursor()
try:
	cur.execute("CREATE TABLE IF NOT EXISTS imdb_actor_info( actorid INT, name VARCHAR(400), gender VARCHAR(1) );")
	conn.commit()
except:
	conn.rollback()

print("MLMOVIES")
cur=conn.cursor()
try:
	cur.execute("CREATE TABLE IF NOT EXISTS mlmovies( movieid INT, moviename VARCHAR(400), year INT, genres VARCHAR(400) );")
	conn.commit()
except:
	conn.rollback()

print("MLRATINGS")
cur=conn.cursor()
try:
	cur.execute("CREATE TABLE IF NOT EXISTS mlratings( movieid INT, userid INT, imdbid INT, rating INT, timst TIMESTAMP );")
	conn.commit()
except:
	conn.rollback()

print("MLTAGS")
cur=conn.cursor()
try:
	cur.execute("CREATE TABLE IF NOT EXISTS mltags( userid INT, movieid INT, tagid INT, timst DATETIME);")
	conn.commit()
except:
	print "Error"
	conn.rollback()

print("MLUSERS")
cur=conn.cursor()
try:
	cur.execute("CREATE TABLE IF NOT EXISTS mlusers( userid INT);")
	conn.commit()
except:
	conn.rollback()

print("ACTOR_MOVIE_RANK")
cur=conn.cursor()
try:
	cur.execute("CREATE TABLE IF NOT EXISTS movie_actor( movieid INT, actorid INT, actor_movie_rank INT);")
	conn.commit()
except:
	conn.rollback()

conn.close()	
