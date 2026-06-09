"""
build_index.py  —  PulseAgent AI  (Fixed)
==========================================
Correctly loads ALL data sources:
  1. items_metadata.pkl  — but checks if it's already the built version
                           and falls back to the original 1,000-item pkl
  2. amazon_fashion.csv  — 115 Nigerian synthetic items
  3. 400 Nigerian restaurants (hardcoded)
  4. Extra synthetic items  (Books, Food, Fashion, Electronics, Beauty)

The key fix: stores a backup of the original Amazon pkl so re-runs
always start from the full 1,000 items, not the previously built 201.

Run from repo root:
    python data/scripts/build_index.py
"""

import os, sys, pickle, random
import numpy as np
import pandas as pd
import faiss
from pathlib import Path
from collections import Counter

random.seed(42)

BASE_DIR = Path(__file__).resolve().parents[2]
OUT_DIR  = BASE_DIR / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PKL_PATH     = OUT_DIR / "items_metadata.pkl"
PKL_ORIG     = OUT_DIR / "items_metadata_original.pkl"   # backup of Amazon-only pkl
CSV_PATH     = OUT_DIR / "amazon_fashion.csv"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalise(item: dict) -> dict:
    item = item.copy()
    item['category'] = str(item.get('category', '')).strip().title()
    item['name']     = str(item.get('name', ''))[:120]
    return item


# ── 1. Load original Amazon items ─────────────────────────────────────────────
def load_amazon_items() -> list[dict]:
    """
    Prefer the backup (items_metadata_original.pkl) if it exists.
    If not, load items_metadata.pkl and save a backup if it looks like
    the raw Amazon data (categories Fashion/Electronics/Beauty only, >500 items).
    """
    if PKL_ORIG.exists():
        with open(PKL_ORIG, 'rb') as f:
            data = pickle.load(f)
        items = [_normalise(v) for v in data.values()]
        print(f"Loaded original Amazon backup: {len(items)} items")
        return items

    if not PKL_PATH.exists():
        print("[WARN] No items_metadata.pkl found — starting from scratch")
        return []

    with open(PKL_PATH, 'rb') as f:
        data = pickle.load(f)

    items = [_normalise(v) for v in data.values()]
    cats  = set(i['category'] for i in items)

    # If it looks like the raw Amazon pkl (only Amazon categories, 500+ items)
    if len(items) >= 500 and cats <= {'Fashion', 'Electronics', 'Beauty'}:
        print(f"Detected raw Amazon pkl ({len(items)} items) — saving backup")
        with open(PKL_ORIG, 'wb') as f:
            pickle.dump(data, f)
    else:
        print(f"[INFO] items_metadata.pkl has {len(items)} items across {cats}")
        print("       If this is wrong, delete it and re-run — the script will rebuild from scratch.")

    return items


# ── 2. Nigerian synthetic CSV ─────────────────────────────────────────────────
def load_synthetic_csv() -> list[dict]:
    if not CSV_PATH.exists():
        print(f"[WARN] {CSV_PATH} not found")
        return []
    df = pd.read_csv(CSV_PATH).fillna('')
    items = []
    for _, row in df.iterrows():
        items.append({
            'id':           str(row.get('id', '')),
            'name':         str(row.get('name', ''))[:120],
            'category':     str(row.get('category', '')).strip().title(),
            'price':        int(row.get('price', 0) or 0),
            'brand':        str(row.get('brand', '')),
            'description':  str(row.get('description', '')),
            'stars':        float(row.get('stars', 4.0) or 4.0),
            'review_count': int(row.get('review_count', 100) or 100),
        })
    print(f"Loaded synthetic CSV: {len(items)} items")
    return items


