"""Mutant SMD: Meebleeps' Mutant generative synth (via the Mutant_Generative_Arduino_Synth Eurorack project), redesigned
for JLC SMD assembly on a board no larger than 100 mm, usable bare, behind a Eurorack panel, or in an enclosure.
  - Power: Eurorack 2x5 header (+12 V via SS14) and/or a 9 V barrel jack (via SS14), diode-OR'd into VRAW
    -> LM78M05 (DPAK) -> +5V for the Nano's 5V pin, the pots and the LED matrix module (the Nano's own regulator
    would overheat at 12 V with the matrix). Nano VIN unused.
  - Arduino Nano on headers, same pin map as the original firmware: A0-A5 pots, D3 D4 D5 D6 D10 D12 buttons
    (internal pull-ups), D7/D11/D13 = MAX7219 module CS/DIN/CLK, D8 sync in, D2 sync out, D9 audio PWM.
  - Pots: 6x B10k 9 mm (Alpha RD901F), 100n on each wiper. Buttons: 6x Tayda A-8796 (as GlitchStorm v3).
  - LED matrix: the standard MAX7219 8x8 plug-in module on two 1x5 headers (in header wired, out header mechanical).
    Its own supply V5M = +5V through R8 2R2 with C16 100u tantalum + C10/C11 (v1.0, 2026-10-19): the module's multiplex
    current pulses come from C16, not the Nano's 5 V, which is also the D9 audio PWM's high level.
  - Audio: D9 -> 1k/10n -> 10k/1n (2nd order, ~16 kHz) -> MCP6002 follower -> 10u -> 470 R -> OUT (100k bleed).
  - Sync in: 22k series, BAT54S clamp to 0 / +5V, 100k pull-down (safe for Eurorack gates up to ~12 V, Volca pulses).
  - Sync out: 1k series.
usage: build_mutant.py <out.kicad_sch>"""
from sch import *
import sys
OUT = sys.argv[1]
g = lambda n: round(n * 2.54, 3)
s = Sheet('MutantSMD', 'A2')
W = lambda *p: s.wire(*p)
P = s.P
def GND(p): s.power('GND', p)
def V5(p): s.power('+5V', p)
def lab(n, p, side='r'): s.label(n, p, side)
def to_lab(p, name, dx, side='r'):
    q = (p[0] + dx, p[1]); W(p, q); lab(name, q, side)
FR = 'Resistor_SMD:R_0805_2012Metric'; FC = 'Capacitor_SMD:C_0805_2012Metric'; FC12 = 'Capacitor_SMD:C_1206_3216Metric'
# JLC part numbers (proven on earlier boards; 10u = Samsung CL31A106KBHNNNE 50 V X5R 1206)
LR = {'470': 'C17710', '1k': 'C17513', '10k': 'C17414', '22k': 'C17560', '100k': 'C149504'}
LC = {'1n': 'C46653', '10n': 'C1710', '100n': 'C49678', '10u': 'C13585'}
def Rh(ref, v, cx, y, d='', text='t'): s.part(ref, 'Device', 'R', v, cx, y, 90, fp=FR, desc=d, text=text, lcsc=LR[v])
def Rv(ref, v, x, cy, side='r', d=''): s.part(ref, 'Device', 'R', v, x, cy, 0, fp=FR, desc=d, text=side, lcsc=LR[v])
def Ch(ref, v, cx, y, d='', text='t', fp=FC): s.part(ref, 'Device', 'C', v, cx, y, 90, fp=fp, desc=d, text=text, lcsc=LC[v])
def Cv(ref, v, x, cy, side='r', d='', fp=FC): s.part(ref, 'Device', 'C', v, x, cy, 0, fp=fp, desc=d, text=side, lcsc=LC[v])
HAND = dict(bom=False)

# ================================================================ POWER
s.box('POWER: Eurorack +12 V and/or 9 V barrel jack, diode-OR -> LM78M05 -> +5V', g(2), g(2), g(64), g(40))
s.part('J1', 'Connector_Generic', 'Conn_02x05_Odd_Even', 'EURORACK', g(10), g(14), 0, fp='Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical',
       desc='Eurorack 10-pin power (pins 1-2 = -12 V, red stripe); optional', text='t', **HAND)
for pin in ('1', '2'): s.noconnect(P('J1', pin))
for pin in ('3', '4', '5', '6', '7', '8'):
    q = P('J1', pin); left = int(pin) % 2 == 1
    e = (q[0] - g(2), q[1]) if left else (q[0] + g(2), q[1]); W(q, e); GND(e)
