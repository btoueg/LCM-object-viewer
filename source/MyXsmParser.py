#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 10/10/10

from array import array
from copy import copy
from MyParserTool import *

lnword = 8
iofmax = 30
maxit = 100
iprim = 3
iwrd = 3
klong = 5+iwrd+(3+iwrd)*iofmax

class xsm:                  # active directory resident-memory xsm structure
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
  def __init__(self, myFile):
    # string
    self.hname = myFile.name # name of the xsm file
    # int_32
    self.header = 200        # header (=200 for an xsm file)
    self.listlen = -1        # number of elements in the list
    self.impf = 0            # type of access (1:modif or 2:read-only)
    self.idir = 0            # offset of active directory on xsm file
    # Block2
    self.ibloc = Block2()    # address of block 2 in memory
    # xsm
    self.father = None       # address of the father active directory resident-memory xsm structure. =0 for root directory.
    self.xsmop(myFile, 2)
  def __str__(self):
    s = "== xsm obj ==\n"
    s += "hname "+str(self.hname)+"\n"
    s += "header "+str(self.header)+"\n"
    s += "listlen "+str(self.listlen)+"\n"
    s += "impf "+str(self.impf)+"\n"
    s += "idir "+str(self.idir)+"\n"
    s += "ibloc\n"+str(self.ibloc)+"\n"
    if self.father != None:
      s += "father "+str(self.father.ibloc.mynam)+"\n"
    else:
      s += "father "+str(self.father)+"\n"
    s += "============"
    return s

  def xsmop(self, myFile, imp):
    """
    OPEN AN EXISTING OR CREATE A NEW XSM FILE. VECTORIAL VERSION.
    INPUT PARAMETERS:
       NAMP : CHARACTER*12 NAME OF THE XSM FILE.
        IMP : TYPE OF ACCESS.  =0: NEW FILE MODE;
                               =1: MODIFICATION MODE;
                               =2: READ ONLY MODE.
       IMPX : IF IMPX=0, WE SUPPRESS PRINTING ON XSMOP.
    
    OUTPUT PARAMETERS:
     IPLIST : ADDRESS OF THE HANDLE TO THE XSM FILE.
       NAMP : CHARACTER*12 NAME OF THE XSM FILE IF IMP=1 OR IMP=2.
    
    THE ACTIVE DIRECTORY IS MADE OF TWO BLOCKS LINKED TOGETHER. A BLOCK 1
    IS ALLOCATED FOR EACH SCALAR DIRECTORY OR VECTOR DIRECTORY COMPONENT.
    BLOCK 2 IS UNIQUE FOR A GIVEN XSM FILE; EVERY BLOCK 1 IS POINTING TO
    THE SAME BLOCK 2.
    """
    self.impf = imp
    my_block2 = self.ibloc
    my_block2.ifile = myFile
    if imp >= 1:
      # RECOVER THE ROOT DIRECTORY IF THE XSM FILE ALREADY EXISTS
      hbuf = kdiget_s(my_block2.ifile,0)
      if hbuf[:4] != "$XSM":
	raise AssertionError("WRONG HEADER ON XSM FILE '%s'."%self.hname)
      my_block2.ioft = kdiget(my_block2.ifile,1).pop()
      my_block2.idir = kdiget(my_block2.ifile,2).pop()
      self.idir = my_block2.idir
      my_block2.xsmdir(1)
      my_block2.modif = 0
    else:
      raise AssertionError("NEW FILE MODE not implemented")

  def xsminf(self):
    """
    RECOVER GLOBAL INFORMATIONS RELATED TO AN XSM FILE.
    
    INPUT PARAMETERS:
     IPLIST : ADDRESS OF THE HANDLE TO THE XSM FILE.
    
    OUTPUT PARAMETERS:
     NAMXSM : CHARACTER*12 NAME OF THE XSM FILE.
      NAMMY : CHARECTER*12 NAME OF THE ACTIVE DIRECTORY.
      EMPTY : =.TRUE. IF THE ACTIVE DIRECTORY IS EMPTY.
      ILONG : =-1: FOR A TABLE; >0: NUMBER OF LIST ITEMS.
     ACCESS : TYPE OF ACCESS. =1: OBJECT OPEN FOR MODIFICATION;
              =2: OBJECT IN READ-ONLY MODE.
    """
    my_block2=self.ibloc
    if (my_block2.idir != self.idir):
      # SWITCH TO THE CORRECT ACTIVE DIRECTORY (BLOCK 2)
      if (my_block2.modif == 1):
	my_block2.xsmdir(2)
      my_block2.idir = self.idir
      my_block2.xsmdir(1)
    namxsm = self.hname
    nammy = my_block2.mynam
    empty = (my_block2.nmt == 0)
    ilong = self.listlen
    access = self.impf
    return namxsm, nammy, empty, ilong, access

  def xsmlen(self,namp):
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
    iii = self.ibloc.xsmrep(namp, 1, self.idir)
    if (iii >= 0):
      ilong = self.ibloc.jlon[iii]
      itype = self.ibloc.jtyp[iii]
    else:
      ilong = 0
      itype = 99
    return ilong, itype

  def xsmnxt(self,namp = " "):
    """
    FIND THE NAME OF THE NEXT BLOCK STORED IN THE ACTIVE DIRECTORY.
    
    INPUT PARAMETERS:
     self : ADDRESS OF THE HANDLE TO THE XSM FILE.
       NAMP : CHARACTER*12 NAME OF A BLOCK. IF NAMP=' ' AT INPUT, FIND
              ANY NAME FOR ANY BLOCK STORED IN THIS DIRECTORY.
    
    OUTPUT PARAMETERS:
       NAMP : CHARACTER*12 NAME OF THE NEXT BLOCK. NAMP=' ' FOR AN EMPTY
              DIRECTORY.
    """
    iii = 0
    my_block2 = self.ibloc
    if namp == " ":
      if my_block2.idir != self.idir:
	#SWITCH TO THE CORRECT ACTIVE DIRECTORY (BLOCK 2)
	if (my_block2.modif == 1):
	  my_block2.xsmdir(2)
	my_block2.idir = self.idir
	my_block2.xsmdir(1)
      iii = min(my_block2.nmt,0)
    else:
      iii = my_block2.xsmrep(namp, 1, self.idir)+1
    if iii == -1 and namp == " ":
      #EMPTY DIRECTORY
      raise AssertionError("THE ACTIVE DIRECTORY '%s' OF THE XSM FILE '%s' IS EMPTY."%(my_block2.mynam,self.hname))
    elif iii == -1:
      raise AssertionError("UNABLE TO FIND BLOCK '%s' INTO DIRECTORY '%s' IN THE XSM FILE '%s'."%(namp,my_block2.mynam,self.hname))
    elif iii < my_block2.nmt:
      namp = my_block2.cmt[iii]
      return namp
    #SWITCH TO THE NEXT DIRECTORY.
    if my_block2.idir != my_block2.link:
      if my_block2.modif == 1:
	my_block2.xsmdir(2)
      my_block2.idir = my_block2.link
      #RECOVER THE NEXT DIRECTORY.
      my_block2.xsmdir(1)
    namp = my_block2.cmt[0]
    if (namp == "***HANDLE***"):
      namp = " "
    return namp

  def xsmget(self, namp, itylcm = 1):
    """
    COPY A BLOCK FROM THE XSM FILE INTO MEMORY.
    
    INPUT PARAMETERS:
     IPLIST : ADDRESS OF THE HANDLE TO THE XSM FILE.
      NAMP  : CHARACTER*12 NAME OF THE CURRENT BLOCK.
    
    OUTPUT PARAMETER:
      DATA2 : INFORMATION ELEMENTS. DIMENSION DATA2(ILONG)
    """
    my_block2=self.ibloc
    iii = my_block2.xsmrep(namp, 1, self.idir)
    if iii >= 0:
      if itylcm == 1:
	data2 = kdiget(my_block2.ifile, my_block2.iofs[iii], my_block2.jlon[iii])
      elif itylcm == 3:
	data2 = kdiget_s(my_block2.ifile, my_block2.iofs[iii], my_block2.jlon[iii])
      else:
	data2 = kdiget(my_block2.ifile, my_block2.iofs[iii], my_block2.jlon[iii], 'd')
    else:
      raise AssertionError("UNABLE TO FIND BLOCK '%s' INTO DIRECTORY '%s' IN THE XSM FILE '%s'."%(namp,my_block2.mynam,iplist.hname))
    return data2

