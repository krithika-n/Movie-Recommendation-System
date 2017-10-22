import MySQLdb
import csv
import sys
import operator
import math
import pandas as pd
import numpy as np
import scipy
import MovieTagMatrix as movtag
import ActorTagMatrix as acttag
import lda
import lda.datasets

def task1d(movieid,outermode):
	conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
	cur=conn.cursor()
	#Get movie-tag mapping and actor-tag mapping.
	movie_tag=movtag.get_movie_tag()
	actor_tag=acttag.get_actor_tag()

	#Dictionary to store distances of actors from this given movie
	dist_from_movie={}
	#Get method to use and movieid as command line arguments
	#Get this movie's tag space
	movietags=movie_tag[movieid]
	cur.execute("SELECT moviename from mlmovies where movieid=%s",(movieid,))
	mov_name=cur.fetchone()[0]

	#TF-IDF Tag vector space
	if outermode== 1:
		cur.execute("SELECT distinct actorid from movie_actor where movieid!=%s;",(movieid,))
		actors=cur.fetchall()
		for a in actors:
			actortags=actor_tag[a[0]]
			#Compute distance from every actor who has not acted in this movie to the given movie using respective tag vectors.
			from scipy import spatial
			dist=spatial.distance.euclidean(movietags, actortags)
			if math.isnan(dist) == False:
				dist_from_movie[a[0]]=math.fabs(dist)

	#Dimensionality reduction
	if outermode == 2:
		#Dictionary to store movieid to index mapping
		movie_dict={}
		i=0
		for movie, scores in movie_tag.iteritems():
			movie_dict[movie]=i
			i=i+1
		#Dictionary to store tagid to index mapping
		tag_dict={}
		i=0
		for tag, scores in movie_tag.T.iteritems():
			tag_dict[tag]=i
			i=i+1
		#Get which method to use
		innermode=int(sys.argv[3])
		#Do SVD
		if innermode == 1:
			[u,s,v]=np.linalg.svd(movie_tag.T, full_matrices=0)
			tottags=len(movie_tag[movieid])
			s_mat=[[0]*5]*5
			s_mat=np.diag(s[:5])
			#Get mappings from movies and tags to reduced latent semantic space
			movies_to_ls=np.dot(u[:,:5],s_mat)
			tags_to_ls=np.dot(s_mat, v[:5,:])
			tags_to_ls=tags_to_ls.T
			#Get this movie's tag vector in reduced space
			thismovietagvector=movies_to_ls[movie_dict[movieid]]
			cur.execute("SELECT distinct actorid from movie_actor where movieid!=%s;",(movieid,))
			actors=cur.fetchall()
			for a in actors:
				#Get actor's tag vector in TF-IDF space
				otheractor_tags=actor_tag[a[0]]
				query=[]
				#Iterate for every tag belonging to this actor
				for other_tag, other_score in otheractor_tags.iteritems():
					#Construct the actor's data point in reduced space by computing centroid.
					if other_score!=0:
						query.append(other_tag)

				actordatapoint=[0]*5
				count=0
				for tags in query:
					actordatapoint=actordatapoint+tags_to_ls[tag_dict[tags]]
					count=count+1
				if count == 0:
					continue
				for x in actordatapoint:
					x=x/count
				#Compute distance from movie to actor in reduced latent semantic space
				from scipy import spatial
				dist=spatial.distance.cosine(thismovietagvector, actordatapoint)
				if math.isnan(dist) == False:
					dist_from_movie[a[0]]=math.fabs(dist)
		#Do PCA
		if innermode == 2:
			#Get covariance matrix
			movie_tag=np.cov(movie_tag)
			[u,s,v]=np.linalg.svd(movie_tag.T, full_matrices=0)
			tottags=len(movie_tag[movie_dict[movieid]])
			s_mat=[[0]*5]*5
			s_mat=np.diag(s[:5])
			#Get mappings from movies and tags to reduced latent semantic space
			movies_to_ls=np.dot(u[:,:5],s_mat)
			tags_to_ls=np.dot(s_mat, v[:5,:])
			tags_to_ls=tags_to_ls.T
			#Get this movie's tag vector
			thismovietagvector=movies_to_ls[movie_dict[movieid]]
			cur.execute("SELECT distinct actorid from movie_actor where movieid!=%s;",(movieid,))
			actors=cur.fetchall()
			for a in actors:
				#Get actor's tag vector in TF-IDF space
				otheractor_tags=actor_tag[a[0]]
				query=[]
				#Construct this actor's data point in reduced latent semantic space.
				for other_tag, other_score in otheractor_tags.iteritems():
					#Iterate for every tag in latent semantic space and compute centroid as the data point for this actor
					if other_score!=0:
						query.append(other_tag)
				actordatapoint=[0]*5
				count=0
				for tags in query:
					actordatapoint=actordatapoint+tags_to_ls[tag_dict[tags]]
					count=count+1
				if count == 0:
					continue
				for x in actordatapoint:
					x=x/count

				#Compute distances from given movie to this actor
				from scipy import spatial
				dist=spatial.distance.cosine(thismovietagvector, actordatapoint)
				if math.isnan(dist) == False:
					dist_from_movie[a[0]]=math.fabs(dist)
		#Do LDA
		if innermode == 3:
			#Dictionary to store movie-tag count matrix
			movie_tag={}
			cur.execute("SELECT distinct movieid from mlmovies;")
			movies=cur.fetchall()
			#Dictionary to store mappings from movies to indexes
			movie_dict={}
			i=0
			for m in movies:
				movie_dict[m[0]]=i
				i=i+1
			#Construct movie-tag count matrix
			for m in movies:
				count_tf={}
				cur.execute("SELECT tagid from mltags where movieid=%s",(m[0],))
				tags=cur.fetchall()
				for t in tags:
					if count_tf.has_key(t[0]):
						count_tf[t[0]]=count_tf[t[0]]+1
					else:
						count_tf[t[0]]=1
				movie_tag[m[0]]=count_tf
			#Convert into DataFrame
			A=pd.DataFrame(movie_tag).fillna(0).astype(int)
			#Dictionary to store tags to indexes mapping
			tags_dict={}
			i=0
			for tag, scores in A.T.iteritems():
				tags_dict[tag]=i
				i=i+1
			#Convert into numpy array
			X=np.array(A)
			model=lda.LDA(n_topics=5, n_iter=10, random_state=1)
			model.fit(X)
			#Get movies to topic mapping
			movie_topic=model.topic_word_.T
			#Get tags to topics mapping
			tags_topic=model.doc_topic_
			#Fetch the vector in topic space for given movie.
			thismovietagvector=movie_topic[movie_dict[movieid]]
			#For every actor who hasn't acted in this movie
			cur.execute("SELECT distinct actorid from movie_actor where movieid!=%s;",(movieid,))
			actors=cur.fetchall()
			for a in actors:
				#Fetch TF-IDF tag vector for this actor
				otheractor_tags=actor_tag[a[0]]
				query=[]
				#Compute actor's data point in topic space as centroid of all tag points in the topic space
				for other_tag, other_score in otheractor_tags.iteritems():
					#Consider only non-zero scored tags
					if other_score!=0:
						query.append(other_tag)
				actordatapoint=[0]*5
				count=0
				for tags in query:
					actordatapoint=actordatapoint+tags_topic[tag_dict[tags]]
					count=count+1
				if count == 0:
					continue
				for x in actordatapoint:
					x=x/count
				#Compute distances from this actor to given movie and store
				from scipy import spatial
				dist=spatial.distance.cosine(thismovietagvector, actordatapoint)
				if math.isnan(dist) == False:
					dist_from_movie[a[0]]=math.fabs(dist)

	#Sort and display the results
	sorted_dist=sorted(dist_from_movie.items(), reverse=0, key=operator.itemgetter(1))
	i=0
	results={}
	print("The top 10 most related actors to the movie with movieid = "+str(movieid)+" and movie name: '"+str(mov_name)+"' who have not acted in the movie are: ")
	print("ActorID ActorName")
	for actor, res in sorted_dist:
		cur.execute("select name from imdb_actor_info where actorid=%s",(actor))
		name=cur.fetchone()[0]
		print(str(actor)+" "+"'"+str(name)+"'")
		if i==10:
			break
		results[actor]=res
		i=i+1
	print("\n")


