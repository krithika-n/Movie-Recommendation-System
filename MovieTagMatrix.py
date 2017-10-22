import MySQLdb
import csv
import sys
import operator
import math
import pandas as pd
import numpy as np
import scipy
def get_movie_tag():
	conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
	cur=conn.cursor();
	movietag={}
	movies_with_tag={}
	#Get maximum timestamp
	cur.execute("select unix_timestamp(max(timst)) from mltags;")
	max_time=cur.fetchone()[0]	
	conn.commit()

	#Get minimum timestamp
	cur.execute("select unix_timestamp(min(timst)) from mltags;")
	min_time=cur.fetchone()[0]
	conn.commit()

	#For normalization
	time_denom=max_time-min_time;
	cur.execute("SELECT distinct movieid FROM mlmovies;")
	allmovies=cur.fetchall()
	cur.execute("SELECT count(distinct movieid) FROM mlmovies;")
	no_of_movies=cur.fetchone()[0]
	conn.commit()
	for m in allmovies:
		count_tf={}
		final_tfidf={}
		timestamps={}
		notagserr=cur.execute("SELECT tagid FROM mltags WHERE movieid=%s", (m[0],))
		tags=cur.fetchall()
		conn.commit()
		cur.execute("SELECT COUNT(distinct tagid) FROM mltags where movieid=%s",(m[0],))
		no_of_tags=cur.fetchone()[0]
		conn.commit()		
		for t in tags:
			if count_tf.has_key(t[0]):
				count_tf[t[0]]=count_tf[t[0]]+1
			else:
				count_tf[t[0]]=1
				#Get set of timestamps for this tag in this movie to get time-weighted TF and TF-IDF
				cur.execute("select unix_timestamp(timst) from mltags where movieid=%s and tagid=%s",(m[0],t[0]))
				times=cur.fetchall()
				conn.commit()		
				#Normalize and add all timestamps of occurences of tag
				norm_tim_sum=0
				for tim in times:
					norm_tim=(float(tim[0]-min_time)/time_denom)
					norm_tim_sum+=norm_tim
				timestamps[t[0]]=norm_tim_sum
				cur.execute("SELECT COUNT(tagid) FROM mltags where movieid=%s",(m[0],))
				movies_with_tag[t[0]]=int(cur.fetchone()[0])
				conn.commit()
		for tag, count in count_tf.iteritems():
			tfscore=(float(count_tf[tag])/no_of_tags)
			idf=float(math.log(float(no_of_movies)/movies_with_tag[tag]))
			final_tfidf[tag]=count_tf[tag]*idf*timestamps[tag]
		movietag[m[0]]=final_tfidf
	A=pd.DataFrame(movietag).fillna(0)
	conn.close()
	return A

