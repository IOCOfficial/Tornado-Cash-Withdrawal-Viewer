#!/usr/bin/env python3
"""
Tornado Cash Withdrawal Viewer
A tool by intelligenceonchain.com

Analyzes withdrawals from Tornado Cash ETH pools using Etherscan API V2.
Shows recipient addresses with withdrawal counts, totals, and date ranges.
"""

import requests
import argparse
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, Tuple, List
from pathlib import Path
import sys


# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG_DIR = Path.home() / ".tornado_viewer"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Tornado Cash ETH Pool Contracts (Ethereum Mainnet)
TORNADO_CASH_POOLS = {
    "1_eth": {
        "address": "0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c3c2936",
        "denomination": 1,
        "name": "1 ETH"
    },
    "10_eth": {
        "address": "0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF",
        "denomination": 10,
        "name": "10 ETH"
    },
    "100_eth": {
        "address": "0xA160cdAB225685dA1d56aa342Ad8841c3b53f291",
        "denomination": 100,
        "name": "100 ETH"
    }
}

BANNER = """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║            ████████╗ ██████╗ ██████╗ ███╗   ██╗ █████╗ ██████╗  ██████╗    ║
║            ╚══██╔══╝██╔═══██╗██╔══██╗████╗  ██║██╔══██╗██╔══██╗██╔═══██╗   ║
║               ██║   ██║   ██║██████╔╝██╔██╗ ██║███████║██║  ██║██║   ██║   ║
║               ██║   ██║   ██║██╔══██╗██║╚██╗██║██╔══██║██║  ██║██║   ██║   ║
║               ██║   ╚██████╔╝██║  ██║██║ ╚████║██║  ██║██████╔╝╚██████╔╝   ║
║               ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ║
║                                                                            ║
║                     ██████╗ █████╗ ███████╗██╗  ██╗                        ║
║                    ██╔════╝██╔══██╗██╔════╝██║  ██║                        ║
║                    ██║     ███████║███████╗███████║                        ║
║                    ██║     ██╔══██║╚════██║██╔══██║                        ║
║                    ╚██████╗██║  ██║███████║██║  ██║                        ║
║                     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                        ║
║                                                                            ║
║                      W I T H D R A W A L   V I E W E R                     ║
║                                                                            ║
║────────────────────────────────────────────────────────────────────────────║
║                       intelligenceonchain.com                              ║
╚════════════════════════════════════════════════════════════════════════════╝
"""


# ============================================================================
# API KEY MANAGEMENT
# ============================================================================

def get_config() -> dict:
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(config: dict) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    os.chmod(CONFIG_FILE, 0o600)


def validate_api_key(api_key: str) -> Tuple[Optional[bool], str]:
    """Validate an Etherscan API key."""
    try:
        response = requests.get(
            "https://api.etherscan.io/v2/api",
            params={
                "chainid": 1,
                "module": "stats",
                "action": "ethsupply",
                "apikey": api_key
            },
            timeout=15
        )
        data = response.json()
        
        if data.get("message") == "NOTOK":
            result_msg = data.get("result", "Unknown error")
            if "Invalid API Key" in result_msg or "invalid api key" in result_msg.lower():
                return False, "Invalid API key"
            return False, f"API error: {result_msg}"
        
        if data.get("status") == "1":
            return True, "Valid"
        
        return True, "Could not fully validate, but key format looks correct"
        
    except requests.exceptions.Timeout:
        return None, "Connection timeout - could not validate (network issue)"
    except requests.exceptions.ConnectionError:
        return None, "Connection error - could not validate (network issue)"
    except Exception as e:
        return None, f"Validation error: {str(e)}"


