import base64
import gzip
import io
import os
import json
import re
import requests
import time
import pickle
import numpy as np
from nbtlib import File
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sklearn.linear_model import LinearRegression
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
import random
from requests.exceptions import RequestException
import pyperclip
import winsound
import pygame
pygame.mixer.init()

BLACKLISTED_ITEMS = {
    'TANK_MINER_BOOTS',
    'BALLOON_SNAKE',
    'TANK_MINER_LEGGINGS',
    'TANK_MINER_CHESTPLATE',
    'TANK_MINER_HELMET',
    'BOUNCY_LEGGINGS',
    'BOUNCY_BOOTS',
    'BOUNCY_CHESTPLATE',
    'BOUNCY_HELMET',
    'MOOGMA_BOOTS',
    'MOOGMA_LEGGINGS',
    'MOOGMA_CHESTPLATE',
    'MOOGMA_HELMET',
    'EARTH_SHARD',
    'CRYPT_BOW',
    'CRYPT_DREADLORD_SWORD',
    'FLAMING_BOOTS',
    'FLAMING_LEGGINGS',
    'FLAMING_CHESTPLATE',
    'FLAMING_HELMET',
    'GHOST_BOOTS',
    'GHOST_LEGGINGS',
    'GHOST_CHESTPLATE',
    'GHOST_HELMET',
    'GOBLIN_BOOTS',
    'GOBLIN_LEGGINGS',
    'GOBLIN_CHESTPLATE',
    'GOBLIN_HELMET',
    'GLACITE_BOOTS',
    'GLACITE_LEGGINGS',
    'GLACITE_CHESTPLATE',
    'GLACITE_HELMET',
    'SLUG_BOOTS',
    'SLUG_LEGGINGS',
    'SLUG_CHESTPLATE',
    'SLUG_HELMET',
    'HEAVY_LEGGINGS',
    'HEAVY_BOOTS',
    'HEAVY_CHESTPLATE',
    'HEAVY_HELMET',
    'SKELETON_MASTER_BOOTS',
    'SKELETON_MASTER_LEGGINGS',
    'SKELETON_MASTER_CHESTPLATE',
    'SKELETON_MASTER_HELMET',
    'SKELETON_SOLDIER_BOOTS',
    'SKELETON_SOLDIER_LEGGINGS',
    'SKELETON_SOLDIER_CHESTPLATE',
    'SKELETON_SOLDIER_HELMET',
    'SUPER_HEAVY_BOOTS',
    'SUPER_HEAVY_LEGGINGS',
    'SUPER_HEAVY_CHESTPLATE',
    'SUPER_HEAVY_HELMET',
    'SKELETOR_BOOTS',
    'SKELETOR_LEGGINGS',
    'SKELETOR_CHESTPLATE',
    'SKELETOR_HELMET',
    'SQUID_BOOTS',
    'SQUID_LEGGINGS',
    'SQUID_CHESTPLATE',
    'SQUID_HELMET',
    'SWORD_OF_BAD_HEALTH',
    'SNIPER_HELMET',
    'SNIPER_CHESTPLATE',
    'SNIPER_LEGGINGS',
    'SNIPER_BOOTS',
    'FEATHER_RING',
    'ZOMBIE_LORD_CHESTPLATE',
    'ZOMBIE_LORD_LEGGINGS',
    'ZOMBIE_LORD_BOOTS',
    'ZOMBIE_LORD_HELMET',
    'ZOMBIE_SOLDIER_CUTLASS',
    'ROTTEN_CHESTPLATE',
    'ROTTEN_LEGGINGS',
    'ROTTEN_BOOTS',
    'ROTTEN_HELMET',
    'ZOMBIE_COMMANDER_WHIP',
    'OBSIDIAN_CHESTPLATE',
    'OBSIDIAN_LEGGINGS',
    'OBSIDIAN_BOOTS',
    'OBSIDIAN_HELMET'
    'STARRED_ADAPTIVE_BOOTS',
    'STARRED_ADAPTIVE_LEGGINGS',
    'STARRED_ADAPTIVE_CHESTPLATE',
    'STARRED_ADAPTIVE_HELMET',
    'ZOMBIE_SOLDIER_HELMET',
    'ZOMBIE_SOLDIER_CHESTPLATE',
    'ZOMBIE_SOLDIER_LEGGINGS',
    'ZOMBIE_SOLDIER_BOOTS',
    'ZOMBIE_COMMANDER_BOOTS',
    'ZOMBIE_COMMANDER_LEGGINGS',
    'ZOMBIE_COMMANDER_CHESTPLATE',
    'ZOMBIE_COMMANDER_HELMET',
    'ZOMBIE_KNIGHT_CHESTPLATE',
    'ZOMBIE_KNIGHT_LEGGINGS',
    'ZOMBIE_KNIGHT_BOOTS',
    'ZOMBIE_KNIGHT_HELMET',
    'ADAPTIVE_BOOTS',
    'ADAPTIVE_LEGGINGS',
    'ADAPTIVE_CHESTPLATE',
    'ADAPTIVE_HELMET',
    'WATER_HYDRA_HEAD',
    'CONJURING_SWORD',
    'ZOMBIE_KNIGHT_SWORD',
    'BLADE_OF_THE_VOLCANO',
    'ICE_ROD',
    'FAIRY_BOOTS',
    'FAIRY_LEGGINGS',
    'FAIRY_CHESTPLATE',
    'FAIRY_HELMET',
    'SKELETON_GRUNT_CHESTPLATE',
    'SKELETON_GRUNT_LEGGINGS',
    'SKELETON_GRUNT_BOOTS',
    'SKELETON_GRUNT_HELMET',
    'SKELETON_LORD_BOOTS',
    'SKELETON_LORD_LEGGINGS',
    'SKELETON_LORD_CHESTPLATE',
    'SKELETON_LORD_HELMET',
    'SNIPER_HELMET',
    'SNIPER_CHESTPLATE',
    'SNIPER_LEGGINGS',
    'SNIPER_BOOTS',
    'FLAMING_SWORD',
    'SPIDER_TALISMAN',
}


