#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 17/04/11

from sys import platform
from array import array

file_path = "../../example/XsmMultiCompoV4"

CHAR_LENGTH_WORD = 8
BYTE_LENGTH_INTEGER = 2
BYTE_STEP_INTEGER = 4
BYTE_STEP = 8

class FileXsm:
  def __init__(self,name):
    self.open(name)
    header = self.read_header_and_rewind()
    if header == '$XSM    ':
      self.xsm_architecture = 64
    else:
      self.xsm_architecture = 32

  def read_header_and_rewind(self):
    header = self.file.read(8)
    self.file.seek(0)
    return header

  def open(self,name,mode='rb'):
    self.file = open(name,'rb')

  def close(self):
    self.file.close()

  def seek(self,cursor):
    self.file.seek(cursor*BYTE_STEP)

  def read(self,type,size):
    step = 1
    if self.xsm_architecture==64:
      if type=='c':
        type='c'
        size *= 2
      elif type=='i':
        type='l'
        if platform == 'win32':
          size *= 2
          step = 2
      elif type=='f':
	type='d'
    data = array(type)
    data.fromfile(self.file,size)
    if step > 1:
      data = data[::step]
    return data.tolist()

  def read_4c(self):
    """
    Read BYTE_STEP characters and truncate the first 4
    """
    return "".join(self.read('c',4)[:4])

  def read_8c(self):
    return self.read_4c()+self.read_4c()

  def read_12c(self):
    return self.read_8c()+self.read_4c()

  def read_ints(self,n):
    return self.read('i',n)

  def read_int(self):
    return self.read('i',1).pop()
  
  def read_reals(self,n):
    return self.read('f',n)

class Node:
  def __init__(self,offset,length,type,name="no name"):
    self.offset = offset
    self.type = type
    self.length = length
    self.name = name
    self.loaded_in_memory = False
  
  def __str__(self):
    s  = "Node '%s'"%(self.name)
    s += "\nOffset : %d"%(self.offset*BYTE_STEP)
    s += "\nType : %d"%(self.type)
    s += "\nLength : %d"%(self.length)
    if self.loaded_in_memory:
      if self.type == -1:
	s += "\nDistance from file start : %d"%(self.offset*BYTE_STEP)
	s += "\nDistance to parent node : %d"%(self.parent_offset*BYTE_STEP)
	s += "\nDistance to next sibling : %d"%(self.next_sibling_offset*BYTE_STEP)
      elif self.type in [1,2,3]:
	s += "\nData :"
	s += ",".join([ str(item) for item in self.data])
    else:
      s += "\nNot yet loaded in memory."
    return s

  def load(self,file_xsm):
    file_xsm.seek(self.offset)
    if self.type == -1 or self.type == 0:
      if file_xsm.read_4c() != "$$$$":
	raise
      max_number_of_children = file_xsm.read_int()
      number_of_children = file_xsm.read_int()
      self.next_sibling_offset = file_xsm.read_int()
      self.parent_offset = file_xsm.read_int()
      self.name = file_xsm.read_12c()
      children_offset = file_xsm.read_ints(max_number_of_children)[:number_of_children]
      children_length = file_xsm.read_ints(max_number_of_children)[:number_of_children]
      children_type = file_xsm.read_ints(max_number_of_children)[:number_of_children]
      children_name = [ file_xsm.read_12c() for child_index in xrange(max_number_of_children) ][:number_of_children]
      self.children = []
      for child_index in xrange(number_of_children):
	node = Node(children_offset[child_index],children_length[child_index],children_type[child_index],children_name[child_index])
	self.children.append(node)
    elif self.type == 1:
      self.data = file_xsm.read_ints(self.length)
    elif self.type == 2:
      self.data = file_xsm.read_reals(self.length)
    elif self.type == 3:
      self.data = [file_xsm.read_4c() for n in xrange(self.length)]
    self.loaded_in_memory = True

if __name__=="__main__":
  file_xsm = FileXsm(file_path)
  print file_xsm.read_4c()
  print file_xsm.read_int()
  offset_root = file_xsm.read_int()
  node = Node(offset_root,1,-1)
  node.load(file_xsm)
  print node
  node = node.children[2]
  node.load(file_xsm)
  children = node.children
  for child in children:
    child.load(file_xsm)
    print child
  #print file_xsm.read_4c(),"|"
  #print file_xsm.read_int(), "|"
  #print file_xsm.read_int(), "|"
  #print file_xsm.read_int(), "|"
  #print file_xsm.read_int(), "|"
  #print file_xsm.read_12c(),"|"
  #print file_xsm.read_ints(30), "|"
  #print file_xsm.read_ints(30), "|"
  #print file_xsm.read_ints(30), "|"
  #print file_xsm.read_12c(), "|"
  #print file_xsm.read_12c(), "|"
  #print file_xsm.read_12c(), "|"
  #file_xsm.seek(191)
  #print file_xsm.read_12c(),"|"
  #file_xsm.seek(194)
  #print file_xsm.read_4c(),"|"
  #file_xsm.seek(8766)
  #print file_xsm.read_4c(),"|"

