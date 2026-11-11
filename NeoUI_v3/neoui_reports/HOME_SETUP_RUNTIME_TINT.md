# Runtime HOME / SETUP tint trace

Source: the user's existing MU1440-lsd.jxe backup, SHA-256 a55d9cfb69c5756f8202b7f7aa4079d4d5b637ae4c2fd0fe723f1d6816cbeea8. The firmware startup script loads /ifs/lsd.jxe. Inspection is static; no firmware class is executed or modified. RUNTIME_TINT_EVIDENCE.json records exact class/method offsets, code hashes, reference sites and two original shader hashes. The targeted J9 reader validates UTF-8/self-relative pointers and declared method counts; it is not a general decompiler.

## Resource selection

SkinImagePoolImpl.createImage(logical) creates two ScaleImage entries at logical*2 and logical*2+1. Image's constructor stores these as dayImage and nightImage. Image.getCurrentImage selects day for mode 0 and night for mode 1. The six ints per logical image are two triples for those day/night ScaleImages.

The second half of scaleImageData is a SECOND BITMAP layer, not a separate day/night bank. createScaleImage reads the primary bitmap ID at scaleIndex*3 and, when supportsSecondScaleImageBitmap is true, the second bitmap ID at arrayLength/2 + scaleIndex*3. Insets and scale mode are preserved. Both day/night triples match on the exact P4526 input, including HOME and SETUP assets. Earlier bank 0/1 labels in reports refer to primary/secondary layers and should not be read as day/night modes.

## Ambient selection and renderer

SkinInformationServiceImpl.readAmbienceColorMap loads the selected skin's ambienceColorMap.res and vehicle-matched color mappings. setIntLightAmbientLightColor updates mapped display colors and notifies receivers. ViewCompositorImpl.SkinInformationHandler checks isAmbientColorEnabled and feeds getAmbientColor (with opaque alpha) into Color.setGlobalDynamicColor, or null when ambient color is disabled. Color.getCurrentColor selects day/night data; its dynamic path calls Color.mix, which multiplies channel values and divides by 255. Current skin mode notifications call the day/night mode setter.

AbstractWidgetUI.updateScaleImageDrawable loads primary into image slot 0 and optional secondary into slot 1. StaticImageUI supplies the current widget color. The shipped ImageComposition.glslf samples the primary, multiplies secondary RGB by vertex/widget color, then alpha-composites secondary over primary. Default image blending is 0, whose shader selector chooses Modulate. For opaque primary P and secondary S with alpha a, the default component composition is (S.rgb * tint.rgb) * a + P.rgb * (1-a). Global alpha and other effects remain runtime controlled.

The local map's BAP blue 0x006EFE maps to display blue 0x0066FF. Preview colors are explicit sample widget tints; a particular view may also multiply its own day/night color. The offline preview does not assert a captured head-unit pixel match or alter the ambient palette.

## Verified graphics scope

HOME symbols 193/194 share primary 2127 and secondary 2126, both 407x300. The source primary is opaque black; the secondary is a grayscale mask with alpha 15..204. The candidate sets primary to graphite #0D131C and scales visible secondary luminance to 45%, preserving every alpha byte. This retains OEM tint response with a restrained overlay.

SETUP/shared list symbol 111 maps only to divider 19 (88x3); its visible luminance is reduced to 45%. Symbol 274 maps only to scrollbar track 84 (25x51), changed to graphite slate #303A46. Scrollbar.updateScrollbarImage selects an image and color by state, assigning WHITE if no state color is present. Foreground/thumb 83 (symbol 275) remains byte-identical because its white mask receives runtime color. The candidate does not force cyan into that binding or restyle focus/disabled states.

The generic list divider/track changes can affect other skin3 list screens. All 208 MAIN_MENU, controlbar and shared foundation protected records match input v1 byte-for-byte. No skin0, viewhandler, selector, ambience map, navigation map, coordinates or touch target is changed. HOME component usage has resource-name/geometry/photo evidence (B), while live unit behavior remains untested.