class Block2:             # active directory resident-memory xsm structure
  def __init__(self):
    # file
    self.ifile = None  # xsm (kdi) file handle
    # int32
    self.idir = 0         # offset of active directory on xsm file
    self.modif = 0        # =1 if the active directory extent have been modified
    self.ioft = 0         # maximum address on xsm file
    self.nmt = 0          # exact number of nodes on the active directory extent
    self.link = 0         # offset of the next directory extent
    self.iroot = 0        # offset of any parent directory extent
    # string
    self.mynam = ""       # character*12 name of the active directory. ='/' for the root level
    # int_32 list (iofmax long)
    self.iofs = [0]*iofmax # offset list (position of the first element of each block)
    self.jlon = [0]*iofmax # length of each record (jlong=0 for a directory) that belong to the active directory extent
    self.jtyp = [0]*iofmax # type of each block that belong to the active directory extent
    # string list (iofmax long)
    self.cmt = []          # list of character*12 names of each block (record or directory) that belong to the active directory extent
  def __str__(self):
    s =  "== Block2 obj ==\n"
    s += "kdi_file "+str(self.ifile)+"\n"
    s += "idir "+str(self.idir)+"\n"
    s += "modif "+str(self.modif)+"\n"
    s += "ioft "+str(self.ioft)+"\n"
    s += "nmt "+str(self.nmt)+"\n"
    s += "link "+str(self.link)+"\n"
    s += "iroot "+str(self.iroot)+"\n"
    s += "mynam "+str(self.mynam)+"\n"
    s += "iofs "+str(self.iofs)+"\n"
    s += "jlon "+str(self.jlon)+"\n"
    s += "jtyp "+str(self.jtyp)+"\n"
    s += "cmt "+str(self.cmt)+"\n"
    s += "================"
    return s
  def xsmdir(self, ind):
    """
    import a directory using the kdi utility

    INPUT PARAMETERS:
     ind = 1 for import ; 2 for export
    """
    ipos = self.idir
    if ind == 1:
      hbuf = kdiget_s(self.ifile,ipos)
      if hbuf[:4] != "$$$$":
	raise AssertionError("UNABLE TO RECOVER DIRECTORY.")
      ipos += 1
      iofma2 = kdiget(self.ifile,ipos).pop()
      ipos += 1
      self.nmt = kdiget(self.ifile,ipos).pop()
      if self.nmt > iofmax:
	raise AssertionError("UNABLE TO RECOVER DIRECTORY.")
      ipos += 1
      self.link = kdiget(self.ifile,ipos).pop()
      ipos += 1
      self.iroot = kdiget(self.ifile,ipos).pop()
      ipos += 1
      self.mynam = kdiget_s(self.ifile,ipos,3)
      if self.nmt != 0:
	ipos += iwrd
	self.iofs = kdiget(self.ifile,ipos,self.nmt)
	ipos += iofma2
	self.jlon = kdiget(self.ifile,ipos,self.nmt)
	ipos += iofma2
	self.jtyp = kdiget(self.ifile,ipos,self.nmt)
	ipos += iofma2
	self.cmt = []
	for i in xrange(self.nmt):
	  self.cmt.append(kdiget_s(self.ifile,ipos,3))
	  ipos += iwrd
    elif ind == 2:
      raise AssertionError("EXPORT not implemented")

  def xsmrep(self, namt, ind, idir):
    """
    FIND A BLOCK (RECORD OR DIRECTORY) POSITION IN THE ACTIVE DIRECTORY
    AND RELATED EXTENTS.
    
    INPUT PARAMETERS:
     NAMT   : CHARACTER*12 NAME OF THE REQUIRED BLOCK.
     IND    : =1 SEARCH NAMT ; =2 SEARCH AND POSITIONNING IN AN EMPTY
              SLOT OF THE ACTIVE DIRECTORY IF NAMT DOES NOT EXISTS.
     IDIR   : OFFSET OF ACTIVE DIRECTORY ON XSM FILE.
     self : ADDRESS OF MEMORY-RESIDENT XSM STRUCTURE (BLOCK 2).
    
    OUTPUT PARAMETER:
     III    : RETURN CODE. =0 IF THE BLOCK NAMED NAMT DOES NOT EXISTS;
              =POSITION IN THE ACTIVE DIRECTORY EXTENT IF NAMT EXTSTS.
              =0 OR 1 IF NAMT=' '.
    """
    i = ipos = ipos2 = irc = irc2 = 0
    if self.idir != idir:
      # SWITCH TO THE CORRECT ACTIVE DIRECTORY (BLOCK 2)
      if (self.modif == 1):
	self.xsmdir(2)
      self.idir = idir
      self.xsmdir(1)
    if namt == "***HANDLE***":
      raise AssertionError("***HANDLE*** IS A RESERVED KEYWORD.")
    namp = namt
    if namp == " ":
      namp = "***HANDLE***"
    ipos = -1
    if (self.nmt < iofmax):
      ipos = self.idir
    if (self.nmt == 0):
      raise AssertionError()
    if namp in self.cmt:
      # THE BLOCK ALREADY EXISTS
      return self.cmt.index(namp)
    # THE BLOCK NAMP DOES NOT EXISTS IN THE ACTIVE DIRECTORY EXTENT. WE
    # SEARCH IN OTHER EXTENTS THAT BELONG TO THE ACTIVE DIRECTORY.
    if (self.idir != self.link):
      # RECOVER A NEW DIRECTORY EXTENT. */
      istart = self.link
      if (self.modif == 1):
	self.xsmdir(2)
      self.idir = istart
      while True:
	self.xsmdir(1)
	if (self.nmt < iofmax):
	  ipos = self.idir
	if namp in self.cmt:
	  # THE BLOCK NAMP WAS FOUND IN THE ACTIVE DIRECTORY EXTENT
	  return self.cmt.index(namp)
	if (self.link == istart):
	  break
	self.idir = self.link
    return -1

