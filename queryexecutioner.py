def queryActioner(openconnection,query):
    cur=openconnection.cursor()
    cur.execute(query)
    result=cur.fetchall();
    return result
