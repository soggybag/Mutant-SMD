"""Place the Mutant SMD board (unrouted) from the schematic netlist.
Panel parts keep the ORIGINAL Mutant board's positions (Eagle mm, origin bottom-left, y up) so the original front panel fits.
Board frame: KiCad X = 100 + x_e, Y = 160 - y_e. Outline x_e 1.016-66.294 (65.3 mm, 13 HP), y_e 4.7-104.7 (100.0 mm).
Panel side = F (front). Nano, Eurorack header and barrel jack on B. SMD on F (JLC, one side).
Run from the project folder with KiCad's python:
  kicad-cli sch export netlist -o <tmp>/mut.net MutantSMD.kicad_sch
  scripts/buildpcb_mutant.py <tmp>/mut.net
Then check overlaps and route with _tools/autoroute.py. Don't re-run after hand edits: it overwrites the board."""
import sys, json, math
sys.path.insert(0, 'scripts')
from sx import parse, find, find1
import pcbnew
NET = sys.argv[1]
MM = pcbnew.FromMM; mm = pcbnew.ToMM
FPDIR = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
POTSTEP = '${KIPRJMOD}/3dmodels/pot_RD901F_T18_shaft_alpha_9mm_vertical.step'
BTNSTEP = '${KIPRJMOD}/3dmodels/SW_Push_Round_D12mm_DAIER_TSL-A064.step'
X0, Y0 = 100.0, 160.0
K = lambda x, y: (X0 + x, Y0 - y)          # Eagle -> KiCad
OUTLINE = (1.016, 4.7, 66.294, 104.7)

# ---------------- netlist
r = parse(open(NET).read())
comps = {}
for c in find(find1(r, 'components'), 'comp'):
    ref = find1(c, 'ref')[1]
    props = {find1(p, 'name')[1]: (find1(p, 'value') or [0, ''])[1] for p in find(c, 'property')}
    flds = {}
    for fs in find(c, 'fields'):
        for f in find(fs, 'field'):
            flds[find1(f, 'name')[1]] = f[2] if len(f) > 2 and not isinstance(f[2], list) else ''
    flds['Description'] = (find1(c, 'description') or [0, ''])[1]
    comps[ref] = dict(value=find1(c, 'value')[1], fp=find1(c, 'footprint')[1], fields=flds, props=props, tstamp=find1(c, 'tstamps')[1])
pinnet = {}
for n in find(find1(r, 'nets'), 'net'):
    for nd in find(n, 'node'):
        pinnet[(find1(nd, 'ref')[1], find1(nd, 'pin')[1])] = find1(n, 'name')[1]

# ---------------- placement (Eagle coords). kind: 'shaft' = pot shaft, 'barrel' = jack barrel, 'origin' = footprint origin,
# 'pads' = centre of the pads, 'edge' = barrel jack (handled below)
POTS = {'RV1': (33.655, 35.611), 'RV2': (7.823, 35.611), 'RV3': (33.655, 11.430), 'RV4': (7.823, 11.430),
        'RV5': (59.487, 35.611), 'RV6': (59.487, 11.430)}
BTNS = {'SW1': (7.823, 81.28), 'SW2': (7.823, 67.31), 'SW3': (7.925, 53.34), 'SW4': (59.487, 81.28), 'SW5': (59.487, 67.31), 'SW6': (59.487, 53.365)}
JACKS = {'J6': (25.044, 97.815), 'J7': (42.266, 97.79), 'J5': (59.487, 97.815)}
SMD = {  # ref: (x_e, y_e, rot)
    # power: band between the pot rows (y 18-29); D2 (the 9 V input diode) sits beside the barrel jack so V9 stays short
    'D1': (31.0, 26.2, 0), 'D2': (15.5, 99.0, 90), 'C1': (37.0, 23.7, 90), 'U1': (45.5, 23.7, 180),
    'C2': (54.5, 23.7, 90), 'C3': (58.0, 23.7, 90),
    # pot wiper caps: in the gaps beside the pots
    'C4': (22.6, 35.611, 90), 'C5': (18.6, 35.611, 90), 'C6': (22.6, 11.43, 90), 'C7': (18.6, 11.43, 90),
    'C8': (45.0, 35.611, 90), 'C9': (45.0, 11.43, 90),
    # matrix supply: beside the matrix IN socket
    'C10': (51.6, 61.5, 90), 'C11': (51.6, 57.5, 90),
    # audio: under the matrix module, between the Nano's pin rows (x 27.5-40)
    'R1': (29.5, 60.0, 90), 'C12': (32.0, 60.0, 90), 'R2': (34.5, 60.0, 90), 'C13': (37.0, 60.0, 90),
    'U2': (33.5, 68.5, 0), 'C15': (38.6, 68.5, 90), 'C14': (33.5, 76.0, 0), 'R3': (29.5, 79.5, 90), 'R4': (33.5, 81.5, 0),
    # sync: left strip under the matrix (x 20.8-24.5) and right strip (x 42.5-47)
    'R5': (22.6, 84.5, 90), 'D3': (22.6, 79.5, 90), 'R6': (22.6, 56.5, 90), 'R7': (45.0, 84.5, 90),
}

def lib_path(fpid):
    lib, name = fpid.split(':')
    return ('SuperFreq.pretty' if lib == 'SuperFreq' else FPDIR + lib + '.pretty'), name

