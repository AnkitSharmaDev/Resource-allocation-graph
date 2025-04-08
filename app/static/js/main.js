/**
 * Resource Allocation Graph Simulator
 * Main JavaScript file for UI interactions and graph rendering
 */

// Initialize Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add fade-in animation to elements
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });

    document.querySelectorAll('.fade-in').forEach((el) => observer.observe(el));

    // Form validation and loading indicators
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const loadingSpinner = document.createElement('div');
                loadingSpinner.className = 'loading-spinner';
                submitBtn.prepend(loadingSpinner);
                submitBtn.disabled = true;
            }
        });
    });

    // Process and resource card hover effects
    document.querySelectorAll('.process-card, .resource-card').forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Update resource visualization
    function updateResourceVisualization() {
        document.querySelectorAll('[data-resource-usage]').forEach(function(element) {
            const usage = parseFloat(element.getAttribute('data-resource-usage'));
            const progressBar = element.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = usage + '%';
                if (usage > 80) {
                    progressBar.classList.remove('bg-success', 'bg-warning');
                    progressBar.classList.add('bg-danger');
                } else if (usage > 60) {
                    progressBar.classList.remove('bg-success', 'bg-danger');
                    progressBar.classList.add('bg-warning');
                } else {
                    progressBar.classList.remove('bg-warning', 'bg-danger');
                    progressBar.classList.add('bg-success');
                }
            }
        });
    }

    // Update resource visualization every 5 seconds
    setInterval(updateResourceVisualization, 5000);
    updateResourceVisualization(); // Initial update
});

/**
 * Initialize the resource allocation graph visualization using Vis.js
 */
function initializeGraphVisualization() {
    const graphContainer = document.getElementById('graph-container');
    if (!graphContainer) return;
    
    // Get graph data from the data attribute or API
    let graphData;
    
    if (graphContainer.hasAttribute('data-graph')) {
        graphData = JSON.parse(graphContainer.getAttribute('data-graph'));
        renderGraph(graphData);
    } else {
        // Fetch graph data from API
        fetch('/api/graph-data')
            .then(response => response.json())
            .then(data => {
                renderGraph(data);
            })
            .catch(error => {
                console.error('Error fetching graph data:', error);
                graphContainer.innerHTML = '<div class="alert alert-danger">Error loading graph data</div>';
            });
    }
}

/**
 * Render the resource allocation graph using Vis.js
 * @param {Object} data - Graph data with nodes and edges
 */
function renderGraph(data) {
    const graphContainer = document.getElementById('graph-container');
    if (!graphContainer) return;
    
    // Create nodes with different shapes for processes and resources
    const nodes = new vis.DataSet(data.nodes.map(node => {
        let nodeConfig = {
            id: node.id,
            label: node.label,
            title: node.title || node.label,
            shape: node.type === 'process' ? 'circle' : 'square',
            color: {
                background: node.type === 'process' ? '#8abced' : '#a5d6a7',
                border: node.type === 'process' ? '#2470df' : '#4caf50',
                highlight: {
                    background: node.type === 'process' ? '#5a9de4' : '#81c784',
                    border: node.type === 'process' ? '#1a56a5' : '#388e3c'
                }
            },
            font: {
                color: '#333333',
                face: 'Arial',
                size: 14
            },
            borderWidth: 2,
            shadow: true
        };
        
        return nodeConfig;
    }));
    
    // Create edges with colors based on edge type (request or allocation)
    const edges = new vis.DataSet(data.edges.map(edge => {
        let edgeConfig = {
            from: edge.from,
            to: edge.to,
            arrows: edge.type === 'request' ? 'to' : 'from',
            color: {
                color: edge.type === 'request' ? '#ff5252' : '#4caf50',
                highlight: edge.type === 'request' ? '#ff8a80' : '#81c784',
                hover: edge.type === 'request' ? '#ff8a80' : '#81c784'
            },
            width: 2,
            title: edge.title || `${edge.from} ${edge.type === 'request' ? 'requests' : 'allocates'} ${edge.to}`
        };
        
        return edgeConfig;
    }));
    
    // Configure physics for better graph layout
    const options = {
        nodes: {
            shape: 'box',
            margin: 10,
            widthConstraint: {
                maximum: 200
            },
            shadow: true
        },
        edges: {
            smooth: {
                type: 'cubicBezier',
                forceDirection: 'horizontal',
                roundness: 0.5
            }
        },
        layout: {
            hierarchical: {
                direction: 'LR',
                sortMethod: 'directed',
                levelSeparation: 150,
                nodeSpacing: 140,
                edgeMinimization: true
            }
        },
        physics: {
            hierarchicalRepulsion: {
                centralGravity: 0.0,
                springLength: 150,
                springConstant: 0.02,
                nodeDistance: 180,
                damping: 0.7
            },
            maxVelocity: 50,
            minVelocity: 0.1,
            solver: 'hierarchicalRepulsion',
            timestep: 0.5,
            stabilization: {
                iterations: 1000
            }
        },
        interaction: {
            navigationButtons: true,
            keyboard: true,
            hover: true
        }
    };
    
    // Create the network visualization
    const network = new vis.Network(graphContainer, { nodes, edges }, options);
    
    // Add event listeners
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = nodes.get(nodeId);
            showNodeInfo(node);
        }
    });
    
    // Stabilize the network once
    network.once('stabilizationIterationsDone', function() {
        const statusElement = document.getElementById('graph-status');
        if (statusElement) {
            statusElement.innerHTML = 'Graph visualization complete';
            statusElement.classList.remove('alert-info');
            statusElement.classList.add('alert-success');
            
            // Hide status after 2 seconds
            setTimeout(() => {
                statusElement.style.display = 'none';
            }, 2000);
        }
    });
}

