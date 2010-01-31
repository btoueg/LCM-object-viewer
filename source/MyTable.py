# -*- Coding : UTF-8 -*-

import wx
from wx.grid import PyGridTableBase

class MyTableColumn(wx.grid.PyGridTableBase):
  def __init__(self,label,contentList):
    wx.grid.PyGridTableBase.__init__(self)
    self.nRow = len(contentList)
    self.nCol = 1
    self.contentList = contentList
    self.rowLabels = [ str(i) for i in range(1,self.nRow+1) ]
    self.colLabels = [label]

  def GetNumberRows(self):
    return self.nRow

  def GetNumberCols(self):
    return self.nCol

  def IsEmptyCell(self, row, col):
    return False

  def GetValue(self, row, col):
    return self.contentList[row]

  def SetValue(self, row, col, value):
    pass

  def GetColLabelValue(self, col):
    return self.colLabels[col]

  def GetRowLabelValue(self, row):
    return self.rowLabels[row]

class MyCalculationTable(wx.grid.PyGridTableBase):
  def __init__(self,row,colLabels):
    wx.grid.PyGridTableBase.__init__(self)
    self.nRow = len(row)
    self.nCol = len(row[0])
    self.row = row
    self.rowLabels = [ str(i) for i in range(1,self.nRow+1) ]
    self.colLabels = colLabels

  def GetNumberRows(self):
    return self.nRow

  def GetNumberCols(self):
    return self.nCol

  def IsEmptyCell(self, row, col):
    return False

  def GetValue(self, iRow, iCol):
    return self.row[iRow][iCol]

  def SetValue(self, row, col, value):
    pass

  def GetColLabelValue(self, col):
    return self.colLabels[col]

  def GetRowLabelValue(self, row):
    return self.rowLabels[row]