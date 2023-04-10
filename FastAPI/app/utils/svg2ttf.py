import sys
sys.path.append("..")
import fontforge

font = fontforge.font()
glyph = font.createChar(ord("가"), "font1")
glyph.importOutlines("/home/software/CHJ/ML/FastAPI/app/dmfont/output/svgs/CHJ/CHJ_AC00.svg")
font.generate("output.ttf")