# Resource Allocation Graph Simulator

A Python-based graphical application for simulating and visualizing resource allocation graphs in operating systems, helping to understand and detect deadlock situations.

## Features

- Interactive GUI built with Tkinter
- Resource management with multiple instances
- Process creation and resource allocation
- Dynamic resource allocation graph visualization
- Deadlock detection functionality
- Real-time graph updates

## Prerequisites

Before running this application, make sure you have Python 3.x installed on your system. The following libraries are required:

```bash
pip install networkx matplotlib tkinter
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/AnkitSharmaDev/Resource-allocation-graph.git
cd Resource-allocation-graph
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the main application:
```bash
python os2.py
```

2. Using the Application:
   - Add resources with their instance counts
   - Create processes
   - Allocate resources to processes
   - Visualize the resource allocation graph
   - Check for potential deadlocks

## Project Structure

- `os2.py` - Main application file containing the GUI and core functionality
- `resource_allocation_graph.png` - Sample visualization output
- `resource_allocation_report.pdf` - Documentation and analysis

## Features in Detail

### Resource Management
- Add new resources with multiple instances
- Track resource availability
- Manage resource allocation

### Process Management
- Create new processes
- Allocate resources to processes
- Track process states and resource holdings

### Visualization
- Dynamic graph generation using NetworkX
- Clear visual distinction between processes and resources
- Real-time updates of resource allocation status

### Deadlock Detection
- Implements deadlock detection algorithm
- Provides detailed analysis of potential deadlocks
- Visual feedback on deadlock situations

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.