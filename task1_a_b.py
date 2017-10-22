import queryexecutioner
import numpy
import lda
import lda.datasets
import MySQLdb
import sys
def task1_a(genre,model):
    try:
        con = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
        tags=queryexecutioner.queryActioner(con, 'select distinct(tagid) from mltags')#collecting all the distinct tags from mltags
        tagnames=queryexecutioner.queryActioner(con,'select * from genome')
        tag_tagnames={}
        for i in tagnames:
            tag_tagnames[i[0]]=i[1]#maintaining a dictionary for tag to tagname reference
        movies=queryexecutioner.queryActioner(con,'select distinct(movieid) from mlmovies where genres like \'%'+genre+'%\'')#selecting all the movies with the particular genre
        finalarray=[]#this is the final movie to tag tf-idf score vector
        #
        #We are looping over each movies and making a movie to tag tf-idf score matrix.
        #if there are no tags for the movies then the score is zero.
        #
        if model=='1' or model=='0':
            for movie in movies:
                movieList=[]
                noOfTags=queryexecutioner.queryActioner(con, 'select count(tagid) from mltags where movieid ='+str(movie[0]))[0][0]
                if noOfTags==0:
                    finalarray.append([0.0 for tag in tags])
                else:
                    for tag in tags:
                        idf=float(len(movies))/(queryexecutioner.queryActioner(con, 'select count(distinct(movieid)) from mltags where tagid ='+str(tag[0])))[0][0]
                        movieList.append((float((queryexecutioner.queryActioner(con, 'select count(*) from mltags where tagid ='+str(tag[0])+' and movieid='+str(movie[0])))[0][0])/noOfTags)*idf)
                    finalarray.append(movieList)
            x=numpy.array(finalarray)
            #x=numpy.matrix.transpose(x)#dimensionality reduction on x
            if model=='1':
                x=numpy.cov(x)#covariance of x
            U, s, V = numpy.linalg.svd(x, full_matrices=False)
            #latent_semantics=U[:,0:3]
            #transpose=numpy.matrix.transpose(V)
            latent_semantics = V[0:3, :]
            for (key,topic) in enumerate(latent_semantics):
                string='topic'+str(key)+'='
                sorted_tags=numpy.argsort(latent_semantics[key])[::-1]
                for tag in sorted_tags:
                    string+=tag_tagnames[tags[tag][0]]+'*'+str(latent_semantics[key][tag])
                print string
                print '--------------'
        if model=='2':
            for movie in movies:
                movieList=[]
                for tag in tags:
                    movieList.append(queryexecutioner.queryActioner(con,'select count(*) from mltags where tagid='+str(tag[0])+' and movieid='+str(movie[0]))[0][0])
                finalarray.append(movieList)
            x=numpy.array(finalarray)
            model = lda.LDA(n_topics=4, n_iter=100, random_state=1)
            model.fit(x)
            topic_word = model.topic_word_
            for key, topic in enumerate(topic_word):
                string = str([[tag_tagnames[tags[i][0]]] for i in numpy.argsort(topic)[::-1]])
                print 'topic' + str(key) + string
    except Exception as e:
        print e
def task1_b(genre,model):
    con = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
    actornames=queryexecutioner.queryActioner(con,'select * from imdb_actor_info')
    actor_actornames={}
    for i in actornames:
        actor_actornames[i[0]]=i[1]
    movies=queryexecutioner.queryActioner(con,'select distinct(movieid) from mlmovies where genres like \'%'+genre+'%\'')
    actors=queryexecutioner.queryActioner(con,'select distinct(movie_actor.actorid) from movie_actor inner join mlmovies on (movie_actor.movieid = mlmovies.movieid) where genres like \'%'+genre+'%\'')
    finalarray=[]
    if model=='0' or model=='1':
        for movie in movies:
            movieList=[]
            noOfActors=queryexecutioner.queryActioner(con, 'select count(actorid) from movie_actor where movieid ='+str(movie[0]))[0][0]
            for actor in actors:
                #print float((queryexecutioner.queryActioner(con, 'select count(*) from mltags where tagid ='+str(tag[0])+' and movieid='+str(movie[0])))[0][0])
                idf=float(len(movies))/(queryexecutioner.queryActioner(con, 'select count(distinct(movieid)) from movie_actor where actorid ='+str(actor[0])))[0][0]
                movieList.append((float((queryexecutioner.queryActioner(con, 'select count(*) from movie_actor where actorid ='+str(actor[0])+' and movieid='+str(movie[0])))[0][0])/noOfActors)*idf)
            finalarray.append(movieList)
        x=numpy.array(finalarray)
        #x=numpy.matrix.transpose(x)
        if model=='1':
            x=numpy.cov(x)
        U, s, V = numpy.linalg.svd(x, full_matrices=False)
        latent_semantics=V[0:3,:]
        #transpose=numpy.matrix.transpose(latent_semantics)
        for (key,topic) in enumerate(latent_semantics):
            string='topic'+str(key)+'='
            sorted_actors=numpy.argsort(latent_semantics[key])[::-1]
            for actor in sorted_actors:
                string+=actor_actornames[actors[actor][0]]+'*'+str(latent_semantics[key][actor])
            print string
            print '--------------'
    if model=='2':
        for movie in movies:
            movieList=[]
            for actor in actors:
                #print float((queryexecutioner.queryActioner(con, 'select count(*) from mltags where tagid ='+str(tag[0])+' and movieid='+str(movie[0])))[0][0])
                #idf=float(len(movies))/(queryexecutioner.queryActioner(con, 'select count(distinct(movieid)) from movieactor where actorid ='+str(actor[0])))[0][0]
                movieList.append(queryexecutioner.queryActioner(con, 'select count(*) from movie_actor where actorid ='+str(actor[0])+' and movieid='+str(movie[0]))[0][0])
            finalarray.append(movieList)
        #print (finalarray)
        x = numpy.array(finalarray)
        #x = numpy.matrix.transpose(x)
        model = lda.LDA(n_topics=4, n_iter=100, random_state=1)
        model.fit(x)
        topic_word = model.topic_word_
        string=''
        for key,topic in enumerate(topic_word):
            string=str([actor_actornames[actors[i][0]]for i in numpy.argsort(topic)[::-1]])
            print 'topic'+str(key)+string