API_KEY = 'own api key for the spreadsheet'
SERVICE_ACCOUNT_EMAIL = 'service email - make one'

# Create a service object using the API key
service = build('sheets', 'v4', developerKey=API_KEY)

SPREADSHEET_ID = '18SOUFkQUYSbh-cTp75QJT9Xoo8V4juSmUX0TrzGlXmg'
RANGE_NAME = 'API!A:C'  # Adjust if necessary to match your sheet structure

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'items.db')
api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key
url = "https://api.hypixel.net/skyblock/auctions"

# SQLAlchemy setup
engine = create_engine(f'sqlite:///{db_path}', poolclass=QueuePool, pool_size=10, max_overflow=20)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class RawAuction(Base):
    __tablename__ = 'raw_auctions'
    auction_uuid = Column(String, primary_key=True)
    item_id = Column(String)
    item_bytes = Column(String)
    price = Column(Float)
    timestamp = Column(Integer)
    enchantment_value = Column(Float, default=0)

class Item(Base):
    __tablename__ = 'items'
    id = Column(String, primary_key=True)
    specific_id = Column(String, primary_key=True)
    name = Column(String)
    color_code = Column(String)
    color_int = Column(Integer)
    lowest_price = Column(Float)
    adjusted_price = Column(Float)
    mean_price = Column(Float)
    sell_price = Column(Float)
    auction_uuid = Column(String)
    enchantments = Column(JSON)
    attributes = Column(JSON)
    rarity_upgrades = Column(Integer)
    hot_potato_count = Column(Integer)
    modifier = Column(String)
    upgrade_level = Column(Integer)
    star_count = Column(Integer)
    similar_items_found = Column(Integer, default=1)
    item_found = Column(Boolean, default=True)
    is_shiny = Column(Boolean, default=False)
    art_of_war_count = Column(Integer, default=0)
    ability_scroll = Column(JSON)
    gems = Column(JSON)
    pet_type = Column(String)
    pet_tier = Column(String)
    pet_candy_used = Column(Integer)