def kdiget_s(myFile,iofset,length=1):
  data = []
  offset = iofset*lnword
  myFile.seek(offset)
  for i in xrange(length):
    data.append(myFile.read(lnword)[:4])
  return "".join(data)

def kdiget(myFile,iofset,length=1, datatype = 'l'):
  data = array(datatype)
  offset = iofset*lnword
  myFile.seek(offset)
  data.fromfile(myFile,length)
  return data.tolist()
  
def xsmdir(ind, my_block2):
  my_block2.xsmdir(ind)

def xsmrep(namt, ind, idir, my_block2):
  return my_block2.xsmrep(namt, ind, idir)

def xsmget(iplist, namp, itylcm = 1):
  return iplist.xsmget(namp, itylcm)

def xsmnxt(iplist,namp = " "):
  return iplist.xsmnxt(namp)

def xsmlen(iplist, namp):
  return iplist.xsmlen(namp)

def xsminf(iplist):
  return iplist.xsminf()

def xsmdid(iplist, namp):
  """
  *-----------------------------------------------------------------------
  *
  * CREATE/ACCESS A DAUGHTER ASSOCIATIVE TABLE IN A FATHER TABLE.
  *
  * INPUT PARAMETERS:
  *  IPLIST : ADDRESS OF THE FATHER TABLE.
  *    NAMP : CHARACTER*12 NAME OF THE DAUGHTER ASSOCIATIVE TABLE.
  *
  * OUTPUT PARAMETER:
  *  JPLIST : ADDRESS OF THE DAUGHTER ASSOCIATIVE TABLE.
  *
  *-----------------------------------------------------------------------
  """
  if (iplist.header != 200):
    raise AssertionError("THE XSM FILE '%s' HAS THE WRONG HEADER."%iplist.hname)

  my_block2=iplist.ibloc
  iii = xsmrep(namp, 2, iplist.idir, my_block2)
  lenold = my_block2.jlon[iii]
  ityold = my_block2.jtyp[iii]
  if (lenold == 0):
    #CREATE A NEW SCALAR DIRECTORY EXTENT ON THE XSM FILE.
    raise AssertionError()
  elif (lenold == -1 and ityold == 0):
    idir = my_block2.iofs[iii]
  else:
    raise AssertionError("BLOCK '%s' IS NOT AN ASSOCIATIVE TABLE OF THE XSM FILE '%s'."%(namp,iplist.hname))

  #COPY BLOCK1
  jplist = copy(iplist)
  jplist.listlen = -1
  jplist.idir  = idir
  jplist.father = iplist
  return jplist

