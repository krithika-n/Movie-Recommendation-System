import MySQLdb
import numpy as np
import collections
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation as LDA

def lda(userid):
    try:
        user_tag={}
        conn = MySQLdb.connect(user='root', passwd='haha123', host='127.0.0.1', db="mwdb")
        cur=conn.cursor();
        
        cur.execute("SELECT distinct userid from mltags")
        users=cur.fetchall()
        #Dictionary to store actor index mapping
        user_dict={}
        i=0
        for u in users:
            user_dict[u[0]]=i
            i=i+1
	    
        
        np.set_printoptions(threshold=np.nan)      
        #user-tag count matrix
        for u in users:
            cur.execute("Select tagid from mltags where userid={}".format(u[0]))
            res=cur.fetchall()
            taglist=[]
            tag_vector={}
            for r in res:
                taglist.append(r[0])
            tag_vector=collections.Counter(taglist)
            user_tag[u[0]]=tag_vector
        A=pd.DataFrame(user_tag).fillna(0).astype(int)
        X=np.array(A.T)
        
        print(X.shape)
        #Apply LDA
        model=LDA(n_components=4, max_iter=10, random_state=0)
        model.fit(X)
        Y=model.transform(X)
        #print(Y[0])
        #print(Y.shape)
        
    except  MySQLdb.Error as e:
       print(e)  
lda(20)                                                                                                                                                                                                                               	