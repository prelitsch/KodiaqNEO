# NeoUI v3 HOME / SETUP offline candidate

This partial candidate adds four HOME/SETUP graphics to the verified sixteen media variants. It is a replacement of existing skin3, not an additional selectable skin.

- New records: 2127 (HOME graphite base), 2126 (HOME ambient overlay), 19 (list divider), 84 (scrollbar track).
- Existing media variants: 16 retained exactly from the prior media stage.
- Alpha and dimensions: unchanged for every graphic. All aliases and source/new record, pixel and PNG hashes are in VERIFIED_HOME_SETUP_BUILD.json.
- Preserved: all 208 protected MENU/controlbar/shared foundation records; runtime-colored scrollbar thumb 83; compiled code, resource metadata and ambient palette.
- Input v1 SHA-1: 641c34e42ed5843c1795bf860fd4cb7bbb913fdb.
- Candidate SHA-1: 44481f3c5b91543799c11c4c6b665c7dd26a1e64.
- Candidate SHA-256: e4f850f5cd71e09083ffa3e7650bad03e02e82a2fadc40a19fd2f5347a434be7.

Validated: all file/TOC/image CRCs; exact 20-record change set; unchanged ID order/count/geometry/alpha; fixed baseline and metadata hashes; MENU protection; independent recovery archive restoration to the complete original v1 SHA-256 dfb37cb771c58fb838d3797c3bf356e8fae9475aa980a236b7e9cba055f5cd58.

Preview: neoui_previews/HOME_SETUP_V3_PREVIEW.html. HOME uses the original shader's primary/secondary composition with explicit tint samples. SETUP is a component/legibility composition, with wording copied from photo 06. All eight original scenarios are included with scope notes. These are not runtime head-unit captures, and other screen components are not redesigned by this stage.

This is PC-validated and not vehicle-tested. No installer or SD operations are prepared. Installed skin3 metadata and live renderer behavior still require the later user-authorized precheck/review gates. A script/record restore on PC is not a recovery guarantee if the car UI cannot boot.