def get_api_key() -> str:
    """Get API key from config or prompt user."""
    config = get_config()
    
    if config.get("etherscan_api_key"):
        return config["etherscan_api_key"]
    
    print("\n" + "=" * 60)
    print("ETHERSCAN API KEY SETUP")
    print("=" * 60)
    print("\nNo API key found. You need an Etherscan API key to use this tool.")
    print("Get a free API key at: https://etherscan.io/apis")
    print()
    
    while True:
        api_key = input("Enter your Etherscan API key: ").strip()
        if not api_key:
            print("API key cannot be empty. Please try again.\n")
            continue
        
        if len(api_key) < 20:
            print("That doesn't look like a valid API key (too short). Please try again.\n")
            continue
        
        print("\nValidating API key...")
        valid, message = validate_api_key(api_key)
        
        if valid is True:
            config["etherscan_api_key"] = api_key
            save_config(config)
            print(f"✓ API key validated and saved to {CONFIG_FILE}")
            print()
            return api_key
        elif valid is False:
            print(f"✗ {message}. Please try again.\n")
        else:
            print(f"⚠ {message}")
            save_anyway = input("Save this API key anyway? (y/N): ").strip().lower()
            if save_anyway == 'y':
                config["etherscan_api_key"] = api_key
                save_config(config)
                print(f"API key saved to {CONFIG_FILE}")
                print()
                return api_key
            print()


def reset_api_key() -> None:
    """Reset/change the API key."""
    config = get_config()
    
    print("\n" + "=" * 60)
    print("RESET ETHERSCAN API KEY")
    print("=" * 60)
    
    if config.get("etherscan_api_key"):
        current_key = config["etherscan_api_key"]
        masked_key = current_key[:8] + "..." + current_key[-4:]
        print(f"\nCurrent API key: {masked_key}")
    
    print("\nEnter a new API key (or press Enter to cancel):")
    new_key = input("> ").strip()
    
    if new_key:
        print("\nValidating API key...")
        valid, message = validate_api_key(new_key)
        
        if valid is True:
            config["etherscan_api_key"] = new_key
            save_config(config)
            print("✓ API key updated successfully!")
        elif valid is False:
            print(f"✗ {message}. No changes made.")
        else:
            print(f"⚠ {message}")
            save_anyway = input("Save this API key anyway? (y/N): ").strip().lower()
            if save_anyway == 'y':
                config["etherscan_api_key"] = new_key
                save_config(config)
                print("API key updated.")
            else:
                print("No changes made.")
    else:
        print("Cancelled. No changes made.")


# ============================================================================
# ETHERSCAN API
# ============================================================================

class EtherscanAPI:
    """Interact with Etherscan API V2."""
    
    BASE_URL = "https://api.etherscan.io/v2/api"
    WEI_TO_ETH = 10**18
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.chain_id = 1  # Ethereum mainnet (TC is only on mainnet)
    
    def _make_request(self, params: dict) -> dict:
        """Make a request to Etherscan API V2."""
        params["apikey"] = self.api_key
        params["chainid"] = self.chain_id
        response = requests.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "1" and data["message"] != "No transactions found":
            raise Exception(f"Etherscan API error: {data.get('result', data.get('message', 'Unknown error'))}")
        
        return data
    
    def get_block_by_timestamp(self, timestamp: int, closest: str = "before") -> int:
        """Get block number closest to a timestamp."""
        params = {
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": closest
        }
        data = self._make_request(params)
        return int(data["result"])
    
    def get_internal_transactions(self, address: str, start_block: int = 0,
                                   end_block: int = 99999999) -> list:
        """Get internal transactions for an address."""
        all_txs = []
        page = 1
        
        while True:
            params = {
                "module": "account",
                "action": "txlistinternal",
                "address": address,
                "startblock": start_block,
                "endblock": end_block,
                "page": page,
                "offset": 10000,
                "sort": "asc"
            }
            data = self._make_request(params)
            
            if data["result"] and isinstance(data["result"], list):
                all_txs.extend(data["result"])
                if len(data["result"]) < 10000:
                    break
                page += 1
            else:
                break
        
        return all_txs
    
    def get_normal_transactions(self, address: str, start_block: int = 0,
                                 end_block: int = 99999999) -> list:
        """Get normal transactions for an address."""
        all_txs = []
        page = 1
        
        while True:
            params = {
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": start_block,
                "endblock": end_block,
                "page": page,
                "offset": 10000,
                "sort": "asc"
            }
            data = self._make_request(params)
            
            if data["result"] and isinstance(data["result"], list):
                all_txs.extend(data["result"])
                if len(data["result"]) < 10000:
                    break
                page += 1
            else:
                break
        
        return all_txs


