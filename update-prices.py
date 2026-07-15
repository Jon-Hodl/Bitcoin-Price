#!/usr/bin/env python3
"""
BTC Price Database Updater
Fetches historical Bitcoin prices from mempool.space API
Updates prices.json with new daily data
"""

import json
import urllib.request
import ssl
from datetime import datetime, timedelta
import os

PRICES_FILE = 'prices.json'
MEMPOOL_API = 'https://mempool.space/api/v1/historical-price'

def fetch_json(url):
    """Fetch JSON from API with SSL context"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
        return json.loads(response.read().decode())

def load_prices():
    """Load existing price data"""
    if not os.path.exists(PRICES_FILE):
        return {}
    
    with open(PRICES_FILE, 'r') as f:
        return json.load(f)

def save_prices(prices):
    """Save price data to JSON"""
    with open(PRICES_FILE, 'w') as f:
        json.dump(prices, f, indent=2)
    
    print(f"Saved {len(prices)} price records to {PRICES_FILE}")

def fetch_historical_prices():
    """Fetch all historical prices from mempool.space"""
    print("Fetching historical prices from mempool.space...")
    
    try:
        data = fetch_json(MEMPOOL_API)
        
        prices = {}
        for item in data.get('prices', []):
            # Convert timestamp to date string
            timestamp = item.get('time', 0)
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            
            # Store OHLC data
            prices[date] = {
                'o': item.get('USD', {}).get('open', 0),
                'h': item.get('USD', {}).get('high', 0),
                'l': item.get('USD', {}).get('low', 0),
                'c': item.get('USD', {}).get('close', 0)
            }
        
        return prices
    
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None

def update_prices():
    """Main update function"""
    print(f"BTC Price Database Updater")
    print(f"Started at: {datetime.now().isoformat()}")
    print("-" * 50)
    
    # Load existing prices
    existing_prices = load_prices()
    print(f"Loaded {len(existing_prices)} existing price records")
    
    # Fetch new prices
    new_prices = fetch_historical_prices()
    
    if new_prices is None:
        print("ERROR: Failed to fetch prices")
        return 1
    
    # Merge with existing (new data takes precedence)
    merged_prices = {**existing_prices, **new_prices}
    
    # Sort by date
    sorted_prices = dict(sorted(merged_prices.items()))
    
    # Check for changes
    if len(sorted_prices) > len(existing_prices):
        new_count = len(sorted_prices) - len(existing_prices)
        print(f"Added {new_count} new price records")
    else:
        print("No new price records to add")
    
    # Save updated prices
    save_prices(sorted_prices)
    
    # Show date range
    dates = list(sorted_prices.keys())
    if dates:
        print(f"\nDate range: {dates[0]} to {dates[-1]}")
        print(f"Total records: {len(sorted_prices)}")
    
    print("-" * 50)
    print("Update complete!")
    return 0

if __name__ == '__main__':
    exit(update_prices())
