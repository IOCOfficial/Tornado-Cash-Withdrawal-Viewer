# Tornado Cash Withdrawal Viewer

**A blockchain forensics tool by [intelligenceonchain.com](https://intelligenceonchain.com)**

Analyze withdrawals from Tornado Cash ETH pools using the Etherscan API. View recipient addresses with withdrawal counts, totals, and date ranges across all three ETH pools.

> 📖 **New to this tool?** See the [Setup Guide](SETUP_GUIDE.md) for step-by-step instructions for macOS and Windows.

## Features

- **Multi-Pool Analysis**: Simultaneously queries all three Tornado Cash ETH pools
- **Pool Selection**: Choose which pools to analyze (1, 10, 100 ETH) to save bandwidth
- **Consolidated View**: Single table showing per-pool statistics and grand totals
- **Date Tracking**: First and last withdrawal dates for each recipient per pool
- **Flexible Date Filtering**: Preset ranges (24h, 7d, 30d, 90d) or custom dates
- **CSV Export**: Export results for further analysis
- **Interactive Mode**: Analyze multiple date ranges without restarting
- **Secure API Key Storage**: API key saved locally with restricted permissions
- **Cross-Platform**: Works on macOS, Linux, and Windows

## Pools Analyzed

| Pool | Contract Address |
|------|-----------------|
| 1 ETH | `0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c3c2936` |
| 10 ETH | `0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF` |
| 100 ETH | `0xA160cdAB225685dA1d56aa342Ad8841c3b53f291` |

## Quick Start

### macOS / Linux

```bash
chmod +x run.sh
./run.sh
```

### Windows

Double-click `run.bat` or run in Command Prompt:
```cmd
run.bat
```

The script will:
- Create a Python virtual environment
- Install dependencies
- Launch the viewer in interactive mode

### First Run: Enter Your API Key

On first run, you'll be prompted to enter your Etherscan API key.

**Get a free API key at:** https://etherscan.io/apis

The key is saved securely in `~/.tornado_viewer/config.json` for future use.

## Usage

### Interactive Mode (Recommended)

**macOS/Linux:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

This launches a menu where you can:
- **Select which pools to analyze** (1 ETH, 10 ETH, 100 ETH, or any combination)
- View Tornado Cash withdrawals for any date range
- Run multiple analyses without restarting
- Change your API key

### Command Line Mode

**macOS/Linux:**
```bash
# All pools (default)
./run.sh --last-24h
./run.sh --last-7d
./run.sh --last-30d --export withdrawals.csv

# Select specific pools to save bandwidth
./run.sh --last-7d --pools 100              # Only 100 ETH pool
./run.sh --last-7d --pools 10,100           # 10 ETH + 100 ETH pools
./run.sh --last-30d --pools 1 --export results.csv

# Custom date range
./run.sh --start-date 2024-01-01 --end-date 2024-03-31

# Reset API key
./run.sh --reset-key
```

**Windows:**
```cmd
run.bat --last-24h
run.bat --last-7d --pools 100
run.bat --last-30d --export withdrawals.csv
```

### Pool Selection

Select which Tornado Cash pools to query using the `--pools` flag:

| Option | Pools Analyzed |
|--------|----------------|
| `--pools 1` | 1 ETH pool only |
| `--pools 10` | 10 ETH pool only |
| `--pools 100` | 100 ETH pool only |
| `--pools 1,10` | 1 ETH + 10 ETH pools |
| `--pools 1,100` | 1 ETH + 100 ETH pools |
| `--pools 10,100` | 10 ETH + 100 ETH pools |
| `--pools 1,10,100` | All pools (default) |

**Why use pool selection?**
- **Save bandwidth**: Skip pools you don't need
- **Faster queries**: Fewer API calls = faster results
- **Focused analysis**: Analyze only high-value pools (10/100 ETH) for significant transactions

## Output Format

The viewer produces a table with dividers separating each pool's data. Columns are shown dynamically based on selected pools:

**All pools selected:**
```
RECIPIENT ADDRESS                            │     #      TOTAL   FIRST DATE    LAST DATE │     #       TOTAL   FIRST DATE    LAST DATE │     #        TOTAL   FIRST DATE    LAST DATE │    TOTAL ETH
                                             │ ───── 1 ETH POOL ─────                     │ ───── 10 ETH POOL ─────                      │ ───── 100 ETH POOL ─────                      │             
─────────────────────────────────────────────┼────────────────────────────────────────────┼─────────────────────────────────────────────┼──────────────────────────────────────────────┼─────────────
0x1234...                                    │     5      5.00   2024-01-15   2024-03-20 │     2      20.00   2024-02-10   2024-02-28 │     1      100.00   2024-01-05   2024-01-05 │       125.00
```

**Only 10 ETH + 100 ETH selected (`--pools 10,100`):**
```
RECIPIENT ADDRESS                            │     #       TOTAL   FIRST DATE    LAST DATE │     #        TOTAL   FIRST DATE    LAST DATE │    TOTAL ETH
                                             │ ───── 10 ETH POOL ─────                      │ ───── 100 ETH POOL ─────                      │             
─────────────────────────────────────────────┼─────────────────────────────────────────────┼──────────────────────────────────────────────┼─────────────
0x1234...                                    │     2      20.00   2024-02-10   2024-02-28 │     1      100.00   2024-01-05   2024-01-05 │       120.00
```

## CSV Export Columns

CSV columns are dynamically generated based on selected pools:

**Always included:**
- Recipient Address
- Grand Total ETH
- Overall First Date, Overall Last Date

**Per selected pool:**
- X ETH Withdrawals, Total X ETH, X ETH First Date, X ETH Last Date

## Command Line Options

| Option | Description |
|--------|-------------|
| `--pools, -p` | Pools to analyze: 1, 10, 100 or combinations (default: 1,10,100) |
| `--last-24h` | Analyze last 24 hours |
| `--last-7d` | Analyze last 7 days |
| `--last-30d` | Analyze last 30 days |
| `--last-90d` | Analyze last 90 days |
| `--start-date YYYY-MM-DD` | Custom start date |
| `--end-date YYYY-MM-DD` | Custom end date |
| `-e, --export FILE` | Export results to CSV |
| `--reset-key` | Reset Etherscan API key |

## Requirements

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Etherscan API key** ([Get free key](https://etherscan.io/apis))
- **Operating System:** macOS, Linux, or Windows 10/11

## Files

```
tornado_cash_viewer/
├── run.sh              # Setup and run script (macOS/Linux)
├── run.bat             # Setup and run script (Windows)
├── tornado_viewer.py   # Main application
├── requirements.txt    # Python dependencies
├── README.md           # Quick reference
└── SETUP_GUIDE.md      # Detailed setup instructions
```

## Use Cases

- **Fund Tracing**: Identify where mixer funds were withdrawn to
- **Pattern Analysis**: Find addresses receiving from multiple pools
- **Compliance**: Generate reports on mixer activity
- **Investigation**: Track withdrawal timing and amounts

---

**intelligenceonchain.com**
