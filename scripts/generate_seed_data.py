#!/usr/bin/env python3
"""
Deterministic seed-data generator for the CoCo Workshop bounty hunt.

Plants 5 hidden insights ("eggs") in the e-commerce dataset:
  1. Category Collapse  — Home & Garden revenue drops ~65% from Jun 2025 onward
  2. Silent Star         — APAC grows from ~5% to ~20% order share with 1.4x AOV
  3. VIP Whale Curve     — Top 5% of customers drive ~45% of total revenue
  4. Pricing Bug         — ~8% of product_id=42 line items are overcharged by 15%
  5. Fraud Cluster       — 12 customers (IDs 900-911) with extreme order velocity & AOV

Outputs 4 Parquet files into data/seed/.
"""

import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "seed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REGIONS = ["US-EAST", "US-WEST", "EU-WEST", "APAC"]
CATEGORIES = ["Electronics", "Apparel", "Home & Garden", "Sports", "Books", "Beauty", "Toys"]
DATE_START = date(2024, 1, 1)
DATE_END = date(2025, 12, 31)

FRAUD_IDS = set(range(900, 912))

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Dorothy", "Andrew", "Kimberly", "Paul", "Emily", "Joshua", "Donna",
    "Kenneth", "Michelle", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Carolyn", "Patrick", "Janet", "Jack", "Catherine",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
    "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers",
    "Long", "Ross", "Foster", "Jimenez",
]

PRODUCT_NAMES = {
    "Electronics": ["Wireless Headphones", "USB-C Charger", "Tablet Pro", "4K Monitor", "Mechanical Keyboard",
                    "Ergonomic Mouse", "Bluetooth Speaker", "HD Webcam", "Mesh Router", "Smartwatch",
                    "Power Bank 20K", "USB Hub 7-Port", "Laptop Stand", "Mini Drone", "VR Headset",
                    "Pocket Projector", "Studio Microphone", "External SSD 1TB", "Graphics Card", "Streaming Stick"],
    "Apparel": ["Classic T-Shirt", "Zip Hoodie", "Rain Jacket", "Slim Jeans", "Running Sneakers",
                "Maxi Dress", "Cargo Shorts", "Polo Shirt", "Winter Beanie", "Cashmere Scarf",
                "Leather Belt", "Athletic Socks 6-Pack", "Trench Coat", "Puffer Vest", "Knit Cardigan"],
    "Home & Garden": ["Ceramic Plant Pot", "Smart LED Bulb", "Velvet Throw Pillow", "Soy Candle Set", "Canvas Wall Art",
                      "Expandable Hose 50ft", "Coir Doormat", "Blackout Curtains", "Garden Tool Kit", "Cedar Bird Feeder",
                      "Wooden Welcome Sign", "Raised Planter Box", "Solar Path Light", "Fleece Blanket", "Floating Shelf"],
    "Sports": ["Premium Yoga Mat", "Hex Dumbbell Set", "Speed Jump Rope", "Insulated Bottle 32oz", "Resistance Band Kit",
               "Carbon Tennis Racket", "Match Soccer Ball", "Padded Cycling Gloves", "High-Density Foam Roller", "Bike Helmet",
               "Hiking Backpack 40L", "GPS Fitness Tracker", "Calf Compression Sleeve", "Anti-Fog Swim Goggles", "Carbon Kayak Paddle"],
    "Books": ["Python Cookbook 3e", "Data Science Handbook", "SQL Deep Dive", "Cloud Architecture Patterns", "Leadership Playbook",
              "Midnight Library", "Rise of AI", "Marketing Masterclass", "Nebula Anthology", "Travel Atlas 2025",
              "Atomic Habits", "Freakonomics Revised", "Great Leaders Bio", "Art of Strategy", "One-Pan Cookbook"],
    "Beauty": ["Hydrating Face Cream", "Argan Shampoo", "Eau de Parfum 50ml", "Beeswax Lip Balm", "SPF 50 Sunscreen",
               "Keratin Hair Serum", "Gel Nail Kit", "Eye Shadow 12-Palette", "Matte Foundation", "Shea Body Lotion",
               "Gentle Cleanser", "Rose Toner", "Night Moisturizer", "Sheet Face Mask 10pk", "Brush Set 12pc"],
    "Toys": ["Mega Building Blocks", "1000pc Puzzle", "Off-Road RC Car", "Strategy Board Game", "Superhero Figure",
             "Giant Stuffed Bear", "Art Craft Kit", "Chemistry Science Kit", "Trading Card Game", "Soft Play Dough 8pk",
             "Dump Truck XL", "Victorian Dollhouse", "Electric Train Set", "Delta Kite", "Bubble Machine Pro"],
}


