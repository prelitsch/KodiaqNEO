# Verified images.res translation

The exact P4526 skin1 file contains four signed-int32 arrays after its 20-byte prefix. Counts are 320 (80 inset groups), 34572 (ScaleImage data), 2732 (image-array ranges), and 25037 (image-array logical references). All array bounds consume the file exactly. All active MCF references and inset indices validate.

The ScaleImage array has two halves: primary bitmap triples, then secondary bitmap triples. Each half contains two triples per logical image: day and night. On this exact input the pairs are identical. The runtime SkinImagePoolImpl.createImage and createScaleImage instructions prove this interpretation; Image's constructor names the pair dayImage/nightImage, and getCurrentImage selects mode 0/day or 1/night. ScaleImage.imageId2 is the optional secondary layer. Earlier numeric bank 0/1 fields mean primary/secondary layers, not day/night selection.

Logical pause 797 maps to primary record 1658, while actual same-number record 797 is unrelated. HOME logical 193/194 maps to primary 2127 and secondary 2126. The secondary layer is tinted and alpha-over composited at runtime, not switched on night mode. See HOME_SETUP_RUNTIME_TINT.md for exact source hashes, runtime chain and shader equation.

images_res.py reproduces these links without modifying metadata. RESOLVED_RESOURCE_MAP.csv and resource_map.json report layer and geometry. Full decoded tables and graphics remain local and out of Git. Installed skin3 metadata still needs a future no-write hash check; the local M.I.B. script establishes its stock skin1 lineage.

MCF file, TOC and image-header/body CRC formulas are resolved and checked by mcf_inventory.py. The v1-derived 20-record candidate passes CRC/bounds checks and independent byte-exact restoration. Indexed palette editing remains out of scope.
