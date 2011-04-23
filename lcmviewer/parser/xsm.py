#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 10/10/10

# original source code from Ganlib Version5 in C and FORTRAN77

from os.path import abspath
import sys
from array import array
from copy import copy
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0,abspath('..'))
    __package__ = "parser"
    module = __import__(__package__)
    reload(module)
    del sys.path[0]
from . import LinkedListElement, Content

MAX_NUMBER_OF_SIBLINGS = 30
WORD_OFFSET = 3
WORD_LENGTH_CHOICE = {
  '32bits': 4,
  '64bits': 8
}
TYPE_CHOICE = {
  '32bits': {
    'integer' : 'i',
    'real'    : 'f',
    'double'  : 'd'
  },
  '64bits': {
    'integer' : 'l',
    'real'    : 'd',
    'double'  : 'd'
  }
}

def xsmToElementList(filePath):
  with open(filePath,'rb') as inputfile:
    head=inputfile.read(8)
    if head == '$XSM    ':
      nbits = '64bits'
    else:
      nbits = '32bits'
    elementList = []
    xsm_handle = xsm(inputfile,nbits)
    browseXsm([xsm_handle],elementList)
  return elementList

class xsm:
  """
  THE XSM DATABASE RESULTS FROM THE JUXTAPOSITION OF A HIERARCHICAL
  LOGICAL STRUCTURE INTO A DIRECT ACCESS FILE WITH FIXE LENGTH RECORDS.
  THE DIRECT ACCESS FILE IS FORTRAN-77 COMPATIBLE AND IS MANAGED BY
  KDIGET/PUT/CL. XSMOP/PUT/GET/LEN/VEC/NXT/CL ENTRIES PROVIDE A SET OF
  METHODS TO ACCESS A XSM FILE.

  THE LOGICAL STRUCTURE OF A XSM FILE IS MADE OF A ROOT DIRECTORY FOL-
  LOWED BY VARIABLE-LENGTH BLOCKS CONTAINING THE USEFUL INFORMATION.
  EACH TIME A DIRECTORY IS FULL, AN EXTENT IS AUTOMATICALLY CREATED AT
  THE END OF THE FILE, SO THAT THE TOTAL NUMBER OF BLOCKS IN A DIREC-
  TORY IS ONLY LIMITED BY THE MAXIMUM SIZE OF THE DIRECT ACCESS FILE.
  ANY BLOCK CAN CONTAIN A SUB-DIRECTORY IN ORDER TO CREATE A HIERAR-
  CHICAL STRUCTURE.
  """
  def __init__(self, file, nbits = '32bits'):
    """
    OPEN AN EXISTING XSM FILE. VECTORIAL VERSION.
    INPUT PARAMETERS:
       file : FILE HANDLE OF THE XSM FILE.
       nbits : encoding of the XSM file
    
    THE ACTIVE DIRECTORY IS MADE OF TWO BLOCKS LINKED TOGETHER. A xsm block
    IS ALLOCATED FOR EACH SCALAR DIRECTORY OR VECTOR DIRECTORY COMPONENT.
    block IS UNIQUE FOR A GIVEN XSM FILE; EVERY xsm block IS POINTING TO
    THE SAME block.
    """
    # string
    self.name = file.name   # name of the xsm file
    # Block
    self.ibloc = Block(file,nbits) # block obj (see class definiton below)
    my_block = self.ibloc
    # recover the root directory
    head = my_block.kdiget_s(0)
    if head[:4] != "$XSM":
      raise AssertionError("WRONG HEADER ON XSM FILE '%s'."%self.name)
    self.maxoffset = my_block.read_int()
    # int_32
    self.offset = my_block.offset = my_block.read_int()
    self.maxoffset = 0        # maximum address on xsm file
    my_block.step_into()

#----------------------------------------------------------------------#

  def __str__(self):
    s = "== xsm obj ==\n"
    s += "name "+str(self.name)+"\n"
    s += "offset "+str(self.offset)+"\n"
    s += "maxoffset "+str(self.maxoffset)+"\n"
    s += "ibloc\n"+str(self.ibloc)+"\n"
    s += "============"
    return s

#----------------------------------------------------------------------#

  def sync(self):
    self.ibloc.offset = self.offset

#----------------------------------------------------------------------#

  def step_into(self):
    self.ibloc.step_into(self.offset)

#----------------------------------------------------------------------#

  def has_siblings(self):
    return (self.ibloc.number_of_siblings > 0)

