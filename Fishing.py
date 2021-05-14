# Variabili Sistema
import clr
clr.AddReference('System.Web.Extensions')
from System.Collections.Generic import List
from time import time
import math
from System.Net import WebRequest
from System.IO import StreamReader, Directory, Path, File
from System.Web.Script.Serialization import JavaScriptSerializer

CONFIGS = {}
RESOURCES = None
config_path = Path.Combine(Directory.GetCurrentDirectory(), 'Scripts\\json\\fishing_config.json')

with open(config_path, 'r') as f:
    CONFIGS = JavaScriptSerializer.DeserializeObject(JavaScriptSerializer(), f.read())


class Spot(object):
    def __init__(self, x, y):
        self.x = Player.Position.X + x
        self.y = Player.Position.Y + y

class Fishing(object):
    ship_key = None
    fish_pos = {
        'x' : None,
        'y' : None,
        'z' : None
        }
    keep = []
    spots = []
    ignored_corpses = []
    must_stop = False    
    cargo_hold = None
    fish_crate = None
     
    def __init__(self):
        for i in Player.Backpack.Contains:
            if i.ItemID in CONFIGS['ids']['shipkey']:
                self.ship_key = i.Serial
                break
        if not self.ship_key is None:
            self.checkKeyInsure()
            
    def keepFish(self):
        crate = None
        hold = None
        fil = Items.Filter()
        fil.OnGround = True
        fil.Movable = False
        fil.RangeMax = 1
        #fil.IsContainer = 1
        groundies = Items.ApplyFilter(fil)
        for g in groundies:
            if g.ItemID in CONFIGS['ids']['holds']:
                hold = g
                self.cargo_hold = hold
                Items.WaitForContents(hold, 7000)
                Misc.Pause(CONFIGS['delays']['base'])
                for i in hold.Contains:
                    if i.ItemID == 0x09A9:
                        crate = i
                        break
                if crate:
                    self.fish_crate = crate
                    Items.WaitForProps(crate, 8000)

                    for pstr in Items.GetPropStringList(crate):

                        if '10/10' in pstr or '15/15' in pstr or '20/20' in pstr:
                            continue

                        if '/10' in pstr or '/15' in pstr or '/20' in pstr:
                            self.keep.append(pstr.split(': ')[0].strip())

                    Misc.SendMessage('Fish to keep: {0}!'.format(', '.join(f for f in self.keep)), 76)
                    break
            
    @property
    def diffWeight(self):
        return Player.MaxWeight - Player.Weight
    
    def checkKeyInsure(self):
        Items.WaitForProps(self.ship_key, 8000)
        if not 'insured' in ' '.join(c.lower() for c in Items.GetPropStringList(self.ship_key)):
            Misc.WaitForContext(Player.Serial, 9000)
            Misc.ContextReply(Player.Serial, 5)
            Target.WaitForTarget(8000)
            Target.TargetExecute(self.ship_key)
            Misc.Pause(500)
                
        Target.Cancel()
        
    def getInPosition(self): # if you cast summon daemon on the recall spot you get location blocked.
        if self.cargo_hold:
            pmobile = Mobiles.FindBySerial(Player.Serial)
            hold = self.cargo_hold
            while self.cargo_hold.DistanceTo(pmobile) > 2:
                Player.PathFindTo(hold.Position.X, hold.Position.Y, hold.Position.Z)
                Misc.Pause(CONFIGS['delays']['walk'])
            return

        fil = Mobiles.Filter()
        fil.RangeMax = 5
        fil.Enabled = True
        mobs = Mobiles.ApplyFilter(fil)
        steward = None

        for mob in mobs:
            if mob.Body == 0x191:
                steward = mob

        if steward is None:
            self.setFishPos()
            return
        for x in xrange(2):
            if steward.Position.Y > Player.Position.Y:
                Player.Walk('North')
            elif steward.Position.Y < Player.Position.Y:
                Player.Walk('South')
            elif steward.Position.X > Player.Position.X:
                Player.Walk('West')
            elif steward.Position.X < Player.Position.X:
                Player.Walk('East')
            
            Misc.Pause(CONFIGS['delays']['walk'])
            
        self.setFishPos()
        
    def checkDaemon(self):
        if Player.Followers >= 4:
            return
            
        while Player.Followers < 4:
            Spells.CastMagery("Summon Daemon")
            Misc.Pause(5000)
            
        Player.ChatSay(71, 'all guard me')

    def calcDistance(self, x0, y0, x1, y1):
        a = abs(x1 - x0) ** 2
        b = abs(y1 - y0) ** 2
        return int(math.sqrt(a + b))

    def checkCorpses(self):
        fil = Items.Filter()
        fil.Movable = 0
        fil.OnGround = 1
        fil.IsCorpse = 1
        fil.RangeMax = 8
        fil.Enabled = True
        
        itms = Items.ApplyFilter(fil)
        corpses = [i for i in itms if not i.Serial in self.ignored_corpses]

        for corpse in corpses:
            Misc.SendMessage('Corpse found!', 76)
            switch = False
            tries = 0

            move_start = time()
            move_end = False
            pmobile = Mobiles.FindBySerial(Player.Serial)
            while corpse.DistanceTo(pmobile) > 2:
                if time() - move_start > 30:
                    move_end = True
                    break
                #Player.PathFindTo(corpse.Position.X, corpse.Position.Y, corpse.Position.Z)
                self.guidedWalk(corpse.Position.X, corpse.Position.Y)
                    
                Misc.Pause(CONFIGS['delays']['walk'])

            if move_end:
                self.ignored_corpses.append(corpse.Serial)
                continue

            Items.WaitForContents(corpse, CONFIGS['delays']['timeout'])
            Misc.Pause(CONFIGS['delays']['base'])
                
            loot = [i for i in corpse.Contains if i.ItemID in CONFIGS['ids']['keep']]
                
            for l in loot:
                bag = Player.Backpack if CONFIGS['loot_bag'] is None else CONFIGS['loot_bag']
                Items.Move(l, bag, 0)
                Misc.Pause(CONFIGS['delays']['drag'])
                    
            self.ignored_corpses.append(corpse.Serial)
        if self.fish_pos['x'] and self.fish_pos['y']:
            while self.calcDistance(Player.Position.X, Player.Position.Y, self.fish_pos['x'], self.fish_pos['y']) > 0:
                self.guidedWalk(self.fish_pos['x'], self.fish_pos['y'])

    def guidedWalk(self, x, y):
        px = Player.Position.X
        py = Player.Position.Y
        if x > px:
            if y > py:
                Player.Walk('Down')
            elif y == py:
                Player.Walk('East')
            elif y < py:
                Player.Walk('Right')
        elif x == px:
            if y > py:
                Player.Walk('South')
            if y == py:
                return
            elif y < py:
                Player.Walk('North')
        elif x < px:
            if y > py:
                Player.Walk('Left')
            elif y == py:
                Player.Walk('West')
            elif y < py:
                Player.Walk('Up')
            
        Misc.Pause(CONFIGS['delays']['step'])


    def setFishPos(self):
        self.fish_pos['x'] = Player.Position.X
        self.fish_pos['y'] = Player.Position.Y
        self.fish_pos['z'] = Player.Position.Z
                
    def checkHits(self):
        while Player.Hits < Player.HitsMax:
            
            if CONFIGS['use_chivalry']:
                if Player.Poisoned:
                    Spells.CastChivalry('Cleanse by Fire')
                else:
                    Spells.CastChivalry('Close Wounds')
                
            else:
                if Player.Poisoned:
                    Spells.CastMagery('Cure')
                else:
                    Spells.CastMagery('Heal')
                
                
            Target.WaitForTarget(CONFIGS['delays']['timeout'])
            Target.Self()
            Misc.Pause(CONFIGS['delays']['cast'])
                        
    def cutFish(self):
        fish = [f for f in Player.Backpack.Contains if f.ItemID in CONFIGS['ids']['fish']]
        for f in fish:
            Items.WaitForProps(f, 8000)
            propstr = ''.join(p.lower() for p in Items.GetPropStringList(f))
            if any(k for k in self.keep if k in propstr):
                Items.Move(f, self.fish_crate, 0)
                Misc.Pause(CONFIGS['delays']['drag'])
                continue
            elif any(l for l in CONFIGS['legendaries'] if l in propstr):
                continue
            Items.UseItemByID(CONFIGS['ids']['dagger'], -1)
            Target.WaitForTarget(8000)
            Target.TargetExecute(f)
            Misc.Pause(300)

    def throwTrash(self):
        trash = [i.Serial for i in Player.Backpack.Contains if i.ItemID in CONFIGS['ids']['trash']]
        for t in trash:
            Items.Move(t, CONFIGS['trash_chest'], 0)
            Misc.Pause(600)

    def imInBank(self):
        return (Player.Position.X == CONFIGS['runebooks']['bank']['x'] and Player.Position.Y == CONFIGS['runebooks']['bank']['y'])
    
    def deposit(self):
        while not self.imInBank():
            Gumps.ResetGump()                
            Items.UseItem(CONFIGS['runebooks']['bank']['book'])
            Gumps.WaitForGump(1431013363, CONFIGS['delays']['timeout'])
            Gumps.SendAction(1431013363, CONFIGS['runebooks']['bank']['rune'])
            Misc.Pause(CONFIGS['delays']['cast'])
        trash = [t for t in Player.Backpack.Contains if t.ItemID in CONFIGS['ids']['trash']]
        if not trash is None:
            for t in trash:
                Items.Move(t, CONFIGS['trash_chest'], 0)
                Misc.Pause(CONFIGS['delays']['drag'])
        Player.ChatSay(33, "Bank")
        Misc.Pause(500)
        keep = [k for k in Player.Backpack.Contains if (k.ItemID in CONFIGS['ids']['keep'] or k.ItemID in CONFIGS['legendaries'])]
        if not keep is None:
            for k in keep:
                Items.Move(k, CONFIGS['bank_bag'], 0)
                Misc.Pause(CONFIGS['delays']['drag'])

    def shipRecall(self):
        tries = 0
        while self.imInBank():
            if self.ship_key is None:
                Gumps.ResetGump()                
                Items.UseItem(CONFIGS['runebooks']['ship']['book'])
                Gumps.WaitForGump(1431013363, CONFIGS['delays']['timeout'])
                Gumps.SendAction(1431013363, CONFIGS['runebooks']['ship']['rune'])
            else:
                if CONFIGS['use_chivalry']:
                    Spells.CastChivalry("Sacred Journey")
                else:
                    Spells.CastMagery("Recall")
                Target.WaitForTarget(7000)
                Target.TargetExecute(self.ship_key)
                
            Misc.Pause(CONFIGS['delays']['cast'])
            
            if tries > 0:
                Misc.Pause(CONFIGS['delays']['recovery'])
                
            tries += 1
            
    def start_fishing(self):
        for spot in self.spots:
            Journal.Clear()
            while not Journal.Search("seem to be biting"):
                self.checkHits()
                self.checkDaemon()
                self.setFishPos()
                self.checkCorpses()
                if self.diffWeight < 20 or Player.Backpack.Contains.Count > 120:
                    Player.ChatSay(71, "Stop")
                    Misc.Pause(500)
                    self.deposit()
                    self.shipRecall()
                    self.getInPosition()
                    
                Items.UseItemByID(CONFIGS['ids']['pole'], -1)
                Target.WaitForTarget(8000)
                Target.TargetExecute(spot.x, spot.y, Player.Position.Z)
                Misc.Pause(1000)
                if not Journal.Search("seem to be biting"):
                    Misc.Pause(8500)
                    self.cutFish()
                    self.throwTrash()

    def start(self):
        while not self.must_stop:
            self.spots = [
                Spot(-4,-4), Spot(-4,4),
                Spot(4, -4), Spot(4,4)
                ]
            self.start_fishing()
            for x in xrange(12):
                self.checkDaemon()       
                Player.ChatSay(71, "Forward One")
                Misc.Pause(1500)
            Misc.Pause(500)
                           
        
fishing = Fishing()
fishing.keepFish()
fishing.getInPosition()
fishing.start()
             
