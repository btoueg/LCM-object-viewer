#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 10/10/10

lnword = 8
iofmax = 30
maxit = 100
iprim = 3
iwrd = 3
klong = 5+iwrd+(3+iwrd)*iofmax

class xsm:                # active directory resident-memory xsm structure
  def __init__(self):
    # string
    self.hname = ""       # character*12 name of the xsm file
    # int_32
    self.header = 0       # header (=200 for an xsm file)
    self.listlen = 0      # number of elements in the list
    self.impf = 0         # type of access (1:modif or 2:read-only)
    self.idir = 0         # offset of active directory on xsm file
    # Block2
    self.ibloc = None     # address of block 2 in memory
    # Db1
    self.icang = None     # address of the database handle
    # xsm
    self.father = None    # address of the father active directory resident-memory xsm structure. =0 for root directory.
    # Db2
    self.icang2 = None    # address of the xsmiof database handle
  def __str__(self):
    s = "== xsm obj ==\n"
    s += "hname "+str(self.hname)+"\n"
    s += "header "+str(self.header)+"\n"
    s += "listlen "+str(self.listlen)+"\n"
    s += "impf "+str(self.impf)+"\n"
    s += "idir "+str(self.idir)+"\n"
    s += "ibloc\n"+str(self.ibloc)+"\n"
    s += "icang "+str(self.icang)+"\n"
    s += "father "+str(self.father)+"\n"
    s += "icang2\n"+str(self.icang2)+"\n"
    s += "============"
    return s

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
    self.iofs = [0]*iofmax # offset list (position of the first element of each block
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

class Db1:                # database handle
  def __init__(self):
    # int_32
    self.nad = 0          # number of addresses in the database
    self.maxad = 0        # maximum slots in the database
    # xsm
    self.idir = None      # address of the array of pointers
  def __str__(self):
    s =  "== Db1 obj ==\n"
    s += "nad "+str(self.nad)+"\n"
    s += "maxad "+str(self.maxad)+"\n"
    s += "idir "+str(self.idir)+"\n"
    s += "============="
    return s

class Db2:                # xsmiof database handle
  def __init__(self):
    self.nad = 0          # number of addresses in the database
    self.maxad = 0        # maximum slots in the database
    self.iref = None      # address of the array of pointers addresses
    self.iofset = None    # address of the array of pointers
    self.lg = None        # address of the array of lengths
  def __str__(self):
    s =  "== Db2 obj ==\n"
    s += "nad "+str(self.nad)+"\n"
    s += "maxad "+str(self.maxad)+"\n"
    s += "iref "+str(self.iref)+"\n"
    s += "iofset "+str(self.iofset)+"\n"
    s += "lg "+str(self.lg)+"\n"
    s += "============="
    return s

def kdiget_s(myFile,iofset,length=1):
  data = []
  offset = iofset*lnword
  myFile.seek(offset)
  for i in range(length):
    data.append(myFile.read(lnword)[:4])
  return "".join(data)

from scipy.io.numpyio import fwrite, fread

def kdiget_i(myFile,iofset,length=1):
  data = []
  offset = iofset*lnword
  myFile.seek(offset)
  datatype = 'i'
  size = 1
  for i in range(length):
    read_data = fread(myFile, size, datatype)
    for rd in read_data:
      data.append(rd)
  if length == 1:
    data = data.pop()
  return data

def xsmdir(ind, my_block2):
  """
  /*
  *-----------------------------------------------------------------------
  *
  * IMPORT OR EXPORT A DIRECTORY USING THE KDI UTILITY.
  *
  * INPUT PARAMETERS:
  *  IND   : =1 FOR IMPORT ; =2 FOR EXPORT.
  *  MY_BLOCK2 : ADDRESS OF MEMORY-RESIDENT XSM STRUCTURE (BLOCK 2).
  *
  *-----------------------------------------------------------------------
  */
  """
  nomsub = "xsmdir"
  i = j = irc = ibuf = ipos = iofma2 = inom = 0
  iname = [0]*3
  hbuf = ""
  ipos = my_block2.idir
  if ind == 1:
    ibuf = kdiget_s(my_block2.ifile,ipos)
    hbuf = ibuf
    if hbuf[:4] != "$$$$":
      raise Exception
    ipos += 1
    iofma2 = kdiget_i(my_block2.ifile,ipos)
    ipos += 1
    my_block2.nmt = kdiget_i(my_block2.ifile,ipos)
    if my_block2.nmt > iofmax:
      raise Exception
    ipos += 1
    my_block2.link = kdiget_i(my_block2.ifile,ipos)
    ipos += 1
    my_block2.iroot = kdiget_i(my_block2.ifile,ipos)
    ipos += 1
    my_block2.mynam = kdiget_s(my_block2.ifile,ipos,3)
    if my_block2.nmt != 0:
      ipos += iwrd
      my_block2.iofs = kdiget_i(my_block2.ifile,ipos,my_block2.nmt)
      ipos += iofma2
      my_block2.jlon = kdiget_i(my_block2.ifile,ipos,my_block2.nmt)
      ipos += iofma2
      my_block2.jtyp = kdiget_i(my_block2.ifile,ipos,my_block2.nmt)
      ipos += iofma2
      for i in xrange(my_block2.nmt):
	my_block2.cmt.append(kdiget_s(my_block2.ifile,ipos,3))
	ipos += iwrd
  elif ind == 2:
    pass

