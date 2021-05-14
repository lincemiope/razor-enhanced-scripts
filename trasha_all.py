src = Target.PromptTarget()

dst = Items.FindByID(0x09B2, 0x0495, Player.Backpack.Serial)

cont_src = Items.FindBySerial(src)

Items.WaitForContents(cont_src, 7000)
Items.WaitForContents(dst, 7000)

items = [i.Serial for i in cont_src.Contains]

for i in items:
    Items.Move(i, dst, 0)
    Misc.Pause(800)