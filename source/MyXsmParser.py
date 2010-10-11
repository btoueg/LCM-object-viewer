#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 10/10/10

#typedef struct Block1 {    /* active directory resident-memory xsm structure */
   #int_32 header;          /* header (=200 for an xsm file) */
   #char hname[13];         /* character*12 name of the xsm file */
   #int_32 listlen;         /* number of elements in the list */
   #int_32 impf;            /* type of access (1:modif or 2:read-only) */
   #int_32 idir;            /* offset of active directory on xsm file */
   #struct Block2 *ibloc;   /* address of block 2 in memory */
   #struct Db1 *icang;      /* address of the database handle */
   #struct Block1 *father;  /* address of the father active directory resident-
                              #memory xsm structure. =0 for root directory. */
   #struct Db2 *icang2;     /* address of the xsmiof database handle */
#} xsm ;

#typedef struct Block2 {   /* active directory resident-memory xsm structure */
   #kdi_file *ifile;       /* xsm (kdi) file handle */
   #int_32 idir;           /* offset of active directory on xsm file */
   #int_32 modif;          /* =1 if the active directory extent have been modified */
   #int_32 ioft;           /* maximum address on xsm file */
   #int_32 nmt;            /* exact number of nodes on the active directory extent */
   #int_32 link;           /* offset of the next directory extent */
   #int_32 iroot;          /* offset of any parent directory extent */
   #char mynam[13];        /* character*12 name of the active directory. ='/' for the root level */
   #int_32 iofs[iofmax];   /* offset list (position of the first element of each block
                             #that belong to the active directory extent) */
   #int_32 jlon[iofmax];   /* length of each record (jlong=0 for a directory) that belong
                             #to the active directory extent */
   #int_32 jtyp[iofmax];   /* type of each block that belong to the active directory extent */
   #char cmt[iofmax][13];  /* list of character*12 names of each block (record or
                             #directory) that belong to the active directory extent */
#} block2 ;

#typedef struct Db1{       /* database handle */
   #int_32 nad;            /* number of addresses in the database */
   #int_32 maxad;          /* maximum slots in the database */
   #xsm **idir;            /* address of the array of pointers */
#} db1 ;

#typedef struct Db2{       /* xsmiof database handle */
   #int_32 nad;            /* number of addresses in the database */
   #int_32 maxad;          /* maximum slots in the database */
   #int_32 ***iref;        /* address of the array of pointers addresses */
   #int_32 **iofset;       /* address of the array of pointers */
   #int_32 *lg;            /* address of the array of lengths */
#} db2 ;

#int_32 kdiget_c(kdi_file *my_file,int_32 *data,int_32 iofset,int_32 length)
#{
  #int_32 irc;
  #offset=iofset*lnword;
  #if (my_file == NULL) {
     #irc = -1;
  #} else if (fseek(my_file->fd,offset,0) >= 0) {
     #int_32 n, iof;
     #irc=0;
     #iof=0;
     #while ((n = fread(&data[iof],lnword,length,my_file->fd)) < length-iof) {
        #if (n < 0) return n-1;
        #iof+=n;
     #}
  #} else {
     #irc = -3;
  #}
  #return irc;
#}

lnword = 8
iwrd = 3

def kdiget_s(myFile,iofset,length=1):
  data = []
  offset = iofset*lnword
  myFile.seek(offset)
  for i in range(length):
    data.append(myFile.read(lnword))
  return data

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
  return data

if __name__ == "__main__":
  import sys
  try:
    filePath = sys.argv[1]
  except:
    filePath="/home/melodie/Bureau/xsm_open/XSMCPO_0004"
  with open(filePath,'rb') as myFile:
    # xsmop
    data = kdiget_s(myFile,0,1)
    print data
    data = kdiget_i(myFile,1)
    print data
    idir = kdiget_i(myFile,2)[0]
    print idir
    ipos = idir
    # xsmdir
    buf = kdiget_s(myFile,ipos)[0]
    ipos += 1
    iofma2 = kdiget_i(myFile,ipos)[0]
    ipos += 1
    nmt = kdiget_i(myFile,ipos)[0]
    ipos += 1
    link = kdiget_i(myFile,ipos)[0]
    ipos += 1
    iroot = kdiget_i(myFile,ipos)[0]
    print buf, iofma2, nmt, link, iroot
    ipos += 1
    data = kdiget_s(myFile,ipos,3)
    print data
    ipos += iwrd
    iofs = kdiget_i(myFile,ipos,nmt)
    ipos += iofma2
    jlon = kdiget_i(myFile,ipos,nmt)
    ipos += iofma2
    jtyp = kdiget_i(myFile,ipos,nmt)
    print iofs, jlon, jtyp
    ipos += iofma2
    for i in range(nmt):
      data = kdiget_s(myFile,ipos,3)
      print data
      ipos += iwrd