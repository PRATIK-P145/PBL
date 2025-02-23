import tkinter as tk

root = tk.Tk()

label1 = tk.Label(root, text="Row 0, Col 0", bg="red")
label1.grid(row=0, column=0, padx=5, pady=5)

label2 = tk.Label(root, text="Row 0, Col 1", bg="green")
label2.grid(row=0, column=1, padx=5, pady=5)

label3 = tk.Label(root, text="Row 1, Col 0", bg="blue")
label3.grid(row=1, column=0, padx=5, pady=5)

label4 = tk.Label(root, text="Row 1, Col 1", bg="yellow")
label4.grid(row=1, column=1, padx=5, pady=5)

root.mainloop()
