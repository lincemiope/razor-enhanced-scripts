# magery trainer
class SpellStat:
    def __init__(self, minimum, code, circle, target=None):
        self.minimum = minimum
        self.code = code
        self.circle = circle
        self.target = target

spells = [
    SpellStat(90.0, 'Earthquake', 8),
    SpellStat(75.0, 'Mana Vampire', 7, 'self'),
    SpellStat(65.0, 'Invisibility', 6, 'self'),
    SpellStat(55.0, 'Magic Reflection', 5),
    SpellStat(45.0, 'Curse', 4, 'self'),
    SpellStat(29.0, 'Bless', 3, 'self'),
]

circleMana = [0, 4, 6, 9, 11, 14, 20, 40, 50]
circleDelay = lambda x: (0.25 + x * 0.25) * 1000
circleRecovery = lambda x: (0.25 + x * 0.7) * 1000
lmc = Player.SumAttribute("Lower Mana Cost")

def waitForMana(circle):
    return int(circleMana[circle] * (1.0 - lmc / 100.0))
    
while Player.GetSkillValue('Magery') < Player.GetSkillCap('Magery'):
    skill_value = Player.GetSkillValue('Magery')
    spell = None

    for s in spells:
        if skill_value >= s.minimum:
            spell = s
            break

    if not spell:
        break

    while Player.Mana < waitForMana(spell.circle):
        Player.UseSkill('Meditation')
        Misc.Pause(4000)

    Spells.CastMagery(spell.code)

    if spell.target:
        Target.WaitForTarget(circleDelay(spell.circle))

        if spell.target == 'self':
            Target.Self()
        elif spell.target == 'last':
            Target.Last()

    Misc.Pause(circleRecovery(spell.circle))
    