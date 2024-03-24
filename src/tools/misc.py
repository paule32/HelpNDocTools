# ------------------------------------------------------------------------------
# File  : misc.py - Tools for compile the observer.py application.
# Author: Jens Kallup - paule32
# Rights: all rights reserved.
#
# only for education, and non-profit usage !
# commercial use not allowed.
# ------------------------------------------------------------------------------
import string
import re

# ------------------------------------------------------------------------------
# convert string to list ...
# ------------------------------------------------------------------------------
def StrToList(string):
    liste = []
    lines = string.split("\r\n")
    
    for line in lines:
        line = re.sub(r"^(\[)|(\],$)|(\]$)", '', line)
        line = line.split(",")
        col1 = re.sub(r'^\"|\"$', '', line[0])
        col2 = re.sub(r'^PROJECT_.*\".*\"$|^\"', '', line[1])
        #col2 = re.sub(r'^ \".*\"$|^\"', '', col2)
        col2 = col2.replace("@",",")
        list_item = [ col1, col2 ]
        liste.append(list_item)
    return liste
