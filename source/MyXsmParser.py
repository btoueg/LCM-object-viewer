#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 10/10/10

from copy import copy

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
    if self.father != None:
      s += "father "+str(self.father.ibloc.mynam)+"\n"
    else:
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
  for i in xrange(length):
    data.append(myFile.read(lnword)[:4])
  return "".join(data)

from scipy.io.numpyio import fwrite, fread

def kdiget_i(myFile,iofset,length=1, datatype = 'l'):
  data = []
  offset = iofset*lnword
  myFile.seek(offset)
  size = 1
  for i in xrange(length):
    read_data = fread(myFile, size, datatype)
    for rd in read_data:
      data.append(rd)
  #if length == 1:
    #data = data.pop()
  return data

#def xsmkep(ipkeep, imode, iplist):
  #"""
  #*-----------------------------------------------------------------------
  #*
  #* KEEP THE ADDRESSES OF THE OPEN ACTIVE DIRECTORIES.
  #*
  #* INPUT PARAMETERS:
  #*  IPKEEP : ADDRESS OF THE DATABASE HANDLE (ALWAYS THE SAME).
  #*  IMODE  : =1: ADD TO THE DATABASE; =2: REMOVE FROM THE DATABASE.
  #*  IPLIST : ADDRESS OF AN ACTIVE DIRECTORY.
  #*
  #* OUTPUT PARAMETER:
  #*  IPLIST : LAST ACTIVE DIRECTORY IN THE DATABASE. =0 IF THE
  #*           DATABASE IS EMPTY.
  #*
  #* DATABASE HANDLE STRUCTURE:
  #*  0 : NUMBER OF ADDRESSES IN THE DATABASE.
  #*  1 : MAXIMUM SLOTS IN THE DATABASE.
  #*  2 : ADDRESS OF THE DATABASE.
  #*
  #*-----------------------------------------------------------------------
  #"""
  #n = ipkeep.nad
  #if (imode == 1):
    #int_32 i;
    #xsm **my_parray;
    #if iplist.header != 200:
      #raise AssertionError("THE XSM FILE '%s' HAS THE WRONG HEADER."%iplist.hname)
    #elif (ipkeep.nad + 1 > ipkeep.maxad):
      #ipkeep.maxad += maxit
      #my_parray = (xsm **) malloc((ipkeep->maxad)*sizeof(i));
      #for (i = 0; i < n; ++i) my_parray[i]=ipkeep->idir[i];
      #if (n > 0):
	#free(ipkeep.idir)
      #ipkeep.idir=my_parray
    #++ipkeep->nad;
    #ipkeep.idir[n] = iplist
  #elif (imode == 2):
    
    #int_32 i, i0;
    #for (i = n; i >= 1; --i) {
	#if (ipkeep->idir[i-1] == *iplist) {
	  #i0 = i;
	  #goto L30;
	#}
    #}
    #sprintf(AbortString,"%s: UNABLE TO FIND AN ADDRESS.",nomsub);
    #xabort_c(AbortString);
  #L30:
      #for (i = i0; i <= n-1; ++i)
	  #ipkeep->idir[i-1]=ipkeep->idir[i];
      #--ipkeep->nad;
      #if (ipkeep->nad == 0) {
	  #*iplist = NULL;
	  #free(ipkeep->idir);
	  #ipkeep->maxad=0;
	  #ipkeep->idir=NULL;
      #} else {
	  #*iplist = ipkeep->idir[n-1];
	  #if ((*iplist)->header != 200) {
	    #sprintf(AbortString,"%s: WRONG HEADER(2).",nomsub);
	    #xabort_c(AbortString);
	  #}
      #}
  #else:
    #raise AssertionError("INVALID VALUE OF IMODE.")
  #return iplist

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
  ipos = my_block2.idir
  if ind == 1:
    hbuf = kdiget_s(my_block2.ifile,ipos)
    if hbuf[:4] != "$$$$":
      raise AssertionError("UNABLE TO RECOVER DIRECTORY.")
    ipos += 1
    iofma2 = kdiget_i(my_block2.ifile,ipos).pop()
    ipos += 1
    my_block2.nmt = kdiget_i(my_block2.ifile,ipos).pop()
    if my_block2.nmt > iofmax:
      raise AssertionError("UNABLE TO RECOVER DIRECTORY.")
    ipos += 1
    my_block2.link = kdiget_i(my_block2.ifile,ipos).pop()
    ipos += 1
    my_block2.iroot = kdiget_i(my_block2.ifile,ipos).pop()
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
      my_block2.cmt = []
      for i in xrange(my_block2.nmt):
	my_block2.cmt.append(kdiget_s(my_block2.ifile,ipos,3))
	ipos += iwrd
  elif ind == 2:
    raise AssertionError()

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
  my_block2 = Block2()
  iplist.icang = Db1()
  iplist.icang2 = Db2()
  iplist.header = 200
  iplist.listlen = -1
  iplist.impf = imp
  iplist.ibloc = my_block2
  iplist.father = None
  iplist.hname = namp
  my_block2.ifile = open(namp,'rb')
  if imp >= 1:
    # RECOVER THE ROOT DIRECTORY IF THE XSM FILE ALREADY EXISTS
    hbuf = kdiget_s(my_block2.ifile,0)
    if hbuf[:4] != "$XSM":
      raise AssertionError("WRONG HEADER ON XSM FILE '%s'."%namp)
    my_block2.ioft = kdiget_i(my_block2.ifile,1).pop()
    my_block2.idir = kdiget_i(my_block2.ifile,2).pop()
    iplist.idir = my_block2.idir
    xsmdir(1,my_block2)
    my_block2.modif = 0
    if impx > 0:
      pass
      #print ("%s: XSM FILE RECOVERY. FILE = '%s'.\n",nomsub,namp);
      #print ("%6s HIGHEST ATTAINABLE ADDRESS = %d\n"," ",my_block2.ioft);
      #print ("%6s ACTIVE DIRECTORY = %s\n"," ",my_block2.mynam);
  else:
    raise AssertionError()

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
  i = ipos = ipos2 = irc = irc2 = 0
  if my_block2.idir != idir:
    # SWITCH TO THE CORRECT ACTIVE DIRECTORY (BLOCK 2)
    if (my_block2.modif == 1):
      xsmdir(2, my_block2)
    my_block2.idir = idir
    xsmdir(1, my_block2)
  if namt == "***HANDLE***":
    raise AssertionError("***HANDLE*** IS A RESERVED KEYWORD.")
  namp = namt
  if namp == " ":
    namp = "***HANDLE***"
  ipos = -1
  if (my_block2.nmt < iofmax):
    ipos = my_block2.idir
  if (my_block2.nmt == 0):
    raise AssertionError()
  if namp in my_block2.cmt:
    # THE BLOCK ALREADY EXISTS
    return my_block2.cmt.index(namp)
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
  return -1

