
def backward_traversal(model, path_to_target, visited, initial_location, target_location):
    """
    This function finds a path from the initial location to the target location
    This path is a list of locations starting at the target and ending at the initial
    """
    
    #model: momba model, path_to_target: list, visited: set, initial_location: momba location, target_location: momba location
    
    #if old_path has at least 3 locations, go back and resume search from there
    #else just start back at the target location
    if(len(path_to_target) > 2):
        path_to_target.pop()
        path_to_target.pop()
        current_location = path_to_target.pop()
    else:
        path_to_target = list()
        current_location = target_location

    visited.add(current_location)

    #search until you reach the initial location
    #all incoming edges are possibile paths
    #examine the next edge if its location has already been seen
    #if a new location is encountered, add it to the path
    #if all backward edges go to known locations, backtrack
    while current_location != initial_location:
        for edge in model.get_incoming_edges(current_location):
            if edge.location in visited:
                continue
            else:
                path_to_target.append(current_location)
                current_location = edge.location
                visited.add(edge.location)
                break
        else:
        #only evaulated if all edges lead to visited locations
        #backtrack 1 step if possible and clear leaf locations from visited set
        #if not possible, all paths are found, return None as the path
            if(len(path_to_target) > 0):
                for edge in model.get_incoming_edges(current_location):
                    if edge.location in visited:
                        visited.remove(edge.location)
                current_location = path_to_target.pop()
            else:
                return (None, None)

    path_to_target.append(current_location)
    return (path_to_target, visited)
    
