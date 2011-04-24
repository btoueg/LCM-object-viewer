#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,types,codecs
from sys import getfilesystemencoding
import ConfigParser

ENCODING=getfilesystemencoding()

CONFIGFILEPATH = os.path.expanduser('~/.lcmviewer.cfg')

CONFIGSECTION='mainconfig'

CONFIG = {
  'splash':True,
  'lastfile':os.path.dirname(__file__)+'/../example/MultiCompoV4',
  'sort':True,
  'expand':True
  }

def loadConfig(cfgFilePath=CONFIGFILEPATH):
  """ load configuration from file """
  if (os.path.isfile(cfgFilePath)):
    cfg = ConfigParser.RawConfigParser()
    try:
      with codecs.open(cfgFilePath, "r", ENCODING) as configFile:
        cfg.readfp(configFile)
      for key,value in CONFIG.items():
	t = type(value)
	if t == types.BooleanType:
	  method = "getboolean"
	elif t ==  types.IntType:
	  method = "getint"
	else:
	  method = "get"
	try:
	  CONFIG[key] = getattr(cfg,method)(CONFIGSECTION,key)
	except ConfigParser.NoOptionError:
	  pass
    except ConfigParser.ParsingError:
      pass
	  
  saveConfig()

def saveConfig(cfgFilePath=CONFIGFILEPATH):
  """ save configuration into a file """
  cfg = ConfigParser.RawConfigParser()
  cfg.add_section(CONFIGSECTION)
  for key,value in CONFIG.items():
    if isinstance( value, basestring ):
      value = value.encode(ENCODING)
    cfg.set(CONFIGSECTION, key, value)
  with open(cfgFilePath, 'wb') as f:
    cfg.write(f)

loadConfig()