def xsmop(iplist, namp, imp, impx = 0):
  """
  * OPEN AN EXISTING OR CREATE A NEW XSM FILE. VECTORIAL VERSION.
  *
  * THE XSM DATABASE RESULTS FROM THE JUXTAPOSITION OF A HIERARCHICAL
  * LOGICAL STRUCTURE INTO A DIRECT ACCESS FILE WITH FIXE LENGTH RECORDS.
  * THE DIRECT ACCESS FILE IS FORTRAN-77 COMPATIBLE AND IS MANAGED BY
  * KDIGET/PUT/CL. XSMOP/PUT/GET/LEN/VEC/NXT/CL ENTRIES PROVIDE A SET OF
  * METHODS TO ACCESS A XSM FILE.
  *
  * THE LOGICAL STRUCTURE OF A XSM FILE IS MADE OF A ROOT DIRECTORY FOL-
  * LOWED BY VARIABLE-LENGTH BLOCKS CONTAINING THE USEFUL INFORMATION.
  * EACH TIME A DIRECTORY IS FULL, AN EXTENT IS AUTOMATICALLY CREATED AT
  * THE END OF THE FILE, SO THAT THE TOTAL NUMBER OF BLOCKS IN A DIREC-
  * TORY IS ONLY LIMITED BY THE MAXIMUM SIZE OF THE DIRECT ACCESS FILE.
  * ANY BLOCK CAN CONTAIN A SUB-DIRECTORY IN ORDER TO CREATE A HIERAR-
  * CHICAL STRUCTURE.
  *
  * INPUT PARAMETERS:
  *    NAMP : CHARACTER*12 NAME OF THE XSM FILE.
  *     IMP : TYPE OF ACCESS.  =0: NEW FILE MODE;
  *                            =1: MODIFICATION MODE;
  *                            =2: READ ONLY MODE.
  *    IMPX : IF IMPX=0, WE SUPPRESS PRINTING ON XSMOP.
  *
  * OUTPUT PARAMETERS:
  *  IPLIST : ADDRESS OF THE HANDLE TO THE XSM FILE.
  *    NAMP : CHARACTER*12 NAME OF THE XSM FILE IF IMP=1 OR IMP=2.
  *
  * THE ACTIVE DIRECTORY IS MADE OF TWO BLOCKS LINKED TOGETHER. A BLOCK 1
  * IS ALLOCATED FOR EACH SCALAR DIRECTORY OR VECTOR DIRECTORY COMPONENT.
  * BLOCK 2 IS UNIQUE FOR A GIVEN XSM FILE; EVERY BLOCK 1 IS POINTING TO
  * THE SAME BLOCK 2.
  """
  nomsub = "xsmop_c"
  irc = ibuf = inom = 0
  hbuf = ""
  my_block2 = Block2()
  my_db1 = Db1()
  my_db2 = Db2()
  iplist.icang2 = my_db2
  iplist.header = 200
  iplist.listlen = -1
  iplist.impf = imp
  iplist.ibloc = my_block2
  iplist.father = None
  iplist.hname = namp
  my_block2.ifile = open(namp,'rb')
  if impx > 1:
    print "toto"
  if imp >= 1:
    # RECOVER THE ROOT DIRECTORY IF THE XSM FILE ALREADY EXISTS
    ibuf = kdiget_s(my_block2.ifile,0)
    hbuf = ibuf
    if hbuf[:4] != "$XSM":
      raise Exception
    my_block2.ioft = kdiget_i(my_block2.ifile,1)
    my_block2.idir = kdiget_i(my_block2.ifile,2)
    iplist.idir = my_block2.idir
    xsmdir(1,my_block2)
    my_block2.modif = 0
    if impx > 0:
      pass
      #print ("%s: XSM FILE RECOVERY. FILE = '%s'.\n",nomsub,namp);
      #print ("%6s HIGHEST ATTAINABLE ADDRESS = %d\n"," ",my_block2->ioft);
      #print ("%6s ACTIVE DIRECTORY = %s\n"," ",my_block2->mynam);

