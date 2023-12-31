# MTAR GEAR

MTAR GEAR allows for modification and swapping of animations of MGS games on PC.

## Features

- **Open and Read MTAR/MAR Files**: Easily load MTAR/MAR files to view their contents.
- **Animation Extraction**: Extract specific animation blocks from MTAR/MAR files for detailed analysis and modification.
- **Replace Animations**: Import new animations into existing MTAR/MAR files.
- **Multi-Platform Support**: Separate tabs and functionalities for different versions of the game, including 3DS and MGS4 formats (experimental). As well as support for Metal Gear Solid 2.
- **MTAR/MAR Data Table Display**: View detailed information about the contents of MTAR/MAR files.

## In Progress

- **Import All Animations Feature**: Currently being refined to address offset problems.
- **Support for More 3DS Animations**: Enhancement in progress; additional 3DS MTAR files are needed for testing.
- **Support for Additional MGS Games**: Plans to extend support, pending acquisition of more test files from various MGS games.
- **Animation Conversion**: Working on being able to convert animations to MGS3 MTAR Format.

## Usage

### General Usage for MC MTAR
Follow these steps to modify animations in MC MTAR files:
1. **Open an MTAR File**: Use the 'Open MTAR File' button to load the MTAR file you want to modify.
2. **Specify the Animation Block**: In the 'Block Index' box, type the index of the animation block you wish to extract or replace.
3. **Extract or Import Animation**:
   - To extract an animation, click the 'Extract' button. This will pull the specified animation block from the MTAR file.
   - To import a new animation, click the 'Import' button. This will replace the animation block at the specified index with your new animation.
4. **Complete the Modification**: Your specified animation block will be extracted or replaced accordingly.

### Extracting and Converting 3DS Animations
1. **Extract Animation Blocks from Info File**: Use this to obtain the offsets required for extracting 3DS animations. PLEASE download file from the code called mtardiction.txt to get 3DS snake's animations.
2. **Convert 3DS to MC**: Select a 3DS animation block to convert it into a format compatible with the Master Collection.
3. **Convert All in Folder**: Automatically convert all 3DS animations in a folder to Master Collection compatible animations.

### MTAR Editor
1. **Open a Block File**: Load the specific animation block file you want to edit.
2. **Edit Frames and Joints**: Modify the number of frames and joints for the selected animation block.

### MGS 4 Tab
1. **Parse MGS4 MTAR File**: Load and parse an MGS4 MTAR file.
2. **Extract Animation Blocks**: Extract animation blocks from the parsed file.
3. **Convert MGS4 to MC**: Convert individual MGS4 animations to the Master Collection format.
4. **Convert All in Folder**: Convert all MGS4 animations in a folder to the Master Collection format.
5. **Export MTCM Data Table**: Export the MTCM data table from the MGS4 MTAR file.
6. **Note**: Some features are experimental and may vary in effectiveness. Endian swapping for MGS4 will be implemented in the next version.

### MGS 2 Tab
Same format as MC MTAR basically for MGS 3 with one additional button:
**Convert MGS2 to MGS3**: Convert individual MGS2 animations to the MGS3 MTAR format. Very experimental and known to crash game (sorry!). Will update if it's possible.

## Acknowledgements

Special thanks to Zoft for showing the process of adding animations to the end of the file, before that I was replacing the data blocks and recalculating offsets which was a bit more time-consuming. Thanks to Jayveer for his past research and clarification on some MGS 4 stuff.