# ── 3. Restaurant catalog ─────────────────────────────────────────────────────
BASE_RESTAURANTS = [
    {"id":"r001","name":"Chicken Republic Mighty Meal Deal","brand":"Chicken Republic","price":6500,"stars":4.5,"review_count":12400,"description":"Nigeria's most popular fast food combo — full chicken meal with sides and drink."},
    {"id":"r002","name":"Chicken Republic Streetwise Combo","brand":"Chicken Republic","price":4200,"stars":4.4,"review_count":9876,"description":"Value combo for students and working-class Lagosians. E dey everywhere."},
    {"id":"r003","name":"Sweet Sensation Jollof Rice and Chicken","brand":"Sweet Sensation","price":5500,"stars":4.3,"review_count":8234,"description":"Party-style smoky jollof rice with grilled chicken. Authentic Nigerian taste."},
    {"id":"r004","name":"Sweet Sensation Pepper Soup Set Meal","brand":"Sweet Sensation","price":7800,"stars":4.4,"review_count":4321,"description":"Hot and spicy pepper soup with assorted meat."},
    {"id":"r005","name":"Mr Biggs Meat Pie 6-pack","brand":"Mr Biggs","price":4200,"stars":4.6,"review_count":21000,"description":"Iconic Nigerian meat pie with flaky pastry. Since 1986, e never disappoint."},
    {"id":"r006","name":"Mr Biggs Full Breakfast Set","brand":"Mr Biggs","price":5500,"stars":4.2,"review_count":3456,"description":"Eggs, sausage, baked beans and toast. Classic Nigerian fast food breakfast."},
    {"id":"r007","name":"Tantalizers Egusi Soup and Eba Set Meal","brand":"Tantalizers","price":5800,"stars":4.3,"review_count":7654,"description":"Authentic egusi soup with smooth eba. True home-cooked taste for less."},
    {"id":"r008","name":"Tantalizers Assorted Peppered Gizzard","brand":"Tantalizers","price":3800,"stars":4.2,"review_count":5432,"description":"Spicy peppered gizzard snack — perfect with cold drink or as side."},
    {"id":"r009","name":"Kilimanjaro Suya Platter for Two","brand":"Kilimanjaro","price":14000,"stars":4.7,"review_count":6789,"description":"Signature suya platter with peanut spice mix, raw onions and fresh tomatoes."},
    {"id":"r010","name":"Kilimanjaro Shawarma Wrap","brand":"Kilimanjaro","price":5200,"stars":4.5,"review_count":9012,"description":"Filled shawarma with grilled chicken, cabbage, mayo and spicy sauce."},
    {"id":"r011","name":"Yellow Chilli Pepper Soup with Catfish","brand":"The Yellow Chilli","price":9500,"stars":4.8,"review_count":4567,"description":"Spicy catfish pepper soup — a Lagos celebrity spot favourite."},
    {"id":"r012","name":"Yellow Chilli Oha Soup and Fufu","brand":"The Yellow Chilli","price":11500,"stars":4.7,"review_count":3210,"description":"Traditional Igbo oha soup with silky fufu. Deep Naija flavour."},
    {"id":"r013","name":"Nando's PERi-PERi Chicken Quarter Meal","brand":"Nando's","price":8500,"stars":4.5,"review_count":11234,"description":"Flame-grilled PERi-PERi quarter chicken with two sides of your choice."},
    {"id":"r014","name":"Nando's Whole PERi-PERi Chicken","brand":"Nando's","price":18000,"stars":4.6,"review_count":7654,"description":"Full PERi-PERi chicken — enough for two. Great for date night in Lagos."},
    {"id":"r015","name":"Domino's Pizza Nigerian Pepperoni Large","brand":"Domino's","price":12500,"stars":4.3,"review_count":15432,"description":"Large pepperoni pizza with extra cheese. Delivery in 30 minutes on the Island."},
    {"id":"r016","name":"Domino's Pizza Jerk Chicken Large","brand":"Domino's","price":13500,"stars":4.4,"review_count":9876,"description":"Jerk chicken pizza — West African-inspired twist on the classic."},
    {"id":"r017","name":"Ocean Basket Fish and Chips Platter","brand":"Ocean Basket","price":16500,"stars":4.4,"review_count":5678,"description":"Fresh hake fillet with crispy chips and tartare sauce."},
    {"id":"r018","name":"Terra Kulture Buka Stew Combo","brand":"Terra Kulture","price":8500,"stars":4.8,"review_count":2345,"description":"Authentic buka-style stew with choice of swallow."},
    {"id":"r019","name":"Spice Route Lamb Suya Skewers","brand":"Spice Route","price":12000,"stars":4.7,"review_count":1876,"description":"Slow-marinated lamb suya on skewers with spiced peanut crust."},
    {"id":"r020","name":"Mega Chicken Whole Fried Chicken Meal","brand":"Mega Chicken","price":7500,"stars":4.3,"review_count":4321,"description":"Crispy whole fried chicken with jollof rice and coleslaw."},
    {"id":"r021","name":"Bukka Hut Buka Lunch Special","brand":"Bukka Hut","price":4500,"stars":4.6,"review_count":6543,"description":"Daily buka lunch — rotating Nigerian classics like efo riro, ofe akwu, edikaikong."},
    {"id":"r022","name":"Bukka Hut Banga Soup and Starch","brand":"Bukka Hut","price":6500,"stars":4.7,"review_count":3456,"description":"Delta-style banga soup with starch. Warri people go appreciate this one."},
    {"id":"r023","name":"The Place Restaurant Afang and Garri","brand":"The Place","price":7500,"stars":4.5,"review_count":4567,"description":"Traditional Efik afang soup with smooth garri. Very filling and authentic."},
    {"id":"r024","name":"The Place Asun Spicy Goat and Drink","brand":"The Place","price":9500,"stars":4.6,"review_count":5678,"description":"Smoky peppered goat meat — perfect finger food for owambe warm-up."},
    {"id":"r025","name":"Sheraton Lagos Eko Kitchen Sunday Brunch","brand":"Sheraton Lagos","price":35000,"stars":4.9,"review_count":1234,"description":"Premium Lagos Sunday brunch — extensive Nigerian and international buffet spread."},
    {"id":"r026","name":"Radisson Blu Lagos Terrace BBQ Night","brand":"Radisson Blu","price":28000,"stars":4.8,"review_count":987,"description":"Rooftop BBQ on Lagos Island. Best view of the city while eating grilled meats."},
    {"id":"r027","name":"Cold Stone Creamery Signature Creation","brand":"Cold Stone","price":4500,"stars":4.5,"review_count":18765,"description":"Made-to-order ice cream mixed with toppings on a frozen stone. Lagos heat fix."},
    {"id":"r028","name":"Pinkberry Yoghurt Original with Toppings","brand":"Pinkberry","price":3800,"stars":4.4,"review_count":9876,"description":"Tart frozen yoghurt with fresh fruit toppings. Healthy Lagos dessert."},
    {"id":"r029","name":"Barcelos Flame-Grilled Chicken Burger","brand":"Barcelos","price":7500,"stars":4.4,"review_count":6543,"description":"Portuguese-style flame-grilled chicken burger with peri-peri sauce."},
    {"id":"r030","name":"Tastee Fried Chicken TFC Box Meal","brand":"Tastee Fried Chicken","price":5500,"stars":4.2,"review_count":8765,"description":"Classic Nigerian fried chicken with spiced coating and jollof rice."},
    {"id":"r031","name":"Cafe Neo Lagos Cold Brew Coffee","brand":"Cafe Neo","price":2800,"stars":4.6,"review_count":7654,"description":"Smooth cold brew from Nigerian-sourced Kafanchan beans. VI crowd favourite."},
    {"id":"r032","name":"Cafe Neo Nigerian Puff Puff and Tea","brand":"Cafe Neo","price":2500,"stars":4.7,"review_count":5432,"description":"Fresh fried puff puff with Nigerian spiced tea. Nostalgic breakfast choice."},
    {"id":"r033","name":"Cactus Restaurant Grilled Tilapia","brand":"Cactus Restaurant","price":14500,"stars":4.7,"review_count":3210,"description":"Whole grilled tilapia with fried plantain and pepper sauce."},
    {"id":"r034","name":"Cactus Restaurant Lamb Pepper Stew","brand":"Cactus Restaurant","price":16500,"stars":4.8,"review_count":2345,"description":"Slow-cooked lamb in rich Nigerian pepper stew."},
    {"id":"r035","name":"Agege Bread with Akara and Groundnut","brand":"Street Vendor","price":800,"stars":4.8,"review_count":54321,"description":"The original Lagos breakfast — soft Agege bread with hot akara balls and groundnut."},
    {"id":"r036","name":"Boli and Groundnut Street Combo","brand":"Street Vendor","price":600,"stars":4.9,"review_count":43210,"description":"Roasted plantain with salted groundnut. Sunset snack on Lagos roads."},
    {"id":"r037","name":"Suya Roll Wrap Lagos Island","brand":"Street Vendor","price":2500,"stars":4.8,"review_count":12345,"description":"Spiced suya in soft wrap with cabbage and pepper sauce."},
    {"id":"r038","name":"Mama Put Rice and Stew Large Plate","brand":"Local Buka","price":1500,"stars":4.7,"review_count":32100,"description":"Big plate of white rice and red stew with fish or beef."},
    {"id":"r039","name":"Lagos Night Market Isi Ewu Goat Head","brand":"Buka Palace","price":4500,"stars":4.9,"review_count":8765,"description":"Freshly cooked isi ewu — Igbo delicacy spiced with ugba and utazi leaves."},
    {"id":"r040","name":"Owambe Caterer Fried Rice and Chicken","brand":"Elite Caterers","price":3500,"stars":4.7,"review_count":15432,"description":"Classic Nigerian party fried rice with grilled chicken and coleslaw."},
    {"id":"r041","name":"Abuja Bistro Grilled Chicken and Chips","brand":"Abuja Bistro","price":9500,"stars":4.5,"review_count":3456,"description":"Flame-grilled chicken breast with crispy chips. Popular Garki Area 11 lunch spot."},
    {"id":"r042","name":"PH Seafood Kitchen Fresh Snails in Sauce","brand":"PH Seafood Kitchen","price":12000,"stars":4.8,"review_count":2345,"description":"Fresh giant snails in pepper sauce — a Rivers State delicacy."},
    {"id":"r043","name":"Ibadan Buka Amala and Gbegiri Soup","brand":"Classic Buka","price":2200,"stars":4.9,"review_count":21000,"description":"Authentic Ibadan amala with gbegiri, ewedu and assorted meat. Naija comfort food."},
    {"id":"r044","name":"Enugu Ofe Nsala White Soup and Fufu","brand":"Oji River Kitchen","price":5800,"stars":4.8,"review_count":3456,"description":"Traditional Igbo white soup with catfish and fufu."},
    {"id":"r045","name":"Kano Tuwon Shinkafa and Miyan Kuka","brand":"Arewa Kitchen","price":2500,"stars":4.9,"review_count":18765,"description":"Northern Nigeria tuwon shinkafa with miyan kuka. True Hausa home cooking."},
    {"id":"r046","name":"Bar Beach Grilled Catfish Platter","brand":"Bar Beach Grill","price":18000,"stars":4.7,"review_count":4567,"description":"Giant catfish grilled to perfection right on the beach."},
    {"id":"r047","name":"Nike Lake Resort Pounded Yam and Ofe Onugbu","brand":"Nike Lake Resort","price":9500,"stars":4.8,"review_count":2109,"description":"Authentic Enugu-style pounded yam with bitter leaf soup."},
    {"id":"r048","name":"Caliente Lagos Shrimp Tacos","brand":"Caliente","price":11500,"stars":4.6,"review_count":3456,"description":"Nigerian-spiced shrimp tacos with avocado and hot suya sauce."},
    {"id":"r049","name":"Crunchies Fried Chicken Family Bucket","brand":"Crunchies","price":15000,"stars":4.3,"review_count":6789,"description":"Nigerian family chicken bucket with sides."},
    {"id":"r050","name":"Yakoyo Restaurant Efo Riro and Semo","brand":"Yakoyo","price":6500,"stars":4.8,"review_count":4321,"description":"Yoruba-style efo riro with assorted meat and smooth semolina."},
]

