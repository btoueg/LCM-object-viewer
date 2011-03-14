#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 10/10/10

# original source code from Ganlib Version5 in C and FORTRAN77

from array import array
from copy import copy
from MyParserTool import LinkedListElement, Content

iofmax = 30
iwrd = 3

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
  def __init__(self, myFile, nbits = '32bits'):
    """
    OPEN AN EXISTING XSM FILE. VECTORIAL VERSION.
    INPUT PARAMETERS:
       myFile : FILE HANDLE OF THE XSM FILE.
       nbits : encoding of the XSM file
    
    THE ACTIVE DIRECTORY IS MADE OF TWO BLOCKS LINKED TOGETHER. A xsm block
    IS ALLOCATED FOR EACH SCALAR DIRECTORY OR VECTOR DIRECTORY COMPONENT.
    block IS UNIQUE FOR A GIVEN XSM FILE; EVERY xsm block IS POINTING TO
    THE SAME block.
    """
    # string
    self.name = myFile.name   # name of the xsm file
    # int_32
    self.idir = 0             # offset of active directory on xsm file
    self.maxoffset = 0        # maximum address on xsm file
    # Block
    self.ibloc = Block(myFile,nbits) # block obj (see class definiton below)
    my_block = self.ibloc
    # recover the root directory
    head = my_block.kdiget_s(0)
    if head[:4] != "$XSM":
      raise AssertionError("WRONG HEADER ON XSM FILE '%s'."%self.name)
    self.maxoffset = my_block.kdiget(1).pop() 
    self.idir = my_block.idir = my_block.kdiget(2).pop()
    my_block.importdir()

#----------------------------------------------------------------------#

  def __str__(self):
    s = "== xsm obj ==\n"
    s += "name "+str(self.name)+"\n"
    s += "idir "+str(self.idir)+"\n"
    s += "maxoffset "+str(self.maxoffset)+"\n"
    s += "ibloc\n"+str(self.ibloc)+"\n"
    s += "============"
    return s

#----------------------------------------------------------------------#

  def info(self):
    return self.ibloc.info(self.idir)

#----------------------------------------------------------------------#

  def length(self,namp):
    return self.ibloc.length(self.idir,namp)

#----------------------------------------------------------------------#

  def next(self,namp = " "):
    return self.ibloc.next(self.idir,namp)

#----------------------------------------------------------------------#

  def getblock(self, namp, itylcm = 1):
    return self.ibloc.getblock(self.idir,namp,itylcm)

#----------------------------------------------------------------------#

  def fetchchildren(self, namp, ilong):
    """
    return children as an xsm list
    
    INPUT PARAMETERS:
      self : ADDRESS OF THE FATHER TABLE.
      NAMP : NAME OF THE DAUGHTER ASSOCIATIVE TABLE.
    
    OUTPUT PARAMETER:
      xsm : ADDRESS OF THE DAUGHTER ASSOCIATIVE TABLE.
    """
    my_block=self.ibloc
    i = my_block.index(namp, self.idir)
    lenold = my_block.jlon[i]
    ityold = my_block.jtyp[i]
    idir = my_block.iofs[i]
    xsm_list = []
    if (lenold,ityold) == (ilong,10):
      for idir in my_block.kdiget(idir, ilong):
	xsm = copy(self)
	xsm.idir = idir
	xsm_list.append(xsm)
    elif (lenold,ityold) == (-1,0):
      xsm = copy(self)
      xsm.idir  = idir
      xsm_list = [xsm]
    else:
      raise AssertionError("INVALID LENGTH,TYPE (%d,%d) FOR NODE '%s' IN THE XSM FILE '%s'."%(ilong,ityold,self.name))
    return xsm_list

#----------------------------------------------------------------------#

