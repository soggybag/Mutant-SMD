"""Add GND pours (F and B) over the whole Mutant SMD board. Run from the project folder with KiCad's python."""
import pcbnew
b = pcbnew.LoadBoard('MutantSMD.kicad_pcb'); MM = pcbnew.FromMM
gnd = b.FindNet('GND')
x0, y0, x1, y1 = 101.016 + 0.3, 55.3 + 0.3, 166.294 - 0.3, 155.3 - 0.3
for layer, name in ((pcbnew.F_Cu, 'GND_F'), (pcbnew.B_Cu, 'GND_B')):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(gnd); z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): o.Append(MM(x), MM(y))
    z.SetLocalClearance(MM(0.3)); z.SetMinThickness(MM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetThermalReliefGap(MM(0.4)); z.SetThermalReliefSpokeWidth(MM(0.5))
    b.Add(z)
pcbnew.SaveBoard('MutantSMD.kicad_pcb', b)
print('zones added')
