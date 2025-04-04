"""
Resource Allocation Graph Manager Module

This module provides the core functionality for managing processes, resources,
and their relationships in a Resource Allocation Graph (RAG) system.
"""

import networkx as nx
import json
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd

@dataclass
class Resource:
    name: str
    total_units: int
    available_units: int
    allocated_to: Dict[str, int] = None  # process_id -> units
    requested_by: Dict[str, int] = None  # process_id -> units
    id: str = None

    def __post_init__(self):
        self.allocated_to = {}
        self.requested_by = {}
        
@dataclass
class Process:
    id: str
    name: str
    allocated_resources: Dict[str, int] = None  # resource_id -> units
    requested_resources: Dict[str, int] = None  # resource_id -> units
    creation_time: datetime = None
    
    def __post_init__(self):
        self.allocated_resources = {}
        self.requested_resources = {}
        self.creation_time = datetime.now()

class ResourceAllocationManager:
    """
    Manages the resource allocation graph, handling processes, resources,
    allocation, requests, and deadlock detection.
    """
    
    def __init__(self):
        """Initialize the resource allocation manager with empty state."""
        self.processes: Dict[str, Process] = {}
        self.resources: Dict[str, Resource] = {}
        self.allocation_history: List[dict] = []
        self.graph = nx.DiGraph()
    
    def add_resource(self, name: str, units: int) -> str:
        """Add a new resource with the specified number of units."""
        if units <= 0:
            raise ValueError("Resource units must be greater than 0")
        
        resource_id = str(uuid.uuid4())
        resource = Resource(name=name, total_units=units, available_units=units)
        resource.id = resource_id  # Add ID to the resource
        self.resources[resource_id] = resource
        self.graph.add_node(resource_id, type='resource', name=name)
        return resource_id
    
    def add_process(self, name: str) -> str:
        """Add a new process."""
        process_id = str(uuid.uuid4())
        self.processes[process_id] = Process(id=process_id, name=name)
        self.graph.add_node(process_id, type='process', name=name)
        return process_id
    
    def remove_process(self, process_id: str) -> None:
        """Remove a process and release all its resources."""
        if process_id not in self.processes:
            raise ValueError(f"Process {process_id} not found")
        
        # Release all allocated resources
        process = self.processes[process_id]
        for resource_id in list(process.allocated_resources.keys()):
            self.release_resource(process_id, resource_id)
        
        # Cancel all resource requests
        for resource_id in list(process.requested_resources.keys()):
            self.cancel_request(process_id, resource_id)
        
        # Remove process from graph and dictionary
        self.graph.remove_node(process_id)
        del self.processes[process_id]
    
    def allocate_resource(self, process_id: str, resource_id: str, units: int = 1):
        """Allocate a resource to a process."""
        if process_id not in self.processes:
            raise ValueError(f"Process {process_id} not found")
        if resource_id not in self.resources:
            raise ValueError(f"Resource {resource_id} not found")
        
        resource = self.resources[resource_id]
        process = self.processes[process_id]
        
        if units > resource.available_units:
            raise ValueError(f"Not enough units available. Requested: {units}, Available: {resource.available_units}")
        
        # Update resource
        resource.available_units -= units
        resource.allocated_to[process_id] = resource.allocated_to.get(process_id, 0) + units
        
        # Update process
        process.allocated_resources[resource_id] = process.allocated_resources.get(resource_id, 0) + units
        
        # Update graph
        self.graph.add_edge(resource_id, process_id, type='allocation', units=units)
        
        # Record in history
        self.allocation_history.append({
            'timestamp': datetime.now(),
            'type': 'allocation',
            'process_id': process_id,
            'resource_id': resource_id,
            'units': units
        })
    
    def request_resource(self, process_id: str, resource_id: str, units: int = 1):
        """Request a resource for a process."""
        if process_id not in self.processes:
            raise ValueError(f"Process {process_id} not found")
        if resource_id not in self.resources:
            raise ValueError(f"Resource {resource_id} not found")
        
        resource = self.resources[resource_id]
        process = self.processes[process_id]
        
        # Add request
        resource.requested_by[process_id] = resource.requested_by.get(process_id, 0) + units
        process.requested_resources[resource_id] = process.requested_resources.get(resource_id, 0) + units
        
        # Update graph
        self.graph.add_edge(process_id, resource_id, type='request', units=units)
        
        # Record in history
        self.allocation_history.append({
            'timestamp': datetime.now(),
            'type': 'request',
            'process_id': process_id,
            'resource_id': resource_id,
            'units': units
        })
    
    def release_resource(self, process_id: str, resource_id: str):
        """Release a resource from a process."""
        if process_id not in self.processes:
            raise ValueError(f"Process {process_id} not found")
        if resource_id not in self.resources:
            raise ValueError(f"Resource {resource_id} not found")
        
        resource = self.resources[resource_id]
        process = self.processes[process_id]
        
        if resource_id not in process.allocated_resources:
            raise ValueError(f"Resource {resource_id} not allocated to process {process_id}")
        
        units = process.allocated_resources[resource_id]
        
        # Update resource
        resource.available_units += units
        del resource.allocated_to[process_id]
        
        # Update process
        del process.allocated_resources[resource_id]
        
        # Update graph
        if self.graph.has_edge(resource_id, process_id):
            self.graph.remove_edge(resource_id, process_id)
        
        # Record in history
        self.allocation_history.append({
            'timestamp': datetime.now(),
            'type': 'release',
            'process_id': process_id,
            'resource_id': resource_id,
            'units': units
        })
    
    def cancel_request(self, process_id: str, resource_id: str):
        """Cancel a resource request."""
        if process_id not in self.processes:
            raise ValueError(f"Process {process_id} not found")
        if resource_id not in self.resources:
            raise ValueError(f"Resource {resource_id} not found")
        
        resource = self.resources[resource_id]
        process = self.processes[process_id]
        
        if resource_id not in process.requested_resources:
            raise ValueError(f"No pending request for resource {resource_id} from process {process_id}")
        
        units = process.requested_resources[resource_id]
        
        # Update resource and process
        del resource.requested_by[process_id]
        del process.requested_resources[resource_id]
        
        # Update graph
        if self.graph.has_edge(process_id, resource_id):
            self.graph.remove_edge(process_id, resource_id)
        
        # Record in history
        self.allocation_history.append({
            'timestamp': datetime.now(),
            'type': 'cancel_request',
            'process_id': process_id,
            'resource_id': resource_id,
            'units': units
        })
    
    def get_processes(self) -> List[Process]:
        """Get all processes with their allocated and requested resources."""
        return list(self.processes.values())
    
    def get_resources(self) -> List[Resource]:
        """Get all resources with their allocation status."""
        return list(self.resources.values())
    
    def get_graph_data(self) -> dict:
        """Get the current state of the resource allocation graph."""
        try:
            # Initialize empty lists for nodes and edges
            nodes = []
            edges = []
            
            # Add process nodes
            for process_id, process in self.processes.items():
                nodes.append({
                    'id': process_id,
                    'label': f"{process.name}",
                    'type': 'process',
                    'title': (f"Process: {process.name}<br>"
                             f"Allocated Resources: {len(process.allocated_resources)}<br>"
                             f"Requested Resources: {len(process.requested_resources)}")
                })
            
            # Add resource nodes
            for resource_id, resource in self.resources.items():
                nodes.append({
                    'id': resource_id,
                    'label': f"{resource.name}\n({resource.available_units}/{resource.total_units})",
                    'type': 'resource',
                    'title': (f"Resource: {resource.name}<br>"
                             f"Available: {resource.available_units}/{resource.total_units} units<br>"
                             f"Allocated: {resource.total_units - resource.available_units} units")
                })
            
            # Add allocation edges (resource -> process)
            for resource_id, resource in self.resources.items():
                for process_id, units in resource.allocated_to.items():
                    if process_id in self.processes:  # Ensure process still exists
                        edges.append({
                            'from': resource_id,
                            'to': process_id,
                            'type': 'allocation',
                            'units': units,
                            'title': f"{units} unit{'s' if units > 1 else ''} allocated"
                        })
            
            # Add request edges (process -> resource)
            for resource_id, resource in self.resources.items():
                for process_id, units in resource.requested_by.items():
                    if process_id in self.processes:  # Ensure process still exists
                        edges.append({
                            'from': process_id,
                            'to': resource_id,
                            'type': 'request',
                            'units': units,
                            'title': f"{units} unit{'s' if units > 1 else ''} requested"
                        })
            
            return {
                'nodes': nodes,
                'edges': edges
            }
            
        except Exception as e:
            print(f"Error generating graph data: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'nodes': [],
                'edges': [],
                'error': str(e)
            }
    
    def detect_deadlock(self) -> dict:
        """Detect deadlocks in the current state."""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            deadlock_cycles = []
            affected_processes = set()
            
            for cycle in cycles:
                # Verify if cycle contains alternating process and resource nodes
                is_valid_cycle = True
                for i in range(len(cycle)):
                    node = cycle[i]
                    next_node = cycle[(i + 1) % len(cycle)]
                    
                    if (self.graph.nodes[node]['type'] == self.graph.nodes[next_node]['type'] or
                        not (self.graph.nodes[node]['type'] in ['process', 'resource'] and
                             self.graph.nodes[next_node]['type'] in ['process', 'resource'])):
                        is_valid_cycle = False
                        break
                        
                if is_valid_cycle:
                    deadlock_cycles.append(cycle)
                    affected_processes.update([node for node in cycle 
                                            if self.graph.nodes[node]['type'] == 'process'])
                    
            return {
                'has_deadlock': len(deadlock_cycles) > 0,
                'cycles': deadlock_cycles,
                'affected_processes': list(affected_processes)
            }
        except Exception as e:
            print(f"Error in deadlock detection: {str(e)}")
            return {'has_deadlock': False, 'cycles': [], 'affected_processes': []}
    
    def analyze_resource_usage(self):
        """Analyze resource usage patterns."""
        try:
            # Convert allocation history to DataFrame
            if not self.allocation_history:
                return {
                    'resource_usage': {},
                    'total_allocations': 0,
                    'total_requests': 0,
                    'allocation_trend': {
                        'timestamps': [],
                        'allocations': []
                    },
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
            # Calculate resource usage patterns
            resource_usage = {}
            total_allocations = 0
            total_requests = 0
            
            for resource_id, resource in self.resources.items():
                allocated_units = sum(resource.allocated_to.values())
                usage_percentage = (allocated_units / resource.total_units) * 100 if resource.total_units > 0 else 0
                
                # Calculate average allocation time for this resource
                resource_history = [entry for entry in self.allocation_history 
                                  if entry['resource_id'] == resource_id]
                total_allocation_time = 0
                allocation_count = 0
                
                for i in range(len(resource_history)):
                    if resource_history[i]['type'] == 'allocation':
                        # Look for the next release of this resource
                        for j in range(i + 1, len(resource_history)):
                            if (resource_history[j]['type'] == 'release' and 
                                resource_history[j]['process_id'] == resource_history[i]['process_id']):
                                time_diff = (resource_history[j]['timestamp'] - 
                                           resource_history[i]['timestamp']).total_seconds()
                                total_allocation_time += time_diff
                                allocation_count += 1
                                break
                
                avg_allocation_time = (total_allocation_time / allocation_count 
                                     if allocation_count > 0 else 0)
                
                resource_usage[resource.name] = {
                    'total_units': resource.total_units,
                    'current_usage': allocated_units,
                    'usage_percentage': round(usage_percentage, 1),
                    'allocation_count': len(resource.allocated_to),
                    'request_count': len(resource.requested_by),
                    'average_allocation_time': round(avg_allocation_time, 1)
                }
                
                total_allocations += len(resource.allocated_to)
                total_requests += len(resource.requested_by)
            
            # Generate trend data
            trend_data = self._generate_trend_data()
                    
            return {
                'resource_usage': resource_usage,
                'total_allocations': total_allocations,
                'total_requests': total_requests,
                'allocation_trend': trend_data,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"Error in resource usage analysis: {str(e)}")
            return {
                'error': str(e),
                'resource_usage': {},
                'total_allocations': 0,
                'total_requests': 0,
                'allocation_trend': {
                    'timestamps': [],
                    'allocations': []
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def get_optimization_recommendations(self):
        """Get AI-powered optimization recommendations."""
        try:
            # First get the resource usage analysis
            analysis = self.analyze_resource_usage()
            if 'error' in analysis:
                raise Exception(analysis['error'])
                
            # Get current system state
            active_processes = len(self.processes)
            total_resources = len(self.resources)
            total_allocations = analysis['total_allocations']
            
            # Initialize suggestions list
            suggestions = []
            resource_usage = {}
            
            # Analyze each resource
            for resource_id, resource in self.resources.items():
                allocated_units = sum(resource.allocated_to.values())
                usage_percentage = (allocated_units / resource.total_units) * 100 if resource.total_units > 0 else 0
                
                resource_data = analysis['resource_usage'].get(resource.name, {})
                avg_allocation_time = resource_data.get('average_allocation_time', 0)
                
                resource_usage[resource.name] = {
                    'name': resource.name,
                    'usage_percentage': round(usage_percentage, 1),
                    'allocated_units': allocated_units,
                    'total_units': resource.total_units,
                    'available_units': resource.available_units,
                    'average_allocation_time': avg_allocation_time
                }
                
                # Generate suggestions based on usage patterns
                if usage_percentage > 90:
                    suggestions.append({
                        'type': 'warning',
                        'priority': 'high',
                        'title': 'High Resource Utilization',
                        'message': f'Resource {resource.name} is highly utilized ({usage_percentage:.1f}%)',
                        'description': f'Consider adding more units to {resource.name} to prevent bottlenecks.',
                        'action': 'increase_units',
                        'resource_id': resource_id
                    })
                elif usage_percentage < 10 and resource.total_units > 1:
                    suggestions.append({
                        'type': 'info',
                        'priority': 'low',
                        'title': 'Low Resource Utilization',
                        'message': f'Resource {resource.name} is underutilized ({usage_percentage:.1f}%)',
                        'description': f'Consider reducing units of {resource.name} to optimize resource allocation.',
                        'action': 'decrease_units',
                        'resource_id': resource_id
                    })
                
                # Add suggestions based on allocation time
                if avg_allocation_time > 60:  # If average allocation time is more than 60 seconds
                    suggestions.append({
                        'type': 'warning',
                        'priority': 'medium',
                        'title': 'High Allocation Time',
                        'message': f'Resource {resource.name} has high average allocation time',
                        'description': f'Average allocation time of {avg_allocation_time:.1f}s for {resource.name}. Consider optimizing usage patterns.',
                        'action': 'optimize_allocation',
                        'resource_id': resource_id
                    })
            
            # Check for potential deadlocks
            deadlock_info = self.detect_deadlock()
            if deadlock_info['has_deadlock']:
                suggestions.append({
                    'type': 'danger',
                    'priority': 'critical',
                    'title': 'Potential Deadlock Detected',
                    'message': 'System may be in a deadlock state',
                    'description': 'Review resource allocation strategy to prevent deadlock situation.',
                    'action': 'resolve_deadlock',
                    'affected_processes': deadlock_info['affected_processes']
                })
            
            # Generate trend data
            timestamps = []
            allocations = []
            datasets = []
            
            # Get the last 10 allocation history entries
            recent_history = self.allocation_history[-10:] if self.allocation_history else []
            
            for entry in recent_history:
                timestamps.append(entry['timestamp'].strftime('%H:%M:%S'))
                if entry['type'] == 'allocation':
                    allocations.append(1)
                elif entry['type'] == 'release':
                    allocations.append(-1)
                else:
                    allocations.append(0)
            
            # Create dataset for the chart
            datasets.append({
                'label': 'Resource Allocations',
                'data': allocations,
                'borderColor': 'rgb(75, 192, 192)',
                'tension': 0.1,
                'fill': False
            })
            
            trend_data = {
                'labels': timestamps,
                'datasets': datasets
            }
            
            return {
                'active_processes': active_processes,
                'total_resources': total_resources,
                'total_allocations': total_allocations,
                'resource_usage': resource_usage,
                'suggestions': suggestions,
                'trend_data': trend_data
            }
            
        except Exception as e:
            print(f"Error generating optimization recommendations: {str(e)}")
            return {
                'error': str(e),
                'active_processes': 0,
                'total_resources': 0,
                'total_allocations': 0,
                'resource_usage': {},
                'suggestions': [],
                'trend_data': {
                    'labels': [],
                    'datasets': []
                }
            }
            
    def _generate_trend_data(self):
        """Generate trend data for visualization."""
        try:
            # Get the last 10 allocation history entries
            recent_history = self.allocation_history[-10:] if self.allocation_history else []
            
            timestamps = []
            allocations = []
            total_allocations = 0
            
            for entry in recent_history:
                timestamps.append(entry['timestamp'].strftime('%H:%M:%S'))
                if entry['type'] == 'allocation':
                    total_allocations += 1
                elif entry['type'] == 'release':
                    total_allocations -= 1
                allocations.append(total_allocations)
            
            return {
                'timestamps': timestamps,
                'allocations': allocations
            }
            
        except Exception as e:
            print(f"Error generating trend data: {str(e)}")
            return {
                'timestamps': [],
                'allocations': []
            }
    
    def _calculate_average_allocation_time(self, usage_data: pd.DataFrame) -> float:
        try:
            allocations = usage_data[usage_data['type'] == 'allocation']
            releases = usage_data[usage_data['type'] == 'release']
            
            if allocations.empty or releases.empty:
                return 0
                
            total_time = 0
            count = 0
            
            for _, allocation in allocations.iterrows():
                matching_release = releases[releases['timestamp'] > allocation['timestamp']].iloc[0] \
                    if not releases[releases['timestamp'] > allocation['timestamp']].empty else None
                    
                if matching_release is not None:
                    time_diff = (matching_release['timestamp'] - allocation['timestamp']).total_seconds()
                    total_time += time_diff
                    count += 1
                    
            return total_time / count if count > 0 else 0
        except Exception:
            return 0
    
    def reset(self) -> None:
        """Reset the entire resource allocation graph state."""
        self.processes = {}
        self.resources = {}
        self.allocation_history = []
        self.graph = nx.DiGraph()
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by its ID."""
        return self.resources.get(resource_id)
    
    def delete_resource(self, resource_id: str) -> None:
        """Delete a resource if it exists and is not allocated."""
        resource = self.get_resource(resource_id)
        if not resource:
            raise ValueError("Resource not found")
            
        # Check if resource is allocated
        if self.is_resource_allocated(resource_id):
            raise ValueError("Cannot delete resource that is currently allocated")
            
        # Remove the resource from the graph and dictionary
        if self.graph.has_node(resource_id):
            self.graph.remove_node(resource_id)
        del self.resources[resource_id]
    
    def is_resource_allocated(self, resource_id: str) -> bool:
        """Check if a resource is allocated to any process."""
        resource = self.get_resource(resource_id)
        if not resource:
            return False
        return resource.total_units != resource.available_units 