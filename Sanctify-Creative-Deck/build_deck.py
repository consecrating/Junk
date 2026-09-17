"""Build the Sanctify creative showcase deck."""
import sys, os
sys.path.insert(0, '/projects/sandbox/.kiro/skills/creative-deck/scripts')
import deck_kit as dk
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---------------------------------------------------------------- brand system
INK      = RGBColor(0x17, 0x12, 0x1C)
INK_SOFT = RGBColor(0x2A, 0x22, 0x33)
MAGENTA  = RGBColor(0xC2, 0x0B, 0x58)
VIOLET   = RGBColor(0x7A, 0x00, 0xDF)
PURPLE   = RGBColor(0x97, 0x26, 0x8F)
LIGHT    = RGBColor(0xF7, 0xF5, 0xFA)
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
GREY     = RGBColor(0x8A, 0x85, 0x94)
MIDGREY  = RGBColor(0x5C, 0x56, 0x68)
LINE     = RGBColor(0xDC, 0xD6, 0xE4)

DISPLAY = 'Montserrat'
BODY    = 'Poppins'

W, H = 13.333, 7.5
LOGO = '/projects/sandbox/.deck-build/logo.png'
LOGO_LIGHT = '/projects/sandbox/.deck-build/logo_light.png'


def make_light_logo(src=LOGO, dst=LOGO_LIGHT):
    """The stock logo is near-black and vanishes on dark slides.

    Knock the black wordmark out to white and lift the magenta mark so both
    read against the deep plum backgrounds.
    """
    im = Image.open(src).convert('RGBA')
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            if max(r, g, b) < 110:                      # black wordmark -> white
                px[x, y] = (255, 255, 255, a)
            else:                                       # magenta mark -> lifted
                px[x, y] = (min(255, r + 90), min(255, g + 60), min(255, b + 95), a)
    im.save(dst)


make_light_logo()

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]


# ---------------------------------------------------------------- primitives
def slide():
    return prs.slides.add_slide(BLANK)


def rect(s, x, y, w, h, fill=None, line=None, lw=0.75, shape=MSO_SHAPE.RECTANGLE, adj=None):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.shadow.inherit = False
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(lw)
    if adj is not None:
        try: sh.adjustments[0] = adj
        except Exception: pass
    sh.text_frame.text = ''
    return sh


def grad(s, x, y, w, h, c1, c2, angle=45):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.shadow.inherit = False
    sh.line.fill.background()
    f = sh.fill; f.gradient()
    st = f.gradient_stops
    st[0].color.rgb, st[0].position = c1, 0.0
    st[1].color.rgb, st[1].position = c2, 1.0
    try: f.gradient_angle = angle
    except Exception: pass
    sh.text_frame.text = ''
    return sh


def spacing(run, pts):
    """Letter-spacing (python-pptx has no API for this)."""
    run.font._rPr.set('spc', str(int(pts * 100)))


