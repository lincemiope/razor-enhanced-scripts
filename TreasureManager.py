#===============================================#
#                   SOS Manager                 #
#===============================================#
#                                               #
#   Author: CookieLover                         #
#   Latest Release: 10/07/2017                  #
#                                               #
#===============================================#
#                                               #
#   Info:                                       #
#   - by selecting a SOS and hitting Move       #
#     all the SOS in that sector will be moved  #
#     in the targeted container                 #
#                                               #
#   What you need:                              #
#   - a bag full of SOS                         #
#                                               #
#   Credits:                                    #
#   the degrees - coordinates formula is taken  #   
#   from Enhanced Map                           #
#                                               #
#===============================================#




import clr, math

clr.AddReference('System')
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Data')

import System
from System.Collections.Generic import List
from System.Drawing import Point, Color, Size
from System.Windows.Forms import (Application, Button, Form, BorderStyle, 
    Label, FlatStyle, DataGridView, DataGridViewAutoSizeColumnsMode,
    DataGridViewSelectionMode, DataGridViewEditMode, CheckBox)
from System.Data import DataTable

class Treasure(object):
    def __init__(self, _serial, _x, _y, distance=0):
        
        self.serial = _serial
        self.x = _x
        self.y = _y
        self.distance = distance
        
class TreasureManager(Form):
    curVer = '1.0.1'
    scriptName = 'Treasure Manager'
    base_btn_offset = (20, 328)
    treasureMaps = []
    
    def __init__(self, bag):
        self.treasureMapsBag = bag
        self.mapCatalogue()

        self.BackColor = Color.FromArgb(25,25,25)
        self.ForeColor = Color.FromArgb(231,231,231)
        self.Size = Size(270, 444)
        self.Text = '{0} - v{1}'.format(self.scriptName, self.curVer)

        self.DataGridSetup()

        self.btnDig = Button()
        self.btnDig.Text = 'Fish'
        self.btnDig.BackColor = Color.FromArgb(50,50,50)
        self.btnDig.Location = self.btn_pos(1, 1)
        self.btnDig.Size = Size(60, 30)
        self.btnDig.FlatStyle = FlatStyle.Flat
        self.btnDig.FlatAppearance.BorderSize = 1
        self.btnDig.Click += self.btnDigPressed

        self.btnMarker = Button()
        self.btnMarker.Text = 'Marker'
        self.btnMarker.BackColor = Color.FromArgb(50,50,50)
        self.btnMarker.Location = self.btn_pos(0, 1)
        self.btnMarker.Size = Size(60, 30)
        self.btnMarker.FlatStyle = FlatStyle.Flat
        self.btnMarker.FlatAppearance.BorderSize = 1
        self.btnMarker.Click += self.btnMarkerPressed

        self.btnRemove = Button()
        self.btnRemove.Text = 'Remove'
        self.btnRemove.BackColor = Color.FromArgb(50,50,50)
        self.btnRemove.Location = self.btn_pos(2)
        self.btnRemove.Size = Size(60, 30)
        self.btnRemove.FlatStyle = FlatStyle.Flat
        self.btnRemove.FlatAppearance.BorderSize = 1
        self.btnRemove.Click += self.btnRemovePressed

        self.btnMove = Button()
        self.btnMove.Text = 'Move'
        self.btnMove.BackColor = Color.FromArgb(50,50,50)
        self.btnMove.Location = self.btn_pos(1)
        self.btnMove.Size = Size(60, 30)
        self.btnMove.FlatStyle = FlatStyle.Flat
        self.btnMove.FlatAppearance.BorderSize = 1
        self.btnMove.Click += self.btnMovePressed

        self.btnOpen = Button()
        self.btnOpen.Text = 'Open'
        self.btnOpen.BackColor = Color.FromArgb(50,50,50)
        self.btnOpen.Location = self.btn_pos(0)
        self.btnOpen.Size = Size(60, 30)
        self.btnOpen.FlatStyle = FlatStyle.Flat
        self.btnOpen.FlatAppearance.BorderSize = 1
        self.btnOpen.Click += self.btnOpenPressed

        self.Controls.Add(self.DataGrid)
        self.Controls.Add(self.btnOpen)
        self.Controls.Add(self.btnMove)
        self.Controls.Add(self.btnRemove)
        self.Controls.Add(self.btnMarker)
        self.Controls.Add(self.btnDig)

        self.TopMost = True

    def btn_pos(self, xidx, yidx=0):
        _x = self.base_btn_offset[0] + xidx * 70
        _y = self.base_btn_offset[1] + yidx * 40
        return Point(_x, _y)

    def DataGridSetup(self):
        self.DataGrid = DataGridView()
        self.DataGrid.RowHeadersVisible = False
        self.DataGrid.MultiSelect = False
        self.DataGrid.SelectionMode = DataGridViewSelectionMode.FullRowSelect
        self.DataGrid.BackgroundColor = Color.FromArgb(25,25,25)
        self.DataGrid.RowsDefaultCellStyle.BackColor = Color.Silver
        self.DataGrid.AlternatingRowsDefaultCellStyle.BackColor = Color.Gainsboro
        self.DataGrid.ForeColor = Color.FromArgb(25,25,25)
        self.DataGrid.Location = Point(20, 12)
        self.DataGrid.Size = Size(230, 306)
        self.DataGrid.DataSource = self.Data()
        self.DataGrid.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.AllCells
        self.DataGrid.EditMode = DataGridViewEditMode.EditProgrammatically
        self.DataGrid.BorderStyle = BorderStyle.None
     
    def btnOpenPressed(self, sender, args):
        row = self.DataGrid.SelectedCells[0].RowIndex
        
        if row == -1:
            Misc.SendMessage('{0}: No row selected.'.format(self.scriptName), 33)
            return
            
        col = self.DataGrid.SelectedCells[0].ColumnIndex
        serial = self.DataGrid.Rows[row].Cells[col].Value
        
        Items.UseItem(int(serial, 0))

    def btnDigPressed(self, sender, args):
        row = self.DataGrid.SelectedCells[0].RowIndex
        
        if row == -1:
            Misc.SendMessage('{0}: No row selected.'.format(self.scriptName), 33)
            return

        serial = int(self.DataGrid.Rows[row].Cells[0].Value)
        x = int(self.DataGrid.Rows[row].Cells[1].Value)
        y = int(self.DataGrid.Rows[row].Cells[2].Value)

        Misc.WaitForContext(serial, 9000)
        Misc.ContextReply(serial, 1) # TODO: controllare il gump per la risposta corretta
        Target.WaitForTarget(6000)
        Target.TargetExecute(x, y, Player.Position.Z)

    def btnMarkerPressed(self, sender, args):
        row = self.DataGrid.SelectedCells[0].RowIndex
        
        if row == -1:
            Misc.SendMessage('{0}: No row selected.'.format(self.scriptName), 33)
            return

        x = str(self.DataGrid.Rows[row].Cells[1].Value)
        y = str(self.DataGrid.Rows[row].Cells[2].Value)

        Misc.SendToClient('--addmarker %s %s' % (x, y))

    def btnMovePressed(self, sender, args):
        row = self.DataGrid.SelectedCells[0].RowIndex
        
        if row == -1:
            Misc.SendMessage('{0}: No row selected.'.format(self.scriptName), 33)
            return
            
        col = self.DataGrid.SelectedCells[3].ColumnIndex
        sector = self.DataGrid.Rows[row].Cells[col].Value
        Misc.SendMessage('{0}: Select the bag in which to put the map.'.format(self.scriptName), 67)
        bag = Target.PromptTarget()
        if bag == -1:
            Misc.SendMessage('{0}: No bag selected.'.format(self.scriptName), 33) 
        Misc.SendMessage('{0}: Please wait until the process is complete.'.format(self.scriptName), 67)
        self.MoveAll(sector, bag)
        
        
    def btnRemovePressed(self, sender, args):
        row = self.DataGrid.SelectedCells[0].RowIndex
        
        if row == -1:
            Misc.SendMessage('{0}: No row selected.'.format(self.scriptName), 33)
            return
            
        col = self.DataGrid.SelectedCells[0].ColumnIndex
        serial = self.DataGrid.Rows[row].Cells[col].Value
        
        self.DeleteRow(serial)
    
    def MoveAll(self, sector, bag):
        rows = []
        for r in xrange(self.DataGrid.DataSource.Rows.Count):
            row = self.DataGrid.DataSource.Rows[r]
            
            if row['Sector'] == sector:
                Items.Move(int(row['ID'], 0), bag, 0)
                rows.append(row)
                Misc.Pause(600)
                
        for r in rows:
            self.DataGrid.DataSource.Rows.Remove(r)
            
        Misc.SendMessage('{0}: Moving process complete.'.format(self.scriptName), 67)
                
    def DeleteRow(self, serial):
        for r in xrange(self.DataGrid.DataSource.Rows.Count):
            row = self.DataGrid.DataSource.Rows[r]
            if row['ID'] == serial:
                self.DataGrid.DataSource.Rows.Remove(row)
                return

    def getPointsDistance(self, x, y):
        _x = abs(Player.Position.X - x) ** 2
        _y = abs(Player.Position.Y - y) ** 2
        if _x == 0 and _y == 0:
            return 0
        return int(math.sqrt(_x + _y))
        
    def Data(self):
        data = DataTable()
        data.Columns.Add('ID', clr.GetClrType(str))
        data.Columns.Add('X', clr.GetClrType(int))
        data.Columns.Add('Y', clr.GetClrType(int))
        data.Columns.Add('Sector', clr.GetClrType(str))
        
        for tmap in self.treasureMaps:
            sector = self.GetSector(tmap.x, tmap.y)
            data.Rows.Add(hex(tmap.serial), tmap.x, tmap.y, sector)
        
        Misc.SendMessage('{0}: SOS Data has been loaded.'.format(self.scriptName), 67)   
        return data
    
    def mapCatalogue(self):
        tmapbag = Items.FindBySerial(self.treasureMapsBag)
        Items.WaitForContents(tmapbag, 8000)
        Misc.Pause(500)
        
        for i in tmapbag.Contains:
            if i.ItemID == 0x14EE:
                Gumps.ResetGump()
                Items.UseItem(i)
                Gumps.WaitForGump(1426736667, 3000)
                
                if Gumps.CurrentGump() != 1426736667 or Gumps.LastGumpGetLineList().Count < 3:
                    Misc.SendMessage('{0}: Gump error. Retry once.'.format(self.scriptName), 33)
                    
                    if self.LoadRetry(i):
                        Misc.SendMessage('{0}: Gump error. Skipped.'.format(self.scriptName), 33)
                        continue
                    
                line = Gumps.LastGumpGetLine(2)
                degrees = line.replace('°', '|').replace('\'', "|").replace(',', '|').split('|')
                lat = int(degrees[0]) + int(degrees[1]) * .01
                lon = int(degrees[3]) + int(degrees[4]) * .01
                dir1 = degrees[2]
                dir2 = degrees[5]
                x, y = self.MapXY(lat, lon, dir1, dir2)
                dist = self.getPointsDistance(x, y)
                self.treasureMaps.append(Treasure(i.Serial, x, y, dist))
                Gumps.SendAction(1426736667, 0)
                Misc.Pause(500)

        self.treasureMaps.sort(key=lambda x: x.distance)
    
    def LoadRetry(self, tmap):
        Misc.Pause(500)
        Gumps.ResetGump()
        Items.UseItem(tmap)
        Gumps.WaitForGump(1426736667, 3000)
        
        if Gumps.CurrentGump() != 1426736667 or Gumps.LastGumpGetLineList().Count < 3:
            return True
            
        return False
            
    def MapXY(self, lat, lon, dir1, dir2):
        if dir1 == 'S':
            y = math.floor(lat) * 60. + lat % 1. * 100.
        else:
            y = -1.0 * math.ceil(lat) * 60. + lat % 1. * 100.
        y = int(y / 21600. * 4096.) + 1624
        
        if y < 0:
            y += 4096
        if y >= 4096:
            y -= 4096
            
        if dir2 == 'E':
            x = math.floor(lon) * 60. + lon % 1. * 100.
        else:
            x = -1.0 * math.ceil(lon) * 60. + lon % 1. * 100.
            
        x = int(x / 21600. * 5120.) + 1323
        
        if x < 0:
            x += 5120
        if x >= 5120:
            x -= 5120

        return x, y

    def GetSector(self, x, y):
        if x < 1385 and 0 <= y < 1280:
            return 'Yew'
        elif x < 1000 and 1280 <= y < 2027:
            return 'Shame'
        elif x < 1000 and 2036 <= y < 2450:
            return 'Skara'
        elif x < 1300 and 2450 <= y < 3200:
            return 'Destard'
        elif x < 1900 and 3200 <= y <= 4096:
            return 'Jhelom'
        elif 1385 <= x < 2690 and y < 900:
            return 'Wrong'
        elif 1385 <= x < 2100 and 1280 <= y < 2030:
            return 'Britain'
        elif 2100 <= x < 2690 and 1280 <= y < 2030:
            return 'Cove'
        elif 1385 <= x < 2690 and 2030 <= y < 3075:
            return 'Trinsic'
        elif 1900 <= x < 2690 and 3075 <= y <= 4096:
            return 'Valor'
        elif 2580 <= x < 3250 and y < 1890:
            return 'Vesper'
        elif 3250 <= x < 4100 and y < 1890:
            return "Nujel'm"
        elif 2100 <= x < 3850 and 1890 <= y < 3075:
            return 'Bucca'
        elif 2690 <= x < 3850 and 3075 <= y <= 4096:
            return 'Fire'
        elif x >= 4100 and y < 1890:
            return 'Moonglow'
        elif x >= 3850 and 1890 <= y < 2890:
            return 'Sea Market'
        elif x >= 3850 and y >= 2890:
            return 'Hythloth'
        else:
            return 'None'

Misc.SendMessage('Select the SOS container.', 67)
sbag = Target.PromptTarget()
if sbag > -1:
    SH = SOSManager(sbag)
    Application.Run(SH)

