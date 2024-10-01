import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, time

def backtest_strategy(file_path, entry_time, exit_time, stop_loss):
    # Read the CSV file
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Initialize results
    trades = []

    # Group data by date
    grouped = df.groupby(df.index.date)

    for date, group in grouped:
        # Check if we have data for both entry and exit times
        entry_datetime = datetime.combine(date, entry_time)
        exit_datetime = datetime.combine(date, exit_time)
        
        if entry_datetime not in group.index or exit_datetime not in group.index:
            continue
        
        # Get entry prices
        entry_price = group.loc[entry_datetime, 'close']
        
        # Initialize stop loss prices
        stop_loss_long = entry_price - stop_loss
        stop_loss_short = entry_price + stop_loss
        
        # Initialize exit variables
        exit_price_long = exit_price_short = None
        exit_time_long = exit_time_short = None
        
        # Simulate the trading day
        for minute in group.loc[entry_datetime:exit_datetime].itertuples():
            current_price = minute.close
            
            # Check for stop loss hit for long position
            if exit_price_long is None and current_price <= stop_loss_long:
                exit_price_long = current_price
                exit_time_long = minute.Index
            
            # Check for stop loss hit for short position
            if exit_price_short is None and current_price >= stop_loss_short:
                exit_price_short = current_price
                exit_time_short = minute.Index
        
        # If no stop loss hit, exit at the specified exit time
        if exit_price_long is None:
            exit_price_long = group.loc[exit_datetime, 'close']
            exit_time_long = exit_datetime
        
        if exit_price_short is None:
            exit_price_short = group.loc[exit_datetime, 'close']
            exit_time_short = exit_datetime
        
        # Record the trade
        trades.append({
            'Date': date,
            'Entry Time': entry_datetime.time(),
            'Entry Price': entry_price,
            'Exit Time Long': exit_time_long.time(),
            'Exit Time Short': exit_time_short.time(),
            'Exit Price Long': exit_price_long,
            'Exit Price Short': exit_price_short
        })
    
    # Create DataFrame
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv("trades.csv", index=False)
    
    return trades_df

# to analyze profits without brokerage and slippages  

"""def analyze_trades(trades_df, lot_size):
    trades_df['P&L Long'] = (trades_df['Exit Price Long'] - trades_df['Entry Price'])*lot_size
    trades_df['P&L Short'] = (trades_df['Entry Price'] - trades_df['Exit Price Short'])*lot_size
    trades_df['Total P&L'] = trades_df['P&L Long'] + trades_df['P&L Short']

    daily_pnl = trades_df.groupby("Date")["Total P&L"].sum().reset_index()
    print(" Strategy performance without costs is this - ")
    print(f"Total Trading Days : {len(daily_pnl)}")
    print(f"Total P&L : {daily_pnl["Total P&L"].sum():.2f}")
    print(f"Average Daily P&L : {daily_pnl["Total P&L"].mean():.2f}")

    return daily_pnl, trades_df

file_path = "nifty50.csv"
entry_time = time(9,16)
exit_time = time(15,25)
stop_loss = 100
lot_size = 25

trades_df = backtest_strategy(file_path, entry_time, exit_time, stop_loss)

daily_pnl, trades_df = analyze_trades(trades_df, lot_size)

trades_df.to_csv("all_trades_without_cost.csv", index = False)
print("\n All trades information saved without costs")
daily_pnl.to_csv("daily_pnl_without_cost.csv", index = False)
print("\n All profit information saved without costs")"""



#analyze with brokerage but not slippages