def make_products(n=200):
    rng = np.random.RandomState(SEED)
    rows = []

    cats_for_products = []
    per_cat = n // len(CATEGORIES)
    remainder = n - per_cat * len(CATEGORIES)
    for i, cat in enumerate(CATEGORIES):
        count = per_cat + (1 if i < remainder else 0)
        cats_for_products.extend([cat] * count)
    rng.shuffle(cats_for_products)

    for pid in range(1, n + 1):
        cat = cats_for_products[pid - 1]
        names = PRODUCT_NAMES[cat]
        name = names[(pid - 1) % len(names)]

        if pid <= 20:
            price = round(float(rng.uniform(300, 500)), 2)
        else:
            price = round(float(np.clip(rng.lognormal(5.07, 0.45), 15, 295)), 2)

        rows.append({"product_id": pid, "product_name": name, "category": cat, "unit_price": price})

    return pd.DataFrame(rows)


def make_customers(n=1000):
    rng = np.random.RandomState(SEED + 1)
    signup_start = date(2023, 1, 1)
    signup_span = (date(2025, 12, 31) - signup_start).days
    rows = []

    for cid in range(1, n + 1):
        fn = FIRST_NAMES[rng.randint(0, len(FIRST_NAMES))]
        ln = LAST_NAMES[rng.randint(0, len(LAST_NAMES))]
        email = f"{fn.lower()}.{ln.lower()}{cid}@example.com"

        if cid in FRAUD_IDS:
            region = "US-WEST"
            sd = date(2024, 3, 10) + timedelta(days=int(rng.randint(0, 10)))
        else:
            region = rng.choice(REGIONS, p=[0.35, 0.30, 0.25, 0.10])
            sd = signup_start + timedelta(days=int(rng.randint(0, signup_span)))

        rows.append({
            "customer_id": cid,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "region": region,
            "signup_date": sd.isoformat(),
        })

    return pd.DataFrame(rows)


def _apac_share(month_idx):
    return 0.02 + 0.28 * (month_idx / 23.0)


