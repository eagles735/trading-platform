import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import datetime
import os

# CSV filename for persistent storage
CSV_FILE = "investment_log.csv"

# Try to load existing data or create an empty DataFrame
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["Date", "Asset", "Amount", "Type"])

# Save data to CSV
def save_data():
    df.to_csv(CSV_FILE, index=False)

# Add new investment entry
def add_investment():
    global df
    date = date_entry.get()
    asset = asset_entry.get().upper()
    amount = amount_entry.get()
    inv_type = type_var.get()

    if not date or not asset or not amount:
        messagebox.showerror("Missing Info", "Please fill in all fields.")
        return

    try:
        amt = float(amount)
    except ValueError:
        messagebox.showerror("Invalid Amount", "Enter a valid number for amount.")
        return

    new_row = pd.DataFrame([[date, asset, amt, inv_type]], columns=df.columns)
 
    df = pd.concat([df, new_row], ignore_index=True)
    save_data()
    refresh_table()
    clear_fields()

# Remove selected row
def remove_selected():
    selected = tree.selection()
    if not selected:
        return
    for item in selected:
        index = tree.index(item)
        df.drop(index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    save_data()
    refresh_table()

# Clear input fields
def clear_fields():
    date_entry.delete(0, tk.END)
    asset_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

# Populate table with data
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    for _, row in df.iterrows():
        tree.insert("", tk.END, values=list(row))

# Calculate totals and mock value
def calculate_summary():
    total_invested = df["Amount"].sum()
    # Mocked value increase: +10% for stocks, +30% for crypto
    value = 0
    for _, row in df.iterrows():
        if row["Type"] == "Stock":
            value += row["Amount"] * 1.1
        else:
            value += row["Amount"] * 1.3
    profit = value - total_invested
    summary_label.config(text=f"Total Invested: ${total_invested:.2f}\n"
                              f"Current Value: ${value:.2f}\n"
                              f"Profit/Loss: ${profit:.2f}")

# GUI Setup
root = tk.Tk()
root.title("Weekly Investment Tracker")
root.geometry("720x500")

# Input Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0)
tk.Label(input_frame, text="Asset (e.g., BTC, AAPL):").grid(row=1, column=0)
tk.Label(input_frame, text="Amount:").grid(row=2, column=0)
tk.Label(input_frame, text="Type:").grid(row=3, column=0)

date_entry = tk.Entry(input_frame)
asset_entry = tk.Entry(input_frame)
amount_entry = tk.Entry(input_frame)
type_var = tk.StringVar(value="Crypto")
type_menu = ttk.Combobox(input_frame, textvariable=type_var, values=["Crypto", "Stock"], state="readonly")

date_entry.grid(row=0, column=1)
asset_entry.grid(row=1, column=1)
amount_entry.grid(row=2, column=1)
type_menu.grid(row=3, column=1)

tk.Button(input_frame, text="Add Entry", command=add_investment).grid(row=4, column=0, pady=10)
tk.Button(input_frame, text="Remove Selected", command=remove_selected).grid(row=4, column=1)

# TreeView Table
tree = ttk.Treeview(root, columns=["Date", "Asset", "Amount", "Type"], show="headings", height=10)
for col in ["Date", "Asset", "Amount", "Type"]:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")
tree.pack(pady=10, fill="x")

# Summary
summary_frame = tk.Frame(root)
summary_frame.pack()
tk.Button(summary_frame, text="Calculate Totals", command=calculate_summary).pack()
summary_label = tk.Label(summary_frame, text="", font=("Arial", 12), pady=10)
summary_label.pack()

# Initial Load
refresh_table()

root.mainloop()
