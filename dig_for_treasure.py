tmap = None
try:
    tmap = [i.Serial for i in Player.Backpack.Contains if i.ItemID == 0x14EC][0]
except:
    pass

rounded = [i for i in xrange(-2, 3) if i != 0]
def dig(offset_x=0, offset_y=0, offset_z=0):
    Journal.Clear()
    Misc.WaitForContext(tmap, 7000)
    Misc.ContextReply(tmap, 1)
    Target.WaitForTarget(7000)
    Target.TargetExecute(Player.Position.X + offset_x, Player.Position.Y + offset_y, Player.Position.Z + offset_z)
    Misc.Pause(700)

already = []
def alreadyBeenThere():
    a = [i for i in already if Player.Position.X == i[0] and Player.Position.Y == i[1] and Player.Position.Z == i[2]]
    return len(a) > 0

def alternative1():
    Journal.Clear()
    dig()

    while Journal.Search('dig and dig') or Journal.Search('no treasure seems to be here'):
        if alreadyBeenThere():
            Player.HeadMessage(77, "There's nothing here")
            Misc.Pause(700)
            continue
        already.append((Player.Position.X, Player.Position.Y, Player.Position.Z))
        Journal.Clear()
        dig()

def aletrnative2():
    if tmap:
        dig()
        Misc.Pause(700)
        if Journal.Search('dig and dig'):
            found = False
            for x in rounded:
                if found:
                    break
                for y in rounded:
                    Player.HeadMessage(77, 'Trying (%s, %s) offset' % (x, y))
                    dig(x, y)
                    Misc.Pause(700)
                    if not Journal.Search('dig and dig') and not Journal.Search('no treasure seems to be here'):
                        found = True
                        break

alternative1()