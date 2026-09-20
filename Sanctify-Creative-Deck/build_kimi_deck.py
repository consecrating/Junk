"""Build the Sanctify creative deck v2 using KimiAgent.

Authors a KimiAgent ``Deck`` spec (the tool's editable intermediate
representation) and renders it with the new portfolio layouts.
"""
import sys, os, json

sys.path.insert(0, '/projects/sandbox/KimiAgent')
sys.path.insert(0, '/projects/sandbox/.kiro/skills/creative-deck/scripts')

import deck_kit as dk
from kimiagent.models import Deck, Slide, SlideType, Stat, TableData, Bullet
from kimiagent.portfolio import render_portfolio

LOGO = '/projects/sandbox/.deck-build/logo_light.png'

# ------------------------------------------------------------------ artwork
arts = dk.extract_artwork('source.pdf', 'art')
A = {a.index: a for a in arts}
assert len(arts) == 19, len(arts)


def palette_of(path, n=5):
    return ['%02X%02X%02X' % c for c in dk.palette(path, n)]


def fmt_of(a):
    return f'{a.orientation.title()} · {a.width}×{a.height}px · {a.megapixels:.1f}MP'


# ------------------------------------------------------------------ content
# (index, client, title, category, description)
PIECES = {
4: ("Mother India · Sree Foods", "Popcorn Tub Cover — Chilli Cheese", "Packaging",
    "Retail tub wrap where the flavour drives the whole colour system: chilli red bleeding into "
    "cheese gold, the popcorn bowl holding the optical centre. Mandatory matter — ingredients, "
    "nutrition, allergens, FSSAI licence, barcode — is set tight into a left column so the "
    "shelf-facing half stays appetising."),
5: ("Mother India · Sree Foods", "Popcorn Tub Cover — Chilli Tomato", "Packaging",
    "The second SKU. Only the colour field and flavour lozenge move — sunflower ground, tomato-red "
    "type, chilli and tomato garnish — while masthead, bowl and legal column hold their exact "
    "positions. That discipline is what makes three packs read as one family from two metres away."),
6: ("Mother India · Sree Foods", "Popcorn Tub Cover — Cream Onion", "Packaging",
    "The mildest flavour takes the softest field: magenta-pink with cream accents and a spoon-and-onion "
    "garnish signalling savoury, not spicy. Same die-line, same typography, same barcode position — "
    "the system can absorb a fourth flavour without redrawing the pack."),
2: ("Shree Karni Chemicals", "A4 Manufacturer Flyer", "Print · B2B",
    "A trust-first leaflet for India's largest manufacturer of precipitated calcium carbonate. The "
    "range is shot as one family photograph rather than isolated packs, then six benefit blocks in a "
    "two-column grid carry the argument. Corporate green anchors the page; a QR code bridges print "
    "to web."),
12: ("Cinders Take Away", "Biryani Flyer — Front", "Print · Food",
    "The front face sells appetite before information. A full-bleed biryani hero fills the upper "
    "field with a hand-script overlay promising the dish at home. Address, delivery radius and a "
    "dial-now number are stacked into one quiet block so the food never competes with logistics."),
11: ("Cinders Take Away", "Biryani Price List — Reverse", "Print · Food",
    "The reverse is pure utility. Veg and non-veg run as parallel columns so the customer compares "
    "across rather than down, and regular versus per-kilo bulk rates split into two banded blocks. "
    "One offer sits reversed out on the fold line, where the eye lands last."),
9: ("Sungmi India Pvt. Ltd.", "Catalogue — Inside Spread", "Catalogue",
    "An interior spread split between persuasion and proof. Five advantages are numbered 01–05 for "
    "fast scanning down the left page; the facing column carries spline-system construction drawings "
    "and a full specification table. The timber palette is sampled from the product itself."),
10: ("Sungmi India Pvt. Ltd.", "Catalogue — Outside Spread", "Catalogue",
    "The outer spread pairs an installed interior photograph with the cover panel. Four blunt "
    "badges — no water, no cement, no sand, no bricks — do the fast selling for a dry-installation "
    "system, while quick-install copy, features and the contact block close the fold."),
1: ("Automotive Detailing Studio", "Google Business Profile Thumbnail", "Social · Local SEO",
    "A map-listing thumbnail engineered to survive heavy downscaling. Condensed caps in "
    "high-visibility yellow and cyan lock over a real workshop photograph, and the service list is "
    "compressed to four words so the offer still resolves at map-pin size on a phone."),
3: ("Hindustan Petroleum · HP Gas", "Hose Expiry Safety Post", "Social · PSU",
    "A public-safety message that had to feel warm, not bureaucratic. A diagonal split divides duty "
    "from delight: hazard-red cylinder and shield on the blue field, a child's smile on the yellow. "
    "One instruction, one interval, one call to action — nothing else competes."),
7: ("Poonia Road Carriers", "Makar Sankranti Greeting", "Social · Festival",
    "A festival greeting doing double duty as a service reminder. Paper kites and a warm sun-disc "
    "frame the wish while a container truck grounds the promise of transporting anything anywhere. "
    "Contact details ride a clean white band so the celebratory half stays uncluttered."),
8: ("Sandi Enterprises", "Gudi Padwa Greeting", "Social · Festival",
    "Here the greeting and the business are the same idea — building new beginnings. The Gudi is "
    "raised against construction cranes at golden hour with tipper trucks entering frame, so a "
    "cement and aggregates supplier gets a festival post that still says what it sells."),
13: ("Mauvin Godinho · BJP Goa", "Teachers' Day Greeting", "Political",
    "Staged on a chalkboard, with slate, apple and globe props establishing the occasion instantly. "
    "The minister is cut out and lit to sit forward of the board, and the designation bar is pinned "
    "bottom-left as the fixed element across the whole series."),
14: ("Mauvin Godinho · BJP Goa", "Ganesh Chaturthi Greeting", "Political",
    "Built vertically for feed dominance. The idol is centred and richly lit against a deep field, "
    "the blessing runs in italic across the lower third, and the party mark holds the top corner. "
    "Different festival, identical structure — the series stays recognisable at thumbnail size."),
15: ("Mauvin Godinho · BJP Goa", "Republic Day Greeting", "Political",
    "Reduced to three elements: a tricolour wash, the Ashoka Chakra, and a salute. Restraint is the "
    "entire design decision — date and greeting lock into the lower right so the flag is never "
    "crowded, and the same designation bar closes the frame."),
16: ("Restaurant Menu", "Biryani, Gravies & Combos", "Menu",
    "A high-density menu that still scans. A deep red ground with gold rules divides veg and non-veg "
    "biryanis, gravies, breads, thalis and combos into vertical columns, and dotted leaders carry "
    "the eye from dish to price. Photography is rationed to one edge so it accents rather than crowds."),
17: ("Cinders Take Away", "Beverages, Policy & Location", "Menu",
    "The service panel. Beverages are priced in a tight table, operating policies become single icon "
    "lines instead of paragraphs, and the address is replaced with a drawn location map — faster for "
    "a customer than any written direction. A dish strip keeps the utility appetising."),
18: ("Protaste Grill", "Dum Biryani Menu", "Menu",
    "Charcoal-grill character built from wood grain, stencil marks and grill icons. Dum biryani "
    "listings sit above a full-width photographic strip that acts as a horizon line for the sheet, "
    "and a self-service note sets expectations before the customer reaches the counter."),
19: ("Protaste Grill", "Sandwiches, Rolls & Beverages", "Menu",
    "The companion sheet extends the range across three columns — sandwiches, kathi rolls, pizza, "
    "burgers, fried rice and beverages. Script section headers do the dividing so no extra rules are "
    "needed, keeping a long list feeling lighter than it is."),
}