def make_orders_and_items(customers_df, products_df):
    rng = np.random.RandomState(SEED + 10)
    rng_item = np.random.RandomState(SEED + 11)
    rng_price = np.random.RandomState(SEED + 12)
    rng_hg = np.random.RandomState(SEED + 13)
    rng_assign = np.random.RandomState(SEED + 20)

    prod_map = {r["product_id"]: r for r in products_df.to_dict("records")}
    all_pids = np.array(sorted(prod_map.keys()))
    top20_pids = np.array(sorted(all_pids, key=lambda p: prod_map[p]["unit_price"], reverse=True)[:20])
    non_hg_pids = np.array([p for p in all_pids if prod_map[p]["category"] != "Home & Garden"])
    cust_region = dict(zip(customers_df["customer_id"], customers_df["region"]))

    normal_ids = sorted(set(range(1, 1001)) - FRAUD_IDS)
    n_normal = len(normal_ids)

    fraud_counts = {}
    for cid in sorted(FRAUD_IDS):
        fraud_counts[cid] = int(rng_assign.randint(80, 151))
    fraud_total = sum(fraud_counts.values())
    target_normal = 10000 - fraud_total

    rng_assign2 = np.random.RandomState(SEED + 21)
    vip_indices = rng_assign2.choice(n_normal, size=38, replace=False)
    vip_set = set(vip_indices)

    vip_total_target = int(target_normal * 0.42)
    regular_total_target = target_normal - vip_total_target

    vip_raw = rng_assign.poisson(lam=vip_total_target / 38, size=38)
    vip_raw = np.maximum(vip_raw, 10)
    vip_scale = vip_total_target / vip_raw.sum()
    vip_counts = np.maximum(10, np.round(vip_raw * vip_scale).astype(int))
    diff = int(vip_counts.sum()) - vip_total_target
    idx = 0
    while diff != 0:
        i = idx % 38
        if diff > 0 and vip_counts[i] > 10:
            vip_counts[i] -= 1
            diff -= 1
        elif diff < 0:
            vip_counts[i] += 1
            diff += 1
        idx += 1

    n_regular = n_normal - 38
    reg_raw = rng_assign.poisson(lam=regular_total_target / n_regular, size=n_regular)
    reg_raw = np.maximum(reg_raw, 1)
    reg_scale = regular_total_target / reg_raw.sum()
    reg_counts = np.maximum(1, np.round(reg_raw * reg_scale).astype(int))
    diff = int(reg_counts.sum()) - regular_total_target
    idx = 0
    while diff != 0:
        i = idx % n_regular
        if diff > 0 and reg_counts[i] > 1:
            reg_counts[i] -= 1
            diff -= 1
        elif diff < 0:
            reg_counts[i] += 1
            diff += 1
        idx += 1

    cust_orders = {}
    vi, ri = 0, 0
    for i, cid in enumerate(normal_ids):
        if i in vip_set:
            cust_orders[cid] = int(vip_counts[vi])
            vi += 1
        else:
            cust_orders[cid] = int(reg_counts[ri])
            ri += 1
    for cid, cnt in fraud_counts.items():
        cust_orders[cid] = cnt

    month_ranges = {}
    for mi in range(24):
        y, m = 2024 + mi // 12, mi % 12 + 1
        d0 = date(y, m, 1)
        d1 = date(y, 12, 31) if m == 12 else date(y, m + 1, 1) - timedelta(days=1)
        month_ranges[mi] = (d0, d1)

    month_probs_apac = np.array([_apac_share(mi) for mi in range(24)])
    month_probs_apac /= month_probs_apac.sum()
    month_probs_uniform = np.ones(24) / 24.0

    statuses = np.array(["COMPLETED"] * 18 + ["PENDING"] + ["CANCELLED"])

    order_rows = []
    item_rows = []
    oid = 1
    iid = 1

    for cid in sorted(cust_orders.keys()):
        n_ord = cust_orders[cid]
        is_fraud = cid in FRAUD_IDS
        region = cust_region.get(cid, "US-EAST")
        is_apac = (not is_fraud) and region == "APAC"

        if is_apac:
            months = rng.choice(24, size=n_ord, p=month_probs_apac)
        else:
            months = rng.choice(24, size=n_ord, p=month_probs_uniform)

        for oi in range(n_ord):
            mi = int(months[oi])
            d0, d1 = month_ranges[mi]
            od = d0 + timedelta(days=int(rng.randint(0, (d1 - d0).days + 1)))
            status = str(rng.choice(statuses))
            created_at = f"{od.isoformat()}T{rng.randint(0,24):02d}:{rng.randint(0,60):02d}:{rng.randint(0,60):02d}"

            if is_fraud:
                n_items = int(rng.choice([1, 2, 2, 3, 3]))
            else:
                n_items = int(rng.choice([2, 3, 3, 3, 4, 4, 4, 5, 5, 6]))

            items = []
            for _ in range(n_items):
                if is_fraud:
                    pid = int(rng.choice(top20_pids) if rng.random() < 0.80 else rng.choice(all_pids))
                else:
                    suppress_hg = od >= date(2025, 6, 1) and rng_hg.random() < 0.88
                    pool = non_hg_pids if suppress_hg else all_pids
                    pid = int(rng.choice(pool))

                prod = prod_map[pid]
                qty = int(rng_item.choice([1, 1, 1, 2, 2, 3]))
                lt = round(qty * prod["unit_price"], 2)

                if pid == 42 and not is_fraud and not is_apac and rng_price.random() < 0.08:
                    lt = round(qty * prod["unit_price"] * 1.15, 2)

                items.append({
                    "order_item_id": iid,
                    "product_id": pid,
                    "quantity": qty,
                    "line_total": lt,
                })
                iid += 1

            raw_total = sum(it["line_total"] for it in items)

            if is_fraud:
                target_aov = float(rng.uniform(650, 950))
                if raw_total > 0:
                    sf = target_aov / raw_total
                    for it in items:
                        it["line_total"] = round(it["line_total"] * sf, 2)
                    raw_total = sum(it["line_total"] for it in items)
            elif is_apac:
                aov_mult = float(rng.uniform(1.5, 1.8))
                for it in items:
                    it["line_total"] = round(it["line_total"] * aov_mult, 2)
                raw_total = sum(it["line_total"] for it in items)

            total = round(raw_total, 2)

            order_rows.append({
                "order_id": oid,
                "customer_id": cid,
                "order_date": od.isoformat(),
                "status": status,
                "total_amount": total,
                "created_at": created_at,
            })
            for it in items:
                it["order_id"] = oid
            item_rows.extend(items)
            oid += 1

    return pd.DataFrame(order_rows), pd.DataFrame(item_rows)


