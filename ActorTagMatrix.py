import MySQLdb
import csv
import sys
import operator
import math
import pandas as pd
import numpy as np
def get_actor_tag ():
	conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
	cur=conn.cursor();
	actortag={}
	cur.execute("SELECT distinct actorid from movie_actor")
	actors=cur.fetchall()
	for actid in actors:
		final_tf={}
		final_tfidf={}
		#Dictionary to store number of movies with a particular tag
		actors_with_this_tag={}
		try:
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
		except:
			print "Error"
			conn.rollback()
		#try:
		#Get all movies for this actor
		movs=cur.execute("select movieid from movie_actor where actorid=%s;",(actid,))
		mov=cur.fetchall()
		conn.commit()
		if movs==0:
			continue;
		for m in mov:
			#Get all tags per movie
			notagserr=cur.execute("select tagid from mltags where movieid=%s",(m[0],))
			tags=cur.fetchall()
			conn.commit()
			tf_normal={}	
			timestamps={}	
			if notagserr==0:
				continue;
			for t in tags:
				#If already exists in dictionary, then increment occurence of tag in movie.
				if tf_normal.has_key(t[0]):
					tf_normal[t[0]]=tf_normal[t[0]]+1
				#Since tag encountered for first time, initialize into dictionary with first occurence
				else:
					tf_normal[t[0]]=1
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
					#Get number of actors having this tag in Database
					cur.execute("select count(distinct actorid) from movie_actor,mltags where movie_actor.movieid=mltags.movieid and tagid=%s",(t[0],))
					actors_with_this_tag[t[0]]=int(cur.fetchone()[0])
					conn.commit()
			#Get actor movie rank
			cur.execute("select actor_movie_rank from movie_actor where movieid=%s and actorid=%s",(m[0], actid[0]))
			a_rank=cur.fetchall()
			actor_rank=a_rank[0][0]
			conn.commit()
			#Get number of tags in this movie
			cur.execute("select count(tagid) from mltags where movieid=%s",(m[0],))
			no_of_tags=cur.fetchall()[0][0]
			#Use formula to calculate Time-Weighted TF
			for tag_in_movie, tag_count in tf_normal.iteritems():
				if final_tf.has_key(tag_in_movie):
					final_tf[tag_in_movie]+=(float(tag_count * timestamps[tag_in_movie])/(no_of_tags * actor_rank))
				else:
					final_tf[tag_in_movie]=(float(tag_count * timestamps[tag_in_movie])/(no_of_tags * actor_rank))
		#Get total number of actors
		cur.execute("select count(actorid) from imdb_actor_info;")
		no_of_actors=cur.fetchone()[0]		
		conn.commit()
		#Calculate IDF
		for tag_in_movie, tf_val in final_tf.iteritems():
			idf=float(math.log(float(no_of_actors)/actors_with_this_tag[tag_in_movie]))
			final_tfidf[tag_in_movie]=final_tf[tag_in_movie]*idf;	
		actortag[actid[0]]=final_tfidf
	A=pd.DataFrame(actortag).fillna(0)
	conn.close()
	return A