class ItemPrices(Base):
    __tablename__ = 'item_prices'
    id = Column(String, primary_key=True)
    lowest_price = Column(Float)
    second_lowest_price = Column(Float)
    last_updated = Column(Integer)

class Flip(Base):
    __tablename__ = 'flips'
    auction_uuid = Column(String, primary_key=True)
    id = Column(String)
    name = Column(String)
    color_code = Column(String)
    original_price = Column(Float)
    adjusted_price = Column(Float)
    sell_price = Column(Float)
    profit = Column(Float)
    enchantments = Column(JSON)
    attributes = Column(JSON)
    rarity_upgrades = Column(Integer)
    hot_potato_count = Column(Integer)
    modifier = Column(String)
    upgrade_level = Column(Integer)
    star_count = Column(Integer)
    display_count = Column(Integer, default=0)
    displayed = Column(Boolean, default=False)
    profit_percentage = Column(Float)
    value_breakdown = Column(String) 
    last_displayed = Column(Integer, default=0)
    end_timestamp = Column(Integer)

class EnchantmentPrice(Base):
    __tablename__ = 'enchantment_prices'
    enchantment = Column(String, primary_key=True)
    level = Column(Integer, primary_key=True)
    price = Column(Float)

def fetch_enchantment_prices():
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    
    enchantment_prices = {}
    for row in values[1:]:  # Skip header row
        if len(row) >= 3:
            item_name = row[0]
            item_id = row[1]
            try:
                price = float(row[2])
                enchantment_prices[item_id] = price
            except ValueError:
                print(f"Skipping row with invalid price: {row}")
                continue
    
    return enchantment_prices

def init_enchantment_prices():
    session = Session()
    enchantment_prices = fetch_enchantment_prices()
    
    for item_id, price in enchantment_prices.items():
        if '_' in item_id:
            enchantment, level = item_id.rsplit('_', 1)
            level = int(level) if level.isdigit() else 0
        else:
            enchantment = item_id
            level = 0
        
        enchant_price = EnchantmentPrice(enchantment=enchantment, level=level, price=price)
        session.merge(enchant_price)

    session.commit()
    session.close()
    print(f"Inserted {len(enchantment_prices)} item prices into the database.")

def clean_item_name(name):
    color_match = re.match(r'^(§[0-9a-fk-or])', name)
    color_code = color_match.group(1) if color_match else ''
    cleaned_name = re.sub(r'§[0-9a-fk-or]', '', name).strip()
    return color_code, cleaned_name

def parse_nbt(item_bytes):
    decoded = base64.b64decode(item_bytes)
    decompressed = gzip.decompress(decoded)
    nbt_file = File.parse(io.BytesIO(decompressed))

    i = nbt_file['i'][0]
    tag = i.get('tag', {})
    display = tag.get('display', {})
    name = display.get('Name', 'Unknown')
   
    color_int = display.get('color', 0)
   
    color_code, cleaned_name = clean_item_name(name)
   
    extra_attributes = tag.get('ExtraAttributes', {})
   
    enchantments = extra_attributes.get('enchantments', {})
    attributes = extra_attributes.get('attributes', {})
    rarity_upgrades = extra_attributes.get('rarity_upgrades', 0)
    hot_potato_count = extra_attributes.get('hot_potato_count', 0)
    modifier = extra_attributes.get('modifier', '')
    upgrade_level = extra_attributes.get('upgrade_level', 0)
    item_id = extra_attributes.get('id', '')
   
    star_count = cleaned_name.count('✪')
    
    is_shiny = extra_attributes.get('is_shiny', False)
    art_of_war_count = extra_attributes.get('art_of_war_count', 0)
    ability_scroll = extra_attributes.get('ability_scroll', [])
    gems = extra_attributes.get('gems', {})

    return {
        'name': cleaned_name,
        'color_code': color_code,
        'color_int': color_int,
        'enchantments': enchantments,
        'attributes': attributes,
        'rarity_upgrades': rarity_upgrades,
        'hot_potato_count': hot_potato_count,
        'modifier': modifier,
        'upgrade_level': upgrade_level,
        'id': item_id,
        'star_count': star_count,
        'is_shiny': is_shiny,
        'art_of_war_count': art_of_war_count,
        'ability_scroll': ability_scroll,
        'gems': gems
    }

