#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#   This file is part of TeamGenerator.
#
#   TeamGenerator is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   TeamGenerator is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with TeamGenerator.  If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright 2011 Jehan Bruggeman <jbruggeman@symzo.be>


import random

from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.readwrite.dot import write
import gv
import copy
import pprint
import itertools
import pickle
import sys

RESULTS_FILE = 'results.pickle'

# this method exports the results as formatted and readable data
def export():
    # get the graph object (people+prefs)
    graph = getGraph()
    outFile = open('results.csv','w')
    # load the "best teams" results
    tb = pickle.load(open(RESULTS_FILE,'r'))
    tb.reverse()
    
    # write to csv
    def teamline(tname,listnames,out):
        out.write(tname+', ')
        for name in listnames:
            out.write(name+', ')
        out.write('\n')
            
    for result in tb:
        outFile.write('\n')
        outFile.write('Result score,'+str(int(result[0]))+'\n')
        teamline(',,équipe 1',unanonymize(result[1]),outFile)
        teamline(',,équipe 2',unanonymize(restOfTheGroup(result[1],graph)),outFile)
        

# read the list of people and their relationships. anonymize the result
def getGraph():
    data = readNodes()
    graph  = anonymize(data)
    return graph

# main. This is called when the script is ran without args (see bottom)
def main():
    # load the graph data
    graph = getGraph()
    
    # run the exhaustive search algorithm on the dataset
    tb = compareContents(graph)
    
    # show the result
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(tb)
    print '-------- ANON -----------'
    for v in tb:
        print '##############################'
        print '----- TEAM 1'
        print v[1]
        print '----- TEAM 2'
        print restOfTheGroup(v[1],graph)
    print '-------------------'
    print '--------- NOT ANON ----------'
    for v in tb:
        diff = diffTeam(v[1],tb[0][1])
        print '##############################'
        print '----- TEAM 1'
        print unanonymize(v[1])
        print '----- TEAM 2'
        print unanonymize(restOfTheGroup(v[1],graph))
        print '----- diff with others'
        print "not in our team 1 :  ", unanonymize(diff[0])
        print "not in their team 1 :", unanonymize(diff[1])
    print '-------------------'
    print([a[0] for a in tb])
    
    # write to output file
    pickle.dump(tb,open(RESULTS_FILE,'w'))
    
def diffTeam(t1,t2):
    notInT2 = list(t1[:])
    notInT1 = list(t2[:])
    
    for elem in t1:
        if elem in notInT1:
            del notInT1[notInT1.index(elem)]
            del notInT2[notInT2.index(elem)]
            
    return (notInT1, notInT2)

# given a team, extract the other one (i.e. everybody not in the first team)
def restOfTheGroup(team1,graph):
    team2 =[]
    for k in graph:
        if not k in team1:
            team2.append(k)
    return team2
    
# calculate the quality of a solution
def measureContent(subGraph):
    total_content=0
    # everybody gets happier as more of their links survive
    contentFunction = { 0: 0, 1: 1000, 2:1100, 3:1110}
    for links in subGraph.values():
        total_content += contentFunction[len(links)]
    return total_content

def measureBonus(teamlist):
    bonus = 0
    # add bonus for nodes we specifically want together or apart
    # create a nucleus of 2 "experienced" persons in each team 
    NUCLEUS = (57,58,59,60) # IDs are changed to keep thing REALLY anonymous
    bonus += 30.1*( bool(NUCLEUS[1] in teamlist) == bool(NUCLEUS[0] in teamlist))
    bonus += 30.3*( bool(NUCLEUS[2] in teamlist) != bool(NUCLEUS[0] in teamlist))
    bonus += 30.5*( bool(NUCLEUS[3] in teamlist) != bool(NUCLEUS[0] in teamlist))   
      
    return bonus
    
    
# extract people and their remaining links from the graph according to 
# the list defined in "sink"     
def graphFromSink(sink,graph):
    cutGraph = {}

    for person,links in graph.items():
        cutGraph[person] = [ x for x in links if ((x in sink) == (person in sink))]
        
    return cutGraph

# main algo method. search for all the possible combinations
def compareContents(graph):
    tenbest = [
            (0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),
            (0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),
            (0,0),(0,0)
            ]
    worstofthebest = 0
    lenGraph = len(graph)
    progress = 0
    
    for team1list in itertools.combinations(range(lenGraph),lenGraph/2):
        grf = graphFromSink(team1list,graph)
        #~ print team1list,grf
        progress+=1
        if 0 == progress%200000:
            print progress
        val = measureContent(grf) + measureBonus(team1list)
        
        # keep the best in the array by sorting it and always replacing the weakest value
        if val > worstofthebest:
            tenbest[0] = (val, team1list)
            tenbest.sort(key = lambda y: y[0])
            worstofthebest = tenbest[0][0]
    return tenbest
    
# load the ID <-> name mapping
def getMap(id_as_key=False):
    mapval = {}
    mapFile = open('mapping-src.csv','r')
    
    for line in mapFile:
        name, id = line.strip().split(', ')
        if id_as_key:
            mapval[int(id)] = name
        else:
            mapval[name] = int(id)
    
    return mapval

# from IDs to names
def unanonymize(listids):
    mapval = getMap(id_as_key=True)
    ret = []
    for id in listids:
        ret.append(mapval[id])
    return ret
    
# from names to IDs
def anonymize(data):
    mapval = getMap()
    
    data2 = {}

    for name in data.keys():
        data2[mapval[name]] = []        
        for n in data[name]:
            data2[mapval[name]].append(mapval[n])
    
    return data2
   
# laod the preferences and list of people into the "graph"
def readNodes():
    f = open('preferences.csv','r')
    people = open('listepersonnes.csv','r').read()
    data = {}
    def strip(val):
        return val.strip(' ,"\n').lower()

    nodenames = people.split(',')
    nodenames = map(strip,nodenames)

    for name in nodenames:
        data[name]=[]
    
    for line in f:
        a = line.split(',',1)
        name = a[0].strip(' ,').lower()
        data[name] = a[1].strip(' ,"\n').split(',')
        data[name] = map(strip,data[name])
        for link in data[name]:
            if link not in data.keys():
                data[link]=[]
        
    return data
   


########################
### SCRIPT STARTS HERE
########################

if 'export' in sys.argv:
    export()
else:
    main()
