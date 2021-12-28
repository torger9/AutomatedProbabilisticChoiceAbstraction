import sys
import re
from foldConstants import fold_constants
from momba import model as momba_model
from momba.model.expressions import *
from momba.model.operators import *
from VariableState import VariableState

def evaluate_possibilities(location, back_edges, incoming_state, visited, initial_state, target_location):
    print(location)
    if location in visited:
        #print("This happened")
        return [incoming_state]
    else:
        new_visited = set(visited)
        new_visited.add(location)

    if location in back_edges:
        final_vals = list()
        i = 0
        for edge in back_edges[location]: 

            #print(f"{tabs} evaluating edge from {location.name} to {edge.location.name}")
            skip_edges = False
            for destination in edge.destinations:      
                dest = edge.location

                # For now the solution to the initial state issue is to skip it
                if dest == initial_state:
                    continue

                if dest == target_location:
                    final_vals.extend([incoming_state])
                    ## Made the assumption to skip other edges here, this only holds if they all go back to the target
                    skip_edges = True
                    continue
                

                backwards_vals = evaluate_possibilities(dest, back_edges, incoming_state, new_visited, initial_state, target_location)
                for val in backwards_vals:
                    #print('One backwards set')
                    #print(val)
                    
                    var_state = VariableState(val)
                    #print(var_state)

                    ## This assumes that a guard does not compare any dependancy variables to other variables, only themselves
                    if check_guard(var_state.var_values, edge.guard):
                        var_state.var_values = substitute_vals(var_state.var_values, destination)
                        var_state.compound_probability(destination.probability)
                        #print(var_state)
                        final_vals.extend([var_state])
                    else:
                        print("Guard false", '\n\n')
                    
                #print(f"{tabs} evaluation dest {destination.location.name}") 
                # var_state = VariableState(incoming_state)
                # var_state.var_values = substitute_vals(var_state.var_values, destination)
                # var_state.compound_probability(destination.probability)
                # var_state.conjuct_guard(edge.guard)
                # if var_state.completely_resolved():
                #     final_vals.extend([var_state])
                    
                # else:
                #     final_vals.extend(evaluate_possibilities(dest, back_edges, var_state, new_visited, initial_state))
            if skip_edges:
                break
        #print(final_vals)
        return final_vals

    else:
        return [incoming_state]


## This needs to be updated to work with the guard variables as well
def substitute_vals(var_values, destination, swap_pattern=re.compile(r":[^:]*>,", re.IGNORECASE)):
    new_var_values = dict(var_values)
    for assignment in destination.assignments:
        for var in new_var_values:
            temp = str(new_var_values[var])
            temp = temp.replace(str(assignment.target), str(assignment.value))
            temp = swap_pattern.sub(",", temp)
            temp = temp.replace('<', '')
            new_var_values[var] = eval(temp)  
    return new_var_values

def check_guard(values, guard, swap_pattern=re.compile(r":[^:]*>,", re.IGNORECASE)):
    guard = str(guard)
    #print("Orignial guard:")
    #print(guard, '\n')
    #print('Values:')
    #print(values, '\n')
    for var in values:
        value = str(values[var])
        guard = guard.replace(str(var), str(value))
        guard = swap_pattern.sub(",", guard)
        guard = guard.replace('<', '')
    guard = eval(guard)
    #print('Swapped guard:')
    #print(guard, '\n')


    evaluated_guard = fold_constants(guard)
    if str(evaluated_guard) ==  'Value(value=False)':
        return False
    else:   
        return True





            

