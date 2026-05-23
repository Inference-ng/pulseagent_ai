"""
data/loader.py — Loads Amazon Reviews 2023 dataset using the new HuggingFace datasets API.
Falls back to a rich multi-domain synthetic catalog (Amazon, Goodreads, Yelp-style)
to demonstrate that PulseAgent AI is a domain-agnostic intelligent agent API.
"""
import os
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../processed"))
OUTPUT_PATH = os.path.join(BASE_DIR, "amazon_fashion.csv")

def load_from_huggingface():
    """Attempt to load Amazon Reviews 2023 (Clothing subset) from HuggingFace."""
    from datasets import load_dataset

    print("Attempting to load Amazon Reviews 2023 from HuggingFace...")
    # Use the new parquet-based loading (no trust_remote_code needed)
    ds = load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023",
        "raw_review_Clothing_Shoes_and_Jewelry",
        split="full",
        streaming=True,
    )

    items = []
    for i, row in enumerate(ds):
        if i >= 500:  # Small subset for speed
            break
        items.append({
            "id": str(row.get("parent_asin", i)),
            "name": row.get("title", f"Fashion Item {i}"),
            "description": row.get("text", ""),
            "category": "Fashion",
            "price": float(row.get("price") or 15000),
            "brand": row.get("store", "Generic"),
        })

    return pd.DataFrame(items)


