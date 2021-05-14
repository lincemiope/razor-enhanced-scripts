import clr
clr.AddReference('System.Web.Extensions')
from System.IO import Directory, Path, File
from System.Web.Script.Serialization import JavaScriptSerializer
from System.Collections.Generic import List
from time import time

class MineSpot(object):
    X = Y = Z = GFX = 0
    def __init__(self, x, y, z, gfx):
        self.X, self.Y, self.Z, self.GFX = x, y, z, gfx
        
class Miner(object):
    Current = {'book' : 0, 'rune' : 0}
    Delay = {
        'dig' : 500,
        'drag' : 600,
        'cast' : 2000,
        'smelt' : 300,
        'recovery' : 2000,
        'timeout' : 4000
        }
    IDs = {
        'color' : {
            '0' : 'iron',
            '2419' : 'dull',
            '2406' : 'shadow',
            '2413' : 'copper',
            '2418', : 'bronze',
            '2213' : 'gold',
            '2425' : 'agapite',
            '2207' : 'verite',
            '2219' : 'valorite'  
            }
        'gem' : {
            'amber' : 0x0F25,
            'amethyst' : 0,
            'blackrock' : 0,
            'citrine' : 0x0F15,
            'diamond' : 0x0F26,
            'emerald' : 0x0F10,
            'ruby' : 0x0F13,
            'sapphire' : 0x0F19,
            'starsapphire' : 0x0F21,
            'turmaline' : 0
            }
        'ingot' : 0x1BF2,
        'ore' : [],
        'rock' : 0x1779,
        'sand' : 0,
        'shovel' : 0x0F3A,
        'tool' : 0x1EB8,
        'unique' : {
            'bluediamond' : 0x3198,
            'darksapphire' : 0x3192,
            'ecrucitrine' : 0x3195,
            'fireruby' : 0x3197,
            'perfectemerald' : 0x3194,
            'turquoise' : 0x3193,
            }
        }
    
    CounterPath = Directory.GetCurrentDirectory() + '\\Scripts\\json\Miner_Counter.json'
    OptPath = Directory.GetCurrentDirectory() + '\\Scripts\\json\Miner_Opt.json'

    Counters = None
    Opt = None
    Spots = []
    
    MineTiles = [
        220, 221, 222, 223, 224, 225, 226, 227, 228, 229,
        230, 231, 236, 237, 238, 239, 240, 241, 242, 243,
        244, 245, 246, 247, 252, 253, 254, 255, 256, 257,
        258, 259, 260, 261, 262, 263, 268, 269, 270, 271,
        272, 273, 274, 275, 276, 277, 278, 279, 286, 287,
        288, 289, 290, 291, 292, 293, 294, 296, 296, 297,
        321, 322, 323, 324, 467, 468, 469, 470, 471, 472,
        473, 474, 476, 477, 478, 479, 480, 481, 482, 483,
        484, 485, 486, 487, 492, 493, 494, 495, 543, 544,
        545, 546, 547, 548, 549, 550, 551, 552, 553, 554,
        555, 556, 557, 558, 559, 560, 561, 562, 563, 564,
        565, 566, 567, 568, 569, 570, 571, 572, 573, 574,
        575, 576, 577, 578, 579, 581, 582, 583, 584, 585,
        586, 587, 588, 589, 590, 591, 592, 593, 594, 595,
        596, 597, 598, 599, 600, 601, 610, 611, 612, 613,
        1010, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749,
        1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1771, 1772,
        1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782,
        1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1801, 1802,
        1803, 1804, 1805, 1806, 1807, 1808, 1809, 1811, 1812, 1813,
        1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823,
        1824, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839,
        1840, 1841, 1842, 1843, 1844, 1845, 1846, 1847, 1848, 1849,
        1850, 1851, 1852, 1853, 1854, 1861, 1862, 1863, 1864, 1865,
        1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875,
        1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1981,
        1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991,
        1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001,
        2002, 2003, 2004, 2028, 2029, 2030, 2031, 2032, 2033, 2100,
        2101, 2102, 2103, 2104, 2105,
        17723, 17724, 17725, 17726, 17727, 17728, 17729, 17730, 17731,
        17732, 17733, 17734, 17735, 17736, 17737, 17738, 17739, 17740,
        17741, 17742, 17743
        ]

    def __init__(self):
        json = open(self.CounterPath, 'r').read()
        self.Counters = JavaScriptSerializer().DeserializeObject(json)
        
        json = open(self.OptPath, 'r').read()
        self.Opt = JavaScriptSerializer().DeserializeObject(json)

    @property
    def IsOverWeight(self):
        return (Player.MaxWeight - Player.Weight < 30)

    @property
    def ImHome(self):
        return sum(abs(Player.Position.X - self.Opt['homepos']['x']), abs(Player.Position.Y - self.Home['y'])) / 2 > 10

    def SaveCount(self):
        open(self.CounterPath, 'w').write(JavaScriptSerializer().Serialize(self.Counters))
        
    def SaveSpots(self):
        if self.Spots != self.m_Spots:
            open(self.SpotPath, 'w').write(JavaScriptSerializer().Serialize(self.Spots))


    def Deposit(self):
        ores = [o for o in Player.Backpack.Contains if o.ItemID in self.IDs['ore']]
                        
        for ore in ores:
            Items.UseItem(ore)
            Target.WaitForTarget(self.Delay['timeout'])
            Target.TargetExecute(self.Opt['homeforge'])
            Misc.Pause(self.Delay['smelt'])

        ingots = [i for i in Player.Backpack.Contains if i.ItemID == self.IDs['ingot']]
        
        for ingot in ingots:
            mat = self.IDs['color'][str(ingot.Hue)]
            self.Counters['ingot'][mat] += ingot.Amount
            Items.Move(ingot, self.Opt['homechest']['ingot'], 0)
            Misc.Pause(self.Delay['drag'])

        gems = [g for g in Player.Backpack.Contains if str(g.ItemID) in self.IDs['gem'].keys()]
        
        for gem in gems:
            mat = self.IDs['gem'][str(gem.ItemID)]
            self.Counters['gem'][mat] += gem.Amount
            Items.Move(gem, self.Opt['homechest']['gem'], 0)
            Misc.Pause(self.Delay['drag'])

        uniques = [u for u in Player.Backpack.Contains if str(u.ItemID) in self.IDs['unique'].keys()]

        for unique in uniques:
            mat = self.IDs['unique'][str(gem.ItemID)]
            self.Counters['unique'][mat] += gem.Amount
            Items.Move(unique, self.Opt['homechest']['gem'], 0)
            Misc.Pause(self.Delay['drag'])

        rocks = [r for r in Player.Backpack.Contains if r.ItemID == self.IDs['rock']]

        for rock in rocks:
            mat = self.IDs['color'][str(rock.Hue)]
            self.Counters['rock'][mat] += rock.Amount
            Items.Move(rock, self.Opt['homechest']['rock'], 0)
            Misc.Pause(self.Delay['drag'])

        sand = next(s for s in Player.Backpack.Contains if s.ItemID == self.IDs['sand'])
        
        if not sand is None:
            self.Counters['sand'] += sand.Amount
            Items.Move(sand, self.Opt['homechest']['rock'], 0)
            Misc.Pause(self.Delay['drag'])
            
        self.SaveCounts()
        
    def GoHome(self):
        while not self.ImHome:
            for rune in xrange(self.Opt['homerune'][0], self.Opt['homerune'][1] + 1):
                
                if Journal.Search('blocked.'):
                    Journal.Clear()
                    Misc.Pause(self.Delay['recovery'])
                    
                r = rune * 6 + 5 + 2 * int(self.Opt['chivalry'])
                Items.UseItem(self.Opt['homebook'])
                Gumps.WaitForGump(1431013363, self.Delay['timeout'])            
                Gumps.SendAction(1431013363, r)
                Misc.Pause(self.Delay['cast'])

        while Player.Position.X != self.Opt['homepos']['x'] or Player.Position.Y != self.Opt['homepos']['y']:
            Player.PathFindTo(self.Opt['homepos']['x'], self.Opt['homepos']['y'], self.Opt['homepos']['z'])
            Misc.Pause(self.Delay['timeout'])

        self.Deposit()
                
    def Recall(self):
        Journal.Clear()
        while Player.Mana < 10:
            Misc.Pause(500)
        # flizz prevention
        _x = Player.Position.X
        _y = Player.Position.Y
        Gumps.ResetGump()
        Items.UseItem(self.Current['book'])
        Gumps.WaitForGump(1431013363, self.Delay['timeout'])            
        Gumps.SendAction(1431013363, self.Current['rune'])
        Misc.Pause(self.Delay['cast'])
        if Journal.Search("blocked.") or self.ImHome:            
            Misc.Pause(self.Delay['recovery'])
            self.Current['rune'] += 6
            if self.Current['rune'] > (95 + int(self.UseChivalry) * 2):
                self.Current['rune'] = 5 + int(self.UseChivalry) * 2
                bindex = self.Minebook.index(self.Current['book'])
                if bindex >= len(self.Minebook):
                    self.Current['book'] = self.Trees['book'][0]
                else:
                    self.Current['book'] = self.Trees['book'][bindex+1]
            self.Recall()
        elif Journal.Search("recover") or self.ImHome:
            Misc.Pause(self.Delay['recovery'])
            self.Recall()
        elif Player.Position.X == _x and Player.Position.Y == _y:
            Misc.Pause(self.Delay['recovery'])
            self.Recall()

    def GetSpots(self):
        self.Spots = []
        for x in xrange(Player.Position.X - Radius, Player.Position.X + Radius + 1):
            for y in xrange(Player.Position.Y -Radius, Player.Position.Y + Radius + 1):
                tile = Statics.GetLandID(x,y,Player.Map)
                
                if tile > -1 and tile in self.MineTiles:
                    z = Statics.GetLandZ(x,y,Player.Map)
                    self.Spots.append(MineSpot(x, y, z, tile))
                
    def Mine(self):
        for spot in self.Spots:
            while not Journal.Search('no ore here') and not Journal.Search('cannot be seen') and not Journal.Search('mine here'):
                self.CheckShovel()
                
                if self.IsOverWeight:
                    self.GoHome()
                    self.Recall()
                    
                Items.UseItemByID(self.IDs['shovel'])
                Target.WaitForTarget(self.Delay['timeout'])
                Target.TargetExecute(spot.X, spot.Y, spot.Z)
                Misc.Pause(self.Delay['dig'])
                
                if not self.Opt['firebeetle'] is None:
                    ores = [o for o in Player.Backpack.Contains if o.ItemID in self.IDs['ore']]
                        
                    for ore in ores:
                        Items.UseItem(ore)
                        Target.WaitForTarget(self.Delay['timeout'])
                        Target.TargetExecute(self.Opt['firebeetle'])
                        Misc.Pause(self.Delay['smelt'])
                        
    def Main(self):
        while True:
            for book in self.Minebook:
                for rune in xrange(16):
                    r = rune * 6 + 5 + 2 * int(self.UseChivalry)
                    self.Current = {'book' : book, 'rune' : r}
                    self.Recall()
                    self.GetSpots()
                    self.Mine()
                    
                    
Mi = Miner()
Mi.Main()