def xsmrep(namt, ind, idir, my_block2):
  """
  *-----------------------------------------------------------------------
  *
  * FIND A BLOCK (RECORD OR DIRECTORY) POSITION IN THE ACTIVE DIRECTORY
  * AND RELATED EXTENTS.
  *
  * INPUT PARAMETERS:
  *  NAMT   : CHARACTER*12 NAME OF THE REQUIRED BLOCK.
  *  IND    : =1 SEARCH NAMT ; =2 SEARCH AND POSITIONNING IN AN EMPTY
  *           SLOT OF THE ACTIVE DIRECTORY IF NAMT DOES NOT EXISTS.
  *  IDIR   : OFFSET OF ACTIVE DIRECTORY ON XSM FILE.
  *  MY_BLOCK2 : ADDRESS OF MEMORY-RESIDENT XSM STRUCTURE (BLOCK 2).
  *
  * OUTPUT PARAMETER:
  *  III    : RETURN CODE. =0 IF THE BLOCK NAMED NAMT DOES NOT EXISTS;
  *           =POSITION IN THE ACTIVE DIRECTORY EXTENT IF NAMT EXTSTS.
  *           =0 OR 1 IF NAMT=' '.
  *
  *-----------------------------------------------------------------------
  """
  nomsub="xsmrep"
  i = ipos = ipos2 = irc = irc2 = istart = 0
  namp = nomC = ""
  if my_block2.idir != idir:
    # SWITCH TO THE CORRECT ACTIVE DIRECTORY (BLOCK 2)
    if (my_block2.modif == 1):
      xsmdir(2, my_block2)
    my_block2.idir = idir
    xsmdir(1, my_block2)
  if namt == "***HANDLE***":
    raise Exception
  namp = namt
  if namp == " ":
    namp = "***HANDLE***"
  ipos = -1
  if (my_block2.nmt < iofmax):
    ipos = my_block2.idir
  if (my_block2.nmt == 0):
    pass # goto L50
  if namp in my_block2.cmt:
    # THE BLOCK ALREADY EXISTS
    return
  # THE BLOCK NAMP DOES NOT EXISTS IN THE ACTIVE DIRECTORY EXTENT. WE
  # SEARCH IN OTHER EXTENTS THAT BELONG TO THE ACTIVE DIRECTORY.
  if (my_block2.idir != my_block2.link):
    # RECOVER A NEW DIRECTORY EXTENT. */
    istart = my_block2.link
    if (my_block2.modif == 1):
      xsmdir(2, my_block2)
    my_block2.idir = istart
    while True:
      xsmdir(1, my_block2)
      if (my_block2.nmt < iofmax):
	ipos = my_block2.idir
      if namp in my_block2.cmt:
	# THE BLOCK NAMP WAS FOUND IN THE ACTIVE DIRECTORY EXTENT
	return my_block2.cmt.index(namp)
      if (my_block2.link == istart):
	break
      my_block2.idir = my_block2.link
  return 0

def xsmget(iplist, namp):
  """
  *-----------------------------------------------------------------------
  *
  * COPY A BLOCK FROM THE XSM FILE INTO MEMORY.
  *
  * INPUT PARAMETERS:
  *  IPLIST : ADDRESS OF THE HANDLE TO THE XSM FILE.
  *   NAMP  : CHARACTER*12 NAME OF THE CURRENT BLOCK.
  *
  * OUTPUT PARAMETER:
  *   DATA2 : INFORMATION ELEMENTS. DIMENSION DATA2(ILONG)
  *
  *-----------------------------------------------------------------------
  """
  nomsub="xsmget_c"
  nomC = ""
  my_block2 = Block2()
  iii = irc = 0
  if iplist.header != 200:
    raise Exception
  my_block2=iplist.ibloc
  iii = xsmrep(namp, 1, iplist.idir, my_block2)
  if iii > 0:
    data2 = kdiget_c(my_block2.ifile, my_block2.iofs[iii], my_block2.jlon[iii])
  return data2

def xsmnxt(iplist, namp):
  

if __name__ == "__main__":
  import sys
  try:
    filePath = sys.argv[1]
  except:
    filePath="/home/melodie/Bureau/xsm_open/XSMCPO_0004"
  iplist = xsm()
  xsmop(iplist,filePath,2)
  print iplist
