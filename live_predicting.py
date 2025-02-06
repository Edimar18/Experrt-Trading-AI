import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from keras import models
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
# Simulated data (replace this with real data)
close_prices = np.random.rand(8) * 10  # Last 8 close prices
predicted_prices = np.random.rand(3) * 10  # Next 3 predicted prices

# GUI Class
class LiveGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Market Prediction")
        mt5.initialize()
        self.model = models.load_model('model.keras')
        # Create figure and axis
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.ax.set_title("Market Prediction (Live)")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")

        # Create canvas for Matplotlib figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        # Start live updates
        self.ani = FuncAnimation(self.fig, self.update_graph, interval=1000)  # Updates every second
        
        self.prev_minute = self.get_live_data().iloc[10]['minute']
        self.features = []
        self.past_close = []
        
        
    def get_live_data(self):
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            return None
        symbol = "EURUSD"
        time_frame = mt5.TIMEFRAME_M1
        # request data
        data = mt5.copy_rates_from_pos(symbol, time_frame, 0, 30)
        data = pd.DataFrame(data)
        data['time'] = pd.to_datetime(data['time'], unit='s')
        data['MA5'] = data['close'].rolling(window=5).mean()
        data['MA8'] = data['close'].rolling(window=8).mean()
        data['MA13'] = data['close'].rolling(window=13).mean()
        data['MA20'] = data['close'].rolling(window=20).mean()
        # Calculate RSI
        def calculate_rsi(data, periods=4):
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        data['RSI-4'] = calculate_rsi(data)
        data['RSI-8'] = calculate_rsi(data, 8)
        data['minute'] = data['time'].dt.minute
        data.dropna(axis=0, inplace=True)
        return data
    
    def fetch_new_data(self):
        """Replace this with actual market data fetching logic."""
        global close_prices, predicted_prices
        new_close = np.random.rand() * 10  # Simulated new close price
        new_predicted = np.random.rand(3) * 10  # Simulated new predictions

        # Shift data and append new values
        close_prices = np.roll(close_prices, -1)
        close_prices[-1] = new_close
        predicted_prices[:] = new_predicted  # Replace predicted prices

    def update_graph(self, frame):
        self.fetch_new_data()  # Get new market data
        if self.prev_minute == self.get_live_data().iloc[10]['minute']:
            return
        else:
            self.prev_minute = self.get_live_data().iloc[10]['minute']
            print('00000000')
            data = self.get_live_data()
            features = np.array([data.iloc[0]['close'], data.iloc[1]['close'], data.iloc[2]['close'], data.iloc[3]['close'], data.iloc[4]['close'], 
                        data.iloc[5]['close'], data.iloc[6]['close'], data.iloc[7]['close'], data.iloc[8]['close'], data.iloc[9]['close'],
                        data.iloc[10]['open'], data.iloc[10]['high'], data.iloc[10]['low'], data.iloc[10]['close'], data.iloc[10]['tick_volume'],    
                        data.iloc[10]['spread'], data.iloc[10]['MA5'], data.iloc[10]['MA8'], data.iloc[10]['MA13'], data.iloc[10]['MA20'],
                        data.iloc[10]['RSI-4'], data.iloc[10]['RSI-8']])
            features = np.array([features])
            past_close = [data.iloc[10-i]['close'] for i in range(10)]
            
            predicted = self.model.predict(features)[0]
            print(f'predictions: {predicted}')
            self.ax.clear()
            self.ax.set_title("Market Prediction (Live)")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Price")
            
            full_x = list(range(len(past_close) + len(predicted)))
            full_y = list(past_close) + list(predicted)
            
            self.ax.plot(range(len(past_close)), past_close, 'b-', label="Close Prices")
            
            # Plot predicted prices connected to last close price
            pred_x = range(len(past_close) - 1, len(past_close) + len(predicted))
            self.ax.plot(pred_x, [past_close[-1]] + list(predicted), 'r--', label="Predictions")
            
            # Plot predicted points with different colors
            self.ax.scatter(pred_x[1], predicted[0], color="red", label="1st Prediction")
            self.ax.scatter(pred_x[2], predicted[1], color="orange", label="2nd Prediction")
            self.ax.scatter(pred_x[3], predicted[2], color="yellow", label="3rd Prediction")
            
            self.ax.legend()
            self.canvas.draw()
            

        
# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = LiveGraphApp(root)
    root.mainloop()
