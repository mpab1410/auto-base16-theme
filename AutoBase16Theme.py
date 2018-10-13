# AutoBase16Theme.py by Macoy Madson
# MIT License
# https://github.com/makuto/auto-base16-theme
import random
import colorsys

"""
This script generates a "base16" color theme intended for code syntax highlighting.

Base16 Style (from https://github.com/chriskempson/base16/blob/master/styling.md):
    base00 - Default Background
    base01 - Lighter Background (Used for status bars)
    base02 - Selection Background
    base03 - Comments, Invisibles, Line Highlighting
    base04 - Dark Foreground (Used for status bars)
    base05 - Default Foreground, Caret, Delimiters, Operators
    base06 - Light Foreground (Not often used)
    base07 - Light Background (Not often used)
    base08 - Variables, XML Tags, Markup Link Text, Markup Lists, Diff Deleted
    base09 - Integers, Boolean, Constants, XML Attributes, Markup Link Url
    base0A - Classes, Markup Bold, Search Text Background
    base0B - Strings, Inherited Class, Markup Code, Diff Inserted
    base0C - Support, Regular Expressions, Escape Characters, Markup Quotes
    base0D - Functions, Methods, Attribute IDs, Headings
    base0E - Keywords, Storage, Selector, Markup Italic, Diff Changed
    base0F - Deprecated, Opening/Closing Embedded Language Tags, e.g. <?php ?>
"""

"""

Configuration

"""
# TODO: Add other options for templates (take as a command line argument)
outputTemplateFilename = 'emacs-base16-theme-template.el'
outputFilename = 'base16-my-auto-theme.el'

# TODO: Make these into modes that auto-set these constraints
# TODO: Make contrast ratio mode which meets accessibility guidelines (see https://webaim.org/resources/contrastchecker/)?

## Background
# Make sure the background is darker than this (for dark themes). In HSL Lightness (0-1)
maximumBackgroundBrightness = 0.29

## Foreground contrasts (i.e. text color HSL lightness - background color HSL lightness)
# These are relative values instead of ratios because you can't figure a ratio on a black background
minimumCommentTextContrast = 0.3
minimumTextContrast = 0.43
maximumTextContrast = 0.65

## Debugging
debugColorsVerbose = False

## Internal constants
# The index for the darkest background color. This is important to make sure contrast is high enough
#  between the darkest background color and the darkest text
BACKGROUND_COLOR_INDEX = 0

class Base16Color:
    def __init__(self, name, selectionFunction):
        self.name = name
        self.color = None
        self.selectionFunction = selectionFunction

"""

Color utility functions

"""

def rgbColorFromStringHex(colorStringHex):
    # From https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
    return tuple(int(colorStringHex.strip('#')[i:i+2], 16) for i in (0, 2 ,4))

def rgb256ToHls(color):
    rgbColor = color
    if type(color) == str:
        rgbColor = rgbColorFromStringHex(color)

    normalizedColor = []
    for component in rgbColor:
        normalizedColor.append(component / 256)

    return colorsys.rgb_to_hls(normalizedColor[0], normalizedColor[1], normalizedColor[2])
    
def getColorBrightness(color):
    hsvColor = rgb256ToHls(color)
        
    return hsvColor[1]

def colorHasBeenUsed(base16Colors, color):
    for base16Color in base16Colors:
        if base16Color.color == color:
            return True
    return False

def isColorWithinContrastRange(color, backgroundColor, minimumContrast, maximumContrast):
    colorBrightness = getColorBrightness(color)
    backgroundBrightness = getColorBrightness(backgroundColor)
    contrast = colorBrightness - backgroundBrightness

    if debugColorsVerbose:
        print('Color {} brightness {} background {} brightness {} difference {}'
              .format(color, colorBrightness, backgroundColor, backgroundBrightness, contrast))
        
    return (contrast >= minimumContrast and contrast <= maximumContrast)

"""

Selection heuristics

"""

# Pick darkest, most grey color for background. If the color is already taken, pick the next unique darkest
def pickDarkestGreyestColorUnique(base16Colors, currentBase16Color, colorPool):
    bestColor = None
    bestColorBrightness = 10000
    for color in colorPool:
        rgbColorBrightness = getColorBrightness(color)
        if rgbColorBrightness < bestColorBrightness and not colorHasBeenUsed(base16Colors, color):
            bestColor = color
            bestColorBrightness = rgbColorBrightness

    return bestColor

# Selects the  darkest color which meets the contrast requirements and which hasn't been used yet
def pickDarkestHighContrastColorUnique(base16Colors, currentBase16Color, colorPool):
    viableColors = []
    for color in colorPool:
        if isColorWithinContrastRange(color, base16Colors[BACKGROUND_COLOR_INDEX].color,
                                      minimumCommentTextContrast, maximumTextContrast):
            viableColors.append(color)

    viableColors = sorted(viableColors,
                          key=lambda color: getColorBrightness(color), reverse=False)

    # We've sorted in order of brightness; pick the darkest one which is unique
    bestColor = None
    for color in viableColors:
        if not colorHasBeenUsed(base16Colors, color):
            bestColor = color
            break

    return bestColor
    