class Block:             # active directory resident-memory xsm structure
  def __init__(self,myFile,nbits):
    # file
    self.ifile = myFile  # xsm (kdi) file handle
    if nbits == '32bits':
      self.lnword = 4
      self.typedico = { 'integer' : 'i',
			'real'    : 'f',
			'double'  : 'd'
		      }
    elif nbits == '64bits':
      self.lnword = 8
      self.typedico = { 'integer' : 'l',
			'real'    : 'd',
			'double'  : 'd'
		      }
    else:
      raise AssertionError('32 or 64 bits ?')
    # int32
    self.idir = 0         # offset of active directory on xsm file
    self.nmt = 0          # number of nodes on the active directory extent
    self.link = 0         # offset of the next directory extent
    self.iroot = 0        # offset of any parent directory extent
    # string
    self.name = ""        # name of the active directory. ='/' for the root level
    # int_32 list
    self.iofs = []        # offset list (position of the first element of each block)
    self.jlon = []        # length of each record (jlong=0 for a directory) that belong to the active directory extent
    self.jtyp = []        # type of each block that belong to the active directory extent
    # string list
    self.cmt = []         # names list of each block (record or directory) that belong to the active directory extent

#----------------------------------------------------------------------#

  def __str__(self):
    s =  "== Block obj ==\n"
    s += "kdi_file "+str(self.ifile)+"\n"
    s += "offset of active directory on xsm file "+str(self.idir)+"\n"
    s += "number of nodes on the active directory extent "+str(self.nmt)+"\n"
    s += "offset of the next directory extent "+str(self.link)+"\n"
    s += "offset of any parent directory extent "+str(self.iroot)+"\n"
    s += "name of the active directory "+str(self.name)+"\n"
    s += "offset list (position of the first element of each block) "+str(self.iofs)+"\n"
    s += "length of each record (jlong=0 for a directory) that belong to the active directory extent "+str(self.jlon)+"\n"
    s += "type of each block that belong to the active directory extent "+str(self.jtyp)+"\n"
    s += "names list of each block (record or directory) that belong to the active directory extent "+str(self.cmt)+"\n"
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

#----------------------------------------------------------------------#

  def importdir(self, idir = -1):
    """
    import a directory
    """
    if idir > -1:
      self.idir = idir
    ipos = self.idir
    hbuf = self.kdiget_s(ipos)
    if hbuf[:4] != "$$$$":
      raise AssertionError("UNABLE TO RECOVER DIRECTORY.")
    ipos += 1
    iofma2 = self.kdiget(ipos).pop()
    ipos += 1
    self.nmt = self.kdiget(ipos).pop()
    if self.nmt > iofmax:
      raise AssertionError("UNABLE TO RECOVER DIRECTORY.")
    ipos += 1
    self.link = self.kdiget(ipos).pop()
    ipos += 1
    self.iroot = self.kdiget(ipos).pop()
    ipos += 1
    self.name = self.kdiget_s(ipos,3)
    if self.nmt != 0:
      ipos += iwrd
      self.iofs = self.kdiget(ipos,self.nmt)
      ipos += iofma2
      self.jlon = self.kdiget(ipos,self.nmt)
      ipos += iofma2
      self.jtyp = self.kdiget(ipos,self.nmt)
      ipos += iofma2
      self.cmt = []
      for i in xrange(self.nmt):
	self.cmt.append(self.kdiget_s(ipos,3))
	ipos += iwrd

#----------------------------------------------------------------------#

  def info(self,idir):
    """
    RECOVER GLOBAL INFORMATIONS RELATED TO AN XSM FILE.
    
    OUTPUT PARAMETERS:
     self.name : NAME OF THE XSM FILE.
     my_block.name : NAME OF THE ACTIVE DIRECTORY.
     empty : =.TRUE. IF THE ACTIVE DIRECTORY IS EMPTY.
    """
    if (self.idir != idir):
      # SWITCH TO THE CORRECT ACTIVE DIRECTORY (BLOCK 2)
      self.importdir(idir)
    empty = (self.nmt == 0)
    return self.ifile.name, self.name, empty