/**
 * Display information about a clicked node
 * @param {Object} node - The node object that was clicked
 */
function showNodeInfo(node) {
    const infoContainer = document.getElementById('node-info');
    if (!infoContainer) return;
    
    const nodeType = node.shape === 'circle' ? 'Process' : 'Resource';
    const icon = node.shape === 'circle' ? 'microchip' : 'cube';
    
    infoContainer.innerHTML = `
        <div class="card shadow-sm mb-3 animate__animated animate__fadeIn">
            <div class="card-header bg-${node.shape === 'circle' ? 'primary' : 'success'} text-white">
                <h5 class="mb-0"><i class="fas fa-${icon} me-2"></i>${nodeType} Information</h5>
            </div>
            <div class="card-body">
                <p class="mb-1"><strong>ID:</strong> ${node.id}</p>
                <p class="mb-1"><strong>Name:</strong> ${node.label}</p>
                <p class="mb-0"><strong>Type:</strong> ${nodeType}</p>
            </div>
        </div>
    `;
    
    infoContainer.style.display = 'block';
}

/**
 * Handle form validation for resource and process forms
 * @param {HTMLFormElement} form - The form element to validate
 * @returns {boolean} - Whether the form is valid
 */
function validateForm(form) {
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return false;
    }
    return true;
}

/**
 * Update allocation values when form inputs change
 * @param {string} processName - The name of the process
 * @param {string} resourceName - The name of the resource
 * @param {HTMLInputElement} input - The input element
 */
function updateAllocation(processName, resourceName, input) {
    if (input.value < 0) {
        input.value = 0;
    }
    
    // Update the display element if it exists
    const displayElement = document.getElementById(`allocation_display_${processName}_${resourceName}`);
    if (displayElement) {
        displayElement.textContent = input.value;
    }
}

// Utility functions

/**
 * Shows validation error message for an input
 */
function showValidationError(inputElement, message) {
    // Clear any existing error message
    clearValidationError(inputElement);
    
    // Add error class to input
    inputElement.classList.add('is-invalid');
    
    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    // Append error message after input
    inputElement.parentNode.appendChild(errorDiv);
    
    // Focus the input
    inputElement.focus();
}

/**
 * Clears validation error message for an input
 */
function clearValidationError(inputElement) {
    inputElement.classList.remove('is-invalid');
    
    const existingError = inputElement.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

/**
 * Updates summary for allocation/request forms
 */
function updateFormSummary() {
    const summary = document.getElementById('form-summary');
    if (!summary) return;
    
    let total = 0;
    const details = [];
    
    document.querySelectorAll('input[type="number"]').forEach(function(input) {
        const value = parseInt(input.value) || 0;
        if (value > 0) {
            const label = input.dataset.resourceName || input.name.split('_').pop();
            details.push(`${label}: ${value}`);
            total += value;
        }
    });
    
    if (total > 0) {
        summary.innerHTML = `<strong>Total: ${total}</strong> units (${details.join(', ')})`;
        summary.style.display = 'block';
    } else {
        summary.style.display = 'none';
    }
}

/**
 * Download data as JSON file
 */
function downloadJson(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = filename;
    link.href = url;
    link.click();
}

/**
 * Format percentage value
 */
function formatPercent(value) {
    return (value * 100).toFixed(1) + '%';
}

/**
 * Check if two arrays have a cycle (for deadlock detection client-side demo)
 * This is a simplistic implementation just for UI demonstration
 */
function hasCycle(graph) {
    const visited = new Set();
    const recStack = new Set();
    
    function dfs(node) {
        if (!visited.has(node)) {
            visited.add(node);
            recStack.add(node);
            
            const neighbors = graph[node] || [];
            for (const neighbor of neighbors) {
                if (!visited.has(neighbor) && dfs(neighbor)) {
                    return true;
                } else if (recStack.has(neighbor)) {
                    return true;
                }
            }
        }
        recStack.delete(node);
        return false;
    }
    
    for (const node in graph) {
        if (dfs(node)) {
            return true;
        }
    }
    
    return false;
}

// Add custom styles for ripple effect
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style); 