import tkinter as tk;

# Function to update the display
def button_click(value):
    current = display.get()
    display.delete(0, tk.END)  # Clear the display
    display.insert(tk.END, current + value)

# Function to evaluate the expression in the display
def calculate():
    try:
        result = eval(display.get())
        display.delete(0, tk.END)
        display.insert(tk.END, result)
    except Exception as e:
        display.delete(0, tk.END)
        display.insert(tk.END, "Error")

# Function to clear the display
def clear_display():
    display.delete(0, tk.END)

# Function to backspace
def backspace():
    current = display.get()
    display.delete(len(current)-1, tk.END)

# Create the main window
root = tk.Tk()
root.title("Calculator")

# Set window size
root.geometry("400x600")
root.config(bg="#302e2e")

# Create a display entry widget
display = tk.Entry(root, font=("Arial", 24), bd=10, relief="sunken", justify="right")
display.grid(row=0, column=0, columnspan=4, sticky="nsew")

# Define the calculator buttons (digits + operations)
buttons = [
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
    ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
    ("C", 5, 0), ("Back", 5, 1)
]

# Create buttons and add them to the grid
for (text, row, col) in buttons:
    if text == "=":
        button = tk.Button(root, text=text, font=("Arial", 18), bd=5, height=2, width=5, command=calculate, relief="raised", bg="#4CAF50", fg="white")
    elif text == "C":
        button = tk.Button(root, text=text, font=("Arial", 18), bd=5, height=2, width=5, command=clear_display, relief="raised", bg="#f44336", fg="white")
    elif text == "Back":
        button = tk.Button(root, text=text, font=("Arial", 18), bd=5, height=2, width=5, command=backspace, relief="raised", bg="#ff9800", fg="white")
    else:
        button = tk.Button(root, text=text, font=("Arial", 18), bd=5, height=2, width=5, command=lambda val=text: button_click(val), relief="raised", bg="#008CBA", fg="white")
    
    button.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

# Make all rows and columns expandable
for i in range(6):
    root.grid_rowconfigure(i, weight=1)
for i in range(4):
    root.grid_columnconfigure(i, weight=1)

# Start the GUI event loop
root.mainloop()