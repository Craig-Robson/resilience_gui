# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 10:34:32 2012

@author: Craig
"""

def geo(G,dim=2, scale=2):
    '''Will draw a network stored using the network schema geographically by 
    extracting the coordinates from the attributes of each node.'''
    print 'in geo'
    try:
        import networkx as nx
        import numpy as np
    except ImportError:
        raise ImportError("requires numpy")
    #this needs the database connection to be used as well
    'will return the positions for the nodes based on coordinates which are attibutes in the nodes'
    #need to get the attribue coordintes here and reduce them to atual coords which can be used
    pos=np.asarray(np.random.random((len(G),dim)),dtype=np.float32)#creates array from input gragh for coords
    #attstring = str(G.node[1]['Wkt'])
    
    try:
        print 'node at zero is: ', G.node[0]
    except:
        print 'no node at zero'
    
    #getting errors here as lokking for node zero which does not exist
    for node in G.nodes_iter():  
        attstring = G.node[node]['Wkt']
        attstring = attstring[7:] #removes the first seven characters
        attstring = attstring[:-1] #removes the final bracket
        a,b = attstring.split()
        temp =np.array([float(a),float(b)])  
        pos[node-1]=temp
    pos=_rescale_layout(pos,scale=scale)
    return dict(zip(G,pos)) #should try/add to all the others so they are the same as the other layouts.
    
def tree_circle(G,bfs,dim=2, scale=2):
    '''Plots a network as a number of circles increasing in size from the 
    source node of the tree in the middle of the plot.'''
    if bfs == True:
        G, sourcenode = assign_levels_bfs(G)
    elif bfs == False:
        G, sourcenode = assign_levels_dfs(G)
    else:
        print 'Internal error with tree circle function'
    try:
        import numpy as np
    except ImportError:
        raise ImportError("requires numpy ")
    if len(G)==0: #if network empty, should never get here though
        return {}
    if len(G)==1: #if network only has one node, again should very rarely get here
        return {G.nodes()[0]:(1,)*dim}
    pos=np.asarray(np.random.random((len(G),dim)),dtype=np.float32)#creates array from input gragh for coords
    #replaced original technique here in this iteration of the module from v5
    G, lvl_max = get_stats(G) #find max level
    levelnodes=[[]]
    i = 0
    while i <= lvl_max:#creates a lists of lists, a list for each level
        levelnodes.append([])
        i+=1
    
    for node in G.nodes():
        n_lvl = G.node[node]["level"]
        levelnodes[n_lvl].append(node)

    print 'levels: ', levelnodes
    #assign positions for all nodes
    circleadjustment = 0.0
    level = 0
    poslist=[[]]
    if level == 0: #assign centre position for central node
        poslist.append([]) #add list entry for this level
        poslist[level] = 0, 0 #add position
        level += 1 #iterate lebel
    if level<>0: #if level is greater than 0
        while len(levelnodes[level]) <> 0: #until all nodes have been clasified
            circleadjustment += 0.2 #adjust circle size
            poslist.append([])
            poslist[level]=np.asarray(np.random.random((len(levelnodes[level]),dim)),dtype=np.float32)#creates array from input gragh for coords        
            t=np.arange((1.0/(len(levelnodes[level])))*2,2.0*np.pi,2.0*np.pi/(len(levelnodes[level])),dtype=np.float32) #set a number of locations on a circle for the points to lie
            i = 0
            for node in levelnodes[level]:
                poslist[level][i] = t[i]
                i +=1
            poslist[level]=np.transpose(np.array([np.cos(t)*circleadjustment,np.sin(t)*circleadjustment])) #assign node       
            level += 1
    print 'this is pos list level ', poslist
    '''
    try:
        if G.node[0]<> None:
            r = 0
    except:
        if G.node[1]<>None:
            r=1
    '''
    s = 0
    '''
    while r <(len(G.nodes())): #for all nodes
        n_lvl = G.node[r]["level"] #get the node level
        if r <> levelnodes[n_lvl][s]: #if the node number matches that in the level at position s do whatevrer
            s +=1
        else: #go onto the next node
            pos[r]=poslist[n_lvl][s] #assign position   
            s = 0
            r += 1
    '''            
    i=0
    for node in G.nodes():
        loop = True
        while loop == True:
            print 'node is: ', node
            n_lvl = G.node[node]["level"] #get the node level
            print levelnodes[n_lvl][s]
            if node <> levelnodes[n_lvl][s]: #if the node number matches that in the level at position the required
                s +=1
            else: #go onto the next node
                pos[i]=poslist[n_lvl][s] #assign position   
                s = 0
                i +=1
                loop = False

    pos=_rescale_layout(pos,scale=scale)
    return dict(zip(G,pos)) #return positions and network

def tree(G,bfs,dim=2, scale=2):
    '''Draws a network as a tree with the source node at the top of the plot.'''
    if bfs == True:
        G, sourcenode = assign_levels_bfs(G)
    elif bfs == False:
        G, sourcenode = assign_levels_dfs(G)
    else:
        print 'Internal error with visualisation algorithm'
    try:
        import numpy as np
    except ImportError:
        raise ImportError("Could not import numpy which is required for this visualisation")
    if len(G)==0: #if network empty, should never get here though
        return {}
    if len(G)==1: #if network only has one node, again should very rarely get here
        return {G.nodes()[0]:(1,)*dim}
     
    pos=np.asarray(np.random.random((len(G),dim)),dtype=np.float32)#creates array from input gragh for coords
    #replaced original technique here in this iteration of the module from v5
    G, lvl_max = get_stats(G) #find max level
    levelnodes=[[]]
    i = 0
    while i <= lvl_max:#creates a lists of lists, a list for each level
        levelnodes.append([])
        i+=1

    for node in G.nodes():         
        n_lvl = G.node[node]["level"] #get node level 
        levelnodes[n_lvl].append(node)
        
        
    vertsplit = 1.0/(lvl_max+4)        
    hozsplit = [0]
    u = 1   
    while u <= lvl_max:
        dist =  1.0/(len(levelnodes[u]))
        hozsplit.append(dist)
        print 'this is a new level. the sep dist between nodes is: ', dist
        u += 1

    print 'levels: ', levelnodes
    #assign positions for all nodes
    level = 0
    poslist=[[]]
    #This small section is superseeded by a single line further below just before the positions are rescaled
    if level == 0: #assign centre position for central node
        poslist.append([]) #add list entry for this level
        poslist[level] =0.5,1 #1-vertsplit  #add position
        level += 1 #iterate level
    if level<>0: #if level is greater than 0
        while len(levelnodes[level]) <> 0: #until all nodes have been clasified
            poslist.append([])
            poslist[level]=np.asarray(np.random.random((len(levelnodes[level]),dim)),dtype=np.float32)#creates array from input gragh for coords        
            i = 0
            for node in levelnodes[level]:
                poslist[level][i] = (hozsplit[level]/2)+hozsplit[level]*(i), 1-vertsplit*level
                i +=1
            level += 1
    #print 'this is pos list level ', poslist
    '''    
    try:
        if G.node[0]<>None:
            r=0
    except:
        if G.node[1]<>None:
            r=1
    '''
    s = 0
    '''
    while r <(len(G.nodes())): #for all nodes
        n_lvl = G.node[r]["level"] #get the node level
        if r <> levelnodes[n_lvl][s]: #if the node number matches that in the level at position the required
            s +=1
        else: #go onto the next node
            pos[r]=poslist[n_lvl][s] #assign position   
            s = 0
            r += 1
    '''
    
    i=0
    for node in G.nodes():
        loop = True
        while loop == True:
            print 'node is: ', node
            n_lvl = G.node[node]["level"] #get the node level
            print levelnodes[n_lvl][s]
            if node <> levelnodes[n_lvl][s]: #if the node number matches that in the level at position the required
                s +=1
            else: #go onto the next node
                pos[i]=poslist[n_lvl][s] #assign position   
                s = 0
                i +=1
                loop = False
            #r += 1                             
          
    n_lvl = -1
    
    for node in G.nodes(): #for all nodes
        n_lvl = G.node[node]["level"] #get the node level
    i=0
    for node in G.nodes():
        if sourcenode == node:
            pos[i]=0.5,1
        i+=1
    #assign the origin node the correct position
    pos=_rescale_layout(pos,scale=scale)
    #print 'this is the pos list', pos    
    return dict(zip(G,pos))
    

def _rescale_layout(pos,scale=1):
    # rescale to (0,pscale) in all axes
    # shift origin to (0,0)
    lim=0 # max coordinate for all axes
    for i in range(pos.shape[1]):
        pos[:,i]-=pos[:,i].min()
        lim=max(pos[:,i].max(),lim)
    # rescale to (0,scale) in all directions, preserves aspect
    for i in range(pos.shape[1]):
        pos[:,i]*=scale/lim
    return pos

def get_stats(G):     
    #draw network as tree given with hierarchical
    try:
        import numpy as np
    except ImportError:
        raise ImportError("random_layout() requires numpy: http://scipy.org/ ")       
    #code to find the number of level and nodes per level
    k = 0  
    lvl_max = 0
    for node in G.nodes():
        if lvl_max <G.node[node]["level"]:
            lvl_max = G.node[node]["level"]
        else:
            lvl_max = lvl_max
    '''
    while k < len(G.nodes()): #find the max_level
        try:
            if lvl_max < G.node[k]["level"]:
                lvl_max = G.node[k]["level"]
        except:
            lvl_max = lvl_max
        k += 1    
    '''
        
  
    '''        
    k = 0      
    while k < len(G.nodes()): #assign a level to nodes which dont have one (max plus one)
        try:
            G.node[k]["level"]
        except:
            G.node[k]["level"] = lvl_max + 1 
        k += 1
    print 'number of levels = ', lvl_max
    '''
    
    #code to find tne number of nodes per level
    g = 0.0
    nodes_per_lvl = []
    while g <= lvl_max:
        nodes_per_lvl.append(0.0)
        g += 1    
    
    for node in G.nodes():
        lvl = G.node[node]["level"]
        n_p_l = nodes_per_lvl[lvl-1]
        nodes_per_lvl[lvl-1] = n_p_l + 1
    '''
    p = 0
    while p < len(G.nodes()):
        lvl = G.node[p]["level"]
        n_p_l = nodes_per_lvl[lvl-1]
        nodes_per_lvl[lvl-1] = n_p_l + 1
        p += 1
    print G.nodes()
    '''
    return G, lvl_max
    
    
def assign_levels_bfs(G):
    "Assign to the node a level in the hierarchy using the breadth-first-search method."
    #find the node with the highest degree
    #val_list = nx.degree(G)
    #betweenness centrality works much better than degree
    val_list = nx.betweenness_centrality(G)
    max_val, node = max_val_random(val_list)
    source=node
    
    #breadth first search
    visited=set([source])
    stack = [(source,iter(G[source]))]
    while stack:
        G.node[source]['level'] = 0
        parent,children = stack[0]
        try:
            child = next(children)
            if child not in visited:
                visited.add(child)
                G.node[child]['level'] = G.node[parent]["level"]+1
                stack.append((child,iter(G[child])))
        except StopIteration:
            stack.pop(0)
    return G, node

def assign_levels_dfs(G):
    '''Assign to the nodes a level in the hierachy based on the 
    depth-first-search algorithm.'''
    #find the node with the highest degree
    #val_list = nx.degree(G)
    #betweenness centrality works much better than degree
    val_list = nx.betweenness_centrality(G)    
    max_val, node = max_val_random(val_list)
    source=node
 
    nodes=[source]
    visited=set()
    levels=set()
    for start in nodes:
            G.node[source]['level']=0
            if start in visited:
                continue
            visited.add(start)
            stack = [(start,iter(G[start]))]
            while stack:
                parent,children = stack[-1]
                try:
                    child = next(children)
                    if child not in visited:
                        #yield parent,child
                        visited.add(child)
                        G.node[child]['level'] = G.node[parent]["level"]+1
                        stack.append((child,iter(G[child])))
                except StopIteration:
                    stack.pop()
    return G, node

def max_element(alist):
    ma=-99999
    i=0
    for i in alist:
        if alist[i]>ma:
            ma=alist[i]
        i+=1
    return ma

def max_val_random(alist):
    '''Find the maximum value in a list, and if tied between two or more 
    values, randomly select one of the ties values.'''
    ma = -99999
    node = -99999 
    tie_list = []
    #i=1
    for i in alist:
        print i,' has a value of: ', alist[i]
        if alist[i] == 0: #dont need to use no isolates here as those with zero should be removed anyway
            node = node
            print 'the node has a degree of zero: ', node
        elif alist[i] > ma: #if the value is higher than the max value already
            tie_list = []#reset to zero in length
            tie_list.append(i) #need to do this in case it is the joint highest
            ma = alist[i]
            print 'this value is higher than the max value. node is: ', i,', value is: ' ,ma
            node = i
        elif alist[i] == ma:
            tie_list.append(i)
            print 'adding node to tie_list'
        else:
            pass
            print 'no action taken for node ', i
        i = i+1
    '''
    while i<len(alist):
            print i,' has a value of: ', alist[i]
            if alist[i] == 0: #dont need to use no isolates here as those with zero should be removed anyway
                node = node
                print 'the node has a degree of zero: ', node
            elif alist[i] > ma: #if the value is higher than the max value already
                tie_list = []#reset to zero in length
                tie_list.append(i) #need to do this in case it is the joint highest
                ma = alist[i]
                print 'this value is higher than the max value. node is: ', i,', value is: ' ,ma
                node = i
            elif alist[i] == ma:
                tie_list.append(i)
                print 'adding node to tie_list'
            else:
                pass
                print 'no action taken for node ', i
            i = i+1
    '''
    node = r.choice(tie_list)
    #print 'node selected to remove is : ', node
    #print 'it has a degree of : ', ma
    return ma, node

import random as r
import pylab as pl    
import networkx as nx

'''
G = nx.gnm_random_graph(25,35)
#G = nx.balanced_tree(2,2)
#G = assign_levels_bfs(G)
#G = assign_levels_dfs(G)
bfs = True
pos= tree(G, bfs)
nx.draw(G,pos,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
pl.show()

#look at geospatial algorithms module for how to create an intersection algorithm
#use an interection algotithm  which utilises the coords of the nodes for the corrds of the edges
#randomly assign the node postions one at level 2 until the number of edge crossing in minimised.
#then repeat for the next level
#dont change for the level above as would damage all the work already done
#set a limit in the number of itertions it performs
#etc
#could be very slow esp on larger graphs.

#need to think about the edges within a level as well.

'''