def build_synthetic_data():
    """Create rich synthetic Nigerian e-commerce product catalog as fallback."""
    print("Building synthetic Nigerian e-commerce product catalog...")

    products = [
        # Fashion
        {"id": "f001", "name": "Nike Air Max 270", "description": "Premium sneakers with Air Max cushioning. Perfect for Lagos streets.", "category": "Fashion", "price": 45000, "brand": "Nike"},
        {"id": "f002", "name": "Adidas Ultraboost 22", "description": "Running shoes with responsive Boost midsole. Fast delivery on Jumia.", "category": "Fashion", "price": 52000, "brand": "Adidas"},
        {"id": "f003", "name": "Ankara Print Dress", "description": "Beautiful Ankara fabric dress. Made in Nigeria. Perfect for owambe.", "category": "Fashion", "price": 8500, "brand": "Adire Collections"},
        {"id": "f004", "name": "Puma Suede Classic", "description": "Iconic Puma suede sneakers. Very comfortable, e no go disappoint.", "category": "Fashion", "price": 28000, "brand": "Puma"},
        {"id": "f005", "name": "Agbada Senator Set", "description": "Premium Agbada senator set for men. Perfect for occasions in Abuja.", "category": "Fashion", "price": 35000, "brand": "Royal Threads"},
        {"id": "f006", "name": "Reebok Classic Leather", "description": "Timeless Reebok classics. Affordable and durable for daily wear.", "category": "Fashion", "price": 22000, "brand": "Reebok"},
        {"id": "f007", "name": "New Balance 574", "description": "Comfortable everyday sneakers. Available on Konga with free delivery.", "category": "Fashion", "price": 31000, "brand": "New Balance"},
        {"id": "f008", "name": "Lace Gown with Beads", "description": "Elegant lace gown with bead work. Perfect for Nigerian weddings.", "category": "Fashion", "price": 18000, "brand": "Aso-Oke Royale"},
        {"id": "f009", "name": "Fila Disruptor II", "description": "Bold chunky sneakers. Very trendy on Nigerian campuses right now.", "category": "Fashion", "price": 19500, "brand": "Fila"},
        {"id": "f010", "name": "Converse Chuck Taylor", "description": "Classic Converse canvas shoes. No be lie, this one na evergreen.", "category": "Fashion", "price": 16000, "brand": "Converse"},
        # Electronics
        {"id": "e001", "name": "Infinix Hot 40i", "description": "Budget smartphone with good camera. Best buy under 100k on Slot.", "category": "Electronics", "price": 85000, "brand": "Infinix"},
        {"id": "e002", "name": "Tecno Spark 20", "description": "Tecno smartphone with large battery. Perfect for areas with NEPA issues.", "category": "Electronics", "price": 75000, "brand": "Tecno"},
        {"id": "e003", "name": "Samsung Galaxy A15", "description": "Samsung mid-range phone with great display. Order on Jumia today.", "category": "Electronics", "price": 145000, "brand": "Samsung"},
        {"id": "e004", "name": "JBL Flip 6 Speaker", "description": "Waterproof Bluetooth speaker. Perfect for owambe and parties.", "category": "Electronics", "price": 62000, "brand": "JBL"},
        {"id": "e005", "name": "Xiaomi Redmi Note 13", "description": "Xiaomi budget king with 108MP camera. Competitive price.", "category": "Electronics", "price": 195000, "brand": "Xiaomi"},
        # Books
        {"id": "b001", "name": "Things Fall Apart - Chinua Achebe", "description": "Classic Nigerian literature. Required reading for every educated Nigerian.", "category": "Books", "price": 3500, "brand": "Heinemann"},
        {"id": "b002", "name": "Purple Hibiscus - Chimamanda Adichie", "description": "Powerful Nigerian novel by Chimamanda. E go move you to tears.", "category": "Books", "price": 4200, "brand": "Farafina"},
        {"id": "b003", "name": "Rich Dad Poor Dad", "description": "Personal finance bestseller. Every Nigerian hustler needs this book.", "category": "Books", "price": 5500, "brand": "Plata Publishing"},
        {"id": "b004", "name": "Atomic Habits - James Clear", "description": "Life-changing habits book. Order on Roving Heights bookshop.", "category": "Books", "price": 6800, "brand": "Avery"},
        {"id": "b005", "name": "The Alchemist - Paulo Coelho", "description": "Inspirational classic. Na motivation in book form.", "category": "Books", "price": 4000, "brand": "HarperOne"},
        # Food
        {"id": "fd001", "name": "Indomie Instant Noodles (40 Pack)", "description": "The classic Nigerian student staple. Indomie e go always save the day.", "category": "Food", "price": 7500, "brand": "Indomie"},
        {"id": "fd002", "name": "Peak Milk Evaporated (48 Cans)", "description": "Peak milk for your morning tea and garri. Quality guaranteed.", "category": "Food", "price": 18000, "brand": "Peak"},
        {"id": "fd003", "name": "Mama's Kitchen Jollof Rice Spice Mix", "description": "Authentic Yoruba jollof spice blend. Your jollof go be the talk of town.", "category": "Food", "price": 2500, "brand": "Mama's Kitchen"},
        # Beauty
        {"id": "bty001", "name": "Nivea Body Lotion 400ml", "description": "Popular body lotion in Nigeria. Light and moisturising for our hot weather.", "category": "Beauty", "price": 3800, "brand": "Nivea"},
        {"id": "bty002", "name": "Cantu Shea Butter Leave-In Conditioner", "description": "For natural hair care. Lagos ladies swear by this product.", "category": "Beauty", "price": 6500, "brand": "Cantu"},
        {"id": "bty003", "name": "Black Opal Even True Fade Gel", "description": "Skin brightening gel. Best seller for Nigerian skin tones.", "category": "Beauty", "price": 4200, "brand": "Black Opal"},
        # Restaurants (Yelp-style — works for hospitality platforms)
        {"id": "rst001", "name": "The Place Restaurant, Lekki", "description": "Best local Nigerian food and jollof rice in Lagos. Fast service, great for lunch breaks.", "category": "Restaurants", "price": 5000, "brand": "The Place"},
        {"id": "rst002", "name": "Mega Chicken, Ikeja", "description": "Huge portions of fried rice, chicken, and pastries. Perfect for family outings in Lagos.", "category": "Restaurants", "price": 4500, "brand": "Mega Chicken"},
        {"id": "rst003", "name": "Shiro Restaurant & Bar", "description": "Premium Pan-Asian dining. Great for upscale date nights and luxury experiences in Victoria Island.", "category": "Restaurants", "price": 45000, "brand": "Shiro"},
        {"id": "rst004", "name": "Ocean Basket, Victoria Island", "description": "Delicious seafood platters and sushi. Family friendly atmosphere by the Lagos waterfront.", "category": "Restaurants", "price": 18000, "brand": "Ocean Basket"},
        {"id": "rst005", "name": "Yellow Chilli by Sisi Yemi", "description": "Authentic Nigerian cuisine from celebrity chef. Great for special occasions and events.", "category": "Restaurants", "price": 12000, "brand": "Yellow Chilli"},
        {"id": "rst006", "name": "Chicken Republic", "description": "Popular fast food chain across Nigeria. Quick, affordable, and reliable for a quick meal.", "category": "Restaurants", "price": 3500, "brand": "Chicken Republic"},
        # Books (Goodreads-style — works for publishers, bookstores, edtech platforms)
        {"id": "b001", "name": "Things Fall Apart - Chinua Achebe", "description": "Classic Nigerian literature about Igbo culture and the impact of colonialism. Required reading for every educated Nigerian.", "category": "Books", "price": 3500, "brand": "Heinemann"},
        {"id": "b002", "name": "Purple Hibiscus - Chimamanda Adichie", "description": "Powerful Nigerian coming-of-age novel. E go move you to tears. Winner of multiple literary awards.", "category": "Books", "price": 4200, "brand": "Farafina"},
        {"id": "b003", "name": "Rich Dad Poor Dad", "description": "Personal finance bestseller about building wealth and financial literacy. Every Nigerian hustler needs this book.", "category": "Books", "price": 5500, "brand": "Plata Publishing"},
        {"id": "b004", "name": "Atomic Habits - James Clear", "description": "Practical guide to building good habits and breaking bad ones. Order on Roving Heights bookshop.", "category": "Books", "price": 6800, "brand": "Avery"},
        {"id": "b005", "name": "The Alchemist - Paulo Coelho", "description": "Inspirational classic about following your dreams. Na motivation in book form, e never get old.", "category": "Books", "price": 4000, "brand": "HarperOne"},
        {"id": "b006", "name": "Half of a Yellow Sun - Chimamanda Adichie", "description": "Epic novel about the Nigerian-Biafran War. A deep and emotional must-read for history lovers.", "category": "Books", "price": 5800, "brand": "Farafina"},
        {"id": "b007", "name": "The Psychology of Money - Morgan Housel", "description": "Modern finance book about how people think about money and wealth. Very practical for young professionals.", "category": "Books", "price": 7200, "brand": "Harriman House"},
        {"id": "b008", "name": "An African in Greenland - Tete-Michel Kpomassie", "description": "Adventure memoir of a Togolese man who traveled to Greenland. Fascinating African travel story.", "category": "Books", "price": 3800, "brand": "NYRB"},
    ]

    return pd.DataFrame(products)
def main():
    os.makedirs(BASE_DIR, exist_ok=True)

    df = None
    try:
        df = load_from_huggingface()
        if df is not None and not df.empty:
            print(f"Loaded {len(df)} items from HuggingFace.")
        else:
            raise ValueError("Empty dataset returned")
    except Exception as e:
        print(f"HuggingFace load failed: {e}")
        df = build_synthetic_data()
        print(f"Synthetic catalog created with {len(df)} items.")

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")
    print(df.head())


if __name__ == "__main__":
    main()
