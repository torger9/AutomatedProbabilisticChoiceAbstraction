import sys
from momba import model as momba_model
from momba.model.expressions import *
from VariableState import VariableState

def evaluate_possibilities(location, back_edges, incoming_state, visited, initial_state):
    if location in visited:
        return [incoming_state]
    else:
        new_visited = set(visited)
        new_visited.add(location)

 
    
    if location in back_edges:
        final_vals = list()
        i = 0
        for edge in back_edges[location]: 
            #print(f"{tabs} evaluating edge from {location.name} to {edge.location.name}")
            for destination in edge.destinations:      
                dest = edge.location

                # For now the solution to the initial state issue is to skip it
                if dest == initial_state:
                    continue

                #print(f"{tabs} evaluation dest {destination.location.name}") 
                var_state = VariableState(incoming_state)
                var_state.var_values = substitute_vals(var_state.var_values, destination)
                var_state.compound_probability(destination.probability)
                var_state.conjuct_guard(edge.guard)
                if var_state.completely_resolved():
                    final_vals.extend([var_state])
                else:
                    final_vals.extend(evaluate_possibilities(dest, back_edges, var_state, new_visited, initial_state))

        return final_vals

    else:
        return [incoming_state]


## This needs to be updated to work with the guard variables as well
def substitute_vals(var_values, destination):
    new_var_values = dict(var_values)
    for assignment in destination.assignments:
        for var in new_var_values:
            temp = str(new_var_values[var])
            temp = temp.replace(str(assignment.target), str(assignment.value))
            new_var_values[var] = eval(temp)  
    return new_var_values






            