# ============================================================================
# TORNADO CASH ANALYSIS
# ============================================================================

def analyze_pool(api: EtherscanAPI, pool_address: str, pool_name: str,
                 start_block: int = 0, end_block: int = 99999999) -> dict:
    """Analyze withdrawals from a single Tornado Cash pool."""
    
    pool_address = pool_address.lower()
    
    print(f"  Fetching transactions from {pool_name} pool...")
    
    # Get internal transactions (TC uses internal txs for withdrawals)
    internal_txs = api.get_internal_transactions(pool_address, start_block, end_block)
    
    # Also get normal transactions
    normal_txs = api.get_normal_transactions(pool_address, start_block, end_block)
    
    print(f"    Found {len(internal_txs)} internal + {len(normal_txs)} normal transactions")
    
    # Aggregate outgoing transfers (withdrawals)
    recipients = defaultdict(lambda: {"count": 0, "total_wei": 0, "transactions": []})
    
    # Process normal transactions (where pool is the sender)
    for tx in normal_txs:
        if tx["from"].lower() == pool_address and int(tx["value"]) > 0:
            to_addr = tx["to"].lower() if tx["to"] else "contract_creation"
            value = int(tx["value"])
            recipients[to_addr]["count"] += 1
            recipients[to_addr]["total_wei"] += value
            recipients[to_addr]["transactions"].append({
                "hash": tx["hash"],
                "value_wei": value,
                "timestamp": int(tx["timeStamp"]),
                "type": "normal"
            })
    
    # Process internal transactions (where pool is the sender)
    for tx in internal_txs:
        if tx["from"].lower() == pool_address and int(tx["value"]) > 0:
            to_addr = tx["to"].lower() if tx["to"] else "contract_creation"
            value = int(tx["value"])
            recipients[to_addr]["count"] += 1
            recipients[to_addr]["total_wei"] += value
            recipients[to_addr]["transactions"].append({
                "hash": tx.get("hash", "internal"),
                "value_wei": value,
                "timestamp": int(tx["timeStamp"]),
                "type": "internal"
            })
    
    return dict(recipients)


