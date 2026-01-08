# Multi-part print patterns

Use this when splitting a model across multiple plates or when joining parts with dovetails, keys, pins, or fasteners.

## Checklist (default)

- Decide the split plane based on printability (minimize overhangs, keep flat faces on the bed).
- Add alignment features so parts self-register (keys, pins, tongues).
- Add mechanical retention for assembly (dovetail, snap, screws, or magnets).
- Add clearance/tolerance for your printer and material; start small and iterate with a test coupon.
- Keep a single assembly SCAD for visual verification.

## Dovetail guidance

- Use shallow angles so parts slide without binding.
- Add a lead-in chamfer on the male part.
- Start with 0.2–0.4 mm total clearance (radial) for FDM; adjust per material.
- Prefer splitting so the dovetail prints without long unsupported overhangs.

## Other joinery options

- **Tongue-and-groove**: easiest to align, lower friction than dovetail.
- **Pin + socket**: good for alignment, add slight taper to ease insertion.
- **Screw bosses**: use heat-set inserts or nut traps; keep wall thickness around bosses.
- **Magnets**: include press-fit pockets and polarity markers.

## Assembly strategy

- Model each part as a module, then create `assembly()` to preview the whole object.
- Expose a `PART` variable to render individual parts: `PART="a"`, `PART="b"`, `PART="all"`.
- Provide a small test coupon that only includes the joiner geometry for fast iteration.

## BOSL2 discovery

- Search for dovetail/key/connector helpers inside BOSL2:
  - `rg -n "dovetail|tongue|groove|join|connector" ~/.scad/BOSL2`
- Search the wiki for usage patterns:
  - `rg -n "dovetail|tongue|groove" references/BOSL2.wiki`