#----------------------------------------------------------------------#

  def length(self,idir,namp):
    """
    return length and type of a block, return 0 and 99 if the block is not found
      namp = name of the current block
    OUTPUT PARAMETERS:
      ilong : NUMBER OF INFORMATION ELEMENTS STORED IN THE CURRENT BLOCK.
              ILONG=-1 IS RETURNED FOR A SCALAR DIRECTORY.
              ILONG=0 IF THE BLOCK DOES NOT EXISTS.
      itype : TYPE OF INFORMATION ELEMENTS STORED IN THE CURRENT BLOCK.
              0: DIRECTORY                1: INTEGER
              2: SINGLE PRECISION         3: CHARACTER*4
              4: DOUBLE PRECISION         5: LOGICAL
              6: COMPLEX                 99: UNDEFINED
    """
    i = self.index(namp, idir)
    if (i > -1):
      ilong = self.jlon[i]
      itype = self.jtyp[i]
    else:
      ilong = 0
      itype = 99
    return ilong, itype

#----------------------------------------------------------------------#

  def next(self,idir,namp = " "):
    """
    return THE NAME OF THE NEXT BLOCK STORED IN THE ACTIVE DIRECTORY.
    
    INPUT PARAMETERS:
       namp : NAME OF THE CURRENT BLOCK. IF namp=' ' AT INPUT, FIND
              ANY NAME FOR ANY BLOCK STORED IN THIS DIRECTORY.
    
    OUTPUT PARAMETERS:
              NAME OF THE NEXT BLOCK OR ' ' FOR AN EMPTY
              DIRECTORY.
    """
    i = 0
    if namp == " ":
      if self.idir != idir:
	#SWITCH TO THE CORRECT ACTIVE DIRECTORY (BLOCK 2)
	self.importdir(idir)
      i = min(self.nmt,0)
    else:
      i = self.index(namp, idir)+1
    if i == -1 and namp == " ":
      #EMPTY DIRECTORY
      raise AssertionError("THE ACTIVE DIRECTORY '%s' OF THE XSM FILE '%s' IS EMPTY."%(self.name,self.ifile.name))
    elif i == -1:
      raise AssertionError("UNABLE TO FIND BLOCK '%s' INTO DIRECTORY '%s' IN THE XSM FILE '%s'."%(namp,self.name,self.ifile.name))
    elif i < self.nmt:
      namp = self.cmt[i]
      return namp
    #SWITCH TO THE NEXT DIRECTORY.
    if self.idir != self.link:
      #RECOVER THE NEXT DIRECTORY.
      self.importdir(self.link)
    namp = self.cmt[0]
    if (namp == "***HANDLE***"):
      namp = " "
    return namp

#----------------------------------------------------------------------#

  def getblock(self, idir, namp, itylcm = 1):
    """
    READ A BLOCK FROM THE XSM FILE
    
    INPUT PARAMETERS:
      NAMP  : NAME OF THE CURRENT BLOCK.
      itylcm : type of data to read
    
    OUTPUT PARAMETER:
      data : INFORMATION ELEMENTS. DIMENSION DATA2(ILONG)
    """
    i = self.index(namp, idir)
    if i >= 0:
      if itylcm == 1:
	data = self.kdiget(self.iofs[i], self.jlon[i])
      elif itylcm == 3:
	data = self.kdiget_s(self.iofs[i], self.jlon[i])
      else:
	data = self.kdiget(self.iofs[i], self.jlon[i], 'real')
    else:
      raise AssertionError("UNABLE TO FIND BLOCK '%s' INTO DIRECTORY '%s' IN THE XSM FILE '%s'."%(namp,self.name,self.ifile.name))
    return data

