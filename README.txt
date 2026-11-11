Kodiaq NeoUI v2 - Navigation Style Research Collector

GOAL
Collect map colour settings and POI/map-marker resource files from YOUR ALREADY-EXTRACTED
Columbus P4526 / MU1440 firmware. This is a READ-ONLY PC operation and does not touch the car or SD card.

BEFORE RUNNING
1. Open COLLECT_NAV_GRAPHICS.ps1 in Notepad and inspect it.
2. Locate your existing app50_extracted folder (the one containing lba0/navigation).

EXAMPLE (change the path if yours differs):
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\COLLECT_NAV_GRAPHICS.ps1" -SourceRoot "C:\Users\aldin\OneDrive\Desktop\Kodiaq Moding\app50_extracted"

The command creates Kodiaq_NeoUI_Navigation_Research.zip next to the lba0 folder (inside app50_extracted).
It will refuse to overwrite an existing ZIP. Move/rename it to run again.

WHAT TO DO AFTER
Upload Kodiaq_NeoUI_Navigation_Research.zip to the ChatGPT conversation.
We will validate the map style XML, compare day/night palettes, identify POI assets and plan a
separate navigation-only build. No installation before verified backup, matching region and rollback.

DO NOT
Do not copy map files or styles to the car yet.
Do not overwrite any working MIB files.
Do not change route visibility, guidance flags, navigation safety warning icons or routing logic.
