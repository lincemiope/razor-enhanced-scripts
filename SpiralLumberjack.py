# Variabili Sistema
import clr
clr.AddReference('System.Web.Extensions')
from System.Collections.Generic import List
from time import time
from System.Net import WebRequest
from System.IO import StreamReader, Directory, Path, File
from System.Web.Script.Serialization import JavaScriptSerializer

CONFIGS = {}
RESOURCES = None
config_path = Path.Combine(Directory.GetCurrentDirectory(), 'Scripts\\json\lnr_config.json')
res_path = Path.Combine(Directory.GetCurrentDirectory(), 'Scripts\\json\lnr_resources.json')

with open(config_path, 'r') as f:
    CONFIGS = JavaScriptSerializer.DeserializeObject(JavaScriptSerializer(), f.read())

## RESOURCES MANAGEMENT START
class ResourceEntry(object):

    def __init__(self, name='', graphic=0, color=0, value=0):
        self.name = name or ''
        self.graphic = graphic or 0
        self.color = color or 0
        self.value = value or 0

    def __iter__(self):
        for k,v in self.__dict__.iteritems():
            yield (k,v)


class ResourceConfig(object):

    def __init__(self):
        # boards
        self.normal = ResourceEntry('Normal', 7127, 0, 0)
        self.oak = ResourceEntry('Oak', 7127, 2010, 0)
        self.ash = ResourceEntry('Ash', 7127, 1191, 0)
        self.yew = ResourceEntry('Yew', 7127, 1192, 0)
        self.hw = ResourceEntry('Heartwood', 7127, 1193, 0)
        self.frost = ResourceEntry('Frostwood', 7127, 1151, 0)
        self.blood = ResourceEntry('Bloodwood', 7127, 1194, 0)
        ## custom
        self.bamboo = ResourceEntry('Bamboo', 7127, 1719, 0)
        self.ebony = ResourceEntry('Ebony', 7127, 1457, 0)
        self.purple = ResourceEntry('Purple Heart', 7127, 114, 0)
        self.red = ResourceEntry('Redwood', 7127, 37, 0)
        # other
        self.plant = ResourceEntry('Parasitic Plant', 12688)
        self.switch = ResourceEntry('Switch', 12127)
        self.fungi = ResourceEntry('Fungi', 12689)
        self.bark = ResourceEntry('Bark Fragment', 12687)
        self.amber = ResourceEntry('Brilliant Amber', 12697)

    def __iter__(self):
        for k,v in self.__dict__.iteritems():
            if hasattr(v, '__iter__'):
                yield (k, dict(v))
            elif hasattr(v, '__dict__'):
                yield (k, v.__dict__)
            else:
                yield (k, v)

    def from_config(self, cnf):
        self.normal.value = cnf['boards']['normal']
        self.oak.value = cnf['boards']['oak']
        self.ash.value = cnf['boards']['ash']
        self.yew.value = cnf['boards']['yew']
        self.hw.value = cnf['boards']['hw']
        self.frost.value = cnf['boards']['frost']
        self.blood.value = cnf['boards']['blood']
        self.bamboo.value = cnf['boards']['bamboo']
        self.ebony.value = cnf['boards']['ebony']
        self.purple.value = cnf['boards']['purple']
        self.red.value = cnf['boards']['red']
        self.plant.value = cnf['other']['plant']
        self.switch.value = cnf['other']['switch']
        self.fungi.value = cnf['other']['fungi']
        self.bark.value = cnf['other']['bark']
        self.amber.value = cnf['other']['amber']
        return self

    def to_config(self):
        return {
            'boards' : {
                'normal' : self.normal.value,
                'oak' : self.oak.value,
                'ash' : self.ash.value,
                'yew' : self.yew.value,
                'hw' : self.hw.value,
                'frost' : self.frost.value,
                'blood' : self.blood.value,
                'bamboo' : self.bamboo.value,
                'ebony' : self.ebony.value,
                'purple' : self.purple.value,
                'red' : self.red.value
            },
            'other' : {
                'plant' : self.plant.value,
                'switch' : self.switch.value,
                'fungi' : self.fungi.value,
                'bark' : self.bark.value,
                'amber' : self.amber.value
            }
        }

    def add(self, kind, amount):
        try:
            curr = getattr(self, kind)
            curr.value += amount
            return curr.value
        except:
            print('Error')
        return -1

    def add_all(self, backpack_items):
        messages = []
        for item in backpack_items:
            attrs = [k for k,v in dict(self).iteritems() if v['graphic'] == item.ItemID and v['color'] == item.Hue]
            if not attrs or len(attrs) < 1:
                continue
            kind = attrs[0]
            curr = getattr(self, kind)
            curr.value += item.Amount
            messages.append('%s: %d / %d' % (curr.name, item.Amount, curr.value))

        return messages