def xsmget(iplist, namp, itylcm = 1):
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
  if iplist.header != 200:
    raise AssertionError("THE XSM FILE '%s' HAS THE WRONG HEADER."%iplist.hname)
  my_block2=iplist.ibloc
  iii = xsmrep(namp, 1, iplist.idir, my_block2)
  if iii >= 0:
    if itylcm == 1:
      data2 = kdiget_i(my_block2.ifile, my_block2.iofs[iii], my_block2.jlon[iii])
    elif itylcm == 3:
      data2 = kdiget_s(my_block2.ifile, my_block2.iofs[iii], my_block2.jlon[iii])
    else:
      data2 = kdiget_i(my_block2.ifile, my_block2.iofs[iii], my_block2.jlon[iii], 'd')
  else:
    raise AssertionError("UNABLE TO FIND BLOCK '%s' INTO DIRECTORY '%s' IN THE XSM FILE '%s'."%(namp,my_block2.mynam,iplist.hname))
  return data2

def xsmnxt(iplist,namp = " "):
  """
  *-----------------------------------------------------------------------
  *
  * FIND THE NAME OF THE NEXT BLOCK STORED IN THE ACTIVE DIRECTORY.
  *
  * INPUT PARAMETERS:
  *  IPLIST : ADDRESS OF THE HANDLE TO THE XSM FILE.
  *    NAMP : CHARACTER*12 NAME OF A BLOCK. IF NAMP=' ' AT INPUT, FIND
  *           ANY NAME FOR ANY BLOCK STORED IN THIS DIRECTORY.
  *
  * OUTPUT PARAMETERS:
  *    NAMP : CHARACTER*12 NAME OF THE NEXT BLOCK. NAMP=' ' FOR AN EMPTY
  *           DIRECTORY.
  *
  *-----------------------------------------------------------------------
  """
  iii = 0
  if (iplist.header != 200):
    raise AssertionError("THE XSM FILE '%s' HAS THE WRONG HEADER."%iplist.hname)
  my_block2 = iplist.ibloc
  if namp == " ":
    if my_block2.idir != iplist.idir:
      #SWITCH TO THE CORRECT ACTIVE DIRECTORY (BLOCK 2)
      if (my_block2.modif == 1):
	xsmdir(2, my_block2)
      my_block2.idir = iplist.idir
      xsmdir(1, my_block2)
    iii = min(my_block2.nmt,0)
  else:
    iii = xsmrep(namp, 1, iplist.idir, my_block2)+1
  if iii == -1 and namp == " ":
    #EMPTY DIRECTORY
    raise AssertionError("THE ACTIVE DIRECTORY '%s' OF THE XSM FILE '%s' IS EMPTY."%(my_block2.mynam,iplist.hname))
  elif iii == -1:
    raise AssertionError("UNABLE TO FIND BLOCK '%s' INTO DIRECTORY '%s' IN THE XSM FILE '%s'."%(namp,my_block2.mynam,iplist.hname))
  elif iii < my_block2.nmt:
    namp = my_block2.cmt[iii]
    return namp
  #SWITCH TO THE NEXT DIRECTORY.
  if my_block2.idir != my_block2.link:
    if my_block2.modif == 1:
      xsmdir(2, my_block2)
    my_block2.idir = my_block2.link
    #RECOVER THE NEXT DIRECTORY.
    xsmdir(1, my_block2)
  namp = my_block2.cmt[0]
  if (namp == "***HANDLE***"):
    namp = " "
  return namp

