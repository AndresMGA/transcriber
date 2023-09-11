
from PyQt5.QtGui import QPainterPath, QPen, QColor , QBrush, QPainterPath, QKeySequence, QImage, QPixmap, QFont,QTextDocument, QFontMetrics,QPainter,QFontDatabase
from scaling import r,f,x,y
import platform

  

if platform.system() == "Linux":
    active_tab_font = QFont("KacstNaskh",round(r(0.5)))
    harm_marks_font = QFont("KacstOne",round(r(0.3)))
else:
    active_tab_font = QFont("Geeza Pro Interface",round(r(0.7)))
    harm_marks_font = QFont("Al Tarikh PUA",round(r(0.5)))


# 0: .Al Bayan PUA
# 1: .Al Nile PUA
# 2: .Al Tarikh PUA
# 3: .Apple Color Emoji UI
# 4: .Apple SD Gothic NeoI
# 5: .Aqua Kana
# 6: .Arabic UI Display
# 7: .Arabic UI Text
# 8: .Arial Hebrew Desk Interface
# 9: .Baghdad PUA
# 10: .Beirut PUA
# 11: .Damascus PUA
# 12: .DecoType Naskh PUA
# 13: .Diwan Kufi PUA
# 14: .Farah PUA
# 15: .Geeza Pro Interface
# 16: .Geeza Pro PUA
# 17: .Helvetica Neue DeskInterface
# 18: .Hiragino Kaku Gothic Interface
# 19: .Hiragino Sans GB Interface
# 20: .Keyboard
# 21: .KufiStandardGK PUA
# 22: .LastResort
# 23: .Lucida Grande UI
# 24: .Muna PUA
# 25: .Nadeem PUA
# 26: .Noto Nastaliq Urdu UI
# 27: .PingFang HK
# 28: .PingFang SC
# 29: .PingFang TC
# 30: .Sana PUA
# 31: .Savoye LET CC.
# 32: .SF Compact Display
# 33: .SF Compact Rounded
# 34: .SF Compact Text
# 35: .SF NS Display
# 36: .SF NS Display Condensed
# 37: .SF NS Symbols
# 38: .SF NS Text
# 39: .SF NS Text Condensed
# 40: Al Bayan
# 41: Al Nile
# 42: Al Tarikh
# 43: American Typewriter
# 44: Andale Mono
# 45: Apple Braille
# 46: Apple Chancery
# 47: Apple Color Emoji
# 48: Apple SD Gothic Neo
# 49: Apple Symbols
# 50: AppleGothic
# 51: AppleMyungjo
# 52: Arial
# 53: Arial Black
# 54: Arial Hebrew
# 55: Arial Hebrew Scholar
# 56: Arial Narrow
# 57: Arial Rounded MT Bold
# 58: Arial Unicode MS
# 59: Athelas
# 60: Avenir
# 61: Avenir Next
# 62: Avenir Next Condensed
# 63: Ayuthaya
# 64: Baghdad
# 65: Bangla MN
# 66: Bangla Sangam MN
# 67: Baskerville
# 68: Beirut
# 69: Big Caslon
# 70: Bodoni 72
# 71: Bodoni 72 Oldstyle
# 72: Bodoni 72 Smallcaps
# 73: Bodoni Ornaments
# 74: Bradley Hand
# 75: Brush Script MT
# 76: Chalkboard
# 77: Chalkboard SE
# 78: Chalkduster
# 79: Charter
# 80: Cochin
# 81: Comic Sans MS
# 82: Copperplate
# 83: Corsiva Hebrew
# 84: Courier
# 85: Courier New
# 86: Damascus
# 87: DecoType Naskh
# 88: Devanagari MT
# 89: Devanagari Sangam MN
# 90: Didot
# 91: DIN Alternate
# 92: DIN Condensed
# 93: Diwan Kufi
# 94: Diwan Thuluth
# 95: Euphemia UCAS
# 96: Farah
# 97: Farisi
# 98: Futura
# 99: GB18030 Bitmap
# 100: Geeza Pro
# 101: Geneva
# 102: Georgia
# 103: Gill Sans
# 104: Gujarati MT
# 105: Gujarati Sangam MN
# 106: Gurmukhi MN
# 107: Gurmukhi MT
# 108: Gurmukhi Sangam MN
# 109: Heiti SC
# 110: Heiti TC
# 111: Helvetica
# 112: Helvetica Neue
# 113: Herculanum
# 114: Hiragino Kaku Gothic Pro
# 115: Hiragino Kaku Gothic ProN
# 116: Hiragino Kaku Gothic Std
# 117: Hiragino Kaku Gothic StdN
# 118: Hiragino Maru Gothic Pro
# 119: Hiragino Maru Gothic ProN
# 120: Hiragino Mincho Pro
# 121: Hiragino Mincho ProN
# 122: Hiragino Sans
# 123: Hiragino Sans GB
# 124: Hoefler Text
# 125: Impact
# 126: InaiMathi
# 127: Iowan Old Style
# 128: ITF Devanagari
# 129: ITF Devanagari Marathi
# 130: Kailasa
# 131: Kannada MN
# 132: Kannada Sangam MN
# 133: Kefa
# 134: Khmer MN
# 135: Khmer Sangam MN
# 136: Kohinoor Bangla
# 137: Kohinoor Devanagari
# 138: Kohinoor Telugu
# 139: Kokonor
# 140: Krungthep
# 141: KufiStandardGK
# 142: Lao MN
# 143: Lao Sangam MN
# 144: Lucida Grande
# 145: Luminari
# 146: Malayalam MN
# 147: Malayalam Sangam MN
# 148: Marion
# 149: Marker Felt
# 150: Menlo
# 151: Microsoft Sans Serif
# 152: Mishafi
# 153: Mishafi Gold
# 154: Monaco
# 155: Montserrat
# 156: Mshtakan
# 157: Muna
# 158: Myanmar MN
# 159: Myanmar Sangam MN
# 160: Nadeem
# 161: New Peninim MT
# 162: Noteworthy
# 163: Noto Nastaliq Urdu
# 164: Optima
# 165: Oriya MN
# 166: Oriya Sangam MN
# 167: Palatino
# 168: Papyrus
# 169: Phosphate
# 170: PingFang HK
# 171: PingFang SC
# 172: PingFang TC
# 173: Plantagenet Cherokee
# 174: PT Mono
# 175: PT Sans
# 176: PT Sans Caption
# 177: PT Sans Narrow
# 178: PT Serif
# 179: PT Serif Caption
# 180: Raanana
# 181: Rockwell
# 182: Sana
# 183: Sathu
# 184: Savoye LET
# 185: Seravek
# 186: Shree Devanagari 714
# 187: SignPainter
# 188: Silom
# 189: Sinhala MN
# 190: Sinhala Sangam MN
# 191: Skia
# 192: Snell Roundhand
# 193: Songti SC
# 194: Songti TC
# 195: STIXGeneral
# 196: STIXIntegralsD
# 197: STIXIntegralsSm
# 198: STIXIntegralsUp
# 199: STIXIntegralsUpD
# 200: STIXIntegralsUpSm
# 201: STIXNonUnicode
# 202: STIXSizeFiveSym
# 203: STIXSizeFourSym
# 204: STIXSizeOneSym
# 205: STIXSizeThreeSym
# 206: STIXSizeTwoSym
# 207: STIXVariants
# 208: STSong
# 209: Sukhumvit Set
# 210: Superclarendon
# 211: Symbol
# 212: Tahoma
# 213: Tamil MN
# 214: Tamil Sangam MN
# 215: Telugu MN
# 216: Telugu Sangam MN
# 217: Thonburi
# 218: Times
# 219: Times New Roman
# 220: Trattatello
# 221: Trebuchet MS
# 222: Verdana
# 223: Waseem
# 224: Webdings
# 225: Wingdings
# 226: Wingdings 2
# 227: Wingdings 3
# 228: Zapf Dingbats
# 229: Zapfino