if File.Exists(res_path):
    with open(res_path, 'r') as f:
        res_dict = JavaScriptSerializer.DeserializeObject(JavaScriptSerializer(), f.read())
        res_class = ResourceConfig()
        RESOURCES = res_class.from_config(res_dict)
else:
    with open(res_path, 'w') as f:
        RESOURCES = ResourceConfig()
        res_dict = RESOURCES.to_config()
        f.write(JavaScriptSerializer.Serialize(JavaScriptSerializer(), res_dict))
## RESOURCES MANAGEMENT END

class TreeEntry(object):

    def __init__(self, x, y, z, gfx):
        self.x = x
        self.y = y
        self.z = z
        self.gfx = gfx

    def __str__(self):
        return 'TreeEntry: %d (%d, %d, %d)' % (self.gfx, self.x, self.y, self.z)

class TelegramApi(object):
    Uri = 'https://api.telegram.org/' + YOUR_BOT_ID_HERE + '/sendMessage?chat_id=' + YOUR_CHAT_ID_HERE '&text='
    
    @staticmethod
    def HTTPRequest(txt):
        request = WebRequest.Create(TelegramApi.Uri + txt)
        response = request.GetResponse()
        return StreamReader(response.GetResponseStream()).ReadToEnd()
        
    @staticmethod
    def SnakeAlert():        
        TelegramApi.HTTPRequest('The damn snake is onto you (HP: {0}/{1})!'.format(Player.Hits, Player.HitsMax))
        
    @staticmethod    
    def TimePast(delta):
        m, s = divmod(delta, 60)
        h, m = divmod(m, 60)
        TelegramApi.HTTPRequest('Done in {0}h {1}m {2}s.'.format(h, m, s))

    @staticmethod
    def CaptchaAlert():
        TelegramApi.HTTPRequest('Captcha alert!')
    
