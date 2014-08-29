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
    '''a = number of levels, b = nodes per level, p = probability'''
    G=nx.balanced_tree(a,b) #generate graph
    e1=nx.number_of_edges(G)
    e1 = e1*p
    round(e1)
    e1=int(e1)
    yrand=r.randint(0,(e1))   #generate number of random edges to add                       
    y = 0
    j = 0
    
    while y<yrand:                    
        w1=r.randint(0,e1)#generate two random node values
        w2=r.randint(0,e1)
        while w1==w2:#need to check not the same value
            w2=r.randint(0,e1)
        G.add_edge(w1,w2)
        y+=1
    return G
    
def ahr(a,b,p):
    print 'this is to be sorted'
    #generate graph
    G=nx.balanced_tree(a,b)
    #add them to a list, identofy them through there predecessor being 0, adn then get the node number from a list of nodes
    gnodes=G.nodes()
    #print gnodes
    level1=[]
    level2=[]
    level3=[]
    level0=[0]
    mlevel=[]
    mlevel.append(level0)
    z=0#z will be  the bottom of the range of nodes to add to the level list
    #level1 will be 0 - a - needs nodes 1-2  
    while z <= a:
        level1.append(gnodes[z])
        z=z+1
    mlevel.append(level1)#0
    #level 2 
    a2=a*a+a
    if a2<=len(gnodes):    
        while z <= a2:	
            level2.append(gnodes[z])
            z=z+1
        mlevel.append(level2)#1
    #level3
    a3=a2*a+a
    if a3<=len(gnodes):
        while z <= a3:
            level3.append(gnodes[z])
            z=z+1
        mlevel.append(level3)#2
    #level4   
    level4=[]    
    a4=a3*a+a
    if a4<=len(gnodes):
        while z <= a4:
            level4.append(gnodes[z])
            z=z+1   
        mlevel.append(level4)#3
    #level4   
    level5=[]    
    a5=a4*a+a
    if a5<=len(gnodes):
        while z <= a5:
            level5.append(gnodes[z])
            z=z+1    
            mlevel.append(level5)#4    
    f=0
    while f< len(mlevel): # goes mlevel for each list
        h=mlevel[f]
        y=len(h)
        t=h[0]
        s=0
        e=round(p*y)
        while s<=e:
            w1=w2=r.randint(t,y+t)#y+t to find the upper most value in list
            while w1==w2:
                w2=r.randint(t,y+t)
            G.add_edge(w1,w2)
            s=s+1
        f=f+1
    #randomly connect nodes in the level below
    #use the mlevel list as above
    #use the probability value from above
    f=0
    while f+1<len(mlevel):
        h=mlevel[f]
        h1=mlevel[f+1]
        y=len(h)
        y1=len(h1)
        t=h[0]
        t1=h1[0]
        s=0
        e=round(p*y)
        while s<=e:
            w1=r.randint(t,y+t)#y+t to find the upper most value in list
            w2=r.randint(t1,y1+t1)
            G.add_edge(w1,w2)
            s=s+1
        f=f+1
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
        d=G.number_of_nodes()-1#255
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
        #print 'l4: ' + str(a) 
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
        return G
        
    G = four_cluster(level)
    return G
  

    
    