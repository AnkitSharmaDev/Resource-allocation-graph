import os
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from app.models.resource_allocation import ResourceAllocationManager

# Initialize Flask app with explicit template and static folders
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'static'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize the resource manager
resource_manager = ResourceAllocationManager()

@app.route('/')
def index():
    """Home page route."""
    return render_template('index.html')

@app.route('/resources', methods=['GET', 'POST'])
def resources():
    """Resource management page route."""
    if request.method == 'POST':
        try:
            resource_name = request.form.get('resource_name')
            total_units = int(request.form.get('total_units', 1))
            
            if not resource_name or resource_name.strip() == '':
                raise ValueError("Resource name is required")
                
            if total_units < 1:
                raise ValueError("Total units must be greater than 0")
                
            resource_manager.add_resource(resource_name, total_units)
            flash(f'Resource {resource_name} added successfully!', 'success')
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error adding resource: {str(e)}', 'error')
        return redirect(url_for('resources'))
        
    return render_template('resources.html', resources=resource_manager.get_resources())

@app.route('/processes', methods=['GET'])
def processes():
    """Process management page route."""
    try:
        processes = resource_manager.get_processes()
        available_resources = resource_manager.get_resources()
        return render_template('processes.html', 
                             processes=processes,
                             available_resources=available_resources)
    except Exception as e:
        flash(f'Error loading processes: {str(e)}', 'error')
        return render_template('processes.html', processes=[], available_resources=[])

@app.route('/graph')
def graph():
    """Resource allocation graph visualization page route."""
    return render_template('graph.html')

@app.route('/api/graph-data')
def api_graph_data():
    """API endpoint for graph data."""
    try:
        # Get processes and resources
        processes = resource_manager.get_processes()
        resources = resource_manager.get_resources()
        
        print(f"API: Found {len(processes)} processes and {len(resources)} resources")
        
        # Debug print each process and resource
        for p in processes:
            print(f"Process: {p.name} (ID: {p.id})")
            print(f"  Allocated: {p.allocated_resources}")
            print(f"  Requested: {p.requested_resources}")
        
        for r in resources:
            print(f"Resource: {r.name} (ID: {r.id})")
            print(f"  Total: {r.total_units}, Available: {r.available_units}")
            print(f"  Allocated to: {r.allocated_to}")
            print(f"  Requested by: {r.requested_by}")
        
        # Get graph data
        graph_data = resource_manager.get_graph_data()
        
        # Ensure we have valid graph data
        if not isinstance(graph_data, dict):
            print("API: Invalid graph data format")
            return jsonify({
                'error': True,
                'message': 'Invalid graph data format',
                'nodes': [],
                'edges': []
            })
        
        # Add process and resource counts to the response
        response_data = {
            'nodes': graph_data.get('nodes', []),
            'edges': graph_data.get('edges', []),
            'stats': {
                'processes': len(processes),
                'resources': len(resources),
                'allocations': sum(len(p.allocated_resources) for p in processes),
                'requests': sum(len(p.requested_resources) for p in processes)
            }
        }
        
        print("API Response:", response_data)
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print(f"API Error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': True,
            'message': f'Error fetching graph data: {str(e)}',
            'nodes': [],
            'edges': []
        }), 500

