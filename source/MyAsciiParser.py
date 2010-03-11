#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 24/11/09

import wx

class LinkedListElement:
  def __init__(self,id,level,labelType,label,contentType,content):
    self.id = id
    self.level = level
    self.labelType = labelType
    self.label = str(label)
    self.contentType = contentType
    self.content = content
    self.table = None # MyTableColumn(self.label,self.content)

  def printIt(self):
    print self.id,self.level,self.labelType,self.label,self.contentType,self.content

def asciiToElementListVersion4(readablefile):
  #readablefile=readablefile.replace(' 4\n',' 4 \n').replace('\n','').split('->')
  readablefile=readablefile.split('->')

  elementList=[]
  id = 0
  for r in readablefile:
    if r != '':
      pos_key=r.split('<-')
      if len(pos_key) != 2:
        print 'Problem with readable file'
        print r
      # process the left part of <-
      pos_key[0] = pos_key[0].split()
      level = int(pos_key[0][0])
      labelType = int(pos_key[0][1])
      contentType = int(pos_key[0][2])
      contentSize = int(pos_key[0][3])
      # process the right part <-
      if labelType != 0:
        pos_key[1] = pos_key[1].lstrip()
      label = pos_key[1][0:12].strip()
      pos_key[1] = pos_key[1][13:]
      pos_key[1] = pos_key[1].lstrip(' ')
      pos_key[1] = pos_key[1].replace('\n','')
      if contentSize!=0:
        if contentType==3:
          pos_key[1]=pos_key[1][10*contentSize:]
          pos_key[1]=pos_key[1].replace('\n','')
          step = fancyStep(pos_key[1])
          content = []
          if step == 0:
            content = pos_key[1].split()
          else:
            while pos_key[1] != '':
              content.append(pos_key[1][0:step].strip())
              pos_key[1] = pos_key[1][step:]
        else:
          content=None
          if contentSize>0:
            content=pos_key[1].split()
        # create a LinkedListElement
        element = LinkedListElement(id,level,labelType,label,contentType,content)
        elementList.append(element)
        id=id+1
  return elementList

def asciiToElementListVersion3(readablefile):
  readablefile=readablefile.replace('\n','')
  def readNodeHeader(string):
    header = string[0:38]
    string = string[38:]
    level = int(header[0:8])
    label = header[9:21]
    contentType = int(header[22:30])
    contentSize = int(header[30:38])
    return string, level, label, contentType, contentSize

  def readNodeContent(string,contentType,contentSize):
    if contentType==0:
      length = 0
      content = []
    elif contentType==1:
      length = contentSize*10
      content = string[0:length].split()
    elif contentType==2:
      length = contentSize*16
      content = string[0:length].split()
    elif contentType==3:
      length = contentSize
      raw_content = string[0:length]
      content = []
      step = fancyStep(raw_content)
      if step == 0:
        content = raw_content.split()
      else:
        while raw_content != '':
          content.append(raw_content[0:step].strip())
          raw_content = raw_content[step:]
    else:
      pass
    string = string[length:]
    return string, content

  elementList=[]
  id = 0
  while readablefile!='':
    readablefile, level, label, contentType, contentSize = readNodeHeader(readablefile)
    readablefile, content = readNodeContent(readablefile,contentType, contentSize)
    element = LinkedListElement(id,level,'12',label,contentType,content)
    elementList.append(element)
    id=id+1
  return elementList

def asciiToElementList(file):
  # we make the file a 1 line string and we split it according to <- and ->
  inputfile=open(file)
  readablefile=inputfile.read()
  if readablefile[0]=='-':
    # if the file begins with "->" it's a Version4 file 
    return asciiToElementListVersion4(readablefile)
  else:
    return asciiToElementListVersion3(readablefile)

