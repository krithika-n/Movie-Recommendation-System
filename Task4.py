import numpy
import scipy
from sklearn.decomposition import PCA
import math
from collections import defaultdict
import MySQLdb
import sys

db = MySQLdb.connect(host="127.0.0.1", 
                      user="root", 
                      passwd="haha123", 
                      db="mwdb") 

cursor = db.cursor() 
movie=[]
suggested=[]
feedback=[]
cursor.execute("select distinct moviename from mlmovies;")
movies=cursor.fetchall()
for i in movies:
	movie.append(i[0])


inputMatrix=numpy.load("MovieTagReduced.npy")
values=[]
W=4

 

def H(inp,X,W):
	
	return (numpy.dot(inp,X)/W);

def closestpositive(W,maxi):
	val=0
	for i in range(0,int(math.floor(maxi)+1),W):
		val=i+W
		if (val>=int(math.floor(maxi)+1)):
			return val

def closestnegative(W,mini):
	val=0
	for i in range(0,int(math.floor(mini)-1),-W):
		val=i-W
		if (val<=int(math.floor(mini)-1)):
			return val

	
		    
def LSH(inputvectors,L,K,moviename,R):
	values=numpy.zeros(len(inputvectors))
	temp=numpy.ones(len(inputvectors)) 
	

	
	for lr in range(0,L):
		for hashfn in range(0,K):
			points=[]
			X=numpy.random.rand(500,1)
			for i in range(0,len(inputvectors)):
				points.extend(H(inputvectors[i,:],X,W))
			temp=temp*points	
			values=values+temp


	

	maxi=max(values)
	mini=min(values)
	

	
	for i in range(0,len(values)):
		values[i]=((values[i]-mini)/maxi-mini)*100
		

	

	highestbinvalue=closestpositive(W,maxi)
	leastbinvalue=closestnegative(W, mini)
	
	
	binNo=[]
	for i in range(0,len(values)):
		binNo.append(math.floor(values[i]/W))
	#print set(binNo)
	Zippedbins=zip(binNo,values)
	Zippedmoviebins=zip(binNo,movie)
	
	bins=defaultdict(list)
	
	for k,v in Zippedmoviebins:
		bins[k].append(v)

	

	#for i in range(int(min(binNo)),int(max(binNo)+1) ):
	#	print i,bins[i]
	
	

	for i in range(int(min(binNo)),int(max(binNo)+1) ):
		if moviename in (bins[i]):
			topmoviesindex=i
			no=len(bins[i])
			print "BinNo",topmoviesindex
			#print "Number of movies considered",len(bins[i])
	
	if len(bins[topmoviesindex])>R:
		
		for i in range(0,R):
			if moviename not in bins[topmoviesindex][i]:
				suggested.append(bins[topmoviesindex][i])
			else:
				suggested.append(bins[topmoviesindex][R])
	
	if len(bins[topmoviesindex])<=R:
		Rem=R-len(bins[topmoviesindex])
		for i in range(0,len(bins[topmoviesindex])):
			if moviename not in (bins[topmoviesindex][i]):
				suggested.append(bins[topmoviesindex][i])
			else:
				Rem+=1
		
		while Rem>0:
			if topmoviesindex==max(binNo):
				topmoviesindex=min(binNo)
			topmoviesindex+=1
			tmp=len(bins[topmoviesindex])
			no=no+tmp
			if tmp>0:
				if(tmp>=Rem):
					for i in range(0,Rem):
						suggested.append(bins[topmoviesindex][i])
					Rem=0

				if(tmp<Rem):
					for i in range(0,tmp):
						suggested.append(bins[topmoviesindex][i])
					Rem=Rem-tmp
			else:
			   Rem=Rem-tmp
	print "Number of movies considered",no
	print "\n"
	print "Suggestions:"
	print "\n"


	
	for i in suggested:
		print i

	if ( neighbours != len(suggested)) :
		print "not enough suggestions"

	print "\nFeedBack:"

	for i in range(0,neighbours):
		print suggested[i], "\t\tpositive(1), negative(-1) or neutral(0) ??"
		feedback.append(str(raw_input()))




	feedback1=zip(feedback, suggested)

	print "Suggestions after Feedback"
	print ""
	

	count=0
	for i,j in feedback1:
				
		if i=='1':
			
			print j
			count+=1
			if j in bins[topmoviesindex]:
				bins[topmoviesindex].remove(j)
	

			
	
		if i=='-1':
			if j in bins[topmoviesindex]:
				bins[topmoviesindex].remove(j)
	
	
	
	remaining=R-count
	if len(bins[topmoviesindex])>remaining:
		for i in range(0,remaining):
			if moviename!= bins[topmoviesindex][i]:
				print bins[topmoviesindex][i]
			else:
				print bins[topmoviesindex][remaining]

	else:
		Rem=remaining-len(bins[topmoviesindex])
		for i in range(0,len(bins[topmoviesindex])):
			if moviename not in (bins[topmoviesindex][i]):
				print bins[topmoviesindex][i]
			else:
				Rem+=1
		
		while Rem>0:
			if topmoviesindex==max(binNo):
				topmoviesindex=min(binNo)
			topmoviesindex+=1
			tmp=len(bins[topmoviesindex])
			no=no+tmp
			if tmp>0:
				if(tmp>=Rem):
					for i in range(0,Rem):
						print bins[topmoviesindex][i]
					Rem=0

				if(tmp<Rem):
					for i in range(0,tmp):
						print bins[topmoviesindex][i]
					Rem=Rem-tmp
			else:
			   Rem=Rem-tmp



layers=int(sys.argv[1])
hashes=int(sys.argv[2])
movieName=sys.argv[3]
neighbours=int(sys.argv[4])
LSH(inputMatrix,layers,hashes,movieName,neighbours)