@app.route('/api/check-deadlock')
def api_check_deadlock():
    """API endpoint for deadlock detection."""
    try:
        deadlock_info = resource_manager.detect_deadlock()
        return jsonify({
            'has_deadlock': deadlock_info['has_deadlock'],
            'message': 'Cycles detected in the resource allocation graph.' if deadlock_info['has_deadlock'] else 'No cycles detected.',
            'cycles': deadlock_info['cycles'],
            'affected_processes': deadlock_info['affected_processes']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/deadlock')
def deadlock():
    """Deadlock detection page route."""
    try:
        deadlock_info = resource_manager.detect_deadlock()
        return render_template('deadlock.html', 
                             has_deadlock=deadlock_info['has_deadlock'],
                             deadlock_info=deadlock_info)
    except Exception as e:
        flash(f'Error detecting deadlock: {str(e)}', 'error')
        return render_template('deadlock.html', has_deadlock=False, deadlock_info=None)

@app.route('/ai_analysis')
def ai_analysis():
    """AI analysis page route."""
    try:
        analysis = resource_manager.analyze_resource_usage()
        if not analysis:
            flash('No data available for analysis.', 'info')
            return render_template('ai_analysis.html', analysis=None)
        return render_template('ai_analysis.html', analysis=analysis)
    except Exception as e:
        flash(f'Error performing AI analysis: {str(e)}', 'error')
        return render_template('ai_analysis.html', analysis={'error': str(e)})

@app.route('/resource_optimization')
def resource_optimization():
    """Resource optimization page route."""
    try:
        recommendations = resource_manager.get_optimization_recommendations()
        if not recommendations:
            flash('No optimization recommendations available.', 'info')
            recommendations = {
                'active_processes': 0,
                'total_resources': 0,
                'total_allocations': 0,
                'resource_usage': {},
                'suggestions': [],
                'allocation_trend': {
                    'timestamps': [],
                    'allocations': []
                }
            }
        return render_template('resource_optimization.html', recommendations=recommendations)
    except Exception as e:
        flash(f'Error generating optimization recommendations: {str(e)}', 'error')
        return render_template('resource_optimization.html', recommendations={
            'error': str(e),
            'active_processes': 0,
            'total_resources': 0,
            'total_allocations': 0,
            'resource_usage': {},
            'suggestions': [],
            'allocation_trend': {
                'timestamps': [],
                'allocations': []
            }
        })

@app.route('/about')
def about():
    """About page route."""
    return render_template('about.html')

# Process Management Routes
@app.route('/add_process', methods=['POST'])
def add_process():
    """Add a new process."""
    try:
        process_name = request.form.get('process_name')
        if not process_name or process_name.strip() == '':
            raise ValueError("Process name is required")
            
        # Create the process
        process_id = resource_manager.add_process(process_name)
        flash(f'Process {process_name} added successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error adding process: {str(e)}', 'error')
    return redirect(url_for('processes'))

@app.route('/remove_process/<process_id>', methods=['POST'])
def remove_process(process_id):
    """Remove a process and release all its allocated resources."""
    try:
        # Get process details for the success message
        process = next((p for p in resource_manager.get_processes() if p.id == process_id), None)
        if not process:
            raise ValueError("Process not found")
            
        # Remove the process (this will also release all allocated resources)
        resource_manager.remove_process(process_id)
        flash(f'Process {process.name} removed successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error removing process: {str(e)}', 'error')
    return redirect(url_for('processes'))

@app.route('/allocate_resource/<process_id>', methods=['POST'])
def allocate_resource(process_id):
    """Allocate a resource to a process."""
    try:
        # Get and validate resource_id
        resource_id = request.form.get('resource_id')
        if not resource_id or resource_id.strip() == '':
            raise ValueError("Please select a resource")
            
        # Get and validate units
        try:
            units = int(request.form.get('units', 1))
            if units < 1:
                raise ValueError("Units must be greater than 0")
        except (TypeError, ValueError):
            raise ValueError("Please enter a valid number of units")
            
        # Perform the allocation
        resource_manager.allocate_resource(process_id, resource_id, units)
        resource = resource_manager.get_resource(resource_id)
        flash(f'Successfully allocated {units} unit(s) of {resource.name} to process', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error allocating resource: {str(e)}', 'error')
    return redirect(url_for('processes'))

@app.route('/request_resource/<process_id>', methods=['POST'])
def request_resource(process_id):
    """Request a resource for a process."""
    try:
        resource_id = request.form.get('resource_id')
        units = int(request.form.get('units', 1))
        if not resource_id:
            raise ValueError("Resource ID is required")
        resource_manager.request_resource(process_id, resource_id, units)
        flash('Resource requested successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error requesting resource: {str(e)}', 'error')
    return redirect(url_for('processes'))

@app.route('/release_resource/<process_id>/<resource_id>', methods=['POST'])
def release_resource(process_id, resource_id):
    """Release a resource from a process."""
    try:
        resource_manager.release_resource(process_id, resource_id)
        flash('Resource released successfully!', 'success')
    except Exception as e:
        flash(f'Error releasing resource: {str(e)}', 'error')
    return redirect(url_for('processes'))

@app.route('/cancel_request/<process_id>/<resource_id>', methods=['POST'])
def cancel_request(process_id, resource_id):
    """Cancel a resource request."""
    try:
        resource_manager.cancel_request(process_id, resource_id)
        flash('Request cancelled successfully!', 'success')
    except Exception as e:
        flash(f'Error cancelling request: {str(e)}', 'error')
    return redirect(url_for('processes'))

@app.route('/delete_resource/<resource_id>', methods=['POST'])
def delete_resource(resource_id):
    """Delete a resource."""
    try:
        # Check if resource exists and is not allocated
        resource = resource_manager.get_resource(resource_id)
        if not resource:
            raise ValueError("Resource not found")
            
        # Check if resource is allocated to any process
        if resource_manager.is_resource_allocated(resource_id):
            raise ValueError("Cannot delete resource that is currently allocated to processes")
            
        # Delete the resource
        resource_manager.delete_resource(resource_id)
        flash(f'Resource {resource.name} deleted successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error deleting resource: {str(e)}', 'error')
    return redirect(url_for('resources'))

if __name__ == '__main__':
    # Add some sample data for testing
    resource_manager.add_resource("CPU", 4)
    resource_manager.add_resource("Memory", 8)
    resource_manager.add_resource("Printer", 2)
    
    app.run(debug=True) 