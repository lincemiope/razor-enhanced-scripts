"""======

======"""
import math
class NinjaTrainer:
    LMC = 0
    can_kill_mirrors=False
    def __init__(self):

        self.LMC = Player.SumAttribute('Lower Mana Cost')

    def WaitForMana(self, mana):
        mp = int(math.ceil(mana * (1.00 - self.LMC / 100.)))
        
        while Player.Mana < mp:
            Misc.Pause(500)
    
    def CheckMirrors(self, spell = "", mana = 0):
        fil = Mobiles.Filter()
        fil.Enabled = True
        fil.RangeMax = 2
        mobiles = Mobiles.ApplyFilter(fil)
        res = False
        mirrors = [m.Serial for m in mobiles if (m.Body == Player.Body and m.Serial != Player.Serial)]
        res = not mirrors is None
        for mirror in mirrors:
            if spell != '':
                self.WaitForMana(mana)
                Spells.CastNinjitsu(spell)
                Misc.Pause(500)
                
            while Mobiles.FindBySerial(mirror):                
                Player.Attack(mirror)
                Misc.Pause(2000)
                
        return res
        
    def Main(self):
        while Player.GetSkillValue('Ninjitsu') < Player.GetSkillCap('Ninjitsu'):
            ninj = Player.GetSkillValue('Ninjitsu')
            
            if ninj < 40.0:
                Player.HeadMessage('You should train it to 40.0 from a Ninjitsu Instructor', 76)
                break
            
            elif ninj < 67.5:
                self.WaitForMana(10)
                Spells.CastNinjitsu('Mirror Image')
                Misc.Pause(1500)
                spell = '' if ninj < 57.5 or not self.can_kill_mirrors else 'Focus Attack'
                  
                if Player.Followers == Player.FollowersMax and self.CheckMirrors(spell, 10):
                    Misc.Pause(500)
                else:
                    Misc.Pause(1500)
                    
            elif ninj < 85.0:
                for x in [4, -4]:
                    for i in xrange(4):
                        self.WaitForMana(15)
                        
                        while Player.Visible:
                            Player.UseSkill('Hiding')
                            Misc.Pause(2750)
                            
                        Spells.CastNinjitsu('Shadow jump')
                        Target.WaitForTarget(8000)
                        Target.TargetExecute(Player.Position.X + x, Player.Position.Y, Player.Position.Z)
                        Misc.Pause(3000)
                        
            else:       
                self.WaitForMana(10)
                Spells.CastNinjitsu("Mirror Image")
                Misc.Pause(1500)
                
                if self.CheckMirrors('Death Strike', 30):
                    Misc.Pause(500)
                    
                else:
                    Misc.Pause(1500)
                

            
NT = NinjaTrainer()
NT.Main()