SECTIONS = [
    ("Packaging Design", "FMCG pack artwork built as a shelf-ready flavour system.", [4, 5, 6]),
    ("Print & Flyers", "Leaflets and takeaway collateral that must work in the hand.", [2, 12, 11]),
    ("Corporate Catalogue", "Multi-page product literature for a manufacturing brand.", [9, 10]),
    ("Social & Festival", "Feed-native posts for retail, PSU and B2B brands.", [1, 3, 7, 8]),
    ("Political Communication", "A consistent greeting series for a serving minister.", [13, 14, 15]),
    ("Menu Design", "High-density food menus engineered to stay scannable.", [16, 17, 18, 19]),
]

# ------------------------------------------------------------------ assemble
slides = [
    Slide(type=SlideType.COVER, title='Graphic Design\nShowcase',
          subtitle='Nineteen selected works in packaging, print, catalogue, social and menu design — '
                   'produced in-house by the award-winning advertising & digital marketing agency in Goa.',
          meta={'logo': LOGO, 'eyebrow': 'Creative Portfolio · 2026', 'watermark': '19',
                'footer': 'advertise to promote....   ·   www.sanctify.in   ·   +91 99233 52923'}),

    # KimiAgent native agenda layout
    Slide(type=SlideType.AGENDA, title='What\'s inside',
          bullets=[Bullet(text=f'{t} — {len(i)} {"piece" if len(i) == 1 else "pieces"}')
                   for t, _s, i in SECTIONS]),

    # KimiAgent native KPI layout
    Slide(type=SlideType.STATS, title='The studio', subtitle='Sanctify — Vasco, South Goa',
          stats=[Stat(value='13+', label='Years of practice', detail='Creative work since 2012'),
                 Stat(value='100+', label='Websites delivered', detail='Designed and developed'),
                 Stat(value='4.8/5', label='Client rating', detail='Across 128 reviews'),
                 Stat(value='1000+', label='Keywords ranking', detail='On Google page one')]),

    # New grid layout: the whole portfolio at a glance
    Slide(type=SlideType.GRID, title='The collection',
          subtitle='All nineteen pieces — packaging, print, catalogue, social, political and menu design.',
          images=[A[i].path for t, s, idxs in SECTIONS for i in idxs],
          meta={'cols': 7}),
]

