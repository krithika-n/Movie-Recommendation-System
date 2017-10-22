import mysql.connector
import sys
import numpy as np
import networkx as nx

no_actors_set=[]
one_row_in_array=[]
actorA_list=[]
actorB_list=[]
list_of_lists=[]
names = []
personal_dict = {}
actor_to_index={}
index_to_actor={}

try:
    # connect to the database
    conn = mysql.connector.connect(user='root',
                                   password='myfirstdb94/',
                                   host='localhost',
                                   database='mwdb')

    # get the db cursor object to interact with db
    k=0
    cur = conn.cursor()
    #get the number of actors
    cur.execute(("SELECT distinct (actorid) FROM mwdb.movie_actor;"))
    for row in cur.fetchall():
        row_ele=row[0]
        no_actors_set.append(row_ele)
        actor_to_index[row_ele]=k
        index_to_actor[k]=row_ele
        k=k+1
    no_actors=len(no_actors_set)

    my_array=np.array([],float)              #initialize numpy array for the transition matrix
    np.set_printoptions(threshold=np.nan)

    for actorA in no_actors_set:
        for actorB in no_actors_set:
            if(actorB==actorA):
                entry=0.0
            else:
                cur.execute(("SELECT movieid FROM mwdb.movie_actor where actorid={} and movieid in (select movieid from movie_actor where actorid={})".format(actorA,actorB)))
                res=cur.fetchall()
                entry=len(res)
            one_row_in_array.append(entry)
        list_of_lists.append(one_row_in_array)
        one_row_in_array=[]

    #create coactor-coactor matrix
    my_array = np.array(list_of_lists)

    #column-normalize the coactor-coactor matrix
    for i in range(my_array.shape[1]):
        sum_column = np.sum((my_array[:, i]))
        my_array[:, i] /= sum_column

    #construct graph
    g=nx.DiGraph(my_array.T)
    weighted_g=nx.DiGraph()
    for u, v in g.edges:
        weighted_g.add_edge(u, v, weight=my_array[v, u])

    teleport = np.zeros((no_actors, 1))  # teleportation matrix
    prscore = np.zeros((no_actors, 1))  # matrix for pagerank scores

    #construct a teleport and initial pagerank matrix from user input
    for i in sys.argv:
        names.append(i)
    names.remove(sys.argv[0])
    for i in names:
        key=int(i)                                            #convert string cmd-line arg to int
        personal_dict[actor_to_index[key]]= 1 / len(names)  #map each actorid to values in (0,308) in graph
        teleport[actor_to_index[key]][0] = 1 / len(names)
        prscore[actor_to_index[key]] = 1
    print("personalization dict=", personal_dict)

    #calculate pagerank with personalization

    mean_error = 1
    alpha = 0.85
    no_iter = 0
    prevscore = np.zeros((no_actors, 1))          #Matrix to compute mean error between successive pagerank scores
    prevscore = prscore

    while (mean_error > 0.00000005):
        #calculate pagerank with rwr approach
        term1 = alpha * np.matmul(my_array, prscore)
        term2 = (1 - alpha) * teleport
        prscore = term1 + term2
        #calculate error between previous and current pagerank values
        diff = abs(prscore - prevscore)
        mean_error = np.mean(diff)
        #set current pagerank scores as prevscore values
        prevscore = prscore
        no_iter = no_iter + 1

    print("Number of iterations -",no_iter)


    #sort the pagerank scores and store the rank of the sorted values in sortlist
    sortlist = np.argsort(prscore, axis=0)

    #store (index,rank) values in a dictionary
    sortdict = {}
    k = 0
    for val in sortlist:
        sortdict[k] = val[0]
        k = k + 1

    #sort the dictionary and print the actorid for the top 10 ppr values
    k = 0
    print("Top ten related actors to the seed set are:\n")
    for i in reversed(range(no_actors)):
        if (k < 10):
            actorpos = [key for key, value in sortdict.items() if value == i]
            print(index_to_actor[actorpos[0]])
            k = k + 1

except mysql.connector.Error as e:
    print(e.msg)