def analyze_tornado_cash(api_key: str, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         selected_pools: Optional[list] = None) -> dict:
    """Analyze withdrawals from selected Tornado Cash ETH pools."""
    
    if selected_pools is None:
        selected_pools = list(TORNADO_CASH_POOLS.keys())
    
    api = EtherscanAPI(api_key)
    
    # Convert dates to block numbers
    start_block = 0
    end_block = 99999999
    
    if start_date:
        start_timestamp = int(start_date.timestamp())
        start_block = api.get_block_by_timestamp(start_timestamp, "after")
        print(f"  Start block: {start_block}")
    
    if end_date:
        end_timestamp = int(end_date.timestamp())
        end_block = api.get_block_by_timestamp(end_timestamp, "before")
        print(f"  End block: {end_block}")
    
    # Analyze each selected pool
    pool_results = {}
    
    for pool_key in selected_pools:
        if pool_key not in TORNADO_CASH_POOLS:
            continue
        pool_info = TORNADO_CASH_POOLS[pool_key]
        print(f"\n  Analyzing {pool_info['name']} pool ({pool_info['address'][:10]}...)...")
        
        try:
            results = analyze_pool(
                api, 
                pool_info['address'], 
                pool_info['name'],
                start_block, 
                end_block
            )
            pool_results[pool_key] = results
            print(f"    Found {len(results)} unique recipients")
        except Exception as e:
            print(f"    Error: {e}")
            pool_results[pool_key] = {}
    
    # Merge results by recipient address
    merged = {}
    all_addresses = set()
    
    for pool_key in selected_pools:
        all_addresses.update(pool_results.get(pool_key, {}).keys())
    
    for address in all_addresses:
        merged[address] = {
            "1_eth_count": 0,
            "1_eth_total": 0.0,
            "1_eth_first_date": None,
            "1_eth_last_date": None,
            "10_eth_count": 0,
            "10_eth_total": 0.0,
            "10_eth_first_date": None,
            "10_eth_last_date": None,
            "100_eth_count": 0,
            "100_eth_total": 0.0,
            "100_eth_first_date": None,
            "100_eth_last_date": None,
            "grand_total": 0.0,
            "first_date": None,
            "last_date": None
        }
        
        all_timestamps = []
        
        # 1 ETH pool
        if "1_eth" in selected_pools and address in pool_results.get("1_eth", {}):
            data = pool_results["1_eth"][address]
            merged[address]["1_eth_count"] = data["count"]
            merged[address]["1_eth_total"] = data["total_wei"] / api.WEI_TO_ETH
            if data["transactions"]:
                timestamps = [tx["timestamp"] for tx in data["transactions"]]
                merged[address]["1_eth_first_date"] = datetime.fromtimestamp(min(timestamps))
                merged[address]["1_eth_last_date"] = datetime.fromtimestamp(max(timestamps))
                all_timestamps.extend(timestamps)
        
        # 10 ETH pool
        if "10_eth" in selected_pools and address in pool_results.get("10_eth", {}):
            data = pool_results["10_eth"][address]
            merged[address]["10_eth_count"] = data["count"]
            merged[address]["10_eth_total"] = data["total_wei"] / api.WEI_TO_ETH
            if data["transactions"]:
                timestamps = [tx["timestamp"] for tx in data["transactions"]]
                merged[address]["10_eth_first_date"] = datetime.fromtimestamp(min(timestamps))
                merged[address]["10_eth_last_date"] = datetime.fromtimestamp(max(timestamps))
                all_timestamps.extend(timestamps)
        
        # 100 ETH pool
        if "100_eth" in selected_pools and address in pool_results.get("100_eth", {}):
            data = pool_results["100_eth"][address]
            merged[address]["100_eth_count"] = data["count"]
            merged[address]["100_eth_total"] = data["total_wei"] / api.WEI_TO_ETH
            if data["transactions"]:
                timestamps = [tx["timestamp"] for tx in data["transactions"]]
                merged[address]["100_eth_first_date"] = datetime.fromtimestamp(min(timestamps))
                merged[address]["100_eth_last_date"] = datetime.fromtimestamp(max(timestamps))
                all_timestamps.extend(timestamps)
        
        # Grand total and overall date range
        merged[address]["grand_total"] = (
            merged[address]["1_eth_total"] +
            merged[address]["10_eth_total"] +
            merged[address]["100_eth_total"]
        )
        
        if all_timestamps:
            merged[address]["first_date"] = datetime.fromtimestamp(min(all_timestamps))
            merged[address]["last_date"] = datetime.fromtimestamp(max(all_timestamps))
    
    return merged


# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

