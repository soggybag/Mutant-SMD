# Mutant SMD: design notes

## Original (Eagle, `Mutant_Generative_Arduino_Synth/Eagle Files - PCB/`)

- **Board:** 65.3 × 106.4 mm, all through-hole.
- **Arduino Nano:** on the back.
- **Controls:**
  - 6 × 9 mm 10k pots on A0–A5: OSC TUNE, DECAY, MUTATION, SHAPE, COLOUR, STEP COUNT.
  - 6 buttons, internal pull-ups: D4 FUNC, D3 TONIC, D6 SCALE, D5 START, D10 REC, D12 RETRIGGER/CLONE.
- **LED matrix:** a MAX7219 8×8 module on two 1×5 headers (D11 DIN, D7 CS, D13 CLK).
- **Sync:** sync in on D8 with a 10k pull-down, no protection; sync out on D2 direct.
- **Audio:** D9 PWM → 270 Ω / 100 nF → jack.
- **Power:**
  - **16-pin Eurorack:** +12 V straight to Nano VIN, no reverse protection. The Nano's own regulator powers the matrix.
  - **9 V battery:** via JST and an on/off toggle.

## Changes

| Block | Change | Why |
|---|---|---|
| Power | **2×5 (10-pin) Eurorack header** (+12 V only) **and/or a 9 V barrel jack** (Tayda A-4118, centre negative), each through an **SS14**, diode-OR'd into VRAW | Bare / Eurorack / enclosure from one board. Reverse protection on both |
| 5 V | **LM78M05 (DPAK)** → the Nano's **5V pin**; VIN unused | The Nano's regulator would dissipate ~0.5–1 W from 12 V with the matrix lit. The DPAK tab sits on a copper pour. USB still works (the Nano has a diode on its USB 5 V) |
| Sync in | 22k series + **BAT54S** clamp to 0 / 5 V + 100k pull-down | Eurorack gates (5–12 V) would exceed the Nano's 5.5 V pin limit |
| Sync out | 1k series | Protects D2 from shorts and hot-plugging |
| Audio | **2nd-order RC (1k/10n + 10k/1n, ~16 kHz) → MCP6002 follower → 10µ → 470 Ω**, 100k bleed | Less PWM whine, low output impedance, ~5 Vpp (fine for modular or line) |
| Matrix supply (2026-10-19) | **R8 2.2 Ω (1206) + C16 100µ tantalum** (KEMET T491B, 3528) feed the module's own rail **V5M**; C10 10µ / C11 100n moved onto V5M | The MAX7219 multiplexes at ~800 Hz with current pulses up to ~300 mA. On a shared 5 V they wobble the Nano's rail, and D9's PWM high level *is* that rail, so the wobble lands in the audio as a whine no output filter can remove. R8/C16 (~720 Hz low-pass) let C16 supply the pulses |
| Pots | **Alpha RD901F 9 mm B10k** + **100n on each wiper** | Tayda-sourced; quieter readings |
| Buttons | **Tayda A-8796** (round Ø12 body, Ø9 cap, 4 pins on a 5 mm square) | As GlitchStorm v3. 14.7 mm tall, so the cap clears a panel ~10 mm above the board |
| Passives | 0805 / 1206 SMD | JLC assembly |
| Battery / on-off switch | dropped | The barrel jack covers enclosure use. A 9 V battery clip can go to a barrel plug |

**Kept:** the Nano on headers, the plug-in MAX7219 module, the pin map (the firmware runs unchanged).

## Current budget (+5V)

