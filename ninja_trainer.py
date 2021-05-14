lmc = 42 # Player.SumAttribute('Lower Mana Cost')

neededMana = 6
Player.HeadMessage(neededMana, neededMana)
class Transform:
    def __init__(self, minimum, button, name):
        self.minimum = minimum
        self.button = button
        self.name = name
        
        
transforms = [
    Transform(50.0, 8, 'giant serpent'),
    Transform(40.0, 10, 'cat')
]

while Player.GetRealSkillValue('Ninjitsu') < Player.GetSkillCap('Ninjitsu'):
    Spells.CastNinjitsu('Animal Form')
    Misc.Pause(2000)
    if not Gumps.HasGump():
        Misc.Pause(1000)
        continue
    for t in transforms:
        if Player.GetSkillValue('Ninjitsu') >= t.minimum:
            Player.HeadMessage(77, 'Attempting %s form' % t.name)
            Gumps.SendAction(3027724650, t.button)
            break

    Misc.Pause(3000)