#----------------------------------------------------------------------#

  def get_description(self,name):
    return self.ibloc.get_description(self.offset,name)

#----------------------------------------------------------------------#

  def get_next_sibling_name(self,name = " "):
    self.sync()
    return self.ibloc.get_next_sibling_name(name)

#----------------------------------------------------------------------#

  def read_block(self, name, type = 1):
    return self.ibloc.read_block(self.offset,name,type)

#----------------------------------------------------------------------#

  def fetchchildren(self, name, length):
    """
    return children as an xsm list
    
    INPUT PARAMETERS:
      self : ADDRESS OF THE FATHER TABLE.
      NAMP : NAME OF THE DAUGHTER ASSOCIATIVE TABLE.
    
    OUTPUT PARAMETER:
      xsm : ADDRESS OF THE DAUGHTER ASSOCIATIVE TABLE.
    """
    my_block=self.ibloc
    i = my_block.index(name, self.offset)
    length = my_block.sibling_lengths[i]
    type = my_block.sibling_types[i]
    offset = my_block.sibling_offsets[i]
    xsm_list = []
    if (length,type) == (length,10):
      for offset in my_block.kdiget(offset, length):
	xsm = copy(self)
	xsm.offset = offset
	xsm_list.append(xsm)
    elif (length,type) == (-1,0):
      xsm = copy(self)
      xsm.offset  = offset
      xsm_list = [xsm]
    else:
      raise AssertionError("INVALID LENGTH,TYPE (%d,%d) FOR NODE '%s' IN THE XSM FILE '%s'."%(length,type,name,self.name))
    return xsm_list

  def fetchchilddata(self, name, length):
    """
    return children as an xsm list
    
    INPUT PARAMETERS:
      self : ADDRESS OF THE FATHER TABLE.
      NAMP : NAME OF THE DAUGHTER ASSOCIATIVE TABLE.
    
    OUTPUT PARAMETER:
      xsm : ADDRESS OF THE DAUGHTER ASSOCIATIVE TABLE.
    """
    my_block=self.ibloc
    i = my_block.index(name, self.offset)
    length = my_block.sibling_lengths[i]
    type = my_block.sibling_types[i]
    offset = my_block.sibling_offsets[i]
    return self.read_block(name,type)

#----------------------------------------------------------------------#

class Block:             # active directory resident-memory xsm structure
  def __init__(self,file,nbits):
    # file
    self.ifile = file  # xsm (kdi) file handle
    # dict
    self.typedico = TYPE_CHOICE[nbits]
    # int32
    self.lnword = WORD_LENGTH_CHOICE[nbits]
    self.offset = 1
    self.number_of_siblings = 0
    self.offset_next_sibling = 0
    self.offset_parent = 0
    # string
    self.name = ""        # "/" for the root level
    # int_32 list
    self.sibling_offsets = []
    self.sibling_lengths = []
    self.sibling_types = []
    # string list
    self.sibling_names = []

#----------------------------------------------------------------------#

  def __str__(self):
    s =  "== Block obj ==\n"
    s += "kdi_file "+str(self.ifile)+"\n"
    s += "offset of active directory on xsm file "+str(self.offset)+"\n"
    s += "number of nodes on the active directory extent "+str(self.number_of_siblings)+"\n"
    s += "offset of the next directory extent "+str(self.offset_next_sibling)+"\n"
    s += "offset of any parent directory extent "+str(self.offset_parent)+"\n"
    s += "name of the active directory "+str(self.name)+"\n"
    s += "offset list (position of the first element of each block) "+str(self.sibling_offsets)+"\n"
    s += "length of each record (jlong=0 for a directory) that belong to the active directory extent "+str(self.sibling_lengths)+"\n"
    s += "type of each block that belong to the active directory extent "+str(self.sibling_types)+"\n"
    s += "names list of each block (record or directory) that belong to the active directory extent "+str(self.sibling_names)+"\n"
    s += "================"
    return s