def build_restaurants() -> list[dict]:
    rests = []
    while len(rests) < 400:
        base = BASE_RESTAURANTS[len(rests) % 50].copy()
        idx  = len(rests)
        base['id']           = f"r{idx+1:03d}"
        base['price']        = int(base['price'] * random.uniform(0.88, 1.12))
        base['review_count'] = max(100, base['review_count'] - random.randint(0,300))
        base['category']     = 'Restaurants'
        rests.append(base)
    return rests


# ── 4. Extra synthetic items ──────────────────────────────────────────────────
EXTRAS = [
    {"id":"ex_f001","name":"New Balance 550 Lifestyle Sneakers","category":"Fashion","brand":"New Balance","price":48000,"stars":4.6,"review_count":34567,"description":"Classic retro court sneaker. White and cream colorway — very popular in Lagos right now."},
    {"id":"ex_f002","name":"Levi's 501 Original Fit Jeans","category":"Fashion","brand":"Levi's","price":38000,"stars":4.5,"review_count":87432,"description":"The iconic straight-fit denim. Works anywhere in Lagos — campus to Eko Hotel."},
    {"id":"ex_f003","name":"Zara Oversized Linen Shirt","category":"Fashion","brand":"Zara","price":22000,"stars":4.3,"review_count":12340,"description":"Lightweight linen shirt perfect for Lagos heat."},
    {"id":"ex_f004","name":"H&M Slim-Fit Chino Trousers","category":"Fashion","brand":"H&M","price":18500,"stars":4.2,"review_count":9870,"description":"Slim-fit cotton chinos in khaki, black and navy."},
    {"id":"ex_f005","name":"Puma RS-X Retro Sneakers","category":"Fashion","brand":"Puma","price":42000,"stars":4.4,"review_count":21000,"description":"Bold chunky-sole sneakers with retro running DNA. Lagos campus favourite."},
    {"id":"ex_f006","name":"Converse Chuck Taylor All Star High","category":"Fashion","brand":"Converse","price":28000,"stars":4.5,"review_count":65432,"description":"The iconic high-top canvas sneaker. Goes with anything."},
    {"id":"ex_f007","name":"Ankara Print Blazer Jacket Women","category":"Fashion","brand":"Ankara House","price":19500,"stars":4.6,"review_count":5432,"description":"Vibrant Ankara blazer for office and events."},
    {"id":"ex_f008","name":"Aso-Oke Wedding Headtie Gele","category":"Fashion","brand":"Royal Fabrics","price":12000,"stars":4.8,"review_count":8765,"description":"Premium aso-oke gele for weddings and owambe."},
    {"id":"ex_f009","name":"Tommy Hilfiger Classic Polo Shirt","category":"Fashion","brand":"Tommy Hilfiger","price":35000,"stars":4.4,"review_count":23456,"description":"Classic cotton polo shirt with iconic flag logo."},
    {"id":"ex_f010","name":"Kaftan Senator Ankara Print Men","category":"Fashion","brand":"Lagos Tailors","price":16500,"stars":4.7,"review_count":6543,"description":"Casual senator kaftan for weekend wear. Multiple Ankara prints."},
    {"id":"ex_f011","name":"Nike Dri-FIT Training T-Shirt","category":"Fashion","brand":"Nike","price":18000,"stars":4.5,"review_count":43210,"description":"Moisture-wicking training shirt. Perfect for Lagos gym sessions."},
    {"id":"ex_f012","name":"Adidas Trefoil Hoodie Classic","category":"Fashion","brand":"Adidas","price":38000,"stars":4.4,"review_count":32100,"description":"Comfortable cotton hoodie with iconic trefoil logo."},
    {"id":"ex_f013","name":"Buba and Sokoto Yoruba Traditional Set","category":"Fashion","brand":"Aso Ebi Palace","price":22000,"stars":4.7,"review_count":4321,"description":"Classic Yoruba buba and sokoto set. Perfect for Eid, owambe and cultural events."},
    {"id":"ex_f014","name":"Polo Ralph Lauren Classic Fit Shirt","category":"Fashion","brand":"Ralph Lauren","price":55000,"stars":4.6,"review_count":18765,"description":"Premium cotton dress shirt. Investment piece for Lagos professionals."},
    {"id":"ex_f015","name":"Iro and Buba Matching Ankara Set Women","category":"Fashion","brand":"Aso Ebi Palace","price":19500,"stars":4.7,"review_count":6543,"description":"Traditional Yoruba iro and buba in premium Ankara. Perfect for owambe."},
    {"id":"ex_e001","name":"Samsung Galaxy A55 5G Smartphone","category":"Electronics","brand":"Samsung","price":265000,"stars":4.5,"review_count":34521,"description":"Mid-range Samsung flagship with AMOLED display, 50MP camera and 5000mAh battery."},
    {"id":"ex_e002","name":"Infinix Note 30 Pro Smartphone","category":"Electronics","brand":"Infinix","price":185000,"stars":4.4,"review_count":18765,"description":"AMOLED display, 45W fast charging, 108MP main camera."},
    {"id":"ex_e003","name":"Hisense 43-inch FHD Smart TV","category":"Electronics","brand":"Hisense","price":265000,"stars":4.3,"review_count":12340,"description":"Full HD Smart TV with Android OS, built-in Netflix and YouTube."},
    {"id":"ex_e004","name":"Anker PowerCore 20000 Power Bank","category":"Electronics","brand":"Anker","price":28000,"stars":4.7,"review_count":43210,"description":"20,000mAh high-capacity power bank. The NEPA solution Lagos deserves."},
    {"id":"ex_e005","name":"Oraimo FreePods 4 TWS Earbuds","category":"Electronics","brand":"Oraimo","price":12500,"stars":4.6,"review_count":54321,"description":"True wireless earbuds with 32hr total playback, ENC noise cancellation."},
    {"id":"ex_e006","name":"JBL Flip 6 Bluetooth Speaker","category":"Electronics","brand":"JBL","price":62000,"stars":4.6,"review_count":43210,"description":"Waterproof Bluetooth speaker with deep bass and 12hr battery life."},
    {"id":"ex_e007","name":"Xiaomi Redmi Note 13 Pro 4G","category":"Electronics","brand":"Xiaomi","price":198000,"stars":4.5,"review_count":32100,"description":"200MP OIS camera, 120Hz AMOLED display, 5100mAh battery."},
    {"id":"ex_e008","name":"itel S24 Budget Smartphone","category":"Electronics","brand":"itel","price":85000,"stars":4.1,"review_count":15432,"description":"Affordable smartphone with decent camera and all-day battery."},
    {"id":"ex_e009","name":"Romoss 30000mAh Power Bank PD","category":"Electronics","brand":"Romoss","price":22000,"stars":4.5,"review_count":9876,"description":"Massive capacity with PD fast charge. Charge laptop and phone simultaneously."},
    {"id":"ex_e010","name":"Tecno Spark 20 Pro Smartphone","category":"Electronics","brand":"Tecno","price":145000,"stars":4.3,"review_count":23456,"description":"6.78 inch FHD+ display, 256GB storage, 5000mAh battery."},
    {"id":"ex_b001","name":"Fenty Beauty Pro Filtr Foundation","category":"Beauty","brand":"Fenty Beauty","price":28000,"stars":4.7,"review_count":87654,"description":"40+ shades including deep Nigerian skin tones. Buildable coverage, no cake-face."},
    {"id":"ex_b002","name":"Black Opal True Color Foundation Stick","category":"Beauty","brand":"Black Opal","price":9000,"stars":4.5,"review_count":12340,"description":"Concealer stick made for deeper complexions."},
    {"id":"ex_b003","name":"Revlon ColorStay Foundation SPF 15","category":"Beauty","brand":"Revlon","price":12500,"stars":4.4,"review_count":23456,"description":"24-hour wear foundation that does not budge in heat or humidity."},
    {"id":"ex_b004","name":"Dark and Lovely Rich Colour Hair Kit","category":"Beauty","brand":"Dark and Lovely","price":5500,"stars":4.3,"review_count":18765,"description":"Long-lasting hair colour kit for natural African hair textures."},
    {"id":"ex_b005","name":"ORS Olive Oil Replenishing Conditioner","category":"Beauty","brand":"ORS","price":7200,"stars":4.5,"review_count":9870,"description":"Deep conditioning treatment for relaxed and natural hair."},
    {"id":"ex_b006","name":"Olay Total Effects 7-in-1 Moisturiser","category":"Beauty","brand":"Olay","price":18500,"stars":4.4,"review_count":34521,"description":"Anti-ageing moisturiser with SPF 15. Works well for Nigerian skin."},
    {"id":"ex_b007","name":"Maybelline Fit Me Matte Poreless Foundation","category":"Beauty","brand":"Maybelline","price":11000,"stars":4.4,"review_count":43210,"description":"Oil-free, pore-minimising foundation with shades for deeper skin tones."},
    {"id":"ex_b008","name":"LOreal Elvive Extraordinary Oil Hair Serum","category":"Beauty","brand":"L'Oreal","price":8500,"stars":4.5,"review_count":21000,"description":"Lightweight hair oil that tames frizz and adds shine in Lagos humidity."},
    {"id":"ex_bk001","name":"Half of a Yellow Sun by Chimamanda Adichie","category":"Books","brand":"Knopf","price":8000,"stars":4.8,"review_count":43210,"description":"Powerful Booker Prize novel set during the Nigeria-Biafra War. Required reading."},
    {"id":"ex_bk002","name":"The Psychology of Money Morgan Housel","category":"Books","brand":"Harriman House","price":9500,"stars":4.7,"review_count":65432,"description":"19 timeless lessons on wealth, greed, and happiness. Top pick for young Nigerians."},
    {"id":"ex_bk003","name":"Rich Dad Poor Dad Robert Kiyosaki","category":"Books","brand":"Plata","price":7500,"stars":4.6,"review_count":87654,"description":"The classic personal finance book. Every Nigerian youth should read this."},
    {"id":"ex_bk004","name":"The 48 Laws of Power Robert Greene","category":"Books","brand":"Penguin","price":9000,"stars":4.5,"review_count":54321,"description":"48 laws distilled from history's most powerful figures."},
    {"id":"ex_bk005","name":"Think and Grow Rich Napoleon Hill","category":"Books","brand":"TarcherPerigee","price":6500,"stars":4.5,"review_count":43210,"description":"Classic mindset and success book for Nigerian entrepreneurs."},
    {"id":"ex_bk006","name":"WAEC Past Questions Answers Compendium","category":"Books","brand":"Tonad","price":3500,"stars":4.6,"review_count":32100,"description":"Comprehensive WAEC past questions 2010-2023. Essential for every SS3 student."},
    {"id":"ex_bk007","name":"Purple Hibiscus Chimamanda Ngozi Adichie","category":"Books","brand":"Algonquin","price":7000,"stars":4.7,"review_count":34521,"description":"Award-winning debut novel about faith, love and revolution in Nigeria."},
    {"id":"ex_bk008","name":"The Alchemist Paulo Coelho","category":"Books","brand":"HarperOne","price":7000,"stars":4.6,"review_count":76543,"description":"Inspirational fable about following your personal legend."},
    {"id":"ex_bk009","name":"Atomic Habits James Clear","category":"Books","brand":"Avery","price":8500,"stars":4.8,"review_count":98765,"description":"The number 1 self-improvement book worldwide. Every Lagos professional reads this."},
    {"id":"ex_bk010","name":"Things Fall Apart Chinua Achebe","category":"Books","brand":"Heinemann","price":4500,"stars":4.9,"review_count":87654,"description":"The African literary classic. A timeless Nigerian story every student must read."},
    {"id":"ex_bk011","name":"Digital Marketing for Nigerians","category":"Books","brand":"Femi Media","price":5500,"stars":4.6,"review_count":3456,"description":"Practical guide to growing a business online in Nigeria."},
    {"id":"ex_bk012","name":"Nigerian Law School Bar Finals Past Questions","category":"Books","brand":"Princeton Legal","price":12000,"stars":4.7,"review_count":2345,"description":"Essential prep for Nigerian Bar Finals."},
    {"id":"ex_fd001","name":"Indomie Instant Noodles Chicken 40-pack","category":"Food","brand":"Indomie","price":9500,"stars":4.8,"review_count":87654,"description":"Nigeria's favourite instant noodle. Bulk pack for great savings."},
    {"id":"ex_fd002","name":"Golden Penny Semolina 5kg","category":"Food","brand":"Golden Penny","price":6500,"stars":4.6,"review_count":23456,"description":"Smooth semolina for swallow. Consistent quality across Nigeria."},
    {"id":"ex_fd003","name":"Milo Chocolate Malt Drink 900g Tin","category":"Food","brand":"Nestle","price":4800,"stars":4.7,"review_count":54321,"description":"Classic Nigerian breakfast staple. Every household knows Milo."},
    {"id":"ex_fd004","name":"Knorr Chicken Seasoning Cubes 50-pack","category":"Food","brand":"Knorr","price":2500,"stars":4.8,"review_count":98765,"description":"The go-to seasoning in every Nigerian kitchen. No cooking without Knorr."},
    {"id":"ex_fd005","name":"Dangote Sugar Refined White Sugar 5kg","category":"Food","brand":"Dangote","price":8500,"stars":4.5,"review_count":32100,"description":"Trusted Nigerian brand refined white sugar."},
    {"id":"ex_fd006","name":"Sunola Vegetable Oil 5 Litres","category":"Food","brand":"Sunola","price":9800,"stars":4.4,"review_count":21000,"description":"Light cooking oil ideal for frying and stewing Nigerian dishes."},
    {"id":"ex_fd007","name":"Titus Sardines in Tomato Sauce 12-pack","category":"Food","brand":"Titus","price":7200,"stars":4.5,"review_count":43210,"description":"Tasty sardines — affordable protein for rice, noodles and bread."},
    {"id":"ex_fd008","name":"Peak Full Cream Milk Powder 900g","category":"Food","brand":"Peak","price":5200,"stars":4.6,"review_count":34521,"description":"Nigerian household favourite for tea, pap and cooking."},
    {"id":"ex_fd009","name":"Honeywell Semovita 5kg","category":"Food","brand":"Honeywell","price":6800,"stars":4.5,"review_count":18765,"description":"Semovita for smooth, stretchy swallow."},
    {"id":"ex_fd010","name":"Cadbury Bournvita Chocolate Drink 900g","category":"Food","brand":"Cadbury","price":4500,"stars":4.6,"review_count":32100,"description":"Energy-boosting chocolate malt drink. Children and adults love this."},
    {"id":"ex_fd011","name":"Maggi Chicken Seasoning Cubes 50-pack","category":"Food","brand":"Maggi","price":2200,"stars":4.7,"review_count":76543,"description":"Classic Maggi seasoning. Many Nigerian cooks use both Maggi and Knorr!"},
    {"id":"ex_fd012","name":"Mama's Pride Palm Oil 2 Litres","category":"Food","brand":"Mama's Pride","price":4800,"stars":4.5,"review_count":18765,"description":"Pure red palm oil for soups, stews and traditional Nigerian cooking."},
    {"id":"ex_fd013","name":"Tropical Sun Ground Egusi 500g","category":"Food","brand":"Tropical Sun","price":3500,"stars":4.6,"review_count":12340,"description":"Pre-ground egusi for quick soup preparation. Saves time in the kitchen."},
    {"id":"ex_fd014","name":"Three Crowns Evaporated Milk 24-pack","category":"Food","brand":"Three Crowns","price":8500,"stars":4.5,"review_count":23456,"description":"Creamy evaporated milk for tea, pap and baking. Nigerian kitchen staple."},
    {"id":"ex_fd015","name":"Nasco Cornflakes 500g","category":"Food","brand":"Nasco","price":3200,"stars":4.4,"review_count":15432,"description":"Crispy cornflakes for a quick Nigerian breakfast. Kids love this one."},
]


