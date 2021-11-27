from momba import model as momba_model


def get_location_dependancies(model, location, target_vars):

    dependancies = set()
    
    for edge in model.get_outgoing_edges(location):
        try:
            ## Here I'm going to assume only one operation, needs to be bolstered for more complicated models
            guard_expression = edge.guard
            dependancies.update(guard_expression.used_names)
            
        except Exception as e:
            print('Exception on guard:')
            print(e)
            print()

        for destination in edge.destinations:
            for assignment in destination.assignments:
                if assignment.target.identifier in target_vars:
                    dependancies.update(assignment.value.used_names)

    return dependancies




   