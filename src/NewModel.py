from momba import jani
from momba import model as momba_model

from VariableState import VariableState


def make_new_model(model, initial_state, target_state, removable_vars_evaluated, cannot_remove_set):
    new_model = momba_model.Automaton(model.ctx, name=model.name)
    new_model.locations.clear()
    new_model.initial_locations.clear()
    new_model.edges.clear()


    location_queue = list()
    location_queue.append(initial_state)
    visited = set()
    visited.add(initial_state)

    new_model.add_location(initial_state, initial=True)
    new_model.initial_locations.add(initial_state)


    while len(location_queue) > 0:
        curr_location = location_queue.pop()


        if curr_location == target_state:
            new_edge_set = evaluate_edges(model.get_outgoing_edges(curr_location), removable_vars_evaluated, cannot_remove_set)
        else:
            new_edge_set = merge_edges(model.get_outgoing_edges(curr_location), cannot_remove_set)
        
        

        for edge in new_edge_set:
            for destination in edge.destinations:
                dest = destination.location
                if dest not in visited:
                    location_queue.append(dest)
                    visited.add(dest)
                    new_model.add_location(dest)
            new_model.add_edge(edge)
    for edge in model.edges:
        for destination in edge.destinations:
            pass
            #print(destination)
            #print('\n')
        #print('\n\n')
    return new_model


# Needs to be modified to work with guards
def merge_edges(edge_set, cannot_remove_set):
    new_edges = set()
    for edge in edge_set:
        new_destinations = list()
        for destination in edge.destinations: 
            needed_assignments = set()
            for assignment in destination.assignments:
                if assignment.target in cannot_remove_set:
                    needed_assignments.add(assignment)
                else:
                    pass

            for assignment in needed_assignments:
                if assignment.target not in cannot_remove_set:
                    print(f"This assignment is messed {assignment}")
            merged = False
            for d in new_destinations:
                if d.location == destination.location and frozenset(needed_assignments) == d.assignments:
                    merged = True
                    break

            if not merged:
                new_destinations.append(momba_model.Destination(destination.location, destination.probability, frozenset(needed_assignments)))
        for destination in new_destinations:
            for assignment in needed_assignments:
                    if assignment.target not in cannot_remove_set:
                        print(f"This assignment is messed {assignment}")
        new_edge = momba_model.Edge(edge.location, frozenset(new_destinations), edge.action_pattern, edge.guard, edge.rate, edge.annotation, edge.observation)
        new_edges.add(new_edge)
    for edge in new_edges:
        for destination in edge.destinations:
                for assignment in destination.assignments:
                        if assignment.target not in cannot_remove_set:
                            print(f"This assignment is messed {assignment}")
    return new_edges


        # Might need to merge the edges here as well
            

#Needs to be modified to work with guards
def evaluate_edges(edge_set, removable_vars_evaluated, cannot_remove_set):
    new_edges = set()
    for edge in edge_set:
        new_destinations = list()
        for destination in edge.destinations: 
            needed_assignments = set()
            for assignment in destination.assignments:
                if assignment.target in removable_vars_evaluated:
                    needed_assignments.add(momba_model.Assignment(assignment.target, removable_vars_evaluated[assignment.target], assignment.index))
                else:
                    needed_assignments.add(assignment)

            merged = False
            for d in new_destinations:
                if d.location == destination.location and frozenset(needed_assignments) == d.assignments:
                    merged = True
                    break

            if not merged:
                new_destinations.append(momba_model.Destination(destination.location, destination.probability, frozenset(needed_assignments)))

        new_edge = momba_model.Edge(edge.location, frozenset(new_destinations), edge.action_pattern, edge.guard, edge.rate, edge.annotation, edge.observation)
        new_edges.add(new_edge)
    return merge_edges(new_edges, cannot_remove_set)
