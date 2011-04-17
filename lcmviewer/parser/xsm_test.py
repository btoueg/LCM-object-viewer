#!/usr/bin/python
# -*- coding: utf-8 -*-

# This snippet is used to output an XSM file in the console
# Copyright (C) 2011  Benjamin Toueg

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from os.path import abspath
from sys import platform
from array import array

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

  def depth_first_search(self,node_list):
    for node in node_list:
      node.load(self)
      yield node
      if node.type == 10:
        for index,list_item in enumerate(node.children):
          list_item.load(self)
          if(list_item.type==0):
            if(len(list_item.children))>0:
              list_item.name = "%08d"%(index+1)
            else:
              list_item.name = "empty"
        for y in self.depth_first_search(node.children):
          yield y
      elif node.type in [0]:
        for y in self.depth_first_search(node.children):
          yield y

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
  def __init__(self,offset,length=-1,type=0,name="no name"):
    self.offset = offset
    self.type = type
    self.length = length
    self.name = name
    self.loaded_in_memory = False
  
  def __str__(self):
    """
    Convert a node into a description string
    """
    s  = "Node '%s'"%(self.name)
    s += "\nOffset : %d"%(self.offset*BYTE_STEP)
    s += "\nType : %d"%(self.type)
    s += "\nLength : %d"%(self.length)
    if self.loaded_in_memory:
      if self.type == 0:
        s += "\nDistance from file start : %d"%(self.offset*BYTE_STEP)
        s += "\nDistance to parent node : %d"%(self.parent_offset*BYTE_STEP)
        s += "\nDistance to next sibling : %d"%(self.next_sibling_offset*BYTE_STEP)
        s += "\nNumber of children : %d"%(len(self.children))
      elif self.type == 10:
        pass
      elif self.type in [1,2]:
        s += "\nData :"
        s += ",".join([ str(item) for item in self.data])
      elif self.type == 3:
        s += "\nData :"
        s += self.data
    else:
      s += "\nNot yet loaded in memory."
    return s

  def load(self,file_xsm):
    file_xsm.seek(self.offset)
    if self.type == 0:
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
        if node.type == 10:
          print node.name,node.length,self.name,self.length,number_of_children
        self.children.append(node)
    elif self.type == 10:
      print 
      children_offset = file_xsm.read_ints(self.length)
      self.children = []
      for child_offset in children_offset:
        node = Node(child_offset)
        self.children.append(node)
    elif self.type == 1:
      self.data = file_xsm.read_ints(self.length)
    elif self.type == 2:
      self.data = file_xsm.read_reals(self.length)
    elif self.type == 3:
      self.data = ""
      for n in xrange(self.length):
        self.data += file_xsm.read_4c()
    else:
      print self.type
      raise
    self.loaded_in_memory = True

def xsmToElementList(filePath):
  file_xsm = FileXsm(file_path)
  if file_xsm.read_4c()!="$XSM":
    raise Exception("%s is not an XSM file"%abspath(file_xsm.file.name))
  print file_xsm.read_int()
  offset_root = file_xsm.read_int()
  root = Node(offset_root)
  elementList = []
  file_xsm.depth_first_search([root])
  file_xsm.close()
  return elementList

if __name__=="__main__":
  file_path = "../../example/XsmMultiCompoV4"
  file_xsm = FileXsm(file_path)
  if file_xsm.read_4c()!="$XSM":
    raise Exception("%s is not an XSM file"%abspath(file_xsm.file.name))
  print file_xsm.read_int()
  offset_root = file_xsm.read_int()
  root = Node(offset_root)
  node_generator = file_xsm.depth_first_search([root])
  for node in node_generator:
    print node
  file_xsm.close()

