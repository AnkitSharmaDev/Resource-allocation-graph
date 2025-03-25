import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ResourceAllocationApp:
    def __init__(self, master):
        self.master = master
        master.title("Resource Allocation Graph Simulator")
        master.geometry("800x600")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        
        # Resource and Process Management
        self.resources = {}
        self.processes = {}
        self.allocation_matrix = {}
        self.request_matrix = {}
        
        # Create UI Components
        self.create_ui()
    
    def create_ui(self):
        # Main Frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Resource Management Section
        ttk.Label(main_frame, text="Resource Management", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Resource Input
        ttk.Label(main_frame, text="Resource Name:").grid(row=1, column=0, sticky=tk.W)
        self.resource_name_entry = ttk.Entry(main_frame)
        self.resource_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(main_frame, text="Resource Count:").grid(row=2, column=0, sticky=tk.W)
        self.resource_count_entry = ttk.Entry(main_frame)
        self.resource_count_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(main_frame, text="Add Resource", command=self.add_resource).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Process Management Section
        ttk.Label(main_frame, text="Process Management", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Label(main_frame, text="Process Name:").grid(row=5, column=0, sticky=tk.W)
        self.process_name_entry = ttk.Entry(main_frame)
        self.process_name_entry.grid(row=5, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(main_frame, text="Add Process", command=self.add_process).grid(row=6, column=0, columnspan=2, pady=5)
        
        # Allocation and Request Section
        ttk.Button(main_frame, text="Allocate Resources", command=self.allocate_resources).grid(row=7, column=0, columnspan=2, pady=5)
        
        # Visualization Button
        ttk.Button(main_frame, text="Generate Resource Allocation Graph", command=self.generate_resource_graph).grid(row=8, column=0, columnspan=2, pady=10)
        
        # Deadlock Detection
        ttk.Button(main_frame, text="Detect Deadlock", command=self.detect_deadlock).grid(row=9, column=0, columnspan=2, pady=5)
    
    def add_resource(self):
        name = self.resource_name_entry.get()
        count = self.resource_count_entry.get()
        
        if not name or not count:
            messagebox.showerror("Error", "Please enter resource name and count")
            return
        
        try:
            count = int(count)
            self.resources[name] = count
            messagebox.showinfo("Success", f"Resource {name} added with {count} units")
            
            # Clear entries
            self.resource_name_entry.delete(0, tk.END)
            self.resource_count_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Resource count must be an integer")
    
    def add_process(self):
        name = self.process_name_entry.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter process name")
            return
        
        # Open dialog to select resources for the process
        resource_allocation = {}
        for resource in self.resources:
            allocation = simpledialog.askinteger(
                "Resource Allocation", 
                f"How many units of {resource} are allocated to {name}?",
                minvalue=0, 
                maxvalue=self.resources[resource]
            )
            if allocation is not None:
                resource_allocation[resource] = allocation
        
        self.processes[name] = resource_allocation
        messagebox.showinfo("Success", f"Process {name} added with resource allocation")
        
        # Clear entry
        self.process_name_entry.delete(0, tk.END)
    
    def allocate_resources(self):
        # Simulate resource allocation
        if not self.processes or not self.resources:
            messagebox.showerror("Error", "Please add resources and processes first")
            return
        
        allocation_details = "Resource Allocation Details:\n"
        for process, resources in self.processes.items():
            allocation_details += f"\n{process}:\n"
            for resource, amount in resources.items():
                allocation_details += f"  - {resource}: {amount} units\n"
        
        messagebox.showinfo("Resource Allocation", allocation_details)
    
    def generate_resource_graph(self):
        # Create a graph using NetworkX
        G = nx.DiGraph()
        
        # Add processes and resources as nodes
        for process in self.processes:
            G.add_node(process, type='process')
        
        for resource in self.resources:
            G.add_node(resource, type='resource')
        
        # Add edges based on resource allocation
        for process, resources in self.processes.items():
            for resource, amount in resources.items():
                if amount > 0:
                    G.add_edge(resource, process)
                    G.add_edge(process, resource)
        
        # Visualization
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G)
        
        # Draw nodes
        process_nodes = [node for node, data in G.nodes(data=True) if data['type'] == 'process']
        resource_nodes = [node for node, data in G.nodes(data=True) if data['type'] == 'resource']
        
        nx.draw_networkx_nodes(G, pos, nodelist=process_nodes, node_color='lightblue', node_size=500)
        nx.draw_networkx_nodes(G, pos, nodelist=resource_nodes, node_color='lightgreen', node_shape='s', node_size=500)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos)
        
        plt.title("Resource Allocation Graph")
        plt.axis('off')
        
        # Create a new window to display the graph
        graph_window = tk.Toplevel(self.master)
        graph_window.title("Resource Allocation Graph")
        
        canvas = FigureCanvasTkAgg(plt.gcf(), master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def detect_deadlock(self):
        # Simple deadlock detection based on resource allocation
        potential_deadlock = False
        deadlock_details = "Deadlock Analysis:\n"
        
        # Check for circular wait condition
        for process in self.processes:
            # Check if process is waiting for resources it can't get
            for resource, allocated in self.processes[process].items():
                if allocated > self.resources[resource]:
                    potential_deadlock = True
                    deadlock_details += f"- {process} might be in deadlock with {resource}\n"
        
        if potential_deadlock:
            messagebox.showwarning("Potential Deadlock Detected", deadlock_details)
        else:
            messagebox.showinfo("Deadlock Detection", "No potential deadlock detected.")

def main():
    root = tk.Tk()
    app = ResourceAllocationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
