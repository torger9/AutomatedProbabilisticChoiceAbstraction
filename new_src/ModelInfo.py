
def model_info(model, target_vars, initial_state):
    """ 
    This function walks through the model to identify three collections:
    1. The set of target locations (locations where target variables are modified)
    2. A dictionary of back edges. A location is the key, and all edges that enter that location
    are the values.
    3. The set of all variables used in the automata
    """

    # Initialize what we are looking for
    back_edges = dict()
    target_locations = set()
    all_vars = set()

    ## These variables are used to implement a breadth-first search of the automata (a graph)
    location_queue = list()
    location_queue.append(initial_state)
    visited = set()
    visited.add(initial_state)

    ## BFS
    while len(location_queue) > 0:
        curr_location = location_queue.pop()

        # Each location has a set of outgoing edges
        # Each edge can have multiple destinations, where the destination is chosen probabilistically
        for edge in model.get_outgoing_edges(curr_location):
            
            # Check for variables used in a guard, if the guard exists
            if (edge.guard != None):
                all_vars.update(edge.guard.used_names)
                    
            for destination in edge.destinations:
                # dest is the actual destination location, not the Destination object
                dest = destination.location

                #Check if a target variable is modified
                for var in target_vars:
                    if var in [assignment.target for assignment in destination.assignments]:
                        target_locations.add(curr_location)

                #Get all variables from the assignments
                for assignment in destination.assignments:
                    all_vars.update(assignment.target.used_names)
                    all_vars.update(assignment.value.used_names)
                
                # Add the edges to the back edge dictionary
                if dest not in back_edges:
                    back_edges[dest] = set()
                back_edges[dest].add(edge)
                

                if dest not in visited:
                    location_queue.append(dest)
                    visited.add(dest)
    print(f"{len(visited)} total locations")                

    return back_edges, target_locations, all_vars