def xsmlid(iplist, namp, ilong):
  """
  *-----------------------------------------------------------------------
  *
  * CREATE/ACCESS THE HIERARCHICAL STRUCTURE OF A LIST IN A XSM FILE.
  *
  * INPUT PARAMETERS:
  *  IPLIST : ADDRESS OF THE FATHER TABLE.
  *    NAMP : CHARACTER*12 NAME OF THE DAUGHTER LIST.
  *   ILONG : DIMENSION OF THE DAUGHTER LIST.
  *
  * OUTPUT PARAMETER:
  *  JPLIST : ADDRESS OF THE DAUGHTER LIST.
  *
  *-----------------------------------------------------------------------
  """
  if (iplist.header != 200):
    raise AssertionError("THE XSM FILE '%s' HAS THE WRONG HEADER."%iplist.hname)
  elif ilong <= 0:
    raise AssertionError("INVALID LENGTH (%d) FOR NODE '%s' IN THE XSM FILE '%s'."%(ilong,iplist.hname))
  my_block2=iplist.ibloc
  iii = xsmrep(namp, 2, iplist.idir, my_block2)
  lenold = my_block2.jlon[iii]
  ityold = my_block2.jtyp[iii]
  if (ilong > lenold and ityold == 10 or lenold == 0):
    #CREATE ILONG-LENOLD NEW LIST EXTENTS ON THE XSM FILE.
    raise AssertionError()
  elif (lenold == ilong and ityold == 10):
    idir = my_block2.iofs[iii]
  elif (ityold != 10):
    raise AssertionError("BLOCK '%s' IS NOT A LIST OF THE XSM FILE '%s'."%(namp,iplist.hname))
  else:
    raise AssertionError("THE LIST '%s' OF THE XSM FILE '%s' HAVE AN INVALID LENGTH (%d)."%(namp,iplist.hname,ilong))
  iivec = kdiget(my_block2.ifile, idir, ilong)
  jplist = []
  for ivec in iivec:
    #COPY BLOCK1
    iofset = copy(iplist)
    iofset.listlen = 0
    iofset.idir = ivec
    iofset.father = iplist
    jplist.append(iofset)
  return jplist

