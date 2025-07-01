#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 13:02:58 2019

@author: lab
"""

from operator import itemgetter, attrgetter

import itertools

class ModuleLayout(object):
    def __init__(self,index,position,start,finish,width,height):
        self.index = index
        self.position = position
        self.startTime = start
        self.finishTime = finish
        self.width = width
        self.height = height
     
    def overlaps(self,other):
        return overlap(self.startTime,self.finishTime,other.startTime,other.finishTime)

    def __repr__(self):
        return repr((self.index,self.startTime,self.finishTime,self.width,self.height))

def overlap(start1,end1,start2,end2):
        if start1 > end1 or start2 > end2:
            print("Start came after end\n")
        if start1 > start2:
            tmps = start1
            tmpe = end1
            start1 = start2
            end1 = end2
            start2 = tmps
            end2 = tmpe
            
        if end1 < start2:
            return False
        elif end1 >= start2:
            return True
        
def getOverlap(layout,remaining):
    
    layouts = [layout]
    rest = []
    
    for ii in range(len(remaining)):
        if layout.overlaps(remaining[ii]):
            layouts.append(remaining[ii])
        else:
            rest.append(remaining[ii])
    
    return layouts, rest

def getOverlaps(layoutGroup,remaining):
    
    layouts = []
    
    if not remaining:
        return layoutGroup, remaining
    else:
        while remaining:
            if layoutGroup:
                layout = layoutGroup.pop(0)
                ls, remaining = getOverlap(layout,remaining)
                layouts = layouts + ls
            else:
                break
    return layouts, remaining

def groupModules(moduleLayouts):
    
    layoutGroups = {}
    num_groups = 0
    
    while len(moduleLayouts) > 0:
        comparator = moduleLayouts.pop(0)
        (lg,rm) = getOverlaps([comparator],moduleLayouts)
        layoutGroups[num_groups] = lg
        moduleLayouts = rm
        num_groups += 1
    
    return layoutGroups

def expandIntervals(widths):
    
    expanded = []
    
    for ii in range(len(widths)):
        for jj in range(len(widths[ii][0])):
            expanded.append((widths[ii][0][jj],widths[ii][1],widths[ii][2]))
            
    expanded.sort(key=itemgetter(0,1,2))

    return expanded

def joinIntervalsGroup(layoutGroup):

    completed = []
    
    intervals = []
    
    for ii in range(len(layoutGroup)):
        intervals.append(([layoutGroup[ii].position],layoutGroup[ii].startTime,layoutGroup[ii].finishTime,layoutGroup[ii].width))
        
    while intervals:
        
        intervals.sort(key = itemgetter(1,2))  

        cmplt, intervals = joinIntervals(intervals)

        completed.append(cmplt)
    
    start_x = 0
    
    widths = []
    
    for ii in range(len(completed)):
        left = start_x + completed[ii][3]
        widths.append((completed[ii][0],start_x,left))
        start_x = left
        
    return expandIntervals(widths)

def joinIntervals(intervals):
    
    first = intervals.pop(0)
    pending = []
    
    while intervals:
        nxt = intervals.pop(0)
        
        fst, rest = doJoin(first,nxt)

        pending = pending + rest
        
        first = fst
        
    return first, pending   

def doJoin(left,right):

    pos = removeDuplicates(left[0]+right[0])
    
    if left[2] < right[1]:
        print("Arguments should be overlapped.\n")
        return (),[]
    if left[1] < right[1]:
        if left[2] == right[1]:
            return (left[0],left[1],left[2],left[3]),[(pos,right[1],right[2],right[3])] # -left[1] pos
        if left[2] < right[2]:
            w1 = left[3]*((right[1]-left[1])/(left[2]-left[1]))
            w2 = left[3]-w1
            w3 = right[3]-w2
            return (left[0],left[1],right[1],w1),[(pos,right[1],left[2],w2),(right[0],left[2],right[2],w3)] # -left[1] pos
        elif left[2] == right[2]:
            w1 = left[3]*((right[1]-left[1])/(left[2]-left[1]))
            w2 = left[3]-w1
            return (left[0],left[1],right[1],w1),[(pos,right[1],left[2],w2)] # -left[1] pos
        else: # left[2] > right[2]
            w1 = left[3]*((right[1]-left[1])/(left[2]-right[1]))
            w2 = right[3]
            w3 = left[3]-(w1+w2)
            return (left[0],left[1],right[1],w1),[(pos,right[1],right[2],w2),(left[0],right[2],left[2],w3)] # -left[1] pos
    elif left[1] == right[1]:
        if left[2] < right[2]:
            w1 = right[3]*((left[2]-left[1])/(right[2]-right[1]))
            w2 = right[3]-w1
            return (pos,left[1],right[1],w1),[(right[0],left[2],right[2],w2)]
        elif left[2] == right[2]:
            return (right[0],left[1],left[2],left[3]),[(pos,right[1],right[2],right[3])] # -left[1] pos
        else:
            w1 = left[3]*((right[2]-right[1])/(left[2]-left[1]))
            w2 = left[3]-w1
            return (pos,left[1],right[1],w1),[(left[0],right[2],left[2],w2)]       # -left[1] pos      
    else:
        print("Arguments the wrong way round.  Should be sorted.\n")
        
def removeDuplicates(pending):
    
    if not pending:
        return pending
    
    first = pending.pop(0)
    
    filtered = filter(lambda x: x != first,itertools.chain(pending))
    
    rest = removeDuplicates(list(filtered))
    
    return [first] + rest