- **Nano:** ~25 mA.
- **MCP6002:** < 1 mA.
- **Matrix:** brightness 4/15 in normal use, ~1.4 mA per lit LED, so ~45 mA half-lit and ~90 mA all lit. The start-up sweep runs to 15/15 briefly (up to ~300 mA for a moment).
- **Total typical:** ~70–120 mA.
- **R8 drop:** ~0.1–0.2 V in normal use; ~0.66 V (V5M ≈ 4.3 V, MAX7219 min 4.0 V) and ~0.2 W in R8 only during the 15/15 start-up sweep.
- **Extended parts added for the filter (~$3 fee each):** R8 2.2 Ω 1206 Uniroyal 1206W4J022JT5E **C25369**; C16 KEMET T491B107K010AT **C122271**. No 2.2 Ω or suitable bulk cap is a JLC Basic part.
- **LCSC numbers (2026-10-11):** every SMD part has one. U1 = **L78M05ABDT-TR C58069** (the AB grade is JLC's Basic part; same regulator, tighter tolerance). The 10µ caps (C1, C2, C10, C14) = **CL31A106KBHNNNE 50 V X5R 1206, C13585**; check Basic/Extended when ordering. Others are the proven parts from earlier boards (resistors C17513/C17414/C17560/C149504/C17710, 100n C49678, 10n C1710, 1n C46653, SS14 C2480, BAT54S C19726, MCP6002 C7377).
- **Why 50 V for the 10µ ceramics:** X5R loses capacitance with DC bias. A 25 V 1206 holds only ~3–5 µF at 12 V; the 50 V part holds ~5–7 µF (the 78M05 needs only 0.33 µF in / 0.1 µF out). All-ceramic input + Eurorack cable can ring to ~2× the rail on hot-plug (~24 V): fine for a 50 V cap and the 78M05 (35 V max), marginal for 25 V. An electrolytic on VRAW would add damping but isn't needed.
- **LM78M05 dissipation at 12 V in:** (11.7 − 5) × 0.1 A ≈ 0.7 W. That's fine for a DPAK on ~2 cm² of copper. At 9 V in it's about half.

## Board plan (next)

- **Outline:** 65.3 mm wide (fits 13 HP) × ≤ 100 mm.
- **Control positions:** copied from the original Eagle board (mm, origin bottom-left):
  - **Pots** (shafts): (7.82, 11.43), (33.66, 11.43), (59.49, 11.43), (7.82, 35.61), (33.66, 35.61), (59.49, 35.61).
  - **Buttons:** (7.82, 53.34 / 67.31 / 81.28) and (59.49, 53.37 / 67.31 / 81.28).
  - **Matrix headers:** x 19.01 and 48.30, centred at y 69.98.
  - **Jacks:** SYNC IN (25.04, 97.82), SYNC OUT (42.27, 97.79), OUT (59.49, 97.82). The original power switch at (7.82, 97.82) is dropped (free space).
- **The span is tight:** pot bodies (±6.5 mm, pins turned sideways) at y 11.43 and jack bodies (~±5 mm) at y 97.8 need about 98 mm. A 100 mm outline only works if the jack pins point into the board (as the original's R180).
- **Placement:**
  - **Nano:** on the back (as the original).
  - **Eurorack header:** on the back.
  - **Barrel jack:** on an edge, top or side, for enclosures. Free on the left of the jack row where the power switch was.
  - **SMD parts:** on the top side between controls, all JLC-assembled on one side.
- **To check:** the A-8796 (Ø12 body) at the original button positions clears the pots and matrix module (the inner body edge ~13.8 mm vs the module edge ~17.6 mm: OK on paper).

## PCB v0.1 (2026-10-11)

- **Outline:** **65.3 × 100.0 mm** (13 HP wide). Frame X = 100 + x_e, Y = 160 − y_e (Eagle mm).
- **Generated by `scripts/buildpcb_mutant.py`** (placement from the netlist) + `scripts/add_zones.py` (GND pours F/B), routed with `_tools/autoroute.py --passes 600`.
- **Result:** 6 vias; DRC 0 errors, 0 unconnected; schematic parity clean. Power-class tracks (+5V, GND, V12, V9, VRAW) are 0.5 mm. 17 silkscreen warnings, for the silk pass.
- **Front (panel side):**
  - the pots, buttons, jacks and matrix sockets, all at the original Mutant positions;
  - all the SMD parts (JLC assembles one side).
- **Back:**
  - the **Nano** upright between the matrix sockets, USB toward the pots;
  - the **Eurorack 2×5 header**, horizontal between the left pot rows (pin 1 = −12 V on the right end, the red stripe; mark it on the silk);
  - the **barrel jack** in the top-left corner, opening at the top edge next to the audio jacks.
- **Pots:** the left column is rotated 180° so their pins stay on the board. Middle and right have their pins to the left.
- **D2** (the 9 V input diode) sits beside the barrel jack. A long V9 run to the middle band wouldn't route.
- **Under the matrix module** (on 8.5 mm sockets): the audio filter / MCP6002 and the sync parts.
- **Not done yet:** silkscreen pass (labels, J1 stripe, version), JLC files, a 3D height check of the matrix module vs the panel.