W(P('J1', '9'), (P('J1', '9')[0] - g(5), P('J1', '9')[1]), (P('J1', '9')[0] - g(5), P('J1', '9')[1] + g(3)), (P('J1', '10')[0] + g(5), P('J1', '9')[1] + g(3)), (P('J1', '10')[0] + g(5), P('J1', '10')[1]), P('J1', '10'))
p12 = (P('J1', '10')[0] + g(5), P('J1', '9')[1] + g(3))
W(p12, (g(22), p12[1])); lab('V12', (g(22), p12[1]))
s.part('J2', 'Connector', 'Barrel_Jack_Switch', 'DC 9V', g(8), g(31), 0, fp='Connector_BarrelJack:BarrelJack_Horizontal',
       desc='9 V DC jack, centre NEGATIVE (pedal standard), Tayda A-4118; optional', text='t', **HAND)
q = P('J2', '1'); W(q, (q[0] + g(2), q[1])); GND((q[0] + g(2), q[1]))
s.noconnect(P('J2', '3'))
q = P('J2', '2'); W(q, (q[0] + g(4), q[1])); lab('V9', (q[0] + g(4), q[1]))
# diode OR
for i, (ref, name, y) in enumerate((('D1', 'V12', g(10)), ('D2', 'V9', g(16)))):
    lab(name, (g(28), y), 'l')
    s.part(ref, 'Device', 'D_Schottky', 'SS14', g(32), y, 180, fp='Diode_SMD:D_SMA', desc=f'Reverse protection / OR ({name})', text='t', lcsc='C2480')
    W((g(28), y), P(ref, '2')); W(P(ref, '1'), (g(36), y))
W((g(36), g(10)), (g(36), g(16)))
vr = (g(36), g(13))
W(vr, (g(42), vr[1]))
Cv('C1', '10u', g(40), vr[1] + 3.81 + g(1), d='VRAW bulk (50 V: holds ~5-7 uF at 12 V, margin for hot-plug ringing)', fp=FC12); W((g(40), vr[1]), (g(40), vr[1] + g(1)), P('C1', '1')); GND(P('C1', '2'))
s.part('U1', 'Regulator_Linear', 'LM78M05_TO252', 'L78M05', g(50), vr[1], 0, fp='Package_TO_SOT_SMD:TO-252-2',
       desc='5 V regulator, 0.5 A DPAK: give the tab plenty of copper (~0.5-1 W at 12 V in)', text='t', lcsc='C58069')
W((g(42), vr[1]), P('U1', '1')); GND(P('U1', '2'))
vo = (g(58), vr[1]); W(P('U1', '3'), vo); V5((vo[0], vo[1]))
Cv('C2', '10u', g(56), vr[1] + 3.81 + g(1), d='+5V bulk', fp=FC12); W((g(56), vr[1]), (g(56), vr[1] + g(1)), P('C2', '1')); GND(P('C2', '2'))
Cv('C3', '100n', g(61), vr[1] + 3.81 + g(1), d='+5V decoupling'); W(vo, (g(61), vr[1]), (g(61), vr[1] + g(1)), P('C3', '1')); GND(P('C3', '2'))
s.power('PWR_FLAG', (g(40), vr[1])); s.power('PWR_FLAG', (g(14), g(36)))
W((g(14), g(36)), (g(16), g(36))); GND((g(16), g(36)))

# ================================================================ NANO
s.box('ARDUINO NANO (on headers): original Mutant pin map', g(68), g(2), g(118), g(40))
s.part('A1', 'MCU_Module', 'Arduino_Nano_v3.x', 'Arduino Nano', g(92), g(21), 0, fp='Module:Arduino_Nano', desc='Arduino Nano on female headers', text='ic', **HAND)
L = {'5': 'SYNC_OUT_D', '6': 'TONIC', '7': 'FUNC', '8': 'START', '9': 'SCALE', '10': 'CS', '11': 'SYNC_IN_D', '12': 'AUDIO_PWM',
     '13': 'REC', '14': 'MOSI', '15': 'RETRIG', '16': 'SCK', '19': 'P1', '20': 'P2', '21': 'P3', '22': 'P4', '23': 'P5', '24': 'P6'}
for pin, name in L.items():
    q = P('A1', pin); left = q[0] < g(92)
    to_lab(q, name, -g(3) if left else g(3), 'l' if left else 'r')
