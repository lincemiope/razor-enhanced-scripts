trash_bag = Items.FindByID(0x09B2, 0x0495, Player.Backpack.Serial)
res_types = {
    'fish' : [
        0x09CC, 0x09CD, 0x09CE, 0x09CF,
        0x4307, 0x44C4, 0x44C6, 0x4306,
        0x44C5, 0x4303, 0x44C3
        ],
    'trash' : [5901, 5905, 5903, 5899, 0x0DD6, 0x14F8],
    'keep' : [0x097A, 0x3196, 0x573A, 0x14EE, 0x0DCA, 0x0996, 0x0EED, 0x99F, 0x14EC]
}

def cut_fish():
    fish = [i.Serial for i in Player.Backpack.Contains if i.ItemID in res_types['fish']]
    for f in fish:
        Items.UseItemByID(0x0F52, 0)
        Target.WaitForTarget(6000)
        Target.TargetExecute(f)
        Misc.Pause(600)

def throw_trash():
    trash = [i.Serial for i in Player.Backpack.Contains if i.ItemID in res_types['trash']]
    for t in trash:
        Items.Move(t, trash_bag, 0)
        Misc.Pause(600)

while Player.GetSkillValue('Fishing') < 100.0:
    cut_fish()
    throw_trash()
    Journal.Clear()
    Items.UseItemByID(0x0DC0, 0)
    Target.WaitForTarget(7000)
    Target.TargetExecuteRelative(Player.Serial, 4)
    while True:
        if Journal.SearchByName('You fish a while', 'System') or Journal.SearchByName('You pull out', 'System'):
            break
        if Journal.SearchByName("The fish don't seem", 'System'):
            Player.ChatSay(40, 'Forward')
            Misc.Pause(4000)
            Player.ChatSay(40, 'Stop')
            break
        Misc.Pause(1000)
