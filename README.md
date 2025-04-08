# Resource Allocation Graph Simulator

A sophisticated web-based application for simulating and visualizing resource allocation in operating systems, featuring advanced deadlock detection and AI-powered analysis. This project provides an intuitive interface for understanding and managing resource allocation scenarios in computer systems.

![Resource Allocation Graph Example](docs/images/rag-example.png)
*Example of a resource allocation graph showing processes (circles), resources (squares), and their relationships. The red cycle indicates a potential deadlock situation.*

## Developer

**Ankit Sharma**
- Full Stack Developer
- Operating Systems & Resource Management Specialist
- GitHub: [AnkitSharmaDev](https://github.com/AnkitSharmaDev)

## Table of Contents
1. [Features](#features)
2. [Technology Stack](#technology-stack)
3. [Installation](#installation)
4. [Project Structure](#project-structure)
5. [Usage Guide](#usage-guide)
6. [Advanced Features](#advanced-features)
7. [API Documentation](#api-documentation)
8. [Contributing](#contributing)
9. [License](#license)

## Features

### Core System Features
- **Process Management**
  - Create and manage processes with unique identifiers
  - Track process states and resource requirements
  - Monitor process resource allocations and requests
  - Automatic process cleanup on termination

- **Resource Management**
  - Add and remove system resources dynamically
  - Configure resource units and availability
  - Track resource allocation states
  - Monitor resource utilization patterns

- **Resource Allocation**
  - Request-based resource allocation system
  - Unit-wise resource distribution
  - Priority-based allocation handling
  - Deadlock prevention mechanisms

- **Request Management**
  - Queue-based request handling
  - Request prioritization
  - Request cancellation support
  - Request state tracking

### Visualization Features
- **Interactive Graph Interface**
  - Dynamic node positioning
  - Drag-and-drop interaction
  - Zoom and pan controls
  - Real-time updates

![Resource Allocation Visualization](docs/images/rag-visualization.png)
*Interactive visualization interface showing resource allocation state with color-coded nodes and edges. The graph updates in real-time as allocations change.*

- **Visual Elements**
  - Color-coded nodes for processes and resources
  - Directional edges for allocations and requests
  - Resource utilization indicators
  - State change animations

### Analysis Features
- **AI-Powered Analysis**
  - Resource usage pattern detection
  - Allocation trend analysis
  - Performance bottleneck identification
  - Optimization recommendations

- **Deadlock Detection**
  - Cycle detection in allocation graph
  - Affected process identification
  - Resource dependency analysis
  - Prevention suggestions

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask Framework**
  - Flask-SQLAlchemy
  - Flask-Login
  - Flask-WTF
  - Werkzeug

### Frontend
- **HTML5/CSS3**
- **JavaScript (ES6+)**
- **Bootstrap 5**
- **Chart.js**
- **vis.js** (for graph visualization)

### Data Management
- **SQLite/PostgreSQL**
- **NetworkX** (for graph algorithms)
- **Pandas** (for data analysis)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AnkitSharmaDev/Resource-allocation-graph.git
   cd Resource-allocation-graph
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Access the Application**
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
Resource-allocation-graph/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── resource_allocation.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       └── ...
├── app.py
├── requirements.txt
└── README.md
```

## Usage Guide

### 1. Process Management
- Navigate to "Processes" page
- Click "Add Process" to create a new process
- Enter process name and priority
- View process details in the table
- Manage process resources through allocation forms

### 2. Resource Management
- Go to "Resources" section
- Add new resources with specified units
- Monitor resource status and availability
- View allocation history and patterns

### 3. Resource Allocation
- Select a process from the process list
- Choose resources to allocate
- Specify allocation units
- Submit allocation request
- Monitor allocation status

### 4. Deadlock Detection
- Access "Deadlock Detection" page
- View current system state graph
- Check for deadlock cycles
- Review affected processes
- Apply suggested resolutions

### 5. AI Analysis
- Visit "AI Analysis" page
- View resource usage charts
- Check allocation trends
- Review performance metrics
- Apply optimization suggestions

## Advanced Features

### 1. Resource Optimization
- **Automatic Recommendations**
  - Resource scaling suggestions
  - Allocation pattern optimization
  - Performance improvement tips
  - Deadlock prevention strategies

- **Trend Analysis**
  - Historical allocation patterns
  - Usage prediction
  - Bottleneck identification
  - Resource utilization forecasting

### 2. Graph Visualization
- **Interactive Controls**
  - Node dragging
  - Zoom controls
  - Layout options
  - Filter controls

- **Real-time Updates**
  - Live state changes
  - Dynamic edge updates
  - Resource status indicators
  - Process state visualization

## API Documentation

### Process Management
```python
# Add Process
POST /add_process
{
    "process_name": "string",
    "priority": "integer"
}

# Remove Process
POST /remove_process/<process_id>
```

### Resource Management
```python
# Add Resource
POST /add_resource
{
    "resource_name": "string",
    "units": "integer"
}

# Delete Resource
POST /delete_resource/<resource_id>
```

### Resource Allocation
```python
# Allocate Resource
POST /allocate_resource/<process_id>
{
    "resource_id": "string",
    "units": "integer"
}

# Release Resource
POST /release_resource/<process_id>/<resource_id>
```

## Contributing

1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Commit your changes
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch
   ```bash
   git push origin feature/YourFeature
   ```
5. Create a Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## About the Developer

Hey I'm **Ankit** a passionate developer. With a strong foundation in computer science and system design,I developed this Resource Allocation Graph Simulator to help students and professionals understand complex resource management concepts through interactive visualization and AI-powered analysis.

### Contact
- GitHub: [AnkitSharmaDev](https://github.com/AnkitSharmaDev)
- LinkedIn: [Ankit Sharma](https://www.linkedin.com/in/ankitsharama/)
- Email: [ankitsharma64604@gmail.com]

---

© 2025 Ankit Sharma. All Rights Reserved.
