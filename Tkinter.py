import tkinter as tk;

window = tk.Tk()
window.title("MY Tkinter Window")
window.geometry("640x480")

display = tk.Entry(window, font=("Arial", 24), bd=10, relief="sunken", justify="right")
display.grid(row=0, column=0, columnspan=4, sticky="nsew")

inp = tk.Entry(window, width=20, font=("Ariel",10))
inp.pack(fill="x",padx=20, pady=5)

lb1 = tk.Label(window, text=inp.get(), font=("Ariel",10), bg="black", fg="cyan")
lb1.pack(fill="x",padx=20)





window.mainloop()