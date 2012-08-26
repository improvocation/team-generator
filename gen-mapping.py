#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#   This file is part of TeamGenerator.
#   This file uses two sources (preferences.csv and listepersonnes.csv)
#   to generate an exhaustive list of people we need to distribute among
#   teams. It generates a CSV with one line per person in the format:
#       UserName, UserId
#
#   * format of preferences.csv: one line per person. First entry is the
#   person's name, second is the list of people he wants to be with      
#   the list is a CSV list surrounded by double quotes. Ex:
#       Superman, "Batman, Ironman, Wonderwoman"
#   * format of listepersonnes.csv: a one-line file with a comma-separated 
#   list of persons.
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
#

# to generate the list of nodes (people), we have two sources:
# - a list of people
# - the people mentionned in the preference file

f = open('preferences.csv','r')
people = open('listepersonnes.csv','r').read()
data = []
k=0

# extract from listpersonnes
def strip(val):
    return val.strip(' ,"\n').lower()

nodenames = people.split(',')
nodenames = map(strip,nodenames)

# extract from preferences 
for line in f:
    data.append({})
    a = line.split(',',1)
    data[k]['name'] = a[0].strip(' ,').lower()
    data[k]['prefs'] = a[1].strip(' ,"\n').split(',')
    data[k]['prefs'] = map(strip,data[k]['prefs'])
    k+=1

# merge names from two sources
for a in data:
    if a['name'] not in nodenames:
        nodenames.append(a['name'])
    for b in a['prefs']:
        if b not in nodenames:
            nodenames.append(b)

# write result
outputFile = open('mapping-src.csv','w')
k=0

for n in nodenames:
    outputFile.write(n+", "+str(k)+"\n")
    k+=1