def format_output(results: dict, show_zero: bool = False, selected_pools: Optional[list] = None) -> None:
    """Format and print Tornado Cash withdrawal results."""
    if selected_pools is None:
        selected_pools = ["1_eth", "10_eth", "100_eth"]
    
    if not results:
        print("\n  No withdrawals found for the specified criteria.")
        return
    
    # Filter out zero totals if requested
    if not show_zero:
        results = {k: v for k, v in results.items() if v["grand_total"] > 0}
    
    # Sort by grand total descending
    sorted_recipients = sorted(results.items(), 
                                key=lambda x: x[1]["grand_total"], 
                                reverse=True)
    
    # Calculate totals for selected pools
    total_1eth_count = sum(r["1_eth_count"] for _, r in sorted_recipients) if "1_eth" in selected_pools else 0
    total_1eth = sum(r["1_eth_total"] for _, r in sorted_recipients) if "1_eth" in selected_pools else 0
    total_10eth_count = sum(r["10_eth_count"] for _, r in sorted_recipients) if "10_eth" in selected_pools else 0
    total_10eth = sum(r["10_eth_total"] for _, r in sorted_recipients) if "10_eth" in selected_pools else 0
    total_100eth_count = sum(r["100_eth_count"] for _, r in sorted_recipients) if "100_eth" in selected_pools else 0
    total_100eth = sum(r["100_eth_total"] for _, r in sorted_recipients) if "100_eth" in selected_pools else 0
    grand_total = sum(r["grand_total"] for _, r in sorted_recipients)
    
    # Dynamic width based on selected pools
    pool_width = 45  # width per pool section
    num_pools = len(selected_pools)
    total_width = 44 + (num_pools * (pool_width + 3)) + 14
    
    print("\n" + "═" * total_width)
    print("  TORNADO CASH WITHDRAWAL SUMMARY")
    print("═" * total_width)
    print(f"  Total unique recipients: {len(sorted_recipients)}")
    if "1_eth" in selected_pools:
        print(f"  Total 1 ETH withdrawals: {total_1eth_count} ({total_1eth:.2f} ETH)")
    if "10_eth" in selected_pools:
        print(f"  Total 10 ETH withdrawals: {total_10eth_count} ({total_10eth:.2f} ETH)")
    if "100_eth" in selected_pools:
        print(f"  Total 100 ETH withdrawals: {total_100eth_count} ({total_100eth:.2f} ETH)")
    print(f"  Grand total: {grand_total:.2f} ETH")
    print("═" * total_width)
    
    def fmt_date(dt):
        """Format date or return dash if None."""
        return dt.strftime("%Y-%m-%d") if dt else "-"
    
    # Build dynamic header
    header1 = f"{'RECIPIENT ADDRESS':<44}"
    header2 = f"{'':<44}"
    divider = "─" * 44
    
    if "1_eth" in selected_pools:
        header1 += f" │ {'#':>5} {'TOTAL':>10} {'FIRST DATE':>12} {'LAST DATE':>12}"
        header2 += f" │ {'───── 1 ETH POOL ─────':^43}"
        divider += "─┼─" + "─" * 43
    
    if "10_eth" in selected_pools:
        header1 += f" │ {'#':>5} {'TOTAL':>11} {'FIRST DATE':>12} {'LAST DATE':>12}"
        header2 += f" │ {'───── 10 ETH POOL ─────':^44}"
        divider += "─┼─" + "─" * 44
    
    if "100_eth" in selected_pools:
        header1 += f" │ {'#':>5} {'TOTAL':>12} {'FIRST DATE':>12} {'LAST DATE':>12}"
        header2 += f" │ {'───── 100 ETH POOL ─────':^45}"
        divider += "─┼─" + "─" * 45
    
    header1 += f" │ {'TOTAL ETH':>12}"
    header2 += f" │ {'':>12}"
    divider += "─┼─" + "─" * 12
    
    print(f"\n{header1}")
    print(header2)
    print(divider)
    
    for address, stats in sorted_recipients:
        row = f"{address:<44}"
        
        if "1_eth" in selected_pools:
            row += (f" │ "
                   f"{stats['1_eth_count']:>5} "
                   f"{stats['1_eth_total']:>10.2f} "
                   f"{fmt_date(stats['1_eth_first_date']):>12} "
                   f"{fmt_date(stats['1_eth_last_date']):>12}")
        
        if "10_eth" in selected_pools:
            row += (f" │ "
                   f"{stats['10_eth_count']:>5} "
                   f"{stats['10_eth_total']:>11.2f} "
                   f"{fmt_date(stats['10_eth_first_date']):>12} "
                   f"{fmt_date(stats['10_eth_last_date']):>12}")
        
        if "100_eth" in selected_pools:
            row += (f" │ "
                   f"{stats['100_eth_count']:>5} "
                   f"{stats['100_eth_total']:>12.2f} "
                   f"{fmt_date(stats['100_eth_first_date']):>12} "
                   f"{fmt_date(stats['100_eth_last_date']):>12}")
        
        row += f" │ {stats['grand_total']:>12.2f}"
        print(row)
    
    print(divider)
    
    # Total row
    total_row = f"{'TOTAL':<44}"
    
    if "1_eth" in selected_pools:
        total_row += (f" │ "
                     f"{total_1eth_count:>5} "
                     f"{total_1eth:>10.2f} "
                     f"{'':>12} "
                     f"{'':>12}")
    
    if "10_eth" in selected_pools:
        total_row += (f" │ "
                     f"{total_10eth_count:>5} "
                     f"{total_10eth:>11.2f} "
                     f"{'':>12} "
                     f"{'':>12}")
    
    if "100_eth" in selected_pools:
        total_row += (f" │ "
                     f"{total_100eth_count:>5} "
                     f"{total_100eth:>12.2f} "
                     f"{'':>12} "
                     f"{'':>12}")
    
    total_row += f" │ {grand_total:>12.2f}"
    print(total_row)


