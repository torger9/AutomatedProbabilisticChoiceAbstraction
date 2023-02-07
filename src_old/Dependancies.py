from momba import model as momba_model


def get_location_dependancies(model, location, target_vars):

    dependancies = set()
    
    for edge in model.get_outgoing_edges(location):
        if edge.guard != None:
            dependancies.update(edge.guard.used_names)
            
        for destination in edge.destinations:
            for assignment in destination.assignments:
                if assignment.target.identifier in target_vars:
                    dependancies.update(assignment.value.used_names)

    return dependancies




   