#----------------------------------------------------------------------#

  def kdiget_s(self, iofset, size = 1):
    """
    read `size` strings from file
    return one big string
    """
    data = []
    offset = iofset*self.lnword
    self.ifile.seek(offset)
    for i in xrange(size):
      data.append(self.ifile.read(self.lnword)[:4])
    return "".join(data)

  def kdiget(self, iofset, size = 1, datatype = 'integer'):
    """
    read `size` datatype from file
    return list
    """
    data = array(self.typedico[datatype])
    offset = iofset*self.lnword
    self.ifile.seek(offset)
    data.fromfile(self.ifile,size)
    return data.tolist()

  def read_block(self, offset, name, type = 1):
    i = self.index(name, offset)
    if i >= 0:
      if type == 1:
	data = self.kdiget(self.sibling_offsets[i], self.sibling_lengths[i])
      elif type == 3:
	data = self.kdiget_s(self.sibling_offsets[i], self.sibling_lengths[i])
      else:
	data = self.kdiget(self.sibling_offsets[i], self.sibling_lengths[i], 'real')
    else:
      raise AssertionError("UNABLE TO FIND BLOCK '%s' INTO DIRECTORY '%s' IN THE XSM FILE '%s'."%(name,self.name,self.ifile.name))
    return data

  def read_int(self):
    item = self.kdiget(self.offset).pop()
    self.offset += 1
    return item
    
  def read_word(self):
    item = self.kdiget_s(self.offset,3)
    self.offset += WORD_OFFSET
    return item
  
  def read_words(self,n):
    items = []
    for i in xrange(n):
      items.append(self.read_word())
    return items

#----------------------------------------------------------------------#

  def step_into(self, offset = -1):
    if offset > -1:
      self.offset = offset
    hbuf = self.kdiget_s(self.offset)
    if hbuf[:4] != "$$$$":
      raise AssertionError("UNABLE TO RECOVER DIRECTORY.")
    self.offset += 1
    leap = self.read_int()
    self.number_of_siblings = self.read_int()
    if self.number_of_siblings > MAX_NUMBER_OF_SIBLINGS:
      raise AssertionError("Number of siblings (%s) exceeds limits (%s)."%(self.number_of_siblings,MAX_NUMBER_OF_SIBLINGS))
    self.offset_next_sibling = self.read_int()
    self.offset_parent = self.read_int()
    self.name = self.read_word()
    if self.number_of_siblings != 0:
      self.sibling_offsets = self.kdiget(self.offset,self.number_of_siblings)
      self.offset += leap
      self.sibling_lengths = self.kdiget(self.offset,self.number_of_siblings)
      self.offset += leap
      self.sibling_types = self.kdiget(self.offset,self.number_of_siblings)
      self.offset += leap
      self.sibling_names = self.read_words(self.number_of_siblings)

#----------------------------------------------------------------------#

  def get_next_sibling_name(self,name = " "):
    """
    return THE NAME OF THE NEXT BLOCK STORED IN THE ACTIVE DIRECTORY.
    
    INPUT PARAMETERS:
       name : NAME OF THE CURRENT BLOCK. IF name=' ' AT INPUT, FIND
              ANY NAME FOR ANY BLOCK STORED IN THIS DIRECTORY.
    
    OUTPUT PARAMETERS:
              NAME OF THE NEXT BLOCK OR ' ' FOR AN EMPTY
              DIRECTORY.
    """
    i = 0
    if name == " ":
      self.step_into(self.offset)
      i = min(self.number_of_siblings,0)
    else:
      i = self.index(name, self.offset)+1
    if i == -1 and name == " ":
      raise AssertionError("THE ACTIVE DIRECTORY '%s' OF THE XSM FILE '%s' IS EMPTY."%(self.name,self.ifile.name))
    elif i == -1:
      raise AssertionError("UNABLE TO FIND BLOCK '%s' INTO DIRECTORY '%s' IN THE XSM FILE '%s'."%(name,self.name,self.ifile.name))
    elif i < self.number_of_siblings:
      name = self.sibling_names[i]
    else:
      self.step_into(self.offset_next_sibling)
      name = self.sibling_names[0]
      if (name == "***HANDLE***"):
	name = " "
    return name

