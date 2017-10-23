import MySQLdb
import csv
import sys
import operator
import math
import pandas as pd
import numpy as np
import scipy
import ActorTagMatrix as acttag
import lda

def task1c(actorid,outermode, innermode):
	conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
	cur=conn.cursor()
	#Fetch the actor tag matrix of TF-IDF scores.
	actor_tag=acttag.get_actor_tag()

	#Get actorid and method from command line

	#Get this actor's tags
	thisactor_tags=actor_tag[actorid]
	#Dictionary to store distances of other actors from this actor
	dist_from_this_actor={}

	if outermode == 1:
		#Fetch all actors
		cur.execute("SELECT distinct actorid from movie_actor;")
		actors=cur.fetchall()

		for a in actors:
			#Do not compute distance to same actor
			if a[0]==actorid:
				continue
			#Fetch other actor's tags
			otheractor_tags=actor_tag[a[0]]
			#Compute distances and store
			from scipy import spatial
			dist=spatial.distance.euclidean(thisactor_tags, otheractor_tags)
			if math.isnan(dist) == False:
				dist_from_this_actor[a[0]]=math.fabs(dist)

	else:
		#Dictionary to store actorid to index mapping before doing dimensionality reduction
		actor_dict={}
		i=0
		for actor, scores in actor_tag.iteritems():
			actor_dict[actor]=i
			i=i+1
		#Do SVD
		if innermode == 1:
			[u,s,v]=np.linalg.svd(actor_tag.T, full_matrices=0)
			tottags=len(actor_tag[actorid])
			s_mat=[[0]*5]*5
			s_mat=np.diag(s[:5])
			actors_to_ls=np.dot(u[:,:5],s_mat)
			#Get this actor's tag vectors
			thisactortagvector=actors_to_ls[actor_dict[actorid]]
			#Get all other actors
			cur.execute("SELECT distinct actorid from movie_actor where actorid!=%s;",(actorid,))
			actors=cur.fetchall()
			for a in actors:
				otheractor_tags=actors_to_ls[actor_dict[a[0]]]
				#Compute distance to other actors
				from scipy import spatial
				dist=spatial.distance.cosine(thisactortagvector, otheractor_tags)
				if math.isnan(dist) == False:
					dist_from_this_actor[a[0]]=math.fabs(dist)
		#Do PCA
		if innermode == 2:
			#Get covariance matrix
			actor_tag_cov=np.cov(actor_tag.T)
			[u,s,v]=np.linalg.svd(actor_tag_cov.T, full_matrices=0)
			tottags=len(actor_tag[actorid])
			s_mat=[[0]*5]*5
			s_mat=np.diag(s[:5])
			actors_to_ls=np.dot(u[:,:5],s_mat)
			#Get this actor's tag vector
			thisactortagvector=actors_to_ls[actor_dict[actorid]]
			cur.execute("SELECT distinct actorid from movie_actor where actorid!=%s;",(actorid,))
			actors=cur.fetchall()
			for a in actors:
				#Get other actor's tag vector
				otheractor_tags=actors_to_ls[actor_dict[a[0]]]
				#Compute distances to other actors
				from scipy import spatial
				dist=spatial.distance.cosine(thisactortagvector, otheractor_tags)
				if math.isnan(dist) == False:
					dist_from_this_actor[a[0]]=math.fabs(dist)
		#Do LDA
		if innermode == 3:
			print "At LDA"
			actor_tag={}
			cur.execute("SELECT distinct actorid from movie_actor")
			actors=cur.fetchall()
			#Dictionary to store actor index mapping
			actor_dict={}
			i=0
			for actor in actors:
				actor_dict[actor[0]]=i
				i=i+1
			#Construct actor-tag count matrix
			for actid in actors:
				tf_normal={}
				movs=cur.execute("select movieid from movie_actor where actorid=%s;",(actid[0],))
				mov=cur.fetchall()
				conn.commit()
				if movs==0:
					continue;
				for m in mov:
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
				actor_tag[actid]=tf_normal
			#Convert into a dataframe
			A=pd.DataFrame(actor_tag).fillna(0).astype(int)
			X=np.array(A)
			#Apply LDA
			model=lda.LDA(n_topics=5, n_iter=10, random_state=1)
			model.fit(X)
			#Get reduced mapping in latent semantic space to documents and words.
			topic_word=model.topic_word_
			actor_topic_ls=topic_word.T
			#Get this actor's mapping in new space
			thisactortagvector=actor_topic_ls[actor_dict[actorid]]
			#Get all other actors
			cur.execute("SELECT distinct actorid from movie_actor where actorid!=%s;",(actorid,))
			actors=cur.fetchall()
			for a in actors:
				otheractor_topics=actor_topic_ls[actor_dict[a[0]]]
				#Compute distance
				from scipy import spatial
				dist=spatial.distance.cosine(thisactortagvector, otheractor_topics)
				if math.isnan(dist) == False:
					dist_from_this_actor[a[0]]=math.fabs(dist)

	#Sort the distances and print the result
	sorted_dist=sorted(dist_from_this_actor.items(), reverse=0, key=operator.itemgetter(1))
	i=0
	results={}
	cur.execute("SELECT name from imdb_actor_info where actorid=%s",(actorid,))
	name=cur.fetchone()[0]
	print("The top 10 related actors to the actor whose actor ID is: "+str(actorid)+" and name: "+str(name))
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

#task1c(3558986, 1, 0)