def export_csv(results: dict, filename: str, selected_pools: Optional[list] = None) -> None:
    """Export results to CSV file."""
    import csv
    
    if selected_pools is None:
        selected_pools = ["1_eth", "10_eth", "100_eth"]
    
    sorted_recipients = sorted(results.items(), 
                                key=lambda x: x[1]["grand_total"], 
                                reverse=True)
    
    def fmt_date(dt):
        """Format date or return empty string if None."""
        return dt.strftime("%Y-%m-%d") if dt else ""
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Build header based on selected pools
        header = ['Recipient Address']
        if "1_eth" in selected_pools:
            header.extend(['1 ETH Withdrawals', 'Total 1 ETH', '1 ETH First Date', '1 ETH Last Date'])
        if "10_eth" in selected_pools:
            header.extend(['10 ETH Withdrawals', 'Total 10 ETH', '10 ETH First Date', '10 ETH Last Date'])
        if "100_eth" in selected_pools:
            header.extend(['100 ETH Withdrawals', 'Total 100 ETH', '100 ETH First Date', '100 ETH Last Date'])
        header.extend(['Grand Total ETH', 'Overall First Date', 'Overall Last Date'])
        
        writer.writerow(header)
        
        for address, stats in sorted_recipients:
            row = [address]
            if "1_eth" in selected_pools:
                row.extend([
                    stats['1_eth_count'],
                    stats['1_eth_total'],
                    fmt_date(stats['1_eth_first_date']),
                    fmt_date(stats['1_eth_last_date'])
                ])
            if "10_eth" in selected_pools:
                row.extend([
                    stats['10_eth_count'],
                    stats['10_eth_total'],
                    fmt_date(stats['10_eth_first_date']),
                    fmt_date(stats['10_eth_last_date'])
                ])
            if "100_eth" in selected_pools:
                row.extend([
                    stats['100_eth_count'],
                    stats['100_eth_total'],
                    fmt_date(stats['100_eth_first_date']),
                    fmt_date(stats['100_eth_last_date'])
                ])
            row.extend([
                stats['grand_total'],
                fmt_date(stats['first_date']),
                fmt_date(stats['last_date'])
            ])
            writer.writerow(row)
    
    print(f"\n  ✓ Results exported to {filename}")


# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def select_pools() -> list:
    """Let user select which pools to analyze."""
    print("\n  Select pools to analyze:")
    print("    1. All pools (1 ETH + 10 ETH + 100 ETH)")
    print("    2. 1 ETH pool only")
    print("    3. 10 ETH pool only")
    print("    4. 100 ETH pool only")
    print("    5. 1 ETH + 10 ETH")
    print("    6. 1 ETH + 100 ETH")
    print("    7. 10 ETH + 100 ETH")
    print("    8. Custom selection")
    print()
    
    choice = input("  Select option (1-8) [1]: ").strip() or "1"
    
    pool_map = {
        "1": ["1_eth", "10_eth", "100_eth"],
        "2": ["1_eth"],
        "3": ["10_eth"],
        "4": ["100_eth"],
        "5": ["1_eth", "10_eth"],
        "6": ["1_eth", "100_eth"],
        "7": ["10_eth", "100_eth"],
    }
    
    if choice in pool_map:
        return pool_map[choice]
    elif choice == "8":
        # Custom selection
        selected = []
        print("\n  Custom selection (y/N for each):")
        if input("    Include 1 ETH pool? (y/N): ").strip().lower() == 'y':
            selected.append("1_eth")
        if input("    Include 10 ETH pool? (y/N): ").strip().lower() == 'y':
            selected.append("10_eth")
        if input("    Include 100 ETH pool? (y/N): ").strip().lower() == 'y':
            selected.append("100_eth")
        
        if not selected:
            print("  No pools selected. Using all pools.")
            return ["1_eth", "10_eth", "100_eth"]
        return selected
    else:
        print("  Invalid option. Using all pools.")
        return ["1_eth", "10_eth", "100_eth"]


