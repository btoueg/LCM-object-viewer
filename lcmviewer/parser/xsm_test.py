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
    data = array(type)
    data.fromfile(self.file,size)
    if step > 1:
      data = data[::step]
    return data.tolist()

  def read_4c(self):
    """
    Read BYTE_STEP characters and tuncate the first 4
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

#class Node:
  #self.offset
  #self.name
  #self.kind
  #self.length
  #self.children

if __name__=="__main__":
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

