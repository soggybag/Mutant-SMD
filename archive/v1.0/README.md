# Mutant SMD v1.0: archived revision

- **Git tag:** `v1.0` (commit `186dd12`, 2026-10-20)
- **Tag note:** v1.0: first JLC order; matrix supply filter (R8/C16); rotation offsets U2/D3; fab files 2026-10-20
- **Archived:** 2026-10-20 with `_tools/archive_version.py`

## Finding a part

1. Open `MutantSMD_ibom.html` in a browser. Type a reference (R14) or a value (100k) in the filter box; the part lights up on the board.
   - Hover over a pad to see its net.
   - F / B switch sides.
2. Find the same reference in `MutantSMD_schematic.pdf` with Cmd-F.
3. `MutantSMD_board_front.pdf` / `_back.pdf` are printable: page 1 has the outlines and references, page 2 the copper. The back is mirrored, as you see it holding the board.

## Files

- `MutantSMD_board_back.pdf`
- `MutantSMD_board_front.pdf`
- `MutantSMD_ibom.html`
- `MutantSMD_render_bottom.png`
- `MutantSMD_render_top.png`
- `MutantSMD_schematic.pdf`
- `docs`/
- `parts.csv`
- `production`/

`production/` holds the files sent to JLCPCB for this revision: MutantSMD.zip, MutantSMD_hand_solder.csv, bom.csv, designators.csv, netlist.ipc, positions.csv.