n = 0
for si, (title, sub, idxs) in enumerate(SECTIONS, start=1):
    slides.append(Slide(type=SlideType.SECTION, title=title, subtitle=sub,
                        caption=f'{len(idxs)} {"piece" if len(idxs) == 1 else "pieces"}',
                        meta={'number': f'{si:02d}', 'eyebrow': f'Section {si:02d}'}))
    for idx in idxs:
        client, ptitle, cat, desc = PIECES[idx]
        a = A[idx]
        n += 1
        slides.append(Slide(
            type=SlideType.GALLERY, title=ptitle, image_path=a.path, caption=desc,
            meta={'client': client, 'category': cat, 'format': fmt_of(a),
                  'palette': palette_of(a.path)},
            notes=f'{client} — {ptitle}. {desc}'))

# KimiAgent native quote + table layouts
slides.append(Slide(type=SlideType.QUOTE,
                    quote='Enthusiastic members. Great for luxury brands. They are fast to learn '
                          'about business needs and strategise digital marketing accordingly.',
                    attribution='Moin · client testimonial, sanctify.in'))

slides.append(Slide(type=SlideType.TABLE, title='Design disciplines',
                    subtitle='What this portfolio covers, and the formats delivered.',
                    table=TableData(
                        headers=['Discipline', 'Pieces', 'Formats delivered'],
                        rows=[['Packaging Design', '3', 'Tub wrap artwork, flavour range systems'],
                              ['Print & Flyers', '3', 'A4 leaflets, double-sided takeaway collateral'],
                              ['Corporate Catalogue', '2', 'Multi-page spreads, spec tables'],
                              ['Social & Festival', '4', 'Square and portrait posts, map thumbnails'],
                              ['Political Communication', '3', 'Greeting series, feed-native posts'],
                              ['Menu Design', '4', 'Multi-column menus, service panels']])))

slides.append(Slide(type=SlideType.CONTACT, title="Let's design\nwhat's next.",
                    subtitle='Award-winning advertising & digital marketing agency in Goa — '
                             'design, web, SEO and social under one roof.',
                    caption='advertise to promote....',
                    meta={'logo': LOGO,
                          'contact': [['Call', '+91 99233 52923'],
                                      ['Studio', 'Vasco, Goa, India'],
                                      ['Web', 'www.sanctify.in']]}))

deck = Deck(title='Sanctify — Graphic Design Showcase',
            subtitle='Creative Portfolio 2026',
            author='Sanctify · Vasco, Goa',
            theme='sanctify', slides=slides)

out = render_portfolio(deck, 'Sanctify-Creative-Deck-v2.pptx')
with open('Sanctify-Creative-Deck-v2.spec.json', 'w') as fh:
    json.dump(deck.to_dict(), fh, indent=2)
print(f'rendered {out} · {len(deck.slides)} slides · gallery pieces: {n}')
print('spec written: Sanctify-Creative-Deck-v2.spec.json')
