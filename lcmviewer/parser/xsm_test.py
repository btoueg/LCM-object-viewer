#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 17/04/11

from array import array

file_path = "../../example/XsmMultiCompoV4"

CHAR_LENGTH_WORD = 8
BYTE_LENGTH_INTEGER = 2
BYTE_STEP_INTEGER = 4
BYTE_STEP = 8

class FileXsm:
  def __init__(self,name):
    self.open(name)
  def open(self,name,mode='rb'):
    self.file = open(name,'rb')
  def close(self):
    self.file.close()
  def seek(self,cursor):
    self.file.seek(cursor*BYTE_STEP)
  def read(self,type,size):
    cursor = self.file.tell()
    data = array(type)
    if type=='c':
      data.fromfile(self.file,size)
      cursor += size
    elif type=='i':
      data.fromfile(self.file,size)
      cursor += size*BYTE_STEP_INTEGER
    self.file.seek(cursor)
    return data.tolist()
  def read_4c(self):
    """
    Read BYTE_STEP characters and tuncate the first 4
    """
    return "".join(self.read('c',CHAR_LENGTH_WORD)[:4])
  def read_8c(self):
    return self.read_4c()+self.read_4c()
  def read_12c(self):
    return self.read_8c()+self.read_4c()
  def read_ints(self,n):
    return self.read('i',n*BYTE_LENGTH_INTEGER)
  def read_int(self):
    return self.read('i',BYTE_LENGTH_INTEGER).pop(0)
    
#class Node:
  #self.offset
  #self.name
  #self.kind
  #self.length
  #self.children


if __name__=="__main__":
  with open(file_path,'rb') as file_handle:
    head=file_handle.read(8)
    if head == '$XSM    ':
      nbits = '64bits'
    else:
      nbits = '32bits'
  file_xsm = FileXsm(file_path)
  print file_xsm.read_4c(),"|"
  print file_xsm.read_int(),"|"
  print file_xsm.read_int(),"|"
  print file_xsm.read_4c(),"|"
  print file_xsm.read_int(), "|"
  print file_xsm.read_int(), "|"
  print file_xsm.read_int(), "|"
  print file_xsm.read_int(), "|"
  print file_xsm.read_12c(),"|"
  print file_xsm.read_ints(30), "|"
  print file_xsm.read_ints(30), "|"
  print file_xsm.read_ints(30), "|"
  print file_xsm.read_12c(), "|"
  print file_xsm.read_12c(), "|"
  print file_xsm.read_12c(), "|"
  file_xsm.seek(191)
  print file_xsm.read_12c(),"|"
  file_xsm.seek(194)
  print file_xsm.read_4c(),"|"
  file_xsm.seek(8766)
  print file_xsm.read_4c(),"|"
  #offset = file_xsm.read_int()
  #print offset
  #file_xsm.seek(offset)
  #print file_xsm.read_4c()