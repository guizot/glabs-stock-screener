from get_idx_tickers import get_idx_tickers, get_available_sectors
import pandas as pd
from datetime import datetime
import os
import subprocess

def run_screener(screener_function, screener_name, sector):
    """Run the selected screener on selected sector"""
    IDX_TICKERS = get_idx_tickers(sector)
    
    print(f"\n=== {screener_name} - {sector} Sector ===")
    print(f"Scanning {len(IDX_TICKERS)} IDX stocks from {sector} sector...")
    
    results = []
    
    for ticker in IDX_TICKERS:
        res = screener_function(ticker)
        if res:
            results.append(res)
            print(f"✓ {ticker} passed")
    
    df = pd.DataFrame(results)
    
    if not df.empty:
        df = df.sort_values("close", ascending=False)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename = f"results_{timestamp}.csv"
        
        # Create results folder if it doesn't exist
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Save to results folder
        filepath = os.path.join(results_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"\nTop Results for {sector} sector:")
        print(df.head(5))
    else:
        print("No stocks passed the filter.")

def select_sector():
    """Display sector selection menu and return selected sector"""
    sectors = get_available_sectors()
    
    print("\nSector Selection Menu")
    print("=" * 40)
    for i, sector in enumerate(sectors, 1):
        print(f"{i}. {sector}")
    print("=" * 40)
    
    while True:
        try:
            choice = input(f"Select sector (1-{len(sectors)}): ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(sectors):
                return sectors[choice_idx]
            else:
                print(f"Invalid choice. Please select 1-{len(sectors)}.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None

def clear_terminal():
    """Clear the terminal screen"""
    try:
        # Try using clear command first (Unix/Linux/macOS)
        subprocess.run(['clear'], check=True, shell=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Fallback to cls command (Windows)
            subprocess.run(['cls'], check=True, shell=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # If both fail, print multiple newlines to simulate clearing
            print('\n' * 50)

def main():
    """Main function with stdin selection menu"""
    print("Stock Screener Selection Menu")
    print("=" * 30)
    print("1. Screener A (Stage 1 + Stage 2)")
    print("2. Screener B (Price Gap Strategy)")
    print("3. Exit")
    print("=" * 30)
    
    while True:
        try:
            choice = input("Select screener (1-3): ").strip()
            
            if choice == "1":
                from screener_stage1_stage2 import screen_stock as screen_a
                screener_function = screen_a
                screener_name = "Screener A"
            elif choice == "2":
                from screener_price_gap import screen_stock as screen_b
                screener_function = screen_b
                screener_name = "Screener"
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1, 2, or 3.")
                continue
            
            # Select sector
            sector = select_sector()
            if sector is None:
                break
                
            # Clear terminal after selections
            clear_terminal()
            
            # Run screener on selected sector
            run_screener(screener_function, screener_name, sector)
            break
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