def asciiToTree(file,tree):
  # this function was designed to be a faster alternative to asciiToElementList and then ConstructAsciiTree
  # but it's not that fast
  # we make the file a 1 line string and we split it according to <- and ->
  inputfile=open(file)
  #readablefile=inputfile.read().replace(' 4\n',' 4 \n').replace('\n','').split('->')
  readablefile=inputfile.read().split('->')

  #elementList=[]
  previousLevel = 0
  root = tree.GetRootItem()
  previousNode = root
  parent = root
  parentLevel = 0
  id = 0
  for r in readablefile:
    if r != '':
      pos_key=r.split('<-')
      if len(pos_key) != 2:
        print 'Problem with readable file'
        print r
      # process the left part of <-
      pos_key[0] = pos_key[0].split()
      level = int(pos_key[0][0])
      if level < 0:
        # we are climbing down the tree
        tree.SortChildren(parent)
        if parentLevel > 1 and tree.GetChildrenCount(parent) > 10:
          pass
        else:
          tree.Expand(parent)
        parent = tree.GetItemParent(parent)
        parentLevel -= 1
        previousLevel = level
      else:
        labelType = int(pos_key[0][1])
        contentType = int(pos_key[0][2])
        contentSize = int(pos_key[0][3])
        # process the right part <-
        if labelType != 0:
          pos_key[1] = pos_key[1].lstrip()
        label = pos_key[1][0:12].strip()
        pos_key[1] = pos_key[1][13:]
        pos_key[1] = pos_key[1].lstrip(' ')
        pos_key[1] = pos_key[1].replace('\n','')
        if contentSize!=0:
          if contentType==3:
            pos_key[1]=pos_key[1][10*contentSize:]
            pos_key[1]=pos_key[1].replace('\n','')
            step = fancyStep(pos_key[1])
            content = []
            if step == 0:
              content = pos_key[1].split()
            else:
              while pos_key[1] != '':
                content.append(pos_key[1][0:step].strip())
                pos_key[1] = pos_key[1][step:]
          else:
            content=None
            if contentSize>0:
              content=pos_key[1].split()
          if previousLevel < 0: # we know that level >= 0.
            parent = tree.GetItemParent(previousNode)
            while tree.GetPyData(parent).level >= level:
              parent = tree.GetItemParent(parent)
              if parent == root:
                break
          elif level > previousLevel:
            # we are climbing up the tree
            parent = previousNode
            parentLevel = previousLevel
          # create a LinkedListElement
          element = LinkedListElement(id,level,labelType,label,contentType,content)
          node = tree.AppendItem(parent, element.label, data=wx.TreeItemData(element))
          #elementList.append(element)
          id+=1
          previousLevel = level
          previousNode = node
  tree.SortChildren(root)
  tree.Expand(root)
  #return elementList

def fancyStep(string):
  """Try to find a proper step to cut the string"""
  n = len(string)
  stepList = [12,8,4]
  myStep = 0
  for s in stepList:
    # try cutting 's' chars by 's' chars
    properStep = (n%s == 0)
    if properStep:
      startingCharList = string[0::s]
      for car in startingCharList:
        if car == ' ':
          properStep = False
          break
    if properStep:
      copy = string[:]
      while copy != '':
        if copy[0:s].strip() == '':
          properStep = False
          break
        copy = copy[s:]
    if properStep:
      myStep = s
      break
  return myStep

def comupl(nvp,nptot,ical,ncals,debarb,arbval):
  """function described in IGE295 as SUBROUTINE COMUPL"""
  """Returns an int list"""
  muplet=[]
  i = nvp - (ncals-1)
  io = -1
  while (i<nvp+1):
    if (int(debarb[i])==int(ical)):
      io=i
      break
    i=i+1
  muplet.insert(0,int(arbval[io-1]))
  ipar = nptot-1
  while (ipar>0):
    for i in range(nvp):
      if int(debarb[i])==0:
        print "problem",i
      if int(debarb[i]) > io:
        io=i
        break
    muplet.insert(0,int(arbval[io-1]))
    ipar=ipar-1
  return muplet

if __name__ == "__main__":
  import sys
  try:
    file = sys.argv[1]
  except:
    file="/home/toueg/etudes/GR514/GR514_branch0.saMCPO"
  elementList=asciiToElementList2(file)
  for e in elementList:
    if e.level < 2:
      e.printIt()