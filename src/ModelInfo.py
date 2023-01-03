def model_info(model, target_vars, initial_state, workfile):
    """ 
    This function walks through the model to identify three collections:
    1. The set of target locations (target variables are modified while transitioning from these locations through a destination)
    2. A dictionary of back edges. A location is the key, and all edges that enter that location
    are the values.
    3. The set of all variables used in the automata
    """
    debug = True
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
        if debug: 
            print(f"\tExploring location {len(visited)-len(location_queue)}: ({curr_location.name})")
            workfile.write(f"\tExploring location {len(visited)-len(location_queue)}: ({curr_location.name})\n")

        # Each location has a set of outgoing edges
        # Each edge can have multiple destinations, where the destination is chosen probabilistically
        for edge in model.get_outgoing_edges(curr_location):
            
            # Check for variables used in a guard, if the guard exists
            if (edge.guard != None):
                all_vars.update(edge.guard.used_names)
                    
            for destination in edge.destinations:
                # dest is the actual destination location, not the Destination object
                dest = destination.location
                if debug: 
                    print(f'\t\tExploring path to {dest.name}')
                    workfile.write(f'\t\tExploring path to {dest.name}\n')

                #Check if a target variable is modified
                for var in target_vars:
                    if var in [assignment.target for assignment in destination.assignments]:
                        target_locations.add(curr_location)
                        if debug: 
                            print ('\t\t\tTARGET LOCATION')
                            workfile.write('\t\t\tTARGET LOCATION\n')

                #Get all variables from the assignments
                for assignment in destination.assignments:
                    all_vars.update(assignment.target.used_names)
                    all_vars.update(assignment.value.used_names)
                    if debug: 
                        print(f'\t\t\tvariable: {assignment.target.used_names}')
                        workfile.write(f'\t\t\tvariable: {assignment.target.used_names}\n')
                
                # Add the edges to the back edge dictionary
                if dest not in back_edges:
                    back_edges[dest] = set()
                back_edges[dest].add(edge)
                
                if dest not in visited:
                    location_queue.append(dest)
                    visited.add(dest)

# print out results if in debug mode
    if debug:
        print(f"\t{len(visited)} total locations\n") 

        count = 1      
        print(f"\t\tTarget locations: {len(target_locations)}")
        for element in target_locations:
            print (f'\t\t\t{count}: {element.name}')
            count = count + 1

        count = 1
        print(f"\t\tBack edges: {len(back_edges)}")
        for element in back_edges:
            #print(f'\t\t\t{count}: source: {element.location}\tdestinations: {element.destinations}')
            print(f'\t\t\t{count}: {element.name}')
            count = count + 1
        
        count = 1
        print(f"\t\tAll vars: {len(all_vars)}")
        for element in all_vars:
            print (f'\t\t\t{count}: {element}')
            count = count + 1

        workfile.write(f"\t{len(visited)} total locations\n\n")  

        count = 1              
        workfile.write(f"\t\tTarget locations: {len(target_locations)}\n")
        for element in target_locations:
            workfile.write(f'\t\t\t{count}: {element.name}\n')
            count = count + 1

        count = 1
        workfile.write(f"\t\tBack edges: {len(back_edges)}\n")
        for element in back_edges:
            workfile.write(f'\t\t\t{count}: {element.name}\n')
            count = count + 1
        
        count = 1
        workfile.write(f"\t\tAll vars: {len(all_vars)}\n")
        for element in all_vars:
            workfile.write(f'\t\t\t{count}: {element}\n')
            count = count + 1

# Notify console process has copleted
    print("\tModel info collected\n________________________________\n")
    workfile.write("\tModel info collected\n________________________________\n\n")

    return back_edges, target_locations, all_vars