def run_analysis(api_key: str) -> None:
    """Run a single analysis."""
    
    # Pool selection
    selected_pools = select_pools()
    
    print(f"\n  Selected pools: {', '.join(TORNADO_CASH_POOLS[p]['name'] for p in selected_pools)}")
    
    # Date range selection
    print("\n  Select date range:")
    print("    1. Last 24 hours")
    print("    2. Last 7 days")
    print("    3. Last 30 days (1 month)")
    print("    4. Last 90 days (3 months)")
    print("    5. Custom date range")
    print("    6. All time (WARNING: This may take a very long time!)")
    print()
    
    date_choice = input("  Select option (1-6): ").strip()
    
    end_date = datetime.now()
    start_date = None
    
    if date_choice == "1":
        start_date = end_date - timedelta(hours=24)
    elif date_choice == "2":
        start_date = end_date - timedelta(days=7)
    elif date_choice == "3":
        start_date = end_date - timedelta(days=30)
    elif date_choice == "4":
        start_date = end_date - timedelta(days=90)
    elif date_choice == "5":
        try:
            start_str = input("  Enter start date (YYYY-MM-DD): ").strip()
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            
            end_str = input("  Enter end date (YYYY-MM-DD) [today]: ").strip()
            if end_str:
                end_date = datetime.strptime(end_str, "%Y-%m-%d")
                end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            print("  Invalid date format. Using last 30 days.")
            start_date = end_date - timedelta(days=30)
    elif date_choice == "6":
        confirm = input("  Analyzing all time data may take a very long time. Continue? (y/N): ").strip().lower()
        if confirm != 'y':
            print("  Cancelled.")
            return
        start_date = None
    else:
        print("  Invalid option. Using last 30 days.")
        start_date = end_date - timedelta(days=30)
    
    # Export option
    export_file = input("\n  Export to CSV file (leave blank to skip): ").strip()
    
    # Run analysis
    print("\n" + "─" * 70)
    print("  FETCHING WITHDRAWAL DATA")
    print("─" * 70)
    if start_date:
        print(f"\n  Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    else:
        print("  Date range: All time")
    
    print("\n  Pools being analyzed:")
    for pool_key in selected_pools:
        pool_info = TORNADO_CASH_POOLS[pool_key]
        print(f"    • {pool_info['name']}: {pool_info['address']}")
    
    try:
        results = analyze_tornado_cash(
            api_key,
            start_date=start_date,
            end_date=end_date,
            selected_pools=selected_pools
        )
        
        format_output(results, selected_pools=selected_pools)
        
        if export_file:
            export_csv(results, export_file, selected_pools=selected_pools)
            
    except Exception as e:
        print(f"\n  Error: {e}")


def interactive_mode(api_key: str) -> None:
    """Run the viewer in interactive mode."""
    
    while True:
        print(BANNER)
        print("\n  Options:")
        print("    1. View Tornado Cash Withdrawals")
        print("    2. Change API Key")
        print("    3. Exit")
        print()
        
        choice = input("  Select option (1-3): ").strip()
        
        if choice == "1":
            run_analysis(api_key)
            input("\n  Press Enter to continue...")
        elif choice == "2":
            reset_api_key()
            api_key = get_api_key()
        elif choice == "3":
            print("\n  Goodbye from intelligenceonchain.com!")
            print()
            break
        else:
            print("\n  Invalid option. Please try again.")


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def parse_date_range(args) -> tuple:
    """Parse date range from command line arguments."""
    end_date = datetime.now()
    start_date = None
    
    if args.last_24h:
        start_date = end_date - timedelta(hours=24)
    elif args.last_7d:
        start_date = end_date - timedelta(days=7)
    elif args.last_30d:
        start_date = end_date - timedelta(days=30)
    elif args.last_90d:
        start_date = end_date - timedelta(days=90)
    elif args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        if args.end_date:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
    
    return start_date, end_date


def main():
    parser = argparse.ArgumentParser(
        description="Tornado Cash Withdrawal Viewer - by intelligenceonchain.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  %(prog)s
  
  # Command line mode - all pools
  %(prog)s --last-24h
  %(prog)s --last-7d
  %(prog)s --last-30d --export withdrawals.csv
  
  # Select specific pools
  %(prog)s --last-7d --pools 10,100
  %(prog)s --last-30d --pools 1
  %(prog)s --last-7d --pools 1,10 --export results.csv
  
  # Custom date range
  %(prog)s --start-date 2024-01-01 --end-date 2024-03-31
  
  # Reset API key
  %(prog)s --reset-key

Pool selection:
  --pools 1        Only 1 ETH pool
  --pools 10       Only 10 ETH pool
  --pools 100      Only 100 ETH pool
  --pools 1,10     1 ETH + 10 ETH pools
  --pools 10,100   10 ETH + 100 ETH pools
  --pools 1,100    1 ETH + 100 ETH pools
  --pools 1,10,100 All pools (default)

─────────────────────────────────────────────────────────────
                  intelligenceonchain.com
─────────────────────────────────────────────────────────────
        """
    )
    
    parser.add_argument("--reset-key", action="store_true",
                        help="Reset/change the Etherscan API key")
    parser.add_argument("--pools", "-p", default="1,10,100",
                        help="Pools to analyze: 1, 10, 100 or combinations like 1,10 (default: 1,10,100)")
    
    # Date range options (mutually exclusive)
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument("--last-24h", action="store_true", 
                            help="Last 24 hours")
    date_group.add_argument("--last-7d", action="store_true", 
                            help="Last 7 days")
    date_group.add_argument("--last-30d", action="store_true", 
                            help="Last 30 days")
    date_group.add_argument("--last-90d", action="store_true", 
                            help="Last 90 days")
    date_group.add_argument("--start-date", 
                            help="Start date (YYYY-MM-DD format)")
    
    parser.add_argument("--end-date", 
                        help="End date (YYYY-MM-DD format, use with --start-date)")
    parser.add_argument("--export", "-e", metavar="FILE",
                        help="Export results to CSV file")
    
    args = parser.parse_args()
    
    # Handle reset key
    if args.reset_key:
        reset_api_key()
        return
    
    # Get API key
    api_key = get_api_key()
    
    # Check if any date option was provided (CLI mode)
    has_date_option = any([
        args.last_24h, args.last_7d, args.last_30d, args.last_90d, args.start_date
    ])
    
    if not has_date_option:
        # Interactive mode
        interactive_mode(api_key)
        return
    
    # CLI mode
    print(BANNER)
    
    # Validate arguments
    if args.end_date and not args.start_date:
        parser.error("--end-date requires --start-date")
    
    # Parse pool selection
    selected_pools = []
    pool_parts = args.pools.replace(" ", "").split(",")
    for p in pool_parts:
        if p == "1":
            selected_pools.append("1_eth")
        elif p == "10":
            selected_pools.append("10_eth")
        elif p == "100":
            selected_pools.append("100_eth")
        else:
            print(f"  Warning: Unknown pool '{p}' ignored. Valid values: 1, 10, 100")
    
    if not selected_pools:
        print("  No valid pools selected. Using all pools.")
        selected_pools = ["1_eth", "10_eth", "100_eth"]
    
    # Parse date range
    start_date, end_date = parse_date_range(args)
    
    print("─" * 70)
    print("  FETCHING WITHDRAWAL DATA")
    print("─" * 70)
    
    if start_date:
        print(f"\n  Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    else:
        print("  Date range: All time")
    
    print(f"\n  Pools being analyzed:")
    for pool_key in selected_pools:
        pool_info = TORNADO_CASH_POOLS[pool_key]
        print(f"    • {pool_info['name']}: {pool_info['address']}")
    
    try:
        results = analyze_tornado_cash(
            api_key,
            start_date=start_date,
            end_date=end_date,
            selected_pools=selected_pools
        )
        
        format_output(results, selected_pools=selected_pools)
        
        if args.export:
            export_csv(results, args.export, selected_pools=selected_pools)
            
    except Exception as e:
        print(f"\n  Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("\n─────────────────────────────────────────────────────────────")
    print("                  intelligenceonchain.com")
    print("─────────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