class LumberNoRecall:
    treeNumber = 0
    treeList = []
    lastCheck = 0
    spiral = []
    current_hatchet = 0
    current_book = 0
    current_rune = 0

    def isCaptchaGump(self):
        if not Gumps.HasGump():
            return False

        if not Gumps.LastGumpGetLineList():
            return False

        if len([l for l in Gumps.LastGumpGetLineList() if l and 'Type the Value' in l]) < 2:
            return False

        return True

    def checkCaptcha(self): # 2081600157
        if self.isCaptchaGump():
            TelegramApi.CaptchaAlert()
            while self.isCaptchaGump():
                Misc.Pause(3000)

    def rangeTree(self, index):
       return abs(Player.Position.X - self.treeList[index].x) <= 1 and abs(Player.Position.Y - self.treeList[index].y) <= 1   
        
    def scanStatic(self):
        Misc.SendMessage("--> Inizio Scansione Tile", 77)
        for _x, _y in self.spiral:
            tileInfo = Statics.GetStaticsTileInfo(Player.Position.X + _x, Player.Position.Y + _y, Player.Map)
            if tileInfo.Count > 0:
                useful = [t for t in tileInfo if t.StaticID in CONFIGS['graphics']['trees']]
                for u in useful:
                    treeX = Player.Position.X + _x
                    treeY = Player.Position.Y + _y
                    self.treeList.append(TreeEntry(treeX, treeY, u.StaticZ, u.StaticID))
        
        self.treeNumber = len(self.treeList)  
        Misc.SendMessage('--> Totale Alberi: %i' % (self.treeNumber), 77)

    def moveToTree(self, spotnumber):
        pathlock = 0
        
        while self.isOverWeight():
            Gumps.ResetGump()
            for plogs in Player.Backpack.Contains:
                if plogs.ItemID == CONFIGS['graphics']['logs']:
                    Items.UseItem(plogs.Serial)
                    Misc.Pause(CONFIGS['delays']['half'])
                    
        while Player.Stam == 0:
            Misc.Pause(CONFIGS['delays']['standard'])
            
        Misc.SendMessage('--> Moving to TreeSpot: %i' % (spotnumber), 77)
        Player.PathFindTo(self.treeList[spotnumber].x, self.treeList[spotnumber].y, self.treeList[spotnumber].z)
        x = Player.Position.X
        y = Player.Position.Y
        while not self.rangeTree(spotnumber):
            self.checkEnemy()  
            Misc.Pause(CONFIGS['delays']['short'])
            pathlock += 1
            if pathlock > 5 and Player.Position.X == x and Player.Position.Y == y:
                Player.HeadMessage(33, 'Albero irraggiungibile - ' + str(self.treeList[spotnumber]))
                return False
            if pathlock > 40:
                Player.HeadMessage(33, 'Albero irraggiungibile')
                return False
            
                Misc.SendMessage('Raggiunto TreeSpot {4} - X: {0} Y: {1} Z: {2} GFX: {3}'.format(self.treeList[spotnumber].x, self.treeList[spotnumber].y, self.treeList[spotnumber].z, self.treeList[spotnumber].gfx, spotnumber), 77)
        
        return True
        
    def equipHatchet(self):
        while not Player.CheckLayer("LeftHand"):
            hasHatchet = False
            for graphic in CONFIGS['graphics']['hatchet']:
                if Items.BackpackCount(graphic, 0) > 0:
                    hasHatchet = True
                    break

            if not hasHatchet:
                if Items.BackpackCount(CONFIGS['graphics']['tinker']) < 2:
                    self.craftTool()
                    Misc.Pause(CONFIGS['delays']['standard'])
                self.craftHatchet()
                Misc.Pause(CONFIGS['delays']['standard'])

            accette = [i for i in Player.Backpack.Contains if i.ItemID in CONFIGS['graphics']['hatchet']]
            if len(accette) == 0:
                return False
            Player.EquipItem(accette[0].Serial)
            Misc.Pause(CONFIGS['delays']['equipHatchet'])

        self.current_hatchet = Player.GetItemOnLayer("LeftHand").Serial
        return True

    def cutTree(self, spotnumber):
        blockcount = 0
        self.checkCaptcha()
        if Target.HasTarget():
            Misc.SendMessage("--> Blocco rilevato target residuo, cancello!", 77)
            Target.Cancel()
            Misc.Pause(CONFIGS['delays']['half'])   
        
        if self.isOverWeight():
            if Target.HasTarget():
                Target.Cancel()
            self.boarding()
        if self.isOverWeight():
            self.deposit()
            self.getIngots()
            self.recall()
            self.cutTree(spotnumber)

        self.checkEnemy()    
        Journal.Clear()
        self.equipHatchet()
        Items.UseItem(self.current_hatchet)
        Target.WaitForTarget(CONFIGS['delays']['action'])
        Target.TargetExecute(self.treeList[spotnumber].x, self.treeList[spotnumber].y, self.treeList[spotnumber].z, self.treeList[spotnumber].gfx)
        Misc.Pause(CONFIGS['delays']['chop'])
        #self.boarding()
        if Journal.Search("broke your axe"):
            Journal.Clear()
            self.equipHatchet()
        if Journal.Search("There's not enough") or Journal.Search("on that") or Journal.Search('cannot be seen') or Journal.Search('far away'):
            Misc.SendMessage("--> Cambio albero", 77)
        elif Journal.Search("That is too far away"):
            blockcount = blockcount + 1
            Journal.Clear()
            if (blockcount > 15):
                blockcount = 0
                Misc.SendMessage("--> Possibile blocco rilevato cambio albero", 77)
            else:
                self.cutTree(spotnumber)
        else:
            self.cutTree(spotnumber)

    def resCount(self):
        items = [i for i in Player.Backpack.Contains]
        messages = RESOURCES.add_all(items)

        if messages and len(messages) > 0:
            Misc.SendMessage('--> Counters:', 77)
            for message in messages:
                Misc.SendMessage('--> ' + message, 77)

        with open(res_path, 'w') as f:
            res_dict = RESOURCES.to_config()
            f.write(JavaScriptSerializer.Serialize(JavaScriptSerializer(), res_dict))
        
    def boarding(self):
        logs = [i.Serial for i in Player.Backpack.Contains if i.ItemID == CONFIGS['graphics']['logs']]
        for log in logs:
            Items.UseItem(self.current_hatchet)
            Target.WaitForTarget(CONFIGS['delays']['action'])
            Target.TargetExecute(log)
            Misc.Pause(CONFIGS['delays']['standard'])
            
    def checkEnemy(self):
        if time() - self.lastCheck > CONFIGS['delays']['check']:            
            fil = Mobiles.Filter()
            fil.Enabled = True
            fil.RangeMax = 2
            enemies = Mobiles.ApplyFilter(fil)
            
            for enemy in enemies:
                if enemy.Body in CONFIGS['graphics']['enemies']:
                    TelegramApi.SnakeAlert()
                    self.lastCheck = time()
                    break
       
    def getSpiral(self, X, Y):
        x = y = 0
        res = list()
        dx = 0
        dy = -1
        for i in range(max(X, Y)**2):
            if (-X/2 < x <= X/2) and (-Y/2 < y <= Y/2):
                res.append([x, y])
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                dx, dy = -dy, dx
            x, y = x+dx, y+dy
        return res

    def recall(self):
        Journal.Clear()
        while Player.Mana < 10:
            Misc.Pause(CONFIGS['delays']['half'])
        # flizz prevention
        _x = Player.Position.X
        _y = Player.Position.Y
        Gumps.ResetGump()
        Items.UseItem(self.current_book)
        Gumps.WaitForGump(1431013363, CONFIGS['delays']['action'])  
        Gumps.SendAction(1431013363, self.current_rune)
        Misc.Pause(CONFIGS['delays']['recovery'])
        if Journal.Search("blocked.") or self.imInBank():            
            Misc.Pause(CONFIGS['delays']['recovery'])
            self.current_rune += 6
            if self.current_rune > (95 + int(CONFIGS['recall']['useChivalry']) * 2):
                self.current_rune = 5 + int(CONFIGS['recall']['useChivalry']) * 2
                bindex = CONFIGS['recall']['treeBooks'].index(self.current_book)
                if bindex >= len(CONFIGS['recall']['treeBooks']):
                    self.current_book = CONFIGS['recall']['treeBooks'][0]
                else:
                    self.current_book = CONFIGS['recall']['treeBooks'][bindex+1]
            self.recall()
        elif Journal.Search("recover") or self.imInBank():
            Misc.Pause(CONFIGS['delays']['recovery'])
            self.recall()
        elif Player.Position.X == _x and Player.Position.Y == _y:
            Misc.Pause(CONFIGS['delays']['recovery'])
            self.recall()

    def isOverWeight(self):
        return Player.Weight >= Player.MaxWeight - CONFIGS['weightMargin']

    def imInBank(self):
        x, y, z = CONFIGS['recall']['bankPos']

        if Player.Position.X != x:
            return False
        if Player.Position.Y != y:
            return False
        if Player.Position.Z != z:
            return False

        return True

    def getRuneCode(self, pos):
        return pos * 6 + 5 + int(CONFIGS['recall']['useChivalry']) * 2

    def encumbered(self):
        wgap = Player.Weight - Player.MaxWeight
        if wgap > 0:
            board = next(b for b in Player.Backpack.Contains if b.ItemID == CONFIGS['graphics']['boards'])
            Items.MoveOnGround(board, wgap, Player.Position.X, Player.Position.Y, Player.Position.Z)
            Misc.Pause(CONFIGS['delays']['drag'])

    def getIngots(self):
        bag_serial = CONFIGS['containers']['ingots']
        if not bag_serial or bag_serial < 1:
            return
        bp_ingots = Items.BackpackCount(CONFIGS['graphics']['ingots'], 0)
        if bp_ingots >= CONFIGS['ingotsAmount']:
            return
        needed = CONFIGS['ingotsAmount'] - bp_ingots
        ingots_bag = Items.FindBySerial(bag_serial)
        if not ingots_bag:
            return
        Items.WaitForContents(ingots_bag, CONFIGS['delays']['action'])
        for i in ingots_bag.Contains:
            if i.ItemID == CONFIGS['graphics']['ingots'] and i.Hue == 0:
                amount = needed if i.Amount >= needed else i.Amount
                Items.Move(i, Player.Backpack, amount)
                Misc.Pause(CONFIGS['delays']['drag'])
                break

    def deposit(self):
        while self.isOverWeight():
            while not self.imInBank():
                self.encumbered()
                self.boarding()
                Gumps.ResetGump()                
                Items.UseItem(CONFIGS['recall']['bankBook'])
                Gumps.WaitForGump(1431013363, CONFIGS['delays']['action'])
                Gumps.SendAction(1431013363, self.getRuneCode(CONFIGS['recall']['bankRune']))
                Misc.Pause(CONFIGS['delays']['recovery'])
            Player.ChatSay(33, "Bank")
            Misc.Pause(300)
            self.boarding()
            #self.ResCount()
            self.resCount()
            for item in Player.Backpack.Contains:
                if item.ItemID in [CONFIGS['graphics']['boards'], CONFIGS['graphics']['logs']]:
                    #Misc.SendMessage("--> Storing boards", 77) 
                    Items.Move(item, CONFIGS['containers']['boards'], 0)
                    Misc.Pause(CONFIGS['delays']['drag'])
                else:
                    for otherid in CONFIGS['graphics']['other']:
                        if item.ItemID == otherid:
                            #Misc.SendMessage("--> Storing other resources", 77) 
                            Items.Move(item, CONFIGS['containers']['other'], 0)
                            Misc.Pause(CONFIGS['delays']['drag'])

    def craftTool(self):
        Items.UseItemByID(CONFIGS['graphics']['tinker'], 0)
        Gumps.WaitForGump(949095101, CONFIGS['delays']['action'])
        Gumps.SendAction(949095101, 15)
        Gumps.WaitForGump(949095101, CONFIGS['delays']['action'])
        Gumps.SendAction(949095101, 23)
        Gumps.WaitForGump(949095101, CONFIGS['delays']['action'])
        Gumps.CloseGump(949095101)

    def craftHatchet(self):
        Items.UseItemByID(CONFIGS['graphics']['tinker'], 0)
        Gumps.WaitForGump(949095101, CONFIGS['delays']['action'])
        Gumps.SendAction(949095101, 15)
        Gumps.WaitForGump(949095101, CONFIGS['delays']['action'])
        Gumps.SendAction(949095101, 30)
        Gumps.WaitForGump(949095101, CONFIGS['delays']['action'])
        Gumps.CloseGump(949095101)
        
    def start(self):
        if CONFIGS['enableRecall']:
            self.start_recall()
        else:
            self.start_no_recall()

    def start_no_recall(self):
        #self.recallNextSpot()
        Misc.SendMessage("--> Avvio Tagliaboschi", 77)
        self.spiral = self.getSpiral(CONFIGS['scanRadius'], CONFIGS['scanRadius'])
        self.scanStatic()
        i = 0
        while i < self.treeNumber:
            if self.moveToTree(i):
                self.cutTree(i)
            i += 1
        self.treeList = []
        self.treeNumber = 0
    
    def start_recall(self):
        Misc.SendMessage("--> Avvio Tagliaboschi", 77)
        self.spiral = self.getSpiral(CONFIGS['scanRadius'], CONFIGS['scanRadius'])
        while 1 < 2:
            for b in CONFIGS['recall']['treeBooks']:
                self.current_book = b
                for r in xrange(16):
                    self.current_rune = self.getRuneCode(r)
                    self.deposit()
                    self.getIngots()
                    self.recall()
                    Misc.SendMessage("--> Runa %i" % r, 77)
                    self.scanStatic()
                    i = 0
                    while i < self.treeNumber:
                        if self.moveToTree(i):
                            self.cutTree(i)

                        i += 1

                    self.treeList = []
                    self.treeNumber = 0


# START/STOP
start_time = time()
Player.HeadMessage(45, 'Inizio Lumber-No-Recall')
lnr = LumberNoRecall()
lnr.start()
Player.HeadMessage(65, 'Fine Lumber-No-Recall')
end_time = time()

TelegramApi.TimePast(int(end_time - start_time))
