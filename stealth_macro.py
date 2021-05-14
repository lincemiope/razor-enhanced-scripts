from time import time
east = (1058, 750)
west = (926, 570)

walk_pause = 300
last_hide = 0
def hide():
    if time() - 11 >= last_hide:
        Player.UseSkill('Hiding')
        last_hide = time()
  
while Player.GetRealSkillValue('Stealth') < Player.GetSkillCap('Stealth'):
    if Player.Direction == 'East':
        while Player.Position.X < east[0]:
            while Player.Visible:
                hide()
                Misc.Pause(500)
            hide()
            Player.Walk('East')
            Misc.Pause(walk_pause)
        Player.Walk('West')
        Misc.Pause(walk_pause)
    else:
        while Player.Position.X > west[0]:
            while Player.Visible:
                hide()
                Misc.Pause(500)
            hide()
            Player.Walk('West')
            Misc.Pause(walk_pause)
        Player.Walk('East')
        Misc.Pause(walk_pause)