# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 20:46:53 2013

@author: Craig

This stores all the metric calculation scripts
"""

import networkx as nx

def count(G):

    degree_sequence=sorted(nx.degree(G).values(),reverse=True) # degree sequence
    dmax=max(degree_sequence)
    graph_count_1 = []
    num_of_nod = G.number_of_nodes()

    while dmax >= 0:
        tot = degree_sequence.count(dmax) 
        graph_count_1.append(tot)
        tot = tot*num_of_nod
        #list ordered by degree, with one being first
        dmax-=1
    graph_count_1.reverse()        
    return graph_count_1


def Betweenness_Calc(G):
    nodeBetweenness = nx.betweenness_centrality(G)
    nodeBetweenness = dict(nodeBetweenness)
    maxBetweenness = max(nodeBetweenness.values())
    minBetweenness = min(nodeBetweenness.values())
    averageBetweenness = (sum(nodeBetweenness.values())/len(nodeBetweenness))
    return maxBetweenness, minBetweenness, averageBetweenness, nodeBetweenness

def Assortativity_Calc(G):
    Assortativity = nx.degree_assortativity_coefficient(G)
    return Assortativity

def Clustering_Calc(G):
    nodeClustering = nx.clustering(G)
    nodeClustering = dict(nodeClustering)
    maxClustering = max(nodeClustering.values())
    minClustering = min(nodeClustering.values())
    averageClustering = (sum(nodeClustering.values())/len(nodeClustering))
    return maxClustering, minClustering, averageClustering, nodeClustering
    
def ClusteringSQ_Calc(G):
    nodeClustering = nx.square_clustering(G)
    nodeClustering = dict(nodeClustering)
    maxClustering = max(nodeClustering.values())
    minClustering = min(nodeClustering.values())
    averageClustering = (sum(nodeClustering.values())/len(nodeClustering))
    return maxClustering, minClustering, averageClustering, nodeClustering

def CycleBasis_Calc(G):
    basis = nx.cycle_basis(G)
    count = len(basis)
    return count, basis


def AveragePathLength_Calc(G):
    subgraphs = []
    whole_graph = 0.0
    for g in nx.connected_component_subgraphs(G):
        #print g.edges()
        tempresult = nx.average_shortest_path_length(g)
        subgraphs.append(tempresult)
        whole_graph += tempresult
    whole_graph = whole_graph/nx.number_connected_components(G)
    return whole_graph, subgraphs

def GeoAveragePathLength_Calc(G, text):
    subgraphs = []
    whole_graph = 0.0
    for g in nx.connected_component_subgraphs(G):
        #print g.edges()
        tempresult = nx.average_shortest_path_length(g, text)
        subgraphs.append(tempresult)
        whole_graph += tempresult
    whole_graph = whole_graph/nx.number_connected_components(G)
    return whole_graph, subgraphs  
  
def Degree(G):
    averageDegree = 0.0
    maxDegree = 0
    minDegree = 999999999
    nodeDegrees = G.degree().values()
    for item in nodeDegrees:
        averageDegree += item
        if item > maxDegree:
            maxDegree = item
        if item < minDegree:
            minDegree = item
    averageDegree = averageDegree/len(nodeDegrees)
    return maxDegree, minDegree, averageDegree, nodeDegrees
    
def DegreeDistribution(G):
    dlist = count(G)    
    return dlist
    
def MassCalc(G):
    return

def PlotGraph(G):
    return    
    
    
    


