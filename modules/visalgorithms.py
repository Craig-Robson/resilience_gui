# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 10:34:32 2012

@author: Craig
"""

def circular_layout(G, dim=2, scale=1):

    try:
        import numpy as np
    except ImportError:
        raise ImportError("circular_layout() requires numpy: http://scipy.org/ ")
    if len(G)==0:
        return {}
    if len(G)==1:
        return {G.nodes()[0]:(1,)*dim}
    t=np.arange(0,2.0*np.pi,2.0*np.pi/len(G),dtype=np.float32)
    pos=np.transpose(np.array([np.cos(t),np.sin(t)]))
    pos=_rescale_layout(pos,scale=scale)
    return dict(zip(G,pos))
    
    
def tree_circle(G,bfs,dim=2, scale=2):
    if bfs == True:
        G = assign_levels_bfs(G)
    elif bfs == False:
        G = assign_levels_dfs(G)
    else:
        print 'Internal error with tree circle function'
    try:
        import numpy as np
    except ImportError:
        raise ImportError("circular_layout() requires numpy: http://scipy.org/ ")
    if len(G)==0: #if network empty, should never get here though
        return {}
    if len(G)==1: #if network only has one node, again should very rarely get here
        return {G.nodes()[0]:(1,)*dim}
    
    pos=np.asarray(np.random.random((len(G),dim)),dtype=np.float32)#creates array from input gragh for coords
    
    level_0 = []
    level_1 = []
    level_2 = []
    level_3 = []
    level_4 = []
    level_other = []
    s = 0
    while s < len(G.nodes()):         
        #get node level
        n_lvl = G.node[s]["level"]   
        if n_lvl == 0:
            level_0.append(s)
        elif n_lvl == 1:  
            level_1.append(s)
        elif n_lvl == 2: 
            level_2.append(s)
        elif n_lvl == 3:
            level_3.append(s)
        elif n_lvl == 4:
            level_4.append(s)
        elif n_lvl > 4:
            level_other.append(s)
        else:
            print 'somethings gone wrong, the node level is,', n_lvl
        s+=1
    print 'level 0', level_0
    print 'level 1', level_1
    print 'level 2', level_2
    print 'level 3', level_3
    print 'level 4', level_4
    print 'level others', level_other
    print (1.0/(len(level_1)))*2
    circleadjustment = 0.0
    if len(level_1) <> 0:
        circleadjustment += 0.2
        pos1=np.asarray(np.random.random((len(level_1),dim)),dtype=np.float32)#creates array from input gragh for coords
        t=np.arange((1.0/(len(level_1)))*2,2.0*np.pi,2.0*np.pi/(len(level_1)),dtype=np.float32) #set a number of locations on a circle for the points to lie
        i = 0
        for node in level_1:
            pos1[i] = t[i]
            i +=1
        pos1=np.transpose(np.array([np.cos(t)*circleadjustment,np.sin(t)*circleadjustment])) #assign nodes to location on circle
        if len(level_2) <> 0:
            circleadjustment += 0.2
            pos2=np.asarray(np.random.random((len(level_2),dim)),dtype=np.float32)#creates array from input gragh for coords
            t2=np.arange((1.0/(len(level_2)))*0.2 ,2.0*np.pi,2.0*np.pi/len(level_2),dtype=np.float32) #set a number of locations on a circle for the points to lie
            i = 0
            for node in level_2:
                pos2[i] = t2[i]
                i +=1
            pos2=np.transpose(np.array([np.cos(t2)*circleadjustment,np.sin(t2)*circleadjustment])) #assign nodes to location on circle
            if len(level_3) <> 0:
                circleadjustment += 0.2
                pos3=np.asarray(np.random.random((len(level_3),dim)),dtype=np.float32)#creates array from input gragh for coords
                t3=np.arange(0,2.0*np.pi,2.0*np.pi/len(level_3),dtype=np.float32) #set a number of locations on a circle for the points to lie
                i = 0
                for node in level_3:
                    pos3[i] = t3[i]
                    i +=1
                pos3=np.transpose(np.array([np.cos(t3)*circleadjustment,np.sin(t3)*circleadjustment])) #assign nodes to location on circle
                if len(level_4) <> 0:
                    circleadjustment += 0.2
                    pos4=np.asarray(np.random.random((len(level_4),dim)),dtype=np.float32)#creates array from input gragh for coords
                    t4=np.arange(0,2.0*np.pi,2.0*np.pi/len(level_4),dtype=np.float32) #set a number of locations on a circle for the points to lie
                    i = 0
                    for node in level_4:
                        pos4[i] = t4[i]
                        i +=1
                    pos4=np.transpose(np.array([np.cos(t4)*circleadjustment,np.sin(t4)*circleadjustment])) #assign nodes to location on circle
                    if len(level_other) <> 0:
                        circleadjustment += 0.2
                        pos_other=np.asarray(np.random.random((len(level_other),dim)),dtype=np.float32)#creates array from input gragh for coords
                        tother=np.arange(0,2.0*np.pi,2.0*np.pi/len(level_other),dtype=np.float32) #set a number of locations on a circle for the points to lie
                        i = 0
                        for node in level_other:
                            pos_other[i] = tother[i]
                            i +=1
                        pos_other=np.transpose(np.array([np.cos(tother)*circleadjustment,np.sin(tother)*circleadjustment])) #assign nodes to location on circle
    #could use a lists of lists
    #[[pos0],[pos1],[pos2],[pos3]]
    o=0
    p=0
    l=0
    k=0
    s=0
    j=0
    while s < len(G.nodes()):         
        #get node level
        n_lvl = G.node[s]["level"]    
        if n_lvl == 0:
            pos[s] = 0,0
        elif n_lvl == 1:
            pos[s] = pos1[o]
            o += 1
        elif n_lvl == 2:
            pos[s] = pos2[p]
            p += 1
        elif n_lvl == 3:
            pos[s] = pos3[l]
            l += 1
        elif n_lvl == 4:
            pos[s] = pos4[k]
            k += 1
        elif n_lvl > 4:
            pos[s] = pos_other[j]
            j += 1
        else:
            print 'somethings gone wrong. The node level is: ', n_lvl
        s+=1  
    pos=_rescale_layout(pos,scale=scale)
    """
    r = 0
    while r <len(G.nodes()):
        n_lvl = G.nodes[s]["level"]
        pos[s] = levels[n_lvl][]
    """
    return pos #return positions and network

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
    while k < len(G.nodes()): #find the max_level
        try:
            if lvl_max < G.node[k]["level"]:
                lvl_max = G.node[k]["level"]
        except:
            lvl_max = lvl_max
        k += 1    
    k = 0  
    while k < len(G.nodes()): #assign a level to nodes which dont have one (max plus one)
        try:
            G.node[k]["level"]
        except:
            G.node[k]["level"] = lvl_max + 1 
        k += 1
    print 'number of levels = ', lvl_max
    
    #code to find tne number of nodes per level
    g = 0.0
    nodes_per_lvl = []
    while g <= lvl_max:
        nodes_per_lvl.append(0.0)
        g += 1    
    p = 0
    while p < len(G.nodes()):
        lvl = G.node[p]["level"]
        n_p_l = nodes_per_lvl[lvl-1]
        nodes_per_lvl[lvl-1] = n_p_l + 1
        p += 1
    print G.nodes()
    return G
    
    
def assign_levels_bfs(G):
    source_node=0 #source node, could be any as idetified in what ever way
    """
    bc_list = nx.degree(G) #the list of nodes and value
    bc_max = max_element(bc_list) #the max value
    node_max = 0
    while node_max <> bc_max: #keep looping until find node whith the max value
       node_max = bc_list[source_node] 
       source_node += 1
    source_node += -1 
    """    
    source=source_node
    
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
    return G

def assign_levels_dfs(G):
    source_node=0 #source node, could be any as idetified in what ever way
    """    
    bc_list = nx.degree(G) #the list of nodes and value
    bc_max = max_element(bc_list) #the max value
    node_max = 0
    while node_max <> bc_max: #keep looping until find node whith the max value
       node_max = bc_list[source_node]
       source_node += 1
    source_node += -1
    """    
    source=source_node    
    # produce edges for components with sourc
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
    return G

def max_element(alist):
    ma=-99999
    i=0
    while i <len(alist):
        if alist[i]>ma:
            ma=alist[i]
        i+=1
    return ma

import pylab as pl    
import networkx as nx

    
"""
#G = nx.gnm_random_graph(50,123)
G = nx.balanced_tree(4,4)
#G = assign_levels_bfs(G)
#G = assign_levels_dfs(G)
bfs = True
pos= tree_circle(G, bfs)
nx.draw(G,pos,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
pl.show()
"""