def self_check(customers_df, products_df, orders_df, items_df):
    print("\n" + "=" * 60)
    print("SELF-CHECK SUMMARY")
    print("=" * 60)

    total_rev = orders_df["total_amount"].sum()
    print(f"\nTotal revenue: ${total_rev:,.2f}")
    print(f"Orders: {len(orders_df):,}  Items: {len(items_df):,}  Customers: {len(customers_df)}  Products: {len(products_df)}")

    od = orders_df.copy()
    od["order_date"] = pd.to_datetime(od["order_date"])

    print("\n--- Egg 1: Category Collapse (Home & Garden) ---")
    ip = items_df.merge(products_df[["product_id", "category"]], on="product_id")
    io_ = ip.merge(orders_df[["order_id", "order_date"]], on="order_id")
    io_["order_date"] = pd.to_datetime(io_["order_date"])
    hg = io_[io_["category"] == "Home & Garden"]
    hg_before = hg[(hg["order_date"] >= "2025-01-01") & (hg["order_date"] < "2025-06-01")]["line_total"].sum()
    hg_after = hg[(hg["order_date"] >= "2025-06-01") & (hg["order_date"] <= "2025-12-31")]["line_total"].sum()
    hg_mb = hg_before / 5
    hg_ma = hg_after / 7
    ratio = hg_ma / hg_mb if hg_mb > 0 else 999
    print(f"  Jan-May 2025 monthly avg: ${hg_mb:,.2f}")
    print(f"  Jun-Dec 2025 monthly avg: ${hg_ma:,.2f}")
    print(f"  Ratio: {ratio:.3f} (target < 0.40)")
    assert ratio < 0.40, f"Egg 1 FAIL: ratio {ratio:.3f}"
    print("  PASS")

    print("\n--- Egg 2: Silent Star (APAC) ---")
    non_fraud_od = od[~od["customer_id"].isin(FRAUD_IDS)]
    rm = non_fraud_od.merge(customers_df[["customer_id", "region"]], on="customer_id")
    rr = rm.groupby("region")["total_amount"].agg(["sum", "mean", "count"])
    print(rr.to_string())
    assert rr["sum"].idxmin() == "APAC", f"Egg 2 FAIL: min rev is {rr['sum'].idxmin()}"
    assert rr["mean"].idxmax() == "APAC", f"Egg 2 FAIL: max AOV is {rr['mean'].idxmax()}"

    q4_25 = rm[rm["order_date"] >= "2025-10-01"]
    q1_24 = rm[rm["order_date"] < "2024-04-01"]
    apac_q4 = q4_25[q4_25["region"] == "APAC"].shape[0] / max(q4_25.shape[0], 1)
    apac_q1 = q1_24[q1_24["region"] == "APAC"].shape[0] / max(q1_24.shape[0], 1)
    print(f"  APAC order share Q1-2024: {apac_q1:.1%}  Q4-2025: {apac_q4:.1%}")
    assert apac_q4 > apac_q1 * 2.5, f"Egg 2 FAIL: growth not strong enough"
    print("  PASS")

    print("\n--- Egg 3: VIP Whale Curve ---")
    cr = od.groupby("customer_id")["total_amount"].sum().sort_values(ascending=False)
    top5n = max(1, int(len(cr) * 0.05))
    top5_share = cr.iloc[:top5n].sum() / total_rev
    print(f"  Top {top5n} customers revenue share: {top5_share:.2%} (target 40-50%)")
    assert 0.40 <= top5_share <= 0.50, f"Egg 3 FAIL: {top5_share:.2%}"
    print("  PASS")

    print("\n--- Egg 4: Pricing Bug (product_id=42) ---")
    p42 = items_df[items_df["product_id"] == 42].copy()
    p42_price = products_df.loc[products_df["product_id"] == 42, "unit_price"].values[0]
    p42["expected"] = (p42["quantity"] * p42_price).round(2)

    fraud_oids = set(orders_df[orders_df["customer_id"].isin(FRAUD_IDS)]["order_id"])
    apac_cids = set(customers_df[customers_df["region"] == "APAC"]["customer_id"])
    apac_oids = set(orders_df[orders_df["customer_id"].isin(apac_cids)]["order_id"])

    p42_clean = p42[~p42["order_id"].isin(fraud_oids | apac_oids)]
    p42_bad = p42_clean[p42_clean["line_total"] != p42_clean["expected"]]
    pct = len(p42_bad) / max(len(p42_clean), 1)
    print(f"  Product 42 clean items: {len(p42_clean)}, mismatches: {len(p42_bad)} ({pct:.1%})")
    assert 0.04 <= pct <= 0.14, f"Egg 4 FAIL: {pct:.1%}"

    other = items_df[items_df["product_id"] != 42].copy()
    other = other.merge(products_df[["product_id", "unit_price"]], on="product_id")
    other["expected"] = (other["quantity"] * other["unit_price"]).round(2)
    other_clean = other[~other["order_id"].isin(fraud_oids | apac_oids)]
    other_bad = other_clean[other_clean["line_total"] != other_clean["expected"]]
    print(f"  Other products (clean) mismatches: {len(other_bad)}")
    assert len(other_bad) == 0, f"Egg 4 FAIL: {len(other_bad)} unexpected"
    print("  PASS")

    print("\n--- Egg 5: Fraud Cluster (IDs 900-911) ---")
    fo = od[od["customer_id"].isin(FRAUD_IDS)]
    fraud_rev = fo["total_amount"].sum()
    fraud_share = fraud_rev / total_rev
    fraud_aov = fo["total_amount"].mean()
    fc = fo.groupby("customer_id").size()
    print(f"  Orders: {len(fo):,}, Revenue: ${fraud_rev:,.2f}, Share: {fraud_share:.2%}")
    print(f"  AOV: ${fraud_aov:,.2f}, Orders/cust: {fc.min()}-{fc.max()}")
    assert 0.08 <= fraud_share <= 0.10, f"Egg 5 FAIL: {fraud_share:.2%}"
    assert fc.min() >= 80, f"Egg 5 FAIL: min orders {fc.min()}"
    print("  PASS")

    nod = od[~od["customer_id"].isin(FRAUD_IDS)]
    nc = nod.groupby("customer_id").size()
    naov = nod["total_amount"]
    print(f"\n  Normal p99 orders: {nc.quantile(0.99):.0f}")
    print(f"  Normal p99 AOV: ${naov.quantile(0.99):,.2f}")

    print("\n" + "=" * 60)
    print("ALL 5 SELF-CHECKS PASSED")
    print("=" * 60)


def main():
    random.seed(SEED)
    np.random.seed(SEED)

    print("Generating seed data (seed=42) ...")

    products_df = make_products(200)
    print(f"  Products: {len(products_df)}")

    customers_df = make_customers(1000)
    print(f"  Customers: {len(customers_df)}")

    orders_df, items_df = make_orders_and_items(customers_df, products_df)
    print(f"  Orders: {len(orders_df)}")
    print(f"  Order items: {len(items_df)}")

    products_df.to_parquet(OUT_DIR / "raw_products.parquet", index=False, engine="pyarrow")
    customers_df.to_parquet(OUT_DIR / "raw_customers.parquet", index=False, engine="pyarrow")
    orders_df.to_parquet(OUT_DIR / "raw_orders.parquet", index=False, engine="pyarrow")
    items_df.to_parquet(OUT_DIR / "raw_order_items.parquet", index=False, engine="pyarrow")
    print(f"\nParquet files written to {OUT_DIR}/")

    self_check(customers_df, products_df, orders_df, items_df)


if __name__ == "__main__":
    main()