def init_db():
    Base.metadata.create_all(engine)

def calculate_base_price(session, item_id):
    raw_auctions = session.query(RawAuction).filter_by(item_id=item_id).all()
    if not raw_auctions:
        return None
   
    total_price = sum(auction.price - auction.enchantment_value for auction in raw_auctions)
    return total_price / len(raw_auctions)

def update_item_prices(session, item_id, buy_price):
    item_prices = session.query(ItemPrices).filter_by(id=item_id).first()
    if not item_prices:
        item_prices = ItemPrices(id=item_id, lowest_price=buy_price, second_lowest_price=buy_price)
    elif buy_price < item_prices.lowest_price:
        item_prices.second_lowest_price = item_prices.lowest_price
        item_prices.lowest_price = buy_price
    elif buy_price < item_prices.second_lowest_price:
        item_prices.second_lowest_price = buy_price
    item_prices.last_updated = int(time.time())
    session.merge(item_prices)

def process_auctions_batch(auctions):
    session = Session()
    processed_count = 0
    blacklisted_count = 0
    MIN_PROFIT_THRESHOLD = 300000  # Set this to your desired minimum profit

    try:
        for auction in auctions:
            item_bytes = auction['item_bytes']
            buy_price = auction['starting_bid']
            auction_uuid = auction['uuid']
            item_data = parse_nbt(item_bytes)
            item_id = auction.get('item_id', item_data['id'])
            specific_id = f"{item_id}_{item_data['name']}"

            if item_id.upper() in (item.upper() for item in BLACKLISTED_ITEMS):
                blacklisted_count += 1
                continue

            raw_auction = RawAuction(
                auction_uuid=auction_uuid,
                item_id=item_id,
                item_bytes=item_bytes,
                price=buy_price,
                timestamp=int(time.time())
            )
            session.merge(raw_auction)

            additives_value, value_breakdown = calculate_additional_value(session, item_data)
            adjusted_price = buy_price - additives_value

            item_prices = session.query(ItemPrices).filter_by(id=item_id).first()
           
            if item_prices:
                base_price = item_prices.lowest_price
                sell_price = base_price + additives_value
                potential_profit = sell_price - buy_price
                is_flip = adjusted_price <= base_price * 0.6 and potential_profit >= MIN_PROFIT_THRESHOLD
                is_new_lowest = adjusted_price < base_price * 1.3  # 10% threshold
            else:
                base_price = adjusted_price
                sell_price = buy_price
                potential_profit = 0
                is_flip = False  # Don't consider it a flip if it's a new item with no profit
                is_new_lowest = True

            if is_flip:
                profit_percentage = (potential_profit / buy_price) * 100

                flip = Flip(
                    id=item_id,
                    name=item_data['name'],
                    color_code=item_data['color_code'],
                    original_price=buy_price,
                    adjusted_price=adjusted_price,
                    sell_price=sell_price,
                    profit=potential_profit,
                    profit_percentage=profit_percentage,
                    auction_uuid=auction_uuid,
                    enchantments=item_data['enchantments'],
                    attributes=item_data['attributes'],
                    rarity_upgrades=item_data['rarity_upgrades'],
                    hot_potato_count=item_data['hot_potato_count'],
                    modifier=item_data['modifier'],
                    upgrade_level=item_data['upgrade_level'],
                    star_count=item_data['star_count'],
                    value_breakdown=json.dumps(value_breakdown)
                )
                session.merge(flip)

            if is_new_lowest:
                update_item_prices(session, item_id, adjusted_price)
               
                item = session.query(Item).filter_by(id=item_id).first()
                if not item:
                    item = Item(
                        id=item_id,
                        specific_id=specific_id,
                        name=item_data['name'],
                        color_code=item_data['color_code'],
                        color_int=item_data['color_int'],
                        lowest_price=adjusted_price,
                        adjusted_price=adjusted_price,
                        mean_price=adjusted_price,
                        auction_uuid=auction_uuid,
                        enchantments=item_data['enchantments'],
                        attributes=item_data['attributes'],
                        rarity_upgrades=item_data['rarity_upgrades'],
                        hot_potato_count=item_data['hot_potato_count'],
                        modifier=item_data['modifier'],
                        upgrade_level=item_data['upgrade_level'],
                        star_count=item_data['star_count'],
                        is_shiny=item_data['is_shiny'],
                        art_of_war_count=item_data['art_of_war_count'],
                        ability_scroll=item_data['ability_scroll'],
                        gems=item_data['gems'],
                        similar_items_found=1
                    )
                else:
                    item.lowest_price = adjusted_price
               
                session.merge(item)

            processed_count += 1

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error processing auctions: {str(e)}")
    finally:
        session.close()