def xsmlen(iplist, namp):
  """
  *-----------------------------------------------------------------------
  *
  * RETURN THE LENGTH AND TYPE OF A BLOCK. RETURN 0 IF THE BLOCK DOES NOT
  * EXISTS.
  *
  * INPUT PARAMETERS:
  *  IPLIST : ADDRESS OF THE HANDLE TO THE XSM FILE.
  *   NAMP  : CHARACTER*12 NAME OF THE CURRENT BLOCK.
  * OUTPUT PARAMETERS:
  *   ILONG : NUMBER OF INFORMATION ELEMENTS STORED IN THE CURRENT BLOCK.
  *           ILONG=-1 IS RETURNED FOR A SCALAR DIRECTORY.
  *           ILONG=0 IF THE BLOCK DOES NOT EXISTS.
  *   ITYPE : TYPE OF INFORMATION ELEMENTS STORED IN THE CURRENT BLOCK.
  *           0: DIRECTORY                1: INTEGER
  *           2: SINGLE PRECISION         3: CHARACTER*4
  *           4: DOUBLE PRECISION         5: LOGICAL
  *           6: COMPLEX                 99: UNDEFINED
  *
  *-----------------------------------------------------------------------
  """
  if (iplist.header != 200):
    raise AssertionError("THE XSM FILE '%s' HAS THE WRONG HEADER."%iplist.hname)
  my_block2=iplist.ibloc
  iii = xsmrep(namp, 1, iplist.idir, my_block2)
  if (iii >= 0):
    ilong = my_block2.jlon[iii]
    itype = my_block2.jtyp[iii]
  else:
    ilong = 0
    itype = 99
  return ilong, itype