for pin in ('1', '2', '3', '28', '18', '17', '25', '26', '30'): s.noconnect(P('A1', pin))
V5(P('A1', '27'))
# The Nano symbol types its +5V pin as a power OUTPUT (the Nano normally supplies 5 V). Here U1 feeds that pin, so make
# it a power input in this schematic's copy of the symbol (otherwise ERC reports two power outputs tied together).
def _retype(node):
    if isinstance(node, list):
        if node and node[0] == 'pin' and any(isinstance(x, list) and x and x[0] == 'number' and x[1] == '27' for x in node):
            node[1] = Sym('power_in')
        for x in node: _retype(x)
_retype(s.libs['MCU_Module:Arduino_Nano_v3.x'])
GND(P('A1', '4')); W(P('A1', '29'), (P('A1', '29')[0], P('A1', '29')[1] + g(1))); GND((P('A1', '29')[0], P('A1', '29')[1] + g(1)))
s.text('VIN not used: +5V from U1 feeds the 5V pin (USB still works: the Nano has a diode on its USB 5 V).', g(70), g(38.5))

# ================================================================ POTS
s.box('POTS: 6x B10k 9 mm (Alpha RD901F), 100n on each wiper', g(122), g(2), g(162), g(40))
names = (('RV1', 'OSC TUNE', 'P1'), ('RV2', 'DECAY', 'P2'), ('RV3', 'MUTATION', 'P3'), ('RV4', 'SHAPE', 'P4'), ('RV5', 'COLOUR', 'P5'), ('RV6', 'STEP COUNT', 'P6'))
for i, (ref, panel, net) in enumerate(names):
    x = g(126 + (i % 3) * 12); y = g(10 + (i // 3) * 16)
    s.part(ref, 'Device', 'R_Potentiometer', 'B10k', x, y, 0, mirror='x', fp='Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical',
           desc=f'{panel} (A{i}); 9 mm Alpha RD901F', extra={'Panel': panel}, text=((x + g(2), y + g(4)), (x + g(2), y + g(5.2)), 'left'), **HAND)
    V5(P(ref, '3')); GND(P(ref, '1'))
    w = P(ref, '2'); wx = (w[0] + g(3), w[1]); W(w, wx); lab(net, wx)
    Cv(f'C{4 + i}', '100n', wx[0], wx[1] + 3.81 + g(1), d=f'{panel} smoothing'); W(wx, (wx[0], wx[1] + g(1)), P(f'C{4 + i}', '1')); GND(P(f'C{4 + i}', '2'))

# ================================================================ BUTTONS
s.box('BUTTONS: 6x Tayda A-8796 (DAIER TSL-A064) to GND, Nano internal pull-ups', g(2), g(44), g(64), g(72))
btns = (('SW1', 'FUNC'), ('SW2', 'TONIC'), ('SW3', 'SCALE'), ('SW4', 'START'), ('SW5', 'REC'), ('SW6', 'RETRIG'))
for i, (ref, net) in enumerate(btns):
    x = g(10 + (i % 3) * 20); y = g(52 + (i // 3) * 12)
    s.part(ref, 'Switch', 'SW_Push', net, x, y, 0, fp='SuperFreq:SW_Push_Round_D12mm_P5.00mm_DAIER_TSL-A064',
           desc=f'{net} button (Tayda A-8796)', extra={'Panel': net}, text='t', **HAND)
    lab(net, (P(ref, '1')[0] - g(2), y), 'l'); W((P(ref, '1')[0] - g(2), y), P(ref, '1'))
    W(P(ref, '2'), (P(ref, '2')[0] + g(1), y), (P(ref, '2')[0] + g(1), y + g(2))); GND((P(ref, '2')[0] + g(1), y + g(2)))

# ================================================================ MATRIX
s.box('LED MATRIX: MAX7219 8x8 module on two 1x5 headers', g(68), g(44), g(118), g(72))
s.part('J3', 'Connector_Generic', 'Conn_01x05', 'MATRIX IN', g(80), g(56), 0, fp='Connector_PinSocket_2.54mm:PinSocket_1x05_P2.54mm_Vertical',
       desc='MAX7219 module input header: VCC GND DIN CS CLK', text='t', **HAND)
for pin, name in (('3', 'MOSI'), ('4', 'CS'), ('5', 'SCK')):
    to_lab(P('J3', pin), name, -g(4), 'l')
q = P('J3', '1')
s.part('R8', 'Device', 'R', '2R2', q[0] - g(6), q[1], 90, fp='Resistor_SMD:R_1206_3216Metric', lcsc='C25369',
       desc='Matrix supply filter: with C16, keeps the MAX7219 multiplex pulses off the Nano / audio 5 V (1206: ~0.2 W worst case)',
       text=((q[0] - g(6), q[1] - g(2.6)), (q[0] - g(6), q[1] - g(1.6)), None))
W(P('R8', '1'), (q[0] - g(9), q[1])); V5((q[0] - g(9), q[1]))
W(P('R8', '2'), (q[0] - g(3), q[1]), q)
W((q[0] - g(3), q[1]), (q[0] - g(3), q[1] - g(3))); lab('V5M', (q[0] - g(3), q[1] - g(3)))
q = P('J3', '2'); W(q, (q[0] - g(11), q[1]), (q[0] - g(11), q[1] + g(9))); GND((q[0] - g(11), q[1] + g(9)))
s.part('J4', 'Connector_Generic', 'Conn_01x05', 'MATRIX OUT', g(108), g(56), 0, fp='Connector_PinSocket_2.54mm:PinSocket_1x05_P2.54mm_Vertical',
       desc='MAX7219 module output header: mechanical support only', text='t', **HAND)
for pin in '12345': s.noconnect(P('J4', pin))
Cv('C10', '10u', g(90), g(60), d='Matrix supply (local)', fp=FC12); lab('V5M', P('C10', '1')); GND(P('C10', '2'))
Cv('C11', '100n', g(94), g(60), d='Matrix supply (local)'); lab('V5M', P('C11', '1')); GND(P('C11', '2'))
s.part('C16', 'Device', 'C_Polarized', '100u', g(99), g(60), 0, fp='Capacitor_Tantalum_SMD:CP_EIA-3528-21_Kemet-B', lcsc='C122271',
       desc='Matrix supply reservoir: 100u 10 V tantalum (KEMET T491B107K010AT); with R8 ~720 Hz low-pass', text='r')
lab('V5M', P('C16', '1')); GND(P('C16', '2'))

# ================================================================ AUDIO OUT
s.box('AUDIO OUT: D9 PWM -> 2nd-order RC (~16 kHz) -> MCP6002 buffer -> OUT', g(122), g(44), g(162), g(72))
lab('AUDIO_PWM', (g(124), g(52)), 'l')
Rh('R1', '1k', g(124) + g(1) + 3.81, g(52), d='PWM filter 1'); W((g(124), g(52)), P('R1', '1'))
n1 = (P('R1', '2')[0] + g(1), g(52)); W(P('R1', '2'), n1)
Cv('C12', '10n', n1[0], n1[1] + 3.81 + g(1), d='PWM filter 1'); W(n1, (n1[0], n1[1] + g(1)), P('C12', '1')); GND(P('C12', '2'))
Rh('R2', '10k', n1[0] + g(1) + 3.81, g(52), d='PWM filter 2'); W(n1, P('R2', '1'))
n2 = (P('R2', '2')[0] + g(1), g(52)); W(P('R2', '2'), n2)
Cv('C13', '1n', n2[0], n2[1] + 3.81 + g(1), d='PWM filter 2'); W(n2, (n2[0], n2[1] + g(1)), P('C13', '1')); GND(P('C13', '2'))
s.part('U2', 'Amplifier_Operational', 'MCP6002-xSN', 'MCP6002', n2[0] + g(6), g(52) + 2.54, 0, unit=1, fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
       desc='Rail-to-rail output buffer', text='ic', lcsc='C7377', extra={'FT Rotation Offset': '270'})
W(n2, P('U2', '3'))
o = P('U2', '1'); m = P('U2', '2')
W(o, (o[0] + g(1), o[1]), (o[0] + g(1), m[1] + g(2)), (m[0] - g(1), m[1] + g(2)), (m[0] - g(1), m[1]), m)
Ch('C14', '10u', o[0] + g(2) + 3.81, o[1], d='Output DC block', fp=FC12); W((o[0] + g(1), o[1]), P('C14', '1'))
no = (P('C14', '2')[0] + g(1), o[1]); W(P('C14', '2'), no)
Rv('R3', '100k', no[0], no[1] + 3.81 + g(1), d='Output bleed'); W(no, (no[0], no[1] + g(1)), P('R3', '1')); GND(P('R3', '2'))
Rh('R4', '470', no[0] + g(1) + 3.81, no[1], d='Output protection'); W(no, P('R4', '1'))
s.part('J5', 'Connector_Audio', 'AudioJack2_SwitchT', 'OUT', P('R4', '2')[0] + g(5) + 5.08, no[1], 180,
       fp='Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles', desc='Audio out (Thonkiconn PJ398SM)', text='t', **HAND)
W(P('R4', '2'), P('J5', 'T')); GND(P('J5', 'S')); s.noconnect(P('J5', 'TN'))
s.part('U2', 'Amplifier_Operational', 'MCP6002-xSN', 'MCP6002', g(130), g(66), 0, unit=2, fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', text='ic', lcsc='C7377', extra={'FT Rotation Offset': '270'})
q = P('U2', '5'); W(q, (q[0] - g(1), q[1])); GND((q[0] - g(1), q[1]))
o2 = P('U2', '7'); m2 = P('U2', '6'); W(o2, (o2[0] + g(1), o2[1]), (o2[0] + g(1), m2[1] + g(2)), (m2[0] - g(1), m2[1] + g(2)), (m2[0] - g(1), m2[1]), m2)
s.text('U2B unused: follower parked at 0 V.', g(136), g(70))
s.part('U2', 'Amplifier_Operational', 'MCP6002-xSN', 'MCP6002', g(154), g(66), 0, unit=3, fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', text='ic', lcsc='C7377', extra={'FT Rotation Offset': '270'})
V5(P('U2', '8')); GND(P('U2', '4'))
Cv('C15', '100n', g(158), g(66), d='U2 decoupling'); V5(P('C15', '1')); GND(P('C15', '2'))

# ================================================================ SYNC
s.box('SYNC: in (22k + BAT54S clamp, 100k pull-down) and out (1k), Volca / Eurorack compatible', g(2), g(76), g(118), g(104))
s.part('J6', 'Connector_Audio', 'AudioJack2_SwitchT', 'SYNC IN', g(10), g(88), 0, mirror='x', fp='Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles',
       desc='Sync in (Thonkiconn PJ398SM)', text='t', **HAND)
GND(P('J6', 'S')); s.noconnect(P('J6', 'TN'))
Rh('R5', '22k', P('J6', 'T')[0] + g(2) + 3.81, P('J6', 'T')[1], d='Sync in: current limit for the clamp'); W(P('J6', 'T'), P('R5', '1'))
ns = (P('R5', '2')[0] + g(3), P('R5', '2')[1]); W(P('R5', '2'), ns)
Rv('R6', '100k', ns[0], ns[1] + g(1) + 3.81, d='Sync in pull-down'); W(ns, P('R6', '1')); GND(P('R6', '2'))
W(ns, (ns[0], ns[1] - g(5)), (ns[0] + g(2), ns[1] - g(5))); lab('SYNC_IN_D', (ns[0] + g(2), ns[1] - g(5)))
ns2 = (ns[0] + g(5), ns[1]); W(ns, ns2)
# BAT54S: pin 1 = anode of the lower diode -> GND, pin 2 = cathode of the upper diode -> +5V, COM = node
s.part('D3', 'Diode', 'BAT54S', 'BAT54S', ns2[0] + 5.08, ns2[1], 90, mirror='y', fp='Package_TO_SOT_SMD:SOT-23', desc='Sync in clamp to 0 V / +5V', text='r', lcsc='C19726', extra={'FT Rotation Offset': '180'})
W(ns2, P('D3', '3'))
GND(P('D3', '1')); V5(P('D3', '2'))
lab('SYNC_OUT_D', (g(64), g(88)), 'l')
Rh('R7', '1k', g(64) + g(1) + 3.81, g(88), d='Sync out protection'); W((g(64), g(88)), P('R7', '1'))
s.part('J7', 'Connector_Audio', 'AudioJack2_SwitchT', 'SYNC OUT', P('R7', '2')[0] + g(5) + 5.08, g(88), 180,
       fp='Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles', desc='Sync out (Thonkiconn PJ398SM)', text='t', **HAND)
W(P('R7', '2'), P('J7', 'T')); GND(P('J7', 'S')); s.noconnect(P('J7', 'TN'))

notes = ('Redesign of the Mutant Eurorack module (MeeBleeps Mutant synth) for SMD (JLC) on a <= 100 mm board.',
         'Panel geometry kept from the original (pots, buttons, matrix, jacks), so the original front panel still fits.',
         'Bare / Eurorack: fit J1 (10-pin). Enclosure: fit J2 (9 V barrel). Both can be fitted (diode-OR).',
         'Firmware: Mutant_Updated (Mozzi 2), unchanged pin map.')
for i, t in enumerate(notes): s.text(t, g(122), g(80 + 2.5 * i), 1.4)
s.write(OUT, shift=(g(4), g(4)), title_block={'title': 'Mutant SMD', 'rev': '1.0', 'company': 'Super-Freq',
        'comments': ['MeeBleeps Mutant generative synth, SMD redesign, <= 100 mm board', 'Eurorack 10-pin and/or 9 V barrel power, Nano on headers']})