#----------------------------------------------------------------------#

  def index(self, name, offset):
    """
    FIND A BLOCK (RECORD OR DIRECTORY) POSITION IN THE ACTIVE DIRECTORY
    AND RELATED EXTENTS.
    
    INPUT PARAMETERS:
     NAMP   : NAME OF THE REQUIRED BLOCK.
     IDIR   : OFFSET OF ACTIVE DIRECTORY ON XSM FILE.
    
    OUTPUT PARAMETER:
              -1 IF THE BLOCK NAMED name DOES NOT EXISTS;
              POSITION IN THE ACTIVE DIRECTORY EXTENT IF name EXTSTS.
              0 OR 1 IF name=' '.
    """
    self.step_into(offset)
    if name == "***HANDLE***":
      raise AssertionError("***HANDLE*** IS A RESERVED KEYWORD.")
    elif name == " ":
      name = "***HANDLE***"
    if (self.number_of_siblings == 0):
      raise AssertionError("BLOCK '%s' IS EMPTY"%name)
    if name in self.sibling_names:
      return self.sibling_names.index(name)
    if (self.offset != self.offset_next_sibling):
      istart = self.offset_next_sibling
      while True:
	self.offset = self.offset_next_sibling
	self.step_into()
	if name in self.sibling_names:
	  return self.sibling_names.index(name)
	if (self.offset_next_sibling != istart):
	  break
    return -1

#----------------------------------------------------------------------#

  def get_description(self,offset,name):
    """
    return length and type of a block, return 0 and 99 if the block is not found
      name = name of the current block
    OUTPUT PARAMETERS:
      length : NUMBER OF INFORMATION ELEMENTS STORED IN THE CURRENT BLOCK.
              ILONG=-1 IS RETURNED FOR A SCALAR DIRECTORY.
              ILONG=0 IF THE BLOCK DOES NOT EXISTS.
      itype : TYPE OF INFORMATION ELEMENTS STORED IN THE CURRENT BLOCK.
              0: DIRECTORY                1: INTEGER
              2: SINGLE PRECISION         3: CHARACTER*4
              4: DOUBLE PRECISION         5: LOGICAL
              6: COMPLEX                 99: UNDEFINED
    """
    i = self.index(name, offset)
    if (i > -1):
      length = self.sibling_lengths[i]
      type = self.sibling_types[i]
    else:
      length = 0
      type = 99
    return length, type

#----------------------------------------------------------------------#

def browseXsm(xsm_list,elementList,ilev=1):
  """
  recursive browsing through an xsm file
    xsm_list = list of xsm objects
    elementList = unfolded xsm file ready to be used for a treeview
    ilev = integer depth
  """
  for i,xsm in enumerate(xsm_list):
    if ilev >= 50:
      raise AssertionError("TOO MANY DIRECTORY LEVELS IN "+xsm.name)
    xsm.step_into()
    if xsm.has_siblings():
      # get next label
      name = xsm.get_next_sibling_name()
      if name == "***HANDLE***":
	# keyword indicating a list item
	length,type = xsm.get_description(" ")
	elementList.append(LinkedListElement(id = len(elementList),level = ilev,labelType = 12,label = "%08d"%(i+1),contentType = 0,content = Content(type,-1,None,False,rawFormat="XSM")))
	# down to children
	try:
	  browseXsm(xsm.fetchchildren(" ",length),elementList,ilev = ilev+1)
	except AssertionError:
	  # get data
	  content = Content(type,length,xsm.read_block(" ",type),False,rawFormat="XSM")
	  lle = elementList.pop()
	  lle.contentType = type
	  lle.content = content
	  elementList.append(lle)
      else:
	first = name
	# cycle thru labels
	while True:
	  length,type = xsm.get_description(name)
	  if length != 0 and ( type == 0 or type == 10 ):
	    elementList.append(LinkedListElement(id = len(elementList),level = ilev,labelType = 12,label = name,contentType = 0,content = Content(type,-1,None,False,rawFormat="XSM")))
	    #down to children
	    browseXsm(xsm.fetchchildren(name,length),elementList,ilev = ilev+1)
	  elif length != 0 and type <= 6:
	    # get data
	    content = Content(type,length,xsm.read_block(name,type),False,rawFormat="XSM")
	    elementList.append(LinkedListElement(id = len(elementList),level = ilev,labelType = 12,label = name,contentType = type,content = content))
	  name = xsm.get_next_sibling_name(name)
	  if (name == first):
	    # cycle ended
	    break

#----------------------------------------------------------------------#

if __name__=="__main__":
  filePath = "../../example/XsmMultiCompoV4"
  with open(filePath,'rb') as inputfile:
    head=inputfile.read(8)
    if head == '$XSM    ':
      nbits = '64bits'
    else:
      nbits = '32bits'
    elementList = []
    xsm_handle = xsm(inputfile,nbits)
    browseXsm([xsm_handle],elementList)
  for i,lle in enumerate(elementList):
    print lle
    if i>100: break