# ── Build + save ──────────────────────────────────────────────────────────────
def build_tfidf_index(texts):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    print("\nBuilding TF-IDF + SVD fallback …")
    vec = TfidfVectorizer(max_features=8000, ngram_range=(1,2), sublinear_tf=True)
    X   = vec.fit_transform(texts)
    n   = min(384, X.shape[0]-1, X.shape[1]-1)
    print(f"  SVD n_components={n}  (items={X.shape[0]})")
    svd = TruncatedSVD(n_components=n, random_state=42)
    E   = svd.fit_transform(X).astype(np.float32)
    norms = np.linalg.norm(E, axis=1, keepdims=True); norms[norms==0]=1; E/=norms
    idx = faiss.IndexFlatIP(E.shape[1]); idx.add(E)
    print(f"  TF-IDF index: {idx.ntotal} vectors, dim={E.shape[1]}")
    return vec, svd, idx, E.shape[1]


def build_neural_index(texts):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("\n[SKIP] sentence-transformers not installed.")
        print("       pip install sentence-transformers  then re-run.")
        return None, None
    print("\nBuilding neural FAISS index (all-MiniLM-L6-v2) …")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    E = model.encode(texts, convert_to_numpy=True, show_progress_bar=True, batch_size=64).astype(np.float32)
    norms = np.linalg.norm(E, axis=1, keepdims=True); norms[norms==0]=1; E/=norms
    idx = faiss.IndexFlatIP(E.shape[1]); idx.add(E)
    print(f"  Neural index: {idx.ntotal} vectors, dim={E.shape[1]}")
    return idx, E.shape[1]