def xsminf(iplist):
  """
  *-----------------------------------------------------------------------
  *
  * RECOVER GLOBAL INFORMATIONS RELATED TO AN XSM FILE.
  *
  * INPUT PARAMETERS:
  *  IPLIST : ADDRESS OF THE HANDLE TO THE XSM FILE.
  *
  * OUTPUT PARAMETERS:
  *  NAMXSM : CHARACTER*12 NAME OF THE XSM FILE.
  *   NAMMY : CHARECTER*12 NAME OF THE ACTIVE DIRECTORY.
  *   EMPTY : =.TRUE. IF THE ACTIVE DIRECTORY IS EMPTY.
  *   ILONG : =-1: FOR A TABLE; >0: NUMBER OF LIST ITEMS.
  *  ACCESS : TYPE OF ACCESS. =1: OBJECT OPEN FOR MODIFICATION;
  *           =2: OBJECT IN READ-ONLY MODE.
  *
  *-----------------------------------------------------------------------
  """
  if (iplist.header != 200):
    raise AssertionError("THE XSM FILE '%s' HAS THE WRONG HEADER."%iplist.hname)
  my_block2=iplist.ibloc
  if (my_block2.idir != iplist.idir):
    # SWITCH TO THE CORRECT ACTIVE DIRECTORY (BLOCK 2)
    if (my_block2.modif == 1):
      xsmdir(2, my_block2)
    my_block2.idir = iplist.idir
    xsmdir(1, my_block2)
  namxsm = iplist.hname
  nammy = my_block2.mynam
  empty = (my_block2.nmt == 0)
  ilong = iplist.listlen
  access = iplist.impf
  return namxsm, nammy, empty, ilong, access

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
    #if (iplist.impf == 2):
      #raise AssertionError("THE XSM FILE '%s' IS OPEN IN READ-ONLY MODE."%iplist.hname)
    #my_block2.jlon[iii-1] = -1
    #my_block2.jtyp[iii-1] = 0
    #my_block2.iofs[iii-1] = my_block2.ioft
    #idir = my_block2.iofs[iii-1]
    #my_block2.ioft += klong
    #xsmdir(2, my_block2)
    #my_block2.iroot = my_block2.idir
    #my_block2.mynam = namp
    #my_block2.idir = my_block2.iofs[iii-1]
    #my_block2.nmt = 0
    #my_block2.link = my_block2.idir
    #my_block2.modif = 1
  elif (lenold == -1 and ityold == 0):
    idir = my_block2.iofs[iii]
  else:
    raise AssertionError("BLOCK '%s' IS NOT AN ASSOCIATIVE TABLE OF THE XSM FILE '%s'."%(namp,iplist.hname))

  #COPY BLOCK1
  jplist = copy(iplist)
  jplist.listlen = -1
  jplist.idir  = idir
  jplist.father = iplist
  #xsmkep(iplist.icang, 1, jplist)
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
    #if (iplist.impf != 2):
      #raise AssertionError("THE XSM FILE '%s' IS OPEN IN READ-ONLY MODE."%iplist.hname)
    #my_block2.jlon[iii-1] = ilong
    #my_block2.jtyp[iii-1] = 10
    #idiold = my_block2.iofs[iii-1]
    #my_block2.iofs[iii-1] = my_block2.ioft
    #idir = my_block2.iofs[iii-1]
    #my_block2.ioft += ilong
    #iroold = my_block2.idir
    #xsmdir(&c__2, my_block2)
    #if (lenold > 0):
      #iivec = kdiget_c(my_block2.ifile, idiold, lenold)
    #for i in xrange(abs(lenold) + 1, ilong + 1):
    ##for (i = abs(lenold) + 1; i <= ilong; ++i) {
      #iivec[i-1] = my_block2.ioft
      #my_block2.iroot = iroold
      #my_block2.mynam = namp
      #my_block2.nmt = 0
      #my_block2.idir = my_block2.ioft
      #my_block2.ioft += klong
      #my_block2.link = my_block2.idir
      #xsmdir(2, my_block2)
    #irc = kdiput_c(my_block2.ifile, iivec, idir, ilong)
  elif (lenold == ilong and ityold == 10):
    idir = my_block2.iofs[iii]
  elif (ityold != 10):
    raise AssertionError("BLOCK '%s' IS NOT A LIST OF THE XSM FILE '%s'."%(namp,iplist.hname))
  else:
    raise AssertionError("THE LIST '%s' OF THE XSM FILE '%s' HAVE AN INVALID LENGTH (%d)."%(namp,iplist.hname,ilong))
  iivec = kdiget_i(my_block2.ifile, idir, ilong)
  jplist = []
  for ivec in iivec:
    #COPY BLOCK1
    iofset = copy(iplist)
    iofset.listlen = 0
    iofset.idir = ivec
    iofset.father = iplist
    #iofset.header = iplist.header
    #iofset.hname = iplist.hname
    #iofset.listlen = 0
    #iofset.impf = iplist.impf
    #iofset.idir = ivec
    #iofset.ibloc = iplist.ibloc
    #iofset.icang = iplist.icang
    #iofset.icang2 = iplist.icang2
    #iofset.father = iplist
    jplist.append(iofset)
  #xsmkep(iplist.icang, 1, jplist)
  return jplist

