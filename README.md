
Safe Graph-The Ultimate Deadlock Visualizer

Safe Graph is an interactive deadlock detection and visualization tool designed to analyze resource allocation systems efficiently. The project combines a powerful C-based backend for implementing Banker’s Algorithm and cycle detection with a Python frontend (Tkinter + Matplotlib + NetworkX) for dynamic graph visualization.

The system allows users to upload process-resource allocation data and automatically detects deadlocks in the Resource Allocation Graph (RAG). If a deadlock is found, the involved processes and resources are highlighted visually with blinking red nodes and edges. In safe conditions, the tool generates and displays the safe sequence using Banker’s Algorithm without modifying the original graph structure.

The backend handles all core computations including allocation matrix processing, need matrix calculation, safe sequence generation, and deadlock identification. The frontend provides a clean and user-friendly interface to visualize real-time results, making the tool suitable for academic learning, operating systems projects, and research purposes.

Safe Graph emphasizes modular architecture, performance efficiency, and clear visualization, helping users better understand deadlock scenarios and resolution strategies in modern computing systems.