maxlev = 50

def browseXsm(iplist_list,elementList,ilev=1):
  """
  recursive browsing of an xsm file
    iplist_list = list of xsm objects
    elementList = unfolded xsm file ready to be used for a treeview
    ilev = integer depth
  """
  for i,iplist in enumerate(iplist_list):
    if ilev >= maxlev:
      raise AssertionError("TOO MANY DIRECTORY LEVELS ON "+namxsm)
    # retrieve info about current block
    namxsm, myname, empty, ilong, lcm = iplist.xsminf()
    #elementList.append(LinkedListElement(id = len(elementList)+1,level = ilev-1,labelType = 12,label = myname,contentType = 0,content = None))
    #print "-->", ilev-1, 12, 0, ilong, "<-"
    #print myname
    if empty:
      # switch to the next xsm object in iplist_list
      break
    # get next label
    namt = iplist.xsmnxt()
    if "***HANDLE***" == namt:
      # key label that indicates the current block is in fact a list
      ilong,itylcm = xsmlen(iplist," ")
      elementList.append(LinkedListElement(id = len(elementList),level = ilev,labelType = 12,label = "%012d"%i,contentType = 0,content = Content(itylcm,-1,None,False)))
      #print "->", ilev, 0, itylcm, ilong, "<-",len(elementList)
      #print i
      if ilong == -1:
	browseXsm([xsmdid(iplist," ")],elementList,ilev = ilev+1)
      else:
	browseXsm(xsmlid(iplist," ",ilong),elementList,ilev = ilev+1)
    else:
      first = namt
      while True:
	ilong,itylcm = xsmlen(iplist,namt)
	if ilong != 0 and ( itylcm == 0 or itylcm == 10 ):
	  elementList.append(LinkedListElement(id = len(elementList),level = ilev,labelType = 12,label = namt,contentType = 0,content = Content(itylcm,-1,None,False)))
	  #print "->", ilev, 12, itylcm, ilong, "<-", len(elementList)
	  #print namt
	  if ilong == -1:
	    browseXsm([xsmdid(iplist,namt)],elementList,ilev = ilev+1)
	  else:
	    browseXsm(xsmlid(iplist,namt,ilong),elementList,ilev = ilev+1)
	elif ilong != 0 and itylcm <= 6:
	  content = Content(itylcm,ilong,xsmget(iplist,namt,itylcm),False)
	  if itylcm != 3:
	    content.processed = True
	  elementList.append(LinkedListElement(id = len(elementList),level = ilev,labelType = 12,label = namt,contentType = itylcm,content = content))
	  #print "->", ilev, 12, itylcm, ilong, "<-", len(elementList)
	  #print namt, xsmget(iplist,namt,itylcm)
	namt = xsmnxt(iplist,namt)
	if (namt == first):
	  break

if __name__ == "__main__":
  import sys
  try:
    filePath = sys.argv[1]
  except:
    filePath="/home/melodie/Bureau/xsm_open/XSMCPO_0004"
  elementList = []
  with open(filePath,'rb') as myFile:
    iplist = xsm(myFile)
    browseXsm([iplist],elementList)
  #for e in elementList:
    #print e