# Pick high contrast foreground
# High contrast = a minimum brightness difference between this and the brightest background)
def pickHighContrastBrightColorUniqueOrRandom(base16Colors, currentBase16Color, colorPool):
    viableColors = []
    for color in colorPool:
        if isColorWithinContrastRange(color, base16Colors[BACKGROUND_COLOR_INDEX].color,
                                      minimumTextContrast, maximumTextContrast):
            viableColors.append(color)

    if not viableColors:
        return None

    # Prefer a color which is unique
    bestColor = None
    for color in viableColors:
        if not colorHasBeenUsed(base16Colors, color):
            bestColor = color
            break
        
    return bestColor if bestColor else random.choice(viableColors)
    
def pickRandomColor(base16Colors, currentBase16Color, colorPool):
    return random.choice(colorPool)

"""

Procedure

"""

def main():
    colorsFile = open('colors.txt', 'r')
    colorsLines = colorsFile.readlines()
    colorsFile.close()

    base16Colors = [
        # These go from darkest to lightest via implicit unique ordering
        # base00 - Default Background
        Base16Color('base00', pickDarkestGreyestColorUnique),
        # base01 - Lighter Background (Used for status bars)
        Base16Color('base01', pickDarkestGreyestColorUnique),
        # base02 - Selection Background
        Base16Color('base02', pickDarkestGreyestColorUnique),
        # base03 - Comments, Invisibles, Line Highlighting
        Base16Color('base03', pickDarkestHighContrastColorUnique),
        # base04 - Dark Foreground (Used for status bars)
        Base16Color('base04', pickDarkestGreyestColorUnique),
        # base05 - Default Foreground, Caret, Delimiters, Operators
        Base16Color('base05', pickDarkestHighContrastColorUnique),
        # base06 - Light Foreground (Not often used)
        Base16Color('base06', pickDarkestGreyestColorUnique),
        # base07 - Light Background (Not often used)
        Base16Color('base07', pickDarkestGreyestColorUnique),
        # base08 - Variables, XML Tags, Markup Link Text, Markup Lists, Diff Deleted
        Base16Color('base08', pickHighContrastBrightColorUniqueOrRandom),
        # base09 - Integers, Boolean, Constants, XML Attributes, Markup Link Url
        Base16Color('base09', pickHighContrastBrightColorUniqueOrRandom),
        # base0A - Classes, Markup Bold, Search Text Background
        Base16Color('base0A', pickHighContrastBrightColorUniqueOrRandom),
        # base0B - Strings, Inherited Class, Markup Code, Diff Inserted
        Base16Color('base0B', pickHighContrastBrightColorUniqueOrRandom),
        # base0C - Support, Regular Expressions, Escape Characters, Markup Quotes
        Base16Color('base0C', pickHighContrastBrightColorUniqueOrRandom),
        # base0D - Functions, Methods, Attribute IDs, Headings
        Base16Color('base0D', pickHighContrastBrightColorUniqueOrRandom),
        # base0E - Keywords, Storage, Selector, Markup Italic, Diff Changed
        Base16Color('base0E', pickHighContrastBrightColorUniqueOrRandom),
        # base0F - Deprecated, Opening/Closing Embedded Language Tags, e.g. <?php ?>
        Base16Color('base0F', pickHighContrastBrightColorUniqueOrRandom)]

    # For testing
    colorPool = ['#001b8c', '#0a126b', '#010e44', '#772e51', '#ca4733', '#381f4d', '#814174',
              '#90142e', '#720d21', '#28217d', '#6d2c88', '#3b0010', '#6e095b', '#827e7b',
              '#645361', '#560041']

    if colorsLines:
        colorPool = colorsLines

    # Process color pool
    for i, color in enumerate(colorPool):
        # Remove newlines
        colorPool[i] = color.strip('\n')
        color = colorPool[i]

        # For debugging
        print(color)
        rgbColor = rgbColorFromStringHex(color)
        print('RGB =', rgbColor)

    # Select a color from the color pool for each base16 color
    for i, base16Color in enumerate(base16Colors):
        color = base16Color.selectionFunction(base16Colors, base16Color, colorPool)

        if not color:
            print('WARNING: {} could not select a color! Picking one at random'.format(base16Color.name))
            color = random.choice(colorPool)

        base16Colors[i].color = color
        
        print('Selected {} for {}'.format(base16Colors[i].color, base16Color.name))

    # Ensure backgrounds are dark enough
    # backgroundColor = base16Colors[BACKGROUND_COLOR_INDEX]
    
    # for i in [0, 1, 2]:
    #     color = base16Colors[i].color
    #     if getColorBrightness

    # Output selected colors
    outputTemplateFile = open(outputTemplateFilename, 'r')
    outputTemplate = ''.join(outputTemplateFile.readlines())
    outputTemplateFile.close()
    
    outputText = outputTemplate.format(base16Colors[0].color, base16Colors[1].color,
                                       base16Colors[2].color, base16Colors[3].color,
                                       base16Colors[4].color, base16Colors[5].color,
                                       base16Colors[6].color, base16Colors[7].color,
                                       base16Colors[8].color, base16Colors[9].color,
                                       base16Colors[10].color, base16Colors[11].color,
                                       base16Colors[12].color, base16Colors[13].color,
                                       base16Colors[14].color, base16Colors[15].color)
    
    outputFile = open(outputFilename, 'w')
    outputFile.write(outputText)
    outputFile.close()
    print('Wrote {} using template {}'.format(outputFilename, outputTemplateFilename))

if __name__ == '__main__':
    main()