#----------------------------------------------------------------------#

  def index(self, namp, idir):
    """
    FIND A BLOCK (RECORD OR DIRECTORY) POSITION IN THE ACTIVE DIRECTORY
    AND RELATED EXTENTS.
    
    INPUT PARAMETERS:
     NAMP   : NAME OF THE REQUIRED BLOCK.
     IDIR   : OFFSET OF ACTIVE DIRECTORY ON XSM FILE.
    
    OUTPUT PARAMETER:
              -1 IF THE BLOCK NAMED namp DOES NOT EXISTS;
              POSITION IN THE ACTIVE DIRECTORY EXTENT IF namp EXTSTS.
              0 OR 1 IF namp=' '.
    """
    if self.idir != idir:
      # SWITCH TO THE CORRECT ACTIVE DIRECTORY (BLOCK 2)
      self.importdir(idir)
    if namp == "***HANDLE***":
      raise AssertionError("***HANDLE*** IS A RESERVED KEYWORD.")
    elif namp == " ":
      namp = "***HANDLE***"
    ipos = -1
    if (self.nmt < iofmax):
      ipos = self.idir
    if (self.nmt == 0):
      raise AssertionError("BLOCK IS EMPTY")
    if namp in self.cmt:
      # THE BLOCK ALREADY EXISTS
      return self.cmt.index(namp)
    # THE BLOCK NAMP DOES NOT EXISTS IN THE ACTIVE DIRECTORY EXTENT. WE
    # SEARCH IN OTHER EXTENTS THAT BELONG TO THE ACTIVE DIRECTORY.
    if (self.idir != self.link):
      # RECOVER A NEW DIRECTORY EXTENT. */
      istart = self.link
      self.idir = istart
      while True:
	self.importdir()
	if (self.nmt < iofmax):
	  ipos = self.idir
	if namp in self.cmt:
	  # THE BLOCK NAMP WAS FOUND IN THE ACTIVE DIRECTORY EXTENT
	  return self.cmt.index(namp)
	if (self.link == istart):
	  break
	self.idir = self.link
    return -1

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
    # retrieve info about current block
    namxsm, namedir, empty = xsm.info()
    if not empty:
      # get next label
      namt = xsm.next()
      if "***HANDLE***" == namt:
	# keyword indicating a list item
	ilong,itylcm = xsm.length(" ")
	elementList.append(LinkedListElement(id = len(elementList),level = ilev,labelType = 12,label = "%08d"%(i+1),contentType = 0,content = Content(itylcm,-1,None,False,rawFormat="XSM")))
	# down to children
	browseXsm(xsm.fetchchildren(" ",ilong),elementList,ilev = ilev+1)
      else:
	first = namt
	# cycle thru labels
	while True:
	  ilong,itylcm = xsm.length(namt)
	  if ilong != 0 and ( itylcm == 0 or itylcm == 10 ):
	    elementList.append(LinkedListElement(id = len(elementList),level = ilev,labelType = 12,label = namt,contentType = 0,content = Content(itylcm,-1,None,False,rawFormat="XSM")))
	    #down to children
	    browseXsm(xsm.fetchchildren(namt,ilong),elementList,ilev = ilev+1)
	  elif ilong != 0 and itylcm <= 6:
	    # get data
	    content = Content(itylcm,ilong,xsm.getblock(namt,itylcm),False,rawFormat="XSM")
	    elementList.append(LinkedListElement(id = len(elementList),level = ilev,labelType = 12,label = namt,contentType = itylcm,content = content))
	  namt = xsm.next(namt)
	  if (namt == first):
	    # cycle ended
	    break

#----------------------------------------------------------------------#

if __name__ == "__main__":
  import sys
  try:
    filePath = sys.argv[1]
  except:
    filePath="/home/melodie/Bureau/xsm_open/XSMCPO_0004"
  elementList = []
  with open(filePath,'rb') as myFile:
    xsm_handle = xsm(myFile)
    browseXsm([xsm_handle],elementList)
  for e in elementList:
    print e