def text(s, x, y, w, h, body, size=12, font=BODY, color=INK, bold=False,
         align=PP_ALIGN.LEFT, line=1.35, spc=None, anchor=MSO_ANCHOR.TOP, space_after=0):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, para_text in enumerate(body.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line
        p.space_after = Pt(space_after)
        r = p.add_run(); r.text = para_text
        r.font.name = font; r.font.size = Pt(size); r.font.bold = bold
        r.font.color.rgb = color
        if spc: spacing(r, spc)
    return tb


def chip(s, x, y, label, fill=MAGENTA, fg=WHITE):
    """Small letterspaced category tag."""
    w = 0.115 * len(label) + 0.42
    sh = rect(s, x, y, w, 0.30, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.5)
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label.upper()
    r.font.name = DISPLAY; r.font.size = Pt(8.5); r.font.bold = True; r.font.color.rgb = fg
    spacing(r, 1.1)
    return w


def art_fit(s, path, bx, by, bw, bh, frame=True, shadow=True):
    """Place artwork centred in a box, aspect preserved, optionally framed."""
    im = Image.open(path)
    scale = min(bw / im.width, bh / im.height)
    w, h = im.width * scale, im.height * scale
    x, y = bx + (bw - w) / 2, by + (bh - h) / 2
    if shadow:
        rect(s, x + 0.055, y + 0.065, w, h, fill=RGBColor(0xDF, 0xD9, 0xE6))
    s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    if frame:
        rect(s, x, y, w, h, fill=None, line=RGBColor(0xC9, 0xC2, 0xD2), lw=0.75)
    return x, y, w, h


def swatches(s, x, y, path, n=5, size=0.19, gap=0.075):
    for i, c in enumerate(dk.palette(path, n)):
        rect(s, x + i * (size + gap), y, size, size,
             fill=RGBColor(*c), line=RGBColor(0xFF, 0xFF, 0xFF), lw=0.5)


# ---------------------------------------------------------------- artwork data
arts = dk.extract_artwork('source.pdf', 'art')
A = {a.index: a.path for a in arts}

SECTIONS = [
    ("Packaging Design", "FMCG pack artwork built as a shelf-ready flavour system.", [4, 5, 6]),
    ("Print & Flyers", "Leaflets and takeaway collateral that have to work in the hand.", [2, 12, 11]),
    ("Corporate Catalogue", "Multi-page product literature for a manufacturing brand.", [9, 10]),
    ("Social & Festival Campaigns", "Feed-native posts for retail, PSU and B2B brands.", [1, 3, 7, 8]),
    ("Political Communication", "A consistent greeting series for a serving minister.", [13, 14, 15]),
    ("Menu Design", "High-density food menus engineered to stay scannable.", [16, 17, 18, 19]),
]

# index -> (client, title, category, description, craft note)
PIECES = {
4: ("Mother India · Sree Foods", "Popcorn Tub Cover — Chilli Cheese", "Packaging",
    "Retail tub wrap where the flavour drives the entire colour system: chilli red bleeding into "
    "cheese gold, with the popcorn bowl holding the optical centre. Mandatory matter — ingredients, "
    "nutrition, allergen status, FSSAI licence and barcode — is set tight into a left-hand column so "
    "the shelf-facing half of the wrap stays appetising and uncluttered.",
    "Flexible pack artwork · flavour-coded masthead · print-ready legal block"),
5: ("Mother India · Sree Foods", "Popcorn Tub Cover — Chilli Tomato", "Packaging",
    "The second SKU in the range. Only the colour field and the flavour lozenge move — sunflower "
    "yellow ground, tomato-red type, ripe tomato and chilli garnish — while masthead, bowl and legal "
    "column hold their exact positions. That discipline is what makes three separate packs read as "
    "one family from two metres away.",
    "Range extension · fixed die-line · variable colour field"),
6: ("Mother India · Sree Foods", "Popcorn Tub Cover — Cream Onion", "Packaging",
    "The mildest flavour gets the softest field: magenta-pink with cream accents and a spoon-and-onion "
    "garnish signalling a savoury, non-spicy profile. Same grid, same typography, same barcode "
    "placement — evidence that the system can absorb a fourth or fifth flavour without redrawing "
    "the pack.",
    "Third SKU · palette-only variation · scalable system"),
2: ("Shree Karni Chemicals", "A4 Manufacturer Flyer", "Print · B2B",
    "A trust-first leaflet for India's largest manufacturer of precipitated calcium carbonate. The "
    "full product range is shot as a single family photograph rather than isolated packs, then six "
    "benefit blocks in a two-column grid carry the argument — purity, consistency, cost, support, "
    "reliability. Corporate green anchors the page and a QR code bridges print to web.",
    "A4 · two-column benefit grid · QR-linked"),
12: ("Cinders Take Away", "Biryani Flyer — Front", "Print · Food",
    "The front face sells appetite before information. A full-bleed biryani hero fills the upper "
    "field, with a hand-script overlay promising the dish 'at the comfort of your home'. Address, "
    "delivery radius and a dial-now number are stacked into a single quiet block so the food is "
    "never competing with the logistics.",
    "Leaflet face · food-forward crop · script overlay"),
11: ("Cinders Take Away", "Biryani Price List — Reverse", "Print · Food",
    "The reverse is pure utility. Veg and non-veg biryanis run as parallel columns so a customer "
    "compares across, not down, and regular versus per-kilo bulk rates are split into two clearly "
    "banded blocks. One offer — a free soft drink with every kilo — sits reversed out on the fold "
    "line where the eye lands last.",
    "Reverse face · parallel price columns · single CTA"),
9: ("Sungmi India Pvt. Ltd.", "Product Catalogue — Inside Spread", "Catalogue",
    "An interior spread for a wall-panel manufacturer, split between persuasion and proof. Five "
    "advantages are numbered 01–05 for fast scanning down the left page; the facing column carries "
    "spline-system construction drawings and a full technical specification table. Timber tones are "
    "sampled from the product itself.",
    "Inside spread · numbered benefits · spec table"),
10: ("Sungmi India Pvt. Ltd.", "Product Catalogue — Outside Spread", "Catalogue",
    "The outer spread pairs an installed interior photograph with the cover panel. Four blunt "
    "badges — no water, no cement, no sand, no bricks — do the fast selling for a dry-installation "
    "system, while quick-install copy, a features list and the contact block close the fold.",
    "Outside spread · benefit badges · cover panel"),
1: ("Automotive Detailing Studio", "Google Business Profile Thumbnail", "Social · Local SEO",
    "A map-listing thumbnail designed to survive heavy downscaling. Condensed caps in high-visibility "
    "yellow and cyan are locked over a real workshop photograph, and the service list is compressed "
    "to four words — ceramic coating, PPF, painting, repairs — so the offer still resolves at "
    "map-pin size on a phone.",
    "16:9 thumbnail · legibility at small scale · location-led copy"),
3: ("Hindustan Petroleum · HP Gas", "Hose Expiry Safety Post", "Social · PSU",
    "A public-safety message that needed to feel warm rather than bureaucratic. A diagonal split "
    "divides duty from delight: hazard-red cylinder, shield motif and the instruction on the blue "
    "field, a child's smile and magnifying glass on the yellow. One instruction, one interval, one "
    "call to action — nothing else competes.",
    "Square post · diagonal split · single-message hierarchy"),
7: ("Poonia Road Carriers", "Makar Sankranti Greeting", "Social · Festival",
    "A festival greeting doing double duty as a service reminder. Paper kites and a warm sun-disc "
    "frame the wish, while a container truck grounds the brand promise of transporting anything "
    "anywhere. Contact details ride a clean white band at the base so the celebratory half stays "
    "uncluttered.",
    "Portrait post · festival iconography · service proof"),
8: ("Sandi Enterprises", "Gudi Padwa Greeting", "Social · Festival",
    "Here the greeting and the business are the same idea: 'Building New Beginnings with Strength "
    "and Prosperity'. The Gudi is raised against construction cranes at golden hour with tipper "
    "trucks entering frame, so a cement and aggregates supplier gets a festival post that still "
    "communicates what it sells.",
    "Portrait post · concept-led composite · golden-hour grade"),
13: ("Mauvin Godinho · BJP Goa", "Teachers' Day Greeting", "Political",
    "A Teachers' Day wish staged on a chalkboard, with slate, apple and globe props establishing the "
    "occasion instantly. The minister is cut out and lit to sit forward of the board, and the "
    "designation bar — Panchayat Minister, MLA Dabolim — is pinned bottom-left as the fixed element "
    "across the whole series.",
    "Square post · staged set · locked identity bar"),
14: ("Mauvin Godinho · BJP Goa", "Ganesh Chaturthi Greeting", "Political",
    "Built vertically for feed dominance. The idol is centred and richly lit against a deep field, "
    "the blessing message runs in italic across the lower third, and the party mark holds the top "
    "corner. Different festival, identical structure — the series stays recognisable at thumbnail "
    "size.",
    "Portrait post · centred focal subject · series grammar"),
15: ("Mauvin Godinho · BJP Goa", "Republic Day Greeting", "Political",
    "Republic Day reduced to three elements: a tricolour wash, the Ashoka Chakra, and a salute. "
    "Restraint is the whole design decision — date and greeting lock into the lower right so the "
    "flag is never crowded, and the same designation bar closes the frame.",
    "Square post · reductive composition · national palette"),
16: ("Restaurant Menu", "Biryani, Gravies & Combos", "Menu",
    "A high-density menu that still scans. A deep red ground with gold rules divides veg and non-veg "
    "biryanis, gravies, breads, thalis, desserts and combos into vertical columns, and dotted leaders "
    "carry the eye from dish to price. Photography is rationed to the right edge so it accents rather "
    "than crowds.",
    "Multi-column menu · dotted price leaders · rationed imagery"),
17: ("Cinders Take Away", "Beverages, Policy & Location Panel", "Menu",
    "The service panel of the menu. Beverages are priced in a tight table, operating policies become "
    "single icon lines instead of paragraphs, and the address is replaced with a drawn location map — "
    "faster for a customer than any written direction. A dish strip keeps the utility appetising.",
    "Service panel · icon-led policy lines · drawn locality map"),
18: ("Protaste Grill", "Dum Biryani Menu", "Menu",
    "Charcoal-grill character built from wood grain, stencil marks and grill icons. Dum biryani "
    "listings sit above a full-width photographic strip that acts as a horizon line for the sheet, "
    "and 'Best quality – Best service' plus a self-service note set expectations before the customer "
    "reaches the counter.",
    "Landscape menu · textured ground · photographic horizon"),
19: ("Protaste Grill", "Sandwiches, Rolls & Beverages", "Menu",
    "The companion sheet extends the range across three columns — sandwiches, kathi rolls, pizza, "
    "burgers, fried rice, cold drinks and hot beverages. Script section headers do the dividing so "
    "no extra rules are needed, keeping a long list feeling lighter than it is.",
    "Companion sheet · three-column grid · script section heads"),
}


# ---------------------------------------------------------------- chrome
def footer(s, n, dark=False):
    c = RGBColor(0x6B, 0x64, 0x78) if not dark else RGBColor(0x9A, 0x92, 0xA8)
    text(s, 0.72, H - 0.52, 4.0, 0.3, 'SANCTIFY  ·  Vasco, Goa', size=8, font=DISPLAY,
         color=c, spc=1.4, bold=True)
    text(s, W - 1.65, H - 0.52, 0.95, 0.3, f'{n:02d}', size=8, font=DISPLAY, color=c,
         align=PP_ALIGN.RIGHT, spc=1.0, bold=True)


# ---------------------------------------------------------------- 1. cover
s = slide()
grad(s, 0, 0, W, H, INK, RGBColor(0x3A, 0x0E, 0x3E), 45)
grad(s, 0, 0, 0.34, H, MAGENTA, VIOLET, 90)
# oversized watermark numeral
text(s, W - 5.4, 0.3, 5.0, 3.0, '19', size=200, font=DISPLAY, bold=True,
     color=RGBColor(0x2B, 0x1B, 0x33), align=PP_ALIGN.RIGHT)
s.shapes.add_picture(LOGO_LIGHT, Inches(1.15), Inches(0.85), Inches(2.35))
text(s, 1.15, 2.15, 8.0, 0.4, 'CREATIVE PORTFOLIO  ·  2026', size=10.5, font=DISPLAY,
     color=RGBColor(0xE9, 0x9C, 0xC4), bold=True, spc=3.2)
text(s, 1.1, 2.75, 10.6, 2.4,
     'Graphic Design\nShowcase', size=62, font=DISPLAY, bold=True, color=WHITE, line=1.02)
rect(s, 1.17, 5.28, 1.5, 0.055, fill=MAGENTA)
text(s, 1.15, 5.62, 8.6, 0.95,
     'Nineteen selected works in packaging, print, catalogue, social and menu design —\n'
     'produced by the award-winning advertising & digital marketing agency in Goa.',
     size=13, color=RGBColor(0xC9, 0xC0, 0xD6), line=1.5)
text(s, 1.15, H - 0.95, 6.0, 0.4, 'advertise to promote....', size=12, font=DISPLAY,
     color=RGBColor(0xB0, 0x6C, 0xB8), bold=True, spc=1.2)
text(s, W - 4.6, H - 0.95, 3.85, 0.4, 'www.sanctify.in   ·   +91 99233 52923', size=10.5,
     font=DISPLAY, color=RGBColor(0x9A, 0x92, 0xA8), align=PP_ALIGN.RIGHT, bold=True)

# ---------------------------------------------------------------- 2. about
s = slide()
rect(s, 0, 0, W, H, fill=LIGHT)
rect(s, 0, 0, W, 0.11, fill=MAGENTA)
chip(s, 0.72, 0.62, 'About the studio')
text(s, 0.72, 1.22, 6.4, 1.5, 'The agency behind\nthe artwork', size=38, font=DISPLAY,
     bold=True, color=INK, line=1.08)
rect(s, 0.78, 2.72, 1.15, 0.05, fill=MAGENTA)
text(s, 0.72, 3.05, 5.9, 1.7,
     'Sanctify is an award-winning advertising and digital marketing agency in Vasco, '
     'South Goa, with over 13 years of creative practice.\n'
     'Every piece in this deck was conceived, art-directed and prepared for production in-house.',
     size=12.5, color=MIDGREY, line=1.62, space_after=9)

# stat panel
rect(s, 7.15, 1.05, 5.45, 4.6, fill=WHITE, line=LINE)
rect(s, 7.15, 1.05, 5.45, 0.075, fill=VIOLET)
stats = [('13+', 'years of creative practice'), ('100+', 'websites designed & built'),
         ('4.8/5', 'rated across 128 reviews'), ('1000+', 'keywords on Google page one')]
yy = 1.42
for big, small in stats:
    text(s, 7.55, yy, 2.0, 0.62, big, size=29, font=DISPLAY, bold=True, color=MAGENTA)
    text(s, 9.55, yy + 0.13, 2.75, 0.6, small, size=11, color=MIDGREY, line=1.3)
    yy += 0.83
    if yy < 4.6:
        rect(s, 7.55, yy - 0.13, 4.65, 0.01, fill=LINE)
text(s, 7.55, 4.92, 4.7, 0.55,
     'Web Design · SEO · SEM · Social Media · Graphic Design · Online Classifieds',
     size=9.5, color=GREY, line=1.45)

# deck index — fills the lower-left field and orients the reader
text(s, 0.72, 4.98, 4.0, 0.3, 'IN THIS DECK', size=8.5, font=DISPLAY, bold=True,
     color=GREY, spc=2.0)
rect(s, 0.75, 5.28, 5.6, 0.01, fill=LINE)
for i, (sec_title, _sub, idxs) in enumerate(SECTIONS):
    cx = 0.72 + (i % 2) * 3.05
    cy = 5.46 + (i // 2) * 0.45
    text(s, cx, cy, 0.35, 0.3, f'{i + 1:02d}', size=9.5, font=DISPLAY, bold=True, color=MAGENTA)
    text(s, cx + 0.38, cy, 2.05, 0.3, sec_title, size=9.5, color=INK_SOFT)
    text(s, cx + 2.42, cy, 0.42, 0.3, str(len(idxs)), size=9.5, font=DISPLAY, color=GREY,
         align=PP_ALIGN.RIGHT)
footer(s, 2)

# ---------------------------------------------------------------- 3. capabilities
s = slide()
rect(s, 0, 0, W, H, fill=WHITE)
rect(s, 0, 0, W, 0.11, fill=VIOLET)
chip(s, 0.72, 0.62, 'Design capabilities', fill=VIOLET)
text(s, 0.72, 1.2, 8.0, 0.8, 'What we design', size=38, font=DISPLAY, bold=True, color=INK)
caps = [
    ('Packaging', 'Flavour systems, die-line artwork,\nlegal and nutrition blocks.'),
    ('Print & Leaflets', 'A4 flyers, takeaway collateral,\ndouble-sided price lists.'),
    ('Catalogues', 'Multi-page product literature,\nspec tables and drawings.'),
    ('Social Media', 'Feed-native posts, festival\ncreatives, campaign series.'),
    ('Menu Design', 'High-density food menus with\nscannable price hierarchy.'),
    ('Brand & Identity', 'Logos, brand marks and\ncampaign themes.'),
]
x0, y0, cw, ch, gx, gy = 0.72, 2.42, 3.86, 1.98, 0.19, 0.22
for i, (t, d) in enumerate(caps):
    cx = x0 + (i % 3) * (cw + gx); cy = y0 + (i // 3) * (ch + gy)
    rect(s, cx, cy, cw, ch, fill=LIGHT)
    rect(s, cx, cy, 0.055, ch, fill=MAGENTA if i % 2 == 0 else VIOLET)
    text(s, cx + 0.42, cy + 0.36, 3.1, 0.4, t, size=15.5, font=DISPLAY, bold=True, color=INK)
    text(s, cx + 0.42, cy + 0.86, 3.15, 1.0, d, size=10.5, color=MIDGREY, line=1.45)
footer(s, 3)

n = 3

# ---------------------------------------------------------------- sections
for si, (sec_title, sec_sub, idxs) in enumerate(SECTIONS, start=1):
    # divider
    n += 1
    s = slide()
    grad(s, 0, 0, W, H, INK, RGBColor(0x33, 0x0D, 0x38), 45)
    grad(s, 0, 0, 0.28, H, MAGENTA, VIOLET, 90)
    text(s, W - 4.7, 1.5, 4.0, 2.6, f'{si:02d}', size=150, font=DISPLAY, bold=True,
         color=RGBColor(0x2C, 0x1B, 0x34), align=PP_ALIGN.RIGHT)
    text(s, 1.05, 1.98, 3.6, 0.4, f'SECTION {si:02d}', size=10, font=DISPLAY,
         color=RGBColor(0xE0, 0x8C, 0xB8), bold=True, spc=3.0)
    # bottom-anchored so a two-line title grows upward instead of into the rule
    # width keeps the title clear of the watermark numeral; long titles wrap upward
    text(s, 1.0, 2.42, 7.5, 1.95, sec_title, size=44, font=DISPLAY, bold=True, color=WHITE,
         line=1.06, anchor=MSO_ANCHOR.BOTTOM)
    rect(s, 1.07, 4.58, 1.25, 0.05, fill=MAGENTA)
    text(s, 1.05, 4.92, 7.4, 0.8, sec_sub, size=13, color=RGBColor(0xC2, 0xB8, 0xD0), line=1.5)
    text(s, 1.05, 5.85, 6.0, 0.4,
         f'{len(idxs)} {"piece" if len(idxs) == 1 else "pieces"}', size=10.5, font=DISPLAY,
         color=RGBColor(0x8E, 0x84, 0x9E), bold=True, spc=1.6)

    # one slide per creative
    for k, idx in enumerate(idxs, start=1):
        n += 1
        client, title, cat, desc, craft = PIECES[idx]
        path = A[idx]
        s = slide()
        rect(s, 0, 0, W, H, fill=LIGHT)
        rect(s, 0, 0, W, 0.11, fill=MAGENTA if si % 2 else VIOLET)
        # left: copy column
        chip(s, 0.72, 0.62, cat, fill=INK)
        text(s, 0.75, 1.22, 4.35, 0.32, client.upper(), size=9.5, font=DISPLAY, bold=True,
             color=MAGENTA, spc=1.6)
        text(s, 0.72, 1.66, 4.45, 1.35, title, size=23, font=DISPLAY, bold=True,
             color=INK, line=1.14)
        rect(s, 0.78, 3.06, 0.95, 0.045, fill=MAGENTA)
        text(s, 0.72, 3.36, 4.45, 2.5, desc, size=11, color=MIDGREY, line=1.58)
        # craft notes
        text(s, 0.72, 5.72, 4.4, 0.28, 'CRAFT NOTES', size=8, font=DISPLAY, bold=True,
             color=GREY, spc=1.8)
        text(s, 0.72, 6.02, 4.45, 0.5, craft, size=9.5, color=INK_SOFT, line=1.4)
        swatches(s, 0.75, 6.63, path)
        # right: artwork stage
        rect(s, 5.62, 0.0, 7.72, H, fill=WHITE)
        art_fit(s, path, 6.05, 0.78, 6.9, 5.9)
        text(s, 6.05, H - 0.62, 6.9, 0.3,
             f'{sec_title}  ·  piece {k} of {len(idxs)}', size=8.5, font=DISPLAY,
             color=GREY, spc=1.2, bold=True, align=PP_ALIGN.RIGHT)
        text(s, 0.72, H - 0.52, 4.0, 0.3, 'SANCTIFY  ·  Vasco, Goa', size=8, font=DISPLAY,
             color=RGBColor(0x6B, 0x64, 0x78), spc=1.4, bold=True)

# ---------------------------------------------------------------- closing
n += 1
s = slide()
grad(s, 0, 0, W, H, INK, RGBColor(0x3A, 0x0E, 0x3E), 45)
grad(s, 0, 0, 0.34, H, MAGENTA, VIOLET, 90)
s.shapes.add_picture(LOGO_LIGHT, Inches(1.15), Inches(0.95), Inches(2.35))
text(s, 1.1, 2.35, 10.0, 1.9, "Let's design\nwhat's next.", size=54, font=DISPLAY, bold=True,
     color=WHITE, line=1.05)
rect(s, 1.17, 4.35, 1.5, 0.055, fill=MAGENTA)
info = [('Call', '+91 99233 52923'), ('Studio', 'Vasco, Goa, India'), ('Web', 'www.sanctify.in')]
xx = 1.15
for lab, val in info:
    text(s, xx, 4.75, 3.4, 0.3, lab.upper(), size=8.5, font=DISPLAY, bold=True,
         color=RGBColor(0xE0, 0x8C, 0xB8), spc=2.0)
    text(s, xx, 5.08, 3.7, 0.45, val, size=16, font=DISPLAY, bold=True, color=WHITE)
    xx += 3.75
text(s, 1.15, 6.02, 10.9, 0.4,
     'Award-winning advertising & digital marketing agency in Goa — '
     'design, web, SEO and social under one roof.',
     size=11.5, color=RGBColor(0xB8, 0xAE, 0xC6), line=1.5)
text(s, 1.15, 6.62, 6.0, 0.4, 'advertise to promote....', size=12, font=DISPLAY,
     color=RGBColor(0xB0, 0x6C, 0xB8), bold=True, spc=1.2)

prs.save('Sanctify-Creative-Deck.pptx')
print(f'saved PPTX with {len(prs.slides.__iter__.__self__._sldIdLst)} slides')
