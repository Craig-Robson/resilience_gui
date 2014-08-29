# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 10:12:43 2012

@author: a8243587
"""

#Theoretic, in-house graph algorthims

import networkx as nx
import random as r

#HR
#HR+
#HC - may take a bit of working to use both square and triangle structures (which also need checking)

def hr(a,b,p):
    '''a = number of levels, b = nodes per level, p = total number of edges wanted'''
    G = nx.balanced_tree(a,b) #generate graph
    nodes = G.number_of_nodes()
    e1 = nx.number_of_edges(G)
    #print 'number of edges is: ', e1
    #print 'number of edges wanted is: ', p
    p = p - e1 #subtract the number of edges in G from the number of edges wanted to find how many to add
    #print 'number of edges to add: ', p
    #round(e1)
    #e1=int(e1)                     
    y = 0
    yrand = p
    while y<yrand:                    
        w1=r.randint(0,nodes) #generate two random node values
        w2=r.randint(0,nodes)
        while w1==w2: #need to check not the same value
            w2=r.randint(0,nodes)
        G.add_edge(w1,w2)
        y+=1
        
    return G
    
'''
def hr(a,b,p):
    ''a = number of levels, b = nodes per level, p = total number of edges wanted''
    G = nx.balanced_tree(a,b) #generate graph
    nodes = G.number_of_nodes()
    e1 = nx.number_of_edges(G)
    print 'number of edges is: ', e1
    print 'number of edges wanted is: ', p
    e1 = e1*p
    round(e1)
    e1=int(e1)                     
    y = 0
    yrand = e1
    while y<yrand:                    
        w1=r.randint(0,nodes) #generate two random node values
        w2=r.randint(0,nodes)
        while w1==w2: #need to check not the same value
            w2=r.randint(0,nodes)
        G.add_edge(w1,w2)
        y+=1
        
    return G
'''
def ahr(a,b,p, numofedges):
    '''a = number of levels, b = nodes per level, p = probability, numofedges = total number of edges wanted'''
    #print 'this has been sorted' #two erros. first was the z value was set to zero, rather than one.
    #secondly, max node value in both loops was one two hogh in all instances.
    #generate graph
    G = nx.balanced_tree(a,b)
    #print 'the number of edges are: ', G.number_of_edges()
    #print 'the number edges needed is: ', numofedges
    #print 'number of nodes is: ', G.number_of_nodes() 
    
    if G.number_of_edges() > numofedges:
        print 'IMPOSSIBLE TO CREATE'
        exit()
    numofedges = numofedges - G.number_of_edges()
    #add them to a list, identofy them through there predecessor being 0, adn then get the node number from a list of nodes  
    gnodes=G.nodes()
    level1=[]
    level0=[0]
    mlevel=[]
    gno = 0
    mlevel.append(level0)
    gno = 1
    z=1#z will be  the bottom of the range of nodes to add to the level list
    #level1 will be 0 - a - needs nodes 1-2  
    while z <= a:
        level1.append(gnodes[z])
        z=z+1
    
    mlevel.append(level1)
    gno = gno + len(level1)
    ai = a*(a+1)
    
    stop = G.number_of_nodes()
    while gno <> stop:            
        temp = []
        while z <= ai:
            temp.append(gnodes[z])
            z += 1
        mlevel.append(temp)
        ai = ai *a + a
        gno = gno + (len(temp))
    #print 'number of nodes in original tree: ', G.number_of_nodes()
    #number of edges to add per method
    prob = r.randint(1,8)/10.0
    #print prob
    toadd1 = round(numofedges * prob) #number of nodes to add in the first step
    #print 'total for 1st addition: ', toadd1
    toadd2 = numofedges-toadd1
    #print 'total for 2nd addition: ',toadd2
    #print 'total added: ', toadd1 + toadd2
    #print 'final total should be: ', G.number_of_nodes() + toadd1 + toadd2
    
    #--calc the numer of new edges per level----------------------------------#
    #need to split the number of nodes between the levels 
    numnewedges1 = []
    numnewedges2 = []
    f = 1    
    while f < len(mlevel): #goes mlevel for each list   
        nodesinlevel = mlevel[f] #get nodes in level
        numofnodesinlevel = len(nodesinlevel) #get number of nodes in level
        #calc the new edges to go in each level
        newedges1 =  r.randint(0, (numofnodesinlevel*(numofnodesinlevel-1)/2))
        if newedges1 > toadd1:
            newedges1 = toadd1
        numnewedges1.append(round(newedges1))
        if f+1 < len(mlevel):
            #print 'f +1 here is: ', f+1
            nodesinnextlevel = mlevel[f+1]
            numofnodesinnextlevel = len(nodesinnextlevel)
        
            newedges2 = r.randint(0, ((numofnodesinlevel-1)*(numofnodesinnextlevel))) #need to change this for the seconf set of new edges as does not work
            numofnodesinnextlevel = None
            if newedges2 > toadd2:
                 newedges2 = toadd2
            numnewedges2.append(round(newedges2))
        f+=1
    
    #print 'sum edge list1 ', sum(numnewedges1)
    #print 'sum edge list2 ', sum(numnewedges2)
    #print 'to add1 = ', toadd1
    #print 'to add2 = ', toadd2
    #---------adjust values to get the right amount of edges in total---------#
    if sum(numnewedges1) > toadd1:
        newdiff = sum(numnewedges1) - toadd1
        i = 1
        while i < newdiff:
            unit = r.randint(1, len(numnewedges1)-1)
            unitval = numnewedges1[unit]            
            while unitval < 1:            
                unit = r.randint(1, len(numnewedges1)-1)
                unitval = numnewedges1[unit] 
            numnewedges1[unit] = numnewedges1[unit] - 1
            i += 1     
    if sum(numnewedges2) > toadd2:
        newdiff = sum(numnewedges2) - toadd2
        i = 1
        while i < newdiff:
            unit = r.randint(1, len(numnewedges2)-1)
            unitval = numnewedges2[unit]
            while unitval < 1:            
                unit = r.randint(1, len(numnewedges2)-1)
                unitval = numnewedges2[unit] 
            numnewedges2[unit] = numnewedges2[unit] - 1
            i += 1     
            
    #may need to add some code in here to cope wth tith the limits of each level  
    if sum(numnewedges1) < toadd1:
        #print 'adding some extra edges'
        newdiff = sum(numnewedges1) - toadd1
        i = 1
        while i < newdiff:
            unit = r.randint(1, len(numnewedges1)-1)
            numnewedges1[unit] = numnewedges1[unit] + 1
            i += 1     
    if sum(numnewedges2) < toadd2:
        #print 'adding some extra edges for 2'
        newdiff = sum(numnewedges2) - toadd2
        i = 1
        while i < newdiff:
            unit = r.randint(1, len(numnewedges2)-1)
            numnewedges2[unit] = numnewedges2[unit] + 1
            i += 1        
            
    #print 'new edge list1 ', numnewedges1
    #print 'new edge list2 ', numnewedges2 
    
    
    #----add first set of edges-----------------------------------------------#
    f=1
    #print 'adding first set of edges'
    while f< len(mlevel): #goes mlevel for each list   
        #print 'f is: ', f
        nodesinlevel = mlevel[f] #get nodes in level
        numofnodesinlevel = len(nodesinlevel) #get number of nodes in level
        t = nodesinlevel[0] #get the value of the first node in the level
        s = 0
        #e=round(p*y)
        e = numnewedges1[f-1]                
        nmax = numofnodesinlevel+t
        midnumofedges = G.number_of_edges()
        #print 'ADDING ', e, ' edges to tree'
        total = midnumofedges + e
        #print 'TOTAL should be: ', midnumofedges + e
        while G.number_of_edges() <> total:
            w1 = r.randint(t,nmax-1)#find the upper most value in list
            w2 = r.randint(t,nmax-1)#find the upper most value in list
            while w1 == w2:
                w2 = r.randint(t,nmax-1)
            #may be check not replicating exsting edges
            #below checks for adding extra nodes on
            if w2 == len(G.nodes()) or w1 == len(G.nodes()): #this if statement should not be used now. if so problem with z value likly
                print 'ERROR!!!!'
            G.add_edge(w1,w2)
            s = s+1
        #print 's is: ',s
        #print 'TOTAL is actually: ', G.number_of_edges()
        f = f+1

    #print 'the number of edges after 1 is: ', G.number_of_edges()
    #print 'the above value should be: ', 585+toadd1   
    
    #---------add second set of new edges-------------------------------------#
    #print 'ADDING 2ND SET OF EDGES'
    f=1
    while f+2 <= len(mlevel):
        #print 'f is: ', f
        #print 'mlevel is: ', len(mlevel)
        h = mlevel[f] #get nodes in the level
        h1 = mlevel[f+1] #get nodes in the next level
        y = len(h)
        y1 = len(h1)
        #print 'nodes in level are: ', y
        #print 'nodes in lower level are: ', y1
        t = h[0] #get number of first node in the level
        t1 = h1[0] #get number of first node in the next level
        s = 0
        e = round(p*y) #get the number of new edges to add, based on the probability value and the number of nodes in the top level      
        e = numnewedges2[f-1]  
        midnumofedges = G.number_of_edges()
        #print 'ADDING ', e, ' edges to tree'
        total = midnumofedges + e
        #print 'TOTAL should be: ', total
        while G.number_of_edges() <> total:
            w1 = r.randint(t,y+t-1)#y+t to find the upper most value in list
            w2 = r.randint(t1,y1+t1-1)
            while w1 == w2:
                w2 = r.randint(t1,y1+t1-1)
            G.add_edge(w1,w2)
            s = s+1
        #print 'TOTAL is actually: ', G.number_of_edges()
        f = f+1
    #print 'finally, the number of edges are: ', G.number_of_edges()
    return G

#def hc(level, struc):      
def square(level):
    #produce a square hierarchical community graph
    def five_cluster(level):
        G=nx.Graph()
        if level==1:
            limit=1
            G,a,b,c,d,e=createnodes(G,limit)        
        elif level==2:
            limit=5
            G,a,b,c,d,e=createnodes(G,limit)
            G=level2(G,a,b,c,d,e)
        elif level==3:
            limit=25
            G,a,b,c,d,e=createnodes(G,limit)
            G=level3(G,a,b,c,d,e)#a=0,b=1,c=2,d=3
        elif level==4:
            limit=125
            G,a,b,c,d,e=createnodes(G,limit)
            G=level4(G,a,b,c,d,e)
        elif level==5:
            limit=625
            G,a,b,c,d,e=createnodes(G,limit)
            G=level5(G,a,b,c,d,e)
        else:
            print 'ERROR! Please enter a suitable level value.'
        return G    
    def createnodes(G,limit):
        i=G.number_of_nodes()
        p=0
        while p<limit: #creats the basic 4 node module and edges
            i=G.number_of_nodes()
            a=i
            b=i+1
            c=i+2
            d=i+3
            e=i+4
            nodeaddlist=(a,b,c,d,e)
            edgeaddlist=([a,b],[a,c],[a,d],[a,e],[b,c],[c,d],[d,e],[e,b],[b,d],[c,e])
            p=p+1
            G.add_nodes_from(nodeaddlist)
            G.add_edges_from(edgeaddlist) 
        return G,a,b,c,d,e        
    def level2(G,a,b,c,d,e):#connecting b,c,d,e to node 0  
        ac=a-a#centre node a must be the 12th node from the 16, thus d=16
        while b>1:
            newedges=([b,ac],[c,ac],[d,ac],[e,ac])
            b=b-5
            c=c-5
            d=d-5
            e=e-5
            G.add_edges_from(newedges)   
        return G    
    def level3(G,a,b,c,d,e):#a=0,b=1,c=2,d=3
        G=level2(G,a,b,c,d,e)#connects all external nodes to centre node   
        while a>24:#as to not do for the central cluster
            ac=a-20#100
            newedges=([e,ac],[d,ac],[c,ac],[b,ac],[e-5,ac],[d-5,ac],[c-5,ac],[b-5,ac],[e-10,ac],[d-10,ac],[c-10,ac],[b-10,ac],[e-15,ac],[d-15,ac],[c-15,ac],[b-15,ac])        
            G.add_edges_from(newedges)       
            a=a-25
            b=b-25
            c=c-25
            d=d-25
            e=e-25        
        return G
    #****what would you add to create a level four hierarchical level*******# 
    def level4(G,a,b,c,d,e):
        G=level3(G,a,b,c,d,e)        
        return G
        
    def level5(G,a,b,c,d,e):
        G=level3(G,a,b,c,d,e)    
        return G

    G = five_cluster(level)
    return G
        
def tri(level):
    
    def four_cluster(level):
        G=nx.Graph()
        if level==1:
            limit=1
            G,a,b,c,d=createnodes(G,limit)        
        elif level==2:
            limit=4
            G,a,b,c,d=createnodes(G,limit)
            G=level2(G,a,b,c,d)
        elif level==3:
            limit=16
            G,a,b,c,d=createnodes(G,limit)
            G=level3(G,a,b,c,d)#a=0,b=1,c=2,d=3
        elif level==4:
            limit=64
            G,a,b,c,d=createnodes(G,limit)
            G=level4(G,a,b,c,d)
        elif level==5:
            limit=256
            G,a,b,c,d=createnodes(G,limit)
            G=level5(G,a,b,c,d)
        else:
            print 'ERROR! Please enter a suitable level value.'
        return G
        
    def createnodes(G,limit):
        i=G.number_of_nodes()
        p=0
        while p<limit: #creats the basic 4 node module and edges
            i=G.number_of_nodes()
            a=i
            b=i+1
            c=i+2
            d=i+3
            nodeaddlist=(a,b,c,d)
            edgeaddlist=([a,b],[b,c],[c,a],[a,d],[b,d],[c,d])
            p=p+1
            G.add_nodes_from(nodeaddlist)
            G.add_edges_from(edgeaddlist) 
        return G,a,b,c,d    
        
    def level2(G,a,b,c,d):#a=12  
        newedges=([a,a-4],[a,a-8],[a-4,a-8])#edges to create the large triangle
        G.add_edges_from(newedges)
        ac=a-12#centre node a must be the 12th node from the 16, thus d=16
        newedges=([a+3,ac],[a+2,ac],[a+1,ac],[a-1,ac],[a-2,ac],[a-3,ac],[a-5,ac],[a-6,ac],[a-7,ac])    
        G.add_edges_from(newedges)    
        return G
        
    def level3(G,a,b,c,d):#a=0,b=1,c=2,d=3
        i=0    
        while i<4:#generating all the level two edges
            G=level2(G,a,b,c,d)   
            a=a-16
            b=b-16
            c=c-16
            d=d-16
            i=i+1
        a=a+4
        newedges=([a+16,a+32],[a+16,a+48],[a+32,a+48])#edges to connect greater clusters to form giant triangle
        G.add_edges_from(newedges) 
        ac=a  #centre most node (=0 in first iteration)
        an=a+16 
        y=k=0 
        while k<3: #for the first cluster of 16 where some new edges are needed
             i=0
             an=an+4  # a=16 in first, needs to equal 21 so add 4 here as 1 added any way in next loop
             while i<3:
                 y=0
                 an=an+1
                 while y<3:
                     G.add_edge(an,ac)
                     an=an+1                
                     y=y+1
                 i=i+1
             k=k+1 
        return G     
        
    def level4(G,a,b,c,d):
        i=0
        #d=G.number_of_nodes()-1#255
        c=d-1#254
        b=d-2#253
        a=d-3#252
        while i<4:         
            G=level3(G,a,b,c,d)  
            a=a-64
            b=b-64
            c=c-64
            d=d-64
            i=i+1         
        
        a=a+4
        newedges=([a+64,a+128],[a+64,a+192],[a+128,a+192])#edges to connect large clusters together
        G.add_edges_from(newedges)    
        ac=a #centre most node (=0 in first iteration)
        an=a+63 
        y=k=0 
        h=0
        while h<3:
            an=an+16
            k=0
            while k<3: #for the first cluster of 16 where some new edges are needed
                 i=0
                 an=an+4  # a=16 in first, needs to equal 21 so add 4 here as 1 added any way in next loop
                 while i<3:
                     y=0
                     an=an+1
                     while y<3:
                         G.add_edge(an,ac)
                         an=an+1                
                         y=y+1
                     i=i+1
                 k=k+1 
            h=h+1     
        return G
    
    
    def level5(G,a,b,c,d):
        ##*****to be done if required/have a bit of spare time******##
        i=0
        d=G.number_of_nodes()-1#255
        print 'LOOK HERE:', G.number_of_nodes()
        c=d-1#254
        b=d-2#253
        a=d-3#252
        while i<4:         
            G=level4(G,a,b,c,d)  
            a=a-256
            b=b-256
            c=c-256
            d=d-256
            i+=1 
                        
        #four level 4 subgraphs now
        jump = 256      
        #these connect the three external clusters via their central nodes
        G.add_edge(jump,jump*2)
        G.add_edge(jump,jump*3)
        G.add_edge(jump*2,jump*3)
        
        #this block add edges between the external nodes and the central node
        h = 1
        number_to_connect = 3
        centre_node = 0
        node_c = 256
        t = 0
        while t < 3: #this should be 3
            node_c += 64 #miss the central group
            h = 1
            while h < 4: #should be 4
                node_c += 16 #skip the next 16 at centre of outer group1
                u = 0
                while u < 3: #should be 3
                    print ''
                    node_c += 4 #skip as at centre of smaller group
                    j = 0
                    while j < 3:
                        k = 0 
                        node_c += 1 #skip as at centre of 4 
                        while k < number_to_connect:
                            G.add_edge(node_c,centre_node)
                            k += 1
                            if node_c == 1024:
                                pass
                            else:
                                node_c += 1
                        j += 1
                    u += 1
                h += 1      
            t += 1
        return G
        
    #this starts the building of the network
    G = four_cluster(level)
    return G
'''
G = tri(5)
print G.number_of_nodes()
print nx.is_connected(G)
for g in nx.connected_component_subgraphs(G):
    print g.number_of_nodes()
print nx.number_connected_components(G)
#print G.degree()
''' 
    