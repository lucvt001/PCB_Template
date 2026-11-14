# PCB Template

This is a PCB folder template for new projects. Clone this, rename the files, and start cooking!

## Directories

- `docs`: datasheets, and user manual if have
- `libs`: symbols and footprints (`.pretty` folders for footprints if using KiCad)
- `mechanical`: 3D step files of the components and final board, and any additional mechanical housing
- `pcb`: schematics and layout files; the templates already contain presets for a 4-layer board for JLCPCB manufacturing
- `production`: BOM, pick-and-place files, and gerbers; you should have subfolders under here, renamed to version number or iterations

Optional folders to add:

- `firmware`: code for your MCU