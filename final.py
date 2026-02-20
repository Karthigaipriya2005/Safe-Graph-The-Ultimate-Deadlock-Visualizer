import time
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
from PIL import Image, ImageTk
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox

import networkx as nx
import matplotlib.pyplot as plt
import subprocess
from tkinter import filedialog, messagebox

loaded_file_path = None  # Keep track of the loaded file path globally

# Function to load input file
def load_input_file(parent):
    file_path = filedialog.askopenfilename(title="Open Input File", filetypes=(("Text Files", ".txt"), ("All Files", ".*")), parent=parent)
    if file_path:
        try:
            with open(file_path, 'r') as f:
                n, m = map(int, f.readline().split())  # Number of processes and resources
                # Further checks to ensure the file contains the required matrices
            global loaded_file_path
            loaded_file_path = file_path
            messagebox.showinfo("File Loaded", f"Input file loaded: {file_path}", parent=parent)
        except Exception as e:
            messagebox.showerror("File Error", f"Failed to load file: {e}", parent=parent)
    else:
        messagebox.showwarning("No File", "No file selected!", parent=parent)

# Function for running Banker's Algorithm (subprocess in C)
def run_banker(input_file_path):
    try:
        result = subprocess.run(['bank.exe'], stdin=open(input_file_path, 'r'), capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


# Function to visualize the graph
def visualize_graph(parent):
    global loaded_file_path
    if not loaded_file_path:
        messagebox.showwarning("Warning", "No input file loaded.", parent=parent)
        return

    with open(loaded_file_path, 'r') as f:
        n, m = map(int, f.readline().split())
        allocation = [list(map(int, f.readline().split())) for _ in range(n)]
        max_resources = [list(map(int, f.readline().split())) for _ in range(n)]
        available = list(map(int, f.readline().split()))

    processes = ["P" + str(i) for i in range(n)]
    resources = ["R" + str(i) for i in range(m)]

    G = nx.DiGraph()

    # Add nodes
    for p in processes:
        G.add_node(p, type='process')
    for r in resources:
        G.add_node(r, type='resource')

    # Add edges
    for i, p in enumerate(processes):
        for j, r in enumerate(resources):
            if allocation[i][j] > 0:
                G.add_edge(p, r, weight=allocation[i][j])
    for i, p in enumerate(processes):
        for j, r in enumerate(resources):
            if max_resources[i][j] > allocation[i][j]:
                G.add_edge(r, p, weight=max_resources[i][j] - allocation[i][j])

    pos = nx.spring_layout(G)

    # Step 1: Draw initial RAG
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, edge_color='gray', font_weight='bold')
    plt.title("Resource Allocation Graph (RAG)")
    plt.axis('off')
    plt.show()

    # Step 2: Solve for Safe Sequence
    output = run_banker(loaded_file_path)

    safe_sequence = []
    deadlocked_nodes = []

    for line in output.strip().split('\n'):
        if line.startswith("Safe Sequence"):
            safe_seq_str = line.replace("Safe Sequence : ", "").strip()
            if safe_seq_str.lower() != 'none' and safe_seq_str != '':
                safe_sequence = safe_seq_str.split()
        elif line.startswith("Deadlock Nodes"):
            deadlock_str = line.replace("Deadlock Nodes : ", "").strip()
            if deadlock_str.lower() != 'none' and deadlock_str != '':
                deadlocked_nodes = deadlock_str.split()

    # NEW: Find missing processes and treat them as deadlocked
    if len(safe_sequence) > 0:
        deadlocked_nodes = [p for p in processes if p not in safe_sequence]

    # Step 3: Correctly Show Dialog Box
    if len(deadlocked_nodes) == 0 and len(safe_sequence) > 0:
        messagebox.showinfo("Result", "No Deadlock Detected.\nSafe Sequence:\n" + ' -> '.join(safe_sequence), parent=parent)
    elif len(deadlocked_nodes) > 0 and len(safe_sequence) > 0:
        messagebox.showinfo("Result", f"Deadlock Detected!\nSafe Sequence:\n{' -> '.join(safe_sequence)}\n\nDeadlock Nodes:\n{' '.join(deadlocked_nodes)}", parent=parent)
    elif len(deadlocked_nodes) > 0 and len(safe_sequence) == 0:
        messagebox.showinfo("Result", "Deadlock Detected!\nNo Safe Sequence Exists.\n\nDeadlock Nodes:\n" + ' '.join(deadlocked_nodes), parent=parent)
    else:
        messagebox.showwarning("Warning", "Unexpected situation.", parent=parent)

    # Step 4: Flashing deadlocked nodes if any
    if len(deadlocked_nodes) > 0:
        flash_deadlock_nodes(G, pos, deadlocked_nodes)