"""def analyze_trades(trades_df, lot_size, cost_per_trade):
    trades_df['P&L Long'] = (trades_df['Exit Price Long'] - trades_df['Entry Price'])*lot_size - cost_per_trade
    trades_df['P&L Short'] = (trades_df['Entry Price'] - trades_df['Exit Price Short'])*lot_size - cost_per_trade
    trades_df['Total P&L'] = trades_df['P&L Long'] + trades_df['P&L Short']

    daily_pnl = trades_df.groupby("Date")["Total P&L"].sum().reset_index()
    print(" Strategy performance without costs is this - ")
    print(f"Total Trading Days : {len(daily_pnl)}")
    print(f"Total P&L : {daily_pnl["Total P&L"].sum():.2f}")
    print(f"Average Daily P&L : {daily_pnl["Total P&L"].mean():.2f}")

    return daily_pnl, trades_df

file_path = "nifty50.csv"
entry_time = time(9,16)
exit_time = time(15,25)
stop_loss = 100
lot_size = 25
cost_per_trade = 200 #4 orders, considering 2 trades 

trades_df = backtest_strategy(file_path, entry_time, exit_time, stop_loss)

daily_pnl, trades_df = analyze_trades(trades_df, lot_size, cost_per_trade)

trades_df.to_csv("all_trades_with_cost.csv", index = False)
print("\n All trades information saved with costs")
daily_pnl.to_csv("daily_pnl_with_cost.csv", index = False)
print("\n All profit information saved with costs")"""


# with both brokeage and slippages

def analyze_trades(trades_df, lot_size, cost_per_trade, slippage_percentage):
    trades_df['Slippage Long'] = trades_df['Entry Price']*slippage_percentage*2
    trades_df['Slippage Short'] = trades_df['Entry Price']*slippage_percentage*2

    trades_df['P&L Long'] = (trades_df['Exit Price Long'] - trades_df['Entry Price']- trades_df['Slippage Long'])*lot_size - cost_per_trade
    trades_df['P&L Short'] = (trades_df['Entry Price'] - trades_df['Exit Price Short']- trades_df['Slippage Short'])*lot_size - cost_per_trade
    trades_df['Total P&L'] = trades_df['P&L Long'] + trades_df['P&L Short']

    daily_pnl = trades_df.groupby("Date")["Total P&L"].sum().reset_index()
    print(" Strategy performance with costs and slippage is this - ")
    print(f"Total Trading Days : {len(daily_pnl)}")
    print(f"Total P&L : {daily_pnl["Total P&L"].sum():.2f}")
    print(f"Average Daily P&L : {daily_pnl["Total P&L"].mean():.2f}")

    return daily_pnl, trades_df

file_path = "nifty50.csv"
entry_time = time(9,16)
exit_time = time(15,25)
stop_loss = 100
lot_size = 25
cost_per_trade = 200 #4 orders, considering 2 trades
slippage_percentage = 0.0005

trades_df = backtest_strategy(file_path, entry_time, exit_time, stop_loss)

daily_pnl, trades_df = analyze_trades(trades_df, lot_size, cost_per_trade, slippage_percentage)

trades_df.to_csv("all_trades_with_cost_and_slippage.csv", index = False)
print("\n All trades information saved with costs adn slippage")
daily_pnl.to_csv("daily_pnl_with_cost_and_slippage.csv", index = False)
print("\n All profit information saved with costs and slippage")

#cumulative Profit
def create_charts(daily_pnl, trades_df):
    plt.figure(figsize=(12,6))
    plt.plot(daily_pnl['Date'], daily_pnl['Total P&L'].cumsum())
    plt.title("Cumulative P&L")
    plt.xlabel("Date")
    plt.ylabel("Cumulative P&L")
    plt.grid(True)
    plt.savefig("cumulative_pnl.png")
    plt.close()


    #Daily P&L Distribution
    plt.figure(figsize=(12,6))
    daily_pnl['Total P&L'].hist(bins=30)
    plt.title("Histogram of Distribution")
    plt.xlabel("Daily P&L")
    plt.ylabel("Frequency")
    plt.savefig("pnl_distribution.png")
    plt.close()

    #Plot Drawdown
    cumulative_pnl = daily_pnl["Total P&L"].cumsum()
    drawdown = cumulative_pnl - cumulative_pnl.cummax()
    plt.figure(figsize=(12,6))
    plt.plot(daily_pnl['Date'],drawdown)
    plt.title("Drawdown over Time")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.grid(True)
    plt.savefig("drawdown.png")
    plt.close()



create_charts(daily_pnl, trades_df)






