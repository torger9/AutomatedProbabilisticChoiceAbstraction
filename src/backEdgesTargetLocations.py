
def add_backedges_find_target_loc(model, target_vars, initial_state):
    back_edges = dict()
    target_locations = set()
    location_queue = list()
    location_queue.append(initial_state)
    visited = set()
    visited.add(initial_state)

    while len(location_queue) > 0:
        curr_location = location_queue.pop()
        for edge in model.get_outgoing_edges(curr_location):
                    
            for destination in edge.destinations:
                dest = destination.location
                for var in target_vars:
                    if var in [assignment.target for assignment in destination.assignments]:
                        target_locations.add(curr_location)

                if dest not in back_edges:
                    back_edges[dest] = set()
                back_edges[dest].add(edge)

                if dest not in visited:
                    location_queue.append(dest)
                    visited.add(dest)

    return back_edges, target_locations