def save_recent_auctions(auctions, filename):
    with open(filename, 'wb') as f:
        pickle.dump(auctions, f)

def fetch_auction_data(max_items=100000, max_retries=5, initial_delay=1):
    for attempt in range(max_retries):
        try:
            total_pages = None
            page = 0
            all_auctions = []
            items_fetched = 0

            while True:
                params = {"page": page}
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = json.loads(response.text)
                auctions = data.get("auctions", [])

                unclaimed_bin_auctions = [auction for auction in auctions if not auction.get("claimed", True) and auction.get("bin", False)]
                all_auctions.extend(unclaimed_bin_auctions)
                items_fetched += len(unclaimed_bin_auctions)

                if total_pages is None:
                    total_pages = data.get("totalPages", 0)

                if items_fetched >= max_items or page >= total_pages - 1:
                    break

                page += 1

            fetched_auctions = all_auctions[:max_items]
            save_recent_auctions(fetched_auctions, "recent_auctions.pkl")

            return {"auctions": fetched_auctions}

        except RequestException as e:
            delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Error fetching data (attempt {attempt + 1}/{max_retries}): {e}")
            print(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

    print("Failed to fetch auction data after multiple attempts.")
    return None


def get_item_details(auction_uuid):
    session = Session()
    try:
        raw_auction = session.query(RawAuction).filter_by(auction_uuid=auction_uuid).first()
        item = session.query(Item).filter_by(auction_uuid=auction_uuid).first()
        
        if raw_auction and item:
            item_data = parse_nbt(raw_auction.item_bytes)
            return {
                'item_bytes': raw_auction.item_bytes,
                'price': raw_auction.price,
                'id': item.id,
                'name': item.name,
                'color_code': item.color_code,
                'lowest_price': item.lowest_price,
                'auction_uuid': item.auction_uuid,
                'enchantments': item.enchantments,
                'attributes': item.attributes,
                'rarity_upgrades': item.rarity_upgrades,
                'hot_potato_count': item.hot_potato_count,
                'modifier': item.modifier,
                'upgrade_level': item.upgrade_level,
                'star_count': item.star_count,
                'is_shiny': item.is_shiny,
                'art_of_war_count': item.art_of_war_count,
                'ability_scroll': item.ability_scroll,
                'gems': item.gems,
                'pet_type': item.pet_type,
                'pet_tier': item.pet_tier,
                'pet_candy_used': item.pet_candy_used,
                **item_data
            }
    finally:
        session.close()
    return None


def update_enchantment_price(enchantment, level, price):
    session = Session()
    try:
        enchant_price = EnchantmentPrice(enchantment=enchantment, level=level, price=price)
        session.merge(enchant_price)
        session.commit()
    finally:
        session.close()

def calculate_enchantment_value(session, enchantments):
    total_value = 0
    for enchant, level in enchantments.items():
        enchant_price = session.query(EnchantmentPrice).filter_by(enchantment=f"ENCHANTMENT_{enchant.upper()}", level=level).first()
        if enchant_price:
            total_value += enchant_price.price
    return total_value

def calculate_mean_price(session, item_id):
    raw_auctions = session.query(RawAuction).filter_by(item_id=item_id).all()
    if not raw_auctions:
        return None
    
    total_adjusted_price = sum(auction.price - auction.enchantment_value for auction in raw_auctions)
    return total_adjusted_price / len(raw_auctions)

def calculate_additional_value(session, item_data):
    additional_value = 0
    value_breakdown = {}

    # Calculate rarity upgrade value
    if item_data['rarity_upgrades'] > 0:
        recombobulator_price = session.query(EnchantmentPrice).filter_by(enchantment='RECOMBOBULATOR', level=3000).first()
        if recombobulator_price:
            rarity_value = recombobulator_price.price * item_data['rarity_upgrades']
            additional_value += rarity_value
            value_breakdown['rarity_upgrades'] = rarity_value

    # Add hot potato book value
    hot_potato_price = session.query(EnchantmentPrice).filter_by(enchantment='HOT_POTATO_BOOK', level=1).first()
    if hot_potato_price:
        potato_value = hot_potato_price.price * item_data['hot_potato_count']
        additional_value += potato_value
        value_breakdown['hot_potato'] = potato_value

    # Add master star value
    upgrade_level = item_data['upgrade_level']
    if upgrade_level > 5:
        star_value = 0
        for i in range(6, upgrade_level + 1):
            master_star_name = f"{['FIRST', 'SECOND', 'THIRD', 'FOURTH', 'FIFTH'][i-6]}_MASTER_STAR"
            master_star_price = session.query(EnchantmentPrice).filter_by(enchantment=master_star_name, level=1).first()
            if master_star_price:
                star_value += master_star_price.price
        additional_value += star_value
        value_breakdown['master_stars'] = star_value

    # Calculate enchantment value
    enchant_value = calculate_enchantment_value(session, item_data['enchantments'])
    additional_value += enchant_value
    value_breakdown['enchantments'] = enchant_value

    return additional_value, value_breakdown
def print_new_flips():
    session = Session()
    try:
        flips = session.query(Flip).filter(Flip.displayed == 0).all()

        if flips:
            print("New flips found:")
            for flip in flips:
                print(f"ID: {flip.id}")
                print(f"Name: {flip.name}")
                print(f"Buy Price: {flip.original_price:,.0f}")
                print(f"Sell Price: {flip.sell_price:,.0f}")
                print(f"Profit: {flip.profit:,.0f}")
                
                view_auction_command = f"/viewauction {flip.auction_uuid}"
                print(f"View Auction: {view_auction_command}")
                pyperclip.copy(view_auction_command)
                print("(Command copied to clipboard)")
                
                print(f"Times Displayed: {flip.display_count + 1}")
                print()

                pygame.mixer.music.load("G:\\ytmp3\\(short) Yippee sound effect!!.mp3")
                pygame.mixer.music.play()

                flip.displayed = 1
                flip.display_count += 1

            session.commit()
        else:
            print("No new flips found.")

    finally:
        session.close()

def main_loop():
    init_db()
    init_enchantment_prices()
    pass_count = 0
    total_processed = 0
    is_first_pass = True

    while True:
        max_items = 50000 if is_first_pass else 20
        auction_data = fetch_auction_data(max_items=max_items)

        if auction_data:
            auctions = auction_data['auctions']
            total_auctions = len(auctions)

            for i in range(0, total_auctions, 10000):
                batch = auctions[i:i+10000]
                process_auctions_batch(batch)
                total_processed += len(batch)
            
            if not is_first_pass:
                print_new_flips()

        else:
            print("Failed to fetch auction data.")

        is_first_pass = False
        pass_count += 1
        time.sleep(5)  # Wait for 30 secs

if __name__ == "__main__":
    main_loop()