if __name__ == '__main__':
    amazon     = load_amazon_items()
    synthetic  = load_synthetic_csv()
    restaurants= build_restaurants()
    extras     = EXTRAS

    all_items  = amazon + synthetic + restaurants + extras

    print(f"\nData sources:")
    print(f"  Amazon (pkl)    : {len(amazon)}")
    print(f"  Synthetic CSV   : {len(synthetic)}")
    print(f"  Restaurants     : {len(restaurants)}")
    print(f"  Extras          : {len(extras)}")

    # Deduplicate
    seen, deduped = {}, []
    for item in all_items:
        key = (str(item.get('name','')).lower()[:60], str(item.get('category','')).lower())
        if key not in seen:
            seen[key] = True
            item['category'] = str(item.get('category','')).strip().title()
            deduped.append(item)

    print(f"\nTotal after dedup: {len(deduped)}")
    cats = Counter(i['category'] for i in deduped)
    for cat, n in sorted(cats.items()):
        print(f"  {cat:<20} {n}")

    # Build texts + metadata
    metadata, texts = {}, []
    for i, item in enumerate(deduped):
        metadata[i] = item
        texts.append(
            f"{item.get('name','')} {item.get('name','')} "
            f"{item.get('description','')} "
            f"{item.get('category','')} {item.get('category','')} "
            f"{item.get('brand','')}"
        )

    # Save metadata
    with open(PKL_PATH, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"\nSaved items_metadata.pkl ({len(metadata)} items)")

    # TF-IDF fallback
    tfidf_vec, tfidf_svd, tfidf_idx, tfidf_dim = build_tfidf_index(texts)
    faiss.write_index(tfidf_idx, str(OUT_DIR / 'items.index'))
    with open(OUT_DIR / 'tfidf_model.pkl', 'wb') as f:
        pickle.dump({'vectorizer': tfidf_vec, 'svd': tfidf_svd}, f)
    (OUT_DIR / 'index_dim.txt').write_text(str(tfidf_dim))
    print("Saved tfidf_model.pkl + items.index (TF-IDF fallback)")

    # Neural index
    neural_idx, neural_dim = build_neural_index(texts)
    if neural_idx is not None:
        faiss.write_index(neural_idx, str(OUT_DIR / 'items.index'))
        (OUT_DIR / 'index_dim.txt').write_text(str(neural_dim))
        print("Replaced items.index with NEURAL embeddings ✓")

    print(f"\n{'='*55}")
    print(f"  Build complete!  {len(metadata)} items indexed.")
    print(f"{'='*55}")
    for fp in sorted(OUT_DIR.iterdir()):
        if fp.is_file():
            print(f"  {fp.name:<35} {fp.stat().st_size//1024:>6} KB")