def xsmgid(iplist, namp):
  """
  *-----------------------------------------------------------------------
  *
  * GET THE ADDRESS OF A TABLE OR OF A LIST LOCATED IN A FATHER TABLE.
  *
  * INPUT PARAMETERS:
  *  IPLIST : ADDRESS OF THE FATHER TABLE.
  *    NAMP : CHARACTER*12 NAME OF THE SON TABLE OR LIST.
  *
  * OUTPUT PARAMETER:
  *  lcmgid_c : ADDRESS OF THE TABLE OR OF THE LIST NAMED NAMP.
  *
  *-----------------------------------------------------------------------
  """
  ilong,itylcm = xsmlen(iplist,namp)
  if (ilong == -1):
    jplist = [xsmdid(iplist,namp)]
  else:
    jplist = xsmlid(iplist,namp,ilong)
  return jplist

if __name__ == "__main__":
  import sys
  try:
    filePath = sys.argv[1]
  except:
    filePath="/home/melodie/Bureau/xsm_open/XSMCPO_0004"
  iplist = xsm()
  xsmop(iplist,filePath,2)

  maxlev = 50

  def browseXsm(iplist_list,ilev=0):
    for iplist in iplist_list:
      if ilev >= maxlev:
	raise AssertionError("TOO MANY DIRECTORY LEVELS ON "+namxsm)
      namxsm, myname, empty, ilong, lcm = xsminf(iplist)
      print myname, ilev, ilong
      if empty:
	break
      namt = xsmnxt(iplist)
      if "***HANDLE***" == namt:
	ilong,itylcm = xsmlen(iplist," ")
	browseXsm(xsmgid(iplist," "),ilev = ilev+1)
      else:
	first = namt
	while True:
	  ilong,itylcm = xsmlen(iplist,namt)
	  if ilong != 0 and ( itylcm == 0 or itylcm == 10 ):
	    browseXsm(xsmgid(iplist,namt),ilev = ilev+1)
	  elif ilong != 0 and itylcm <= 6:
	    print namt, ilong, xsmget(iplist,namt,itylcm)
	  namt = xsmnxt(iplist,namt)
	  if (namt == first):
	    break
  browseXsm([iplist])