# Function to flash deadlock nodes
def flash_deadlock_nodes(G, pos, deadlocked_nodes):
    fig, ax = plt.subplots(figsize=(10, 8))  # Create a figure and axis once

    for _ in range(6):  # Flash 6 times
        colors = []
        for node in G.nodes():
            if node in deadlocked_nodes:
                colors.append('red')
            else:
                colors.append('lightblue')

        ax.clear()
        nx.draw(G, pos, ax=ax, with_labels=True, node_color=colors, node_size=2000, edge_color='gray', font_weight='bold')
        ax.set_title("Deadlock Detected - Flashing Nodes")
        plt.pause(0.5)

        colors = []
        for node in G.nodes():
            colors.append('lightblue')

        ax.clear()
        nx.draw(G, pos, ax=ax, with_labels=True, node_color=colors, node_size=2000, edge_color='gray', font_weight='bold')
        ax.set_title("Deadlock Detected - Flashing Nodes")
        plt.pause(0.5)

    plt.close(fig)  # <<< Close after flashing# Safe Sequence Function

def SolveProblem(parent):
    global loaded_file_path
    if loaded_file_path:
        output = run_banker(loaded_file_path)
    else:
        messagebox.showwarning("Warning", "No input file loaded.", parent=parent)

    # Create a new full-screen window
    result_window = tk.Toplevel(parent)
    result_window.title("Banker's Algorithm Solver")
    result_window.geometry("1400x800")
    result_window.configure(bg="white")

    # Create a Canvas and a Scrollbar
    canvas = tk.Canvas(result_window, bg="white")
    scrollbar = tk.Scrollbar(result_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Scrollable frame
    scrollable_frame = tk.Frame(canvas, bg="white")
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    try:
        with open(loaded_file_path, 'r') as f:
            n, m = map(int, f.readline().split())
            allocation = [list(map(int, f.readline().split())) for _ in range(n)]
            max_resources = [list(map(int, f.readline().split())) for _ in range(n)]
            available = list(map(int, f.readline().split()))
        need = [[max_resources[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]
        work = available[:]
        finish = [False] * n
        safe_sequence = []
        processes = ["P" + str(i) for i in range(n)]

        y_pos = 20

        # Title
        title = tk.Label(scrollable_frame, text="Banker's Algorithm Execution", font=("Helvetica", 20, "bold"), fg="#2d3436", bg="white")
        title.pack(pady=(10, 20))

        # Table Headers
        table_frame = tk.Frame(scrollable_frame, bg="white")
        table_frame.pack()

        headers = ["Process"] + [f"Alloc[{i}]" for i in range(m)] + [f"Max[{i}]" for i in range(m)] + [f"Need[{i}]" for i in range(m)]
        for col, h in enumerate(headers):
            tk.Label(table_frame, text=h, font=("Helvetica", 10, "bold"), bg="#ffeaa7", width=10).grid(row=0, column=col, padx=2, pady=2)

        # Table Values
        for i in range(n):
            row = [processes[i]] + allocation[i] + max_resources[i] + need[i]
            for col, val in enumerate(row):
                tk.Label(table_frame, text=str(val), font=("Helvetica", 10), bg="white", width=10).grid(row=i+1, column=col, padx=2, pady=2)

        # Initial Available
        y_pos += (n+2)*30
        tk.Label(scrollable_frame, text=f"Initial Available: {available}", font=("Helvetica", 12, "bold"), fg="#6c5ce7", bg="white").pack(pady=(30, 10))

        # Step-by-step Execution
        tk.Label(scrollable_frame, text="Step-by-step Execution:", font=("Helvetica", 14, "bold"), bg="white").pack(pady=(10, 10))

        step_frame = tk.Frame(scrollable_frame, bg="white")
        step_frame.pack()

        step = 1
        deadlocked_processes = []
        d_process = []

        # Modify this logic to implement round-robin check
        while len(safe_sequence) < n:
            progress = False
            for i in range(n):
                if not finish[i]:
                    # Exclude processes with negative Need values
                    if any(need[i][j] < 0 for j in range(m)):
                        if processes[i] not in deadlocked_processes:
                           d_process.append(processes[i])
                        deadlocked_processes.append(processes[i])
                        continue

                    condition = all(need[i][j] <= work[j] for j in range(m))
                    step_text = f"Step {step}: Check if Need[{processes[i]}] <= Available → {need[i]} <= {work} → {'Yes' if condition else 'No'}"
                    tk.Label(step_frame, text=step_text, font=("Helvetica", 10), bg="white", anchor="w", justify="left").pack(anchor="w")
                    step += 1
                    if condition:
                        for j in range(m):
                            work[j] += allocation[i][j]
                        safe_sequence.append(processes[i])
                        finish[i] = True
                        tk.Label(step_frame, text=f"{processes[i]} executes. New Available: {work}", font=("Helvetica", 10), fg="green", bg="white", anchor="w", justify="left").pack(anchor="w", padx=20, pady=(0, 5))
                        progress = True
            # If no process was able to execute, check for deadlock
            if not progress:
                break

        # Display both Safe Sequence (if any) and Deadlock
        if len(safe_sequence) == 0:
            deadlocked = [processes[i] for i in range(n) if not finish[i]]
            tk.Label(scrollable_frame, text=f"Deadlock Detected among: {', '.join(deadlocked)}", font=("Helvetica", 12, "bold"), fg="red", bg="white").pack(pady=(20, 10))

        if safe_sequence:
            tk.Label(scrollable_frame, text=f"Safe Sequence: {' → '.join(safe_sequence)}", font=("Helvetica", 12, "bold"), fg="green", bg="white").pack(pady=(20, 5))

        if deadlocked_processes:
            tk.Label(scrollable_frame, text=f"Deadlock Detected among: {', '.join(d_process)}", font=("Helvetica", 12, "bold"), fg="red", bg="white").pack(pady=(5, 10))

    except Exception as e:
        messagebox.showerror("Error", f"Error processing the file:\n{e}", parent=result_window)

    def show_algorithm():
        algorithm = """1. Work = Available
2. Finish[i] = False
3. For each i:
   if Request[i] <= Work and not Finish[i]:
      Work += Allocation[i]
      Finish[i] = True
4. If all Finish[i] == True → Safe
   Else → Deadlock"""
        messagebox.showinfo("Algorithm (Pseudo Code)", algorithm,parent=result_window)

    # Buttons at the bottom
    button_frame = tk.Frame(scrollable_frame, bg="white")
    button_frame.pack(pady=30)

    algo_button = tk.Button(button_frame, text="Show Algorithm", font=("Helvetica", 12), bg="#0984e3", fg="white", command=show_algorithm, width=20)
    algo_button.pack(side="left", padx=20)

    back_button = tk.Button(button_frame, text="Back", font=("Helvetica", 12), bg="#636e72", fg="white", command=result_window.destroy, width=20)
    back_button.pack(side="left", padx=20)
# Create a frame to hold the buttons
def show_help(parent):
    messagebox.showinfo("Help", "The input file should consist of:\n- Number of processes and resources\n- Allocation matrix\n- Max Request matrix\n- Resources r\nIt should be in .txt format.",parent=parent)

# Function to go back to the main page
def go_back(window):
    window.destroy()  # Close only the second window, not the entire app

# Second Page Window
def second_page():
    second_window = tk.Toplevel(root)  # New window for second page
    second_window.title("Deadlock Solver - Second Page")
    second_window.geometry("800x500")

    # Background Image
    bg_image = Image.open(r"C:\Users\HP\Downloads\OS\os_bg1.jpeg")  # Your background image path
    bg_image = bg_image.resize((800, 500), Image.Resampling.LANCZOS)  # Resizing the background
    bg_photo = ImageTk.PhotoImage(bg_image)
    
    bg_label = tk.Label(second_window, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)  # Set the background image to fill the window

    # Load Input Button
    load_input_btn = tk.Button(second_window, text="Load Input", font=("Helvetica", 16), bg="#00b894", fg="white", width=20, command=lambda:load_input_file(second_window))
    load_input_btn.pack(pady=20)

    # Visualize Button
    visualize_btn = tk.Button(second_window, text="Visualize", font=("Helvetica", 16), bg="#0984e3", fg="white", width=20, command=lambda:visualize_graph(second_window))
    visualize_btn.pack(pady=10)

    # Solve Button
    solve_btn = tk.Button(second_window, text="Solve", font=("Helvetica", 16), bg="#d63031", fg="white", width=20, command=lambda:SolveProblem(second_window))
    solve_btn.pack(pady=10)

    # Help Button
    help_btn = tk.Button(second_window, text="Help", font=("Helvetica", 16), bg="#f39c12", fg="white", width=20, command=lambda:show_help(second_window))
    help_btn.pack(pady=10)

    # Back Button
    back_btn = tk.Button(second_window, text="Back", font=("Helvetica", 16), bg="#2d3436", fg="white", width=20, command=lambda:go_back(second_window))
    back_btn.pack(pady=20)

    second_window.mainloop()

# Function for About Us Button
def about_us():
    messagebox.showinfo(
        "About_Us",
        "• Interactive and educational tool for understanding Deadlock in Operating Systems.\n"
        "• Visualizes Resource Allocation Graph (RAG) based on the input file.\n"
        "• Uses Banker's Algorithm to detect and prevent deadlocks.\n"
        "• Highlights deadlocked processes with flashing or color effects.\n"
        "• Provides safe sequence.\n"
        "• User-friendly layout with step-by-step interaction.\n"
        "• Displays manual solving process.\n"
        "• Includes built-in help section to guide input format and usage.\n"
        "• Ideal for understanding the topic, mini projects, and self-learning.\n"
        "• Designed to make learning OS concepts intuitive and engaging."
    )

# Function to Exit App
def exit_app():
    plt.close('all')
    root.destroy()

# Main Window
root = tk.Tk()
root.title("Deadlock Solver and Visualizer")
root.geometry("800x500")

# Load and set background image
bg_image = Image.open(r"C:\Users\HP\Downloads\OS\os_bg2.webp")
bg_image = bg_image.resize((800, 500), Image.Resampling.LANCZOS)  # Updated line
bg_photo = ImageTk.PhotoImage(bg_image)

# Canvas for background
canvas = tk.Canvas(root, width=800, height=500)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Title Label
title = tk.Label(root, text="Deadlock Solver and Visualizer", font=("Helvetica", 24, "bold"), bg="#ffffff", fg="#003366")
canvas.create_window(400, 80, window=title)

# Buttons
start_btn = tk.Button(root, text="Start", font=("Helvetica", 16), bg="#00b894", fg="white", width=15, command=second_page)
about_btn = tk.Button(root, text="About Us", font=("Helvetica", 16), bg="#0984e3", fg="white", width=15, command=about_us)
exit_btn = tk.Button(root, text="Exit", font=("Helvetica", 16), bg="#d63031", fg="white", width=15, command=exit_app)

# Add buttons to canvas
canvas.create_window(400, 200, window=start_btn)
canvas.create_window(400, 270, window=about_btn)
canvas.create_window(400, 340, window=exit_btn)

root.mainloop()