fps = {}
for ref, c in comps.items():
    path, name = lib_path(c['fp'])
    f = pcbnew.FootprintLoad(path, name)
    assert f, c['fp']
    f.SetFPID(pcbnew.LIB_ID(c['fp'].split(':')[0], name))
    fps[ref] = f

b = pcbnew.BOARD()
nets = {}
for name in sorted(set(pinnet.values())):
    ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni); nets[name] = ni

x0, y0, x1, y1 = OUTLINE
corners = [K(x0, y0), K(x1, y0), K(x1, y1), K(x0, y1)]
for (ax, ay), (bx, by) in zip(corners, corners[1:] + corners[:1]):
    sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT); sh.SetLayer(pcbnew.Edge_Cuts); sh.SetWidth(MM(0.1))
    sh.SetStart(pcbnew.VECTOR2I(MM(ax), MM(ay))); sh.SetEnd(pcbnew.VECTOR2I(MM(bx), MM(by))); b.Add(sh)

def pads_centre(f):
    xs = [p.GetPosition().x for p in f.Pads()]; ys = [p.GetPosition().y for p in f.Pads()]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2

def put(f, x, y, rot=0, side='F'):
    f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    if side == 'B': f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot)

def move_by(f, dx, dy):
    f.SetPosition(pcbnew.VECTOR2I(f.GetPosition().x + int(dx), f.GetPosition().y + int(dy)))

def model(f, step, off=(0, 0, 0), rot=(0, 0, 0)):
    f.Models().clear(); m = pcbnew.FP_3DMODEL(); m.m_Filename = step
    m.m_Offset = pcbnew.VECTOR3D(*off); m.m_Rotation = pcbnew.VECTOR3D(*rot); f.Models().push_back(m)

for ref, c in sorted(comps.items()):
    f = fps[ref]; b.Add(f)
    f.SetReference(ref); f.SetValue(c['value'])
    f.SetPath(pcbnew.KIID_PATH('/' + c['tstamp'])); f.SetSheetname('Root'); f.SetSheetfile('MutantSMD.kicad_sch')
    for k, v in c['fields'].items():
        if k in ('Footprint', 'Reference', 'Value'): continue
        f.SetField(k, v); f.GetField(k).SetVisible(False)
    hand = 'exclude_from_bom' in c['props']
    f.SetExcludedFromBOM(hand); f.SetExcludedFromPosFiles(hand)
    for p in f.Pads():
        k = (ref, p.GetNumber())
        if k in pinnet: p.SetNet(nets[pinnet[k]])

    if ref in POTS:
        sx, sy = K(*POTS[ref]); left_col = POTS[ref][0] < 20
        rot = 180 if left_col else 0           # pins away from the board edge
        dx, dy = (7.5, 2.5) if rot == 0 else (-7.5, -2.5)
        put(f, sx - dx, sy - dy, rot)
        model(f, POTSTEP, (6.6, -2.5, 4), (-90, 0, 0))
    elif ref in BTNS:
        put(f, *K(*BTNS[ref]), 0); model(f, BTNSTEP)
    elif ref in JACKS:
        bx, by = K(*JACKS[ref]); put(f, bx, by + 6.48, 180)   # tip pin toward the top edge
    elif ref in ('J3', 'J4'):
        x = 48.298 if ref == 'J3' else 19.012
        put(f, *K(x, 69.977 - 5.08), 180)                      # pin 1 at the bottom, as the original
    elif ref == 'A1':
        put(f, 0, 0, 180, 'B'); cx, cy = pads_centre(f); tx, ty = K(33.655, 67.0)   # USB end toward the pots
        move_by(f, MM(tx) - cx, MM(ty) - cy)
    elif ref == 'J1':
        put(f, 0, 0, 90, 'B'); cx, cy = pads_centre(f); tx, ty = K(16.0, 23.5)
        move_by(f, MM(tx) - cx, MM(ty) - cy)
    elif ref == 'J2':
        # barrel jack on B, opening flush with the top edge, in the original power switch's corner
        best = None
        for rot in (0, 90, 180, 270):
            put(f, 0, 0, rot, 'B') if rot == 0 else None
            f.SetOrientationDegrees(rot)
            cy = f.GetCourtyard(pcbnew.B_CrtYd).BBox(); p1 = [p for p in f.Pads() if p.GetNumber() == '1'][0].GetPosition()
            if abs(mm(p1.y - cy.GetY()) - 14.04) < 0.5: best = rot; break
        f.SetOrientationDegrees(best)
        cy = f.GetCourtyard(pcbnew.B_CrtYd).BBox(); tx, ty = K(8.0, OUTLINE[3])
        move_by(f, MM(tx) - (cy.GetX() + cy.GetWidth() // 2), MM(ty) - cy.GetY())
    elif ref in SMD:
        x, y, rot = SMD[ref]; put(f, *K(x, y), rot)
    else:
        print('UNPLACED', ref)

pcbnew.SaveBoard('MutantSMD.kicad_pcb', b)
# SaveBoard rewrites the project's net classes: use the GlitchStorm v3 classes (Power 0.5 mm, default 0.25)
src = json.load(open('../GlitchStorm v3/GlitchStorm3.kicad_pro'))
p = json.load(open('MutantSMD.kicad_pro'))
p['net_settings'] = src['net_settings']
p['net_settings']['netclass_patterns'] = [{'netclass': 'Power', 'pattern': n} for n in ('+5V', 'GND', '/V12', '/V9', 'Net-(D1-K)')]
json.dump(p, open('MutantSMD.kicad_pro', 'w'), indent=2)
print('board written')
