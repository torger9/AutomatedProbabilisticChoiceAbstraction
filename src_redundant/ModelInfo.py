from TotalSize import total_size

def model_info(model, target_vars, initial_state, workfile):
    """ 
    This function walks through the model to identify three collections:
    1. The set of target locations (target variables are modified while transitioning to these locations)
    2. A dictionary of back edges. A location is the key, and all edges that enter that location
    are the values.
    3. The set of all variables used in the automata
    """
    # Notify console process is beginning
    print("Collecting model info...")
    workfile.write("Collecting model info...\n")

    # Initialize what we are looking for
    back_edges = dict()
    target_locations = set()
    all_vars = set()

    # These variables are used to implement a breadth-first search of the automata (a graph)
    location_queue = list()
    location_queue.append(initial_state)
    visited = set()
    visited.add(initial_state)

    # BFS
    while len(location_queue) > 0:
        curr_location = location_queue.pop()
        workfile.write(f"\tExploring location {len(visited)-len(location_queue)}\n")
        print(f"\tExploring location {len(visited)-len(location_queue)}")

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

    print(f"\t{len(visited)} total locations\n")                
    print(f"\tTarget locations: {len(target_locations)}\n\t\t{total_size(target_locations)} bytes")
    print(f"\tBack edges: {len(back_edges)}\n\t\t{total_size(back_edges)} bytes")
    print(f"\tAll vars: {len(all_vars)}\n\t\t{total_size(all_vars)} bytes\n")
    workfile.write(f"\t{len(visited)} total locations\n\n")                
    workfile.write(f"\tTarget locations: {len(target_locations)}\n\t\t{total_size(target_locations)} bytes\n")
    workfile.write(f"\tBack edges: {len(back_edges)}\n\t\t{total_size(back_edges)} bytes\n")
    workfile.write(f"\tAll vars: {len(all_vars)}\n\t\t{total_size(all_vars)} bytes\n\n")
    
    print("\tModel info collected\n")
    workfile.write("\tModel info collected\n\n")

    return back_edges, target_locations, all_vars

