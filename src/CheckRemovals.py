import sys
import re
from NewModel import evaluate_edges
from foldConstants import fold_constants
from momba import model as momba_model
from momba.model.expressions import *
from momba.model.operators import *
from VariableState import VariableState

def evaluate_possibilities(location, back_edges, incoming_state, visited, initial_state, target_location):
    """
    This function recursively searches backward from a target location, evaluation all possible variable values
    in the target location
    """
    # TODO: This function gets tricky if edges come from multiple different locations into another
    # This would represent a case where both edges can result in reaching the location, and the guards
    # and probabilities are not mutually exclusive, which is what this function currently assumes.
    # It could be tricky to fix this, so it hasn't been attempted yet.


    if location in visited:
        # The incoming state is the default value of the variables.
        # We recurse backwards through the edges until we hit locations we have already seen.
        # Then we start with the incoming state and build the variable values as the recursion is unwound
        return [incoming_state]
    else:
        new_visited = set(visited)
        new_visited.add(location)

    if location in back_edges:
        final_vals = list()
        i = 0
        for edge in back_edges[location]: 

            skip_edges = False
            for destination in edge.destinations:      
                dest = edge.location

                # TODO: For now we skip edges that go back to the initial state as they tend
                # to be duplicates of other existing edges. 
                if dest == initial_state:
                    continue
                
                # Currently edges back to the target location are skipped because these are the 
                # edges for which we are trying to determine the var values in the first place
                if dest == target_location:
                    final_vals.extend([incoming_state])
                    ## TODO: Made the assumption to skip other edges here, this only holds 
                    # if they all go back to the target location instead of just one edge doing it.
                    skip_edges = True
                    continue
                
                # Recurse down each path all the way first before doing the evaluations.
                # This allows the current variable values to be accesible when evaluating the proper
                # guards that should be considered true
                backwards_vals = evaluate_possibilities(dest, back_edges, incoming_state, new_visited, initial_state, target_location)

                # For each possible set of variable values
                for val in backwards_vals:            
                    var_state = VariableState(val)


                    ## TODO: This check guard function doesn't work in a lot of cases:
                    # 1. If the variables haven't been fully evaluated yet, it may not return false when expected,
                    # resulting in possilby multiple guards being considered as true when in reality only one can
                    # 2. If a target variable is compared to an evaluated variable, we can't say anything about the truth
                    # value of the guard. So they will all be considered true, which is faulty behavior at this point 
                    if check_guard(var_state.var_values, edge.guard):

                        # Apply this set of assignments to the variable values, along with the proper probability update
                        var_state.var_values = substitute_vals(var_state.var_values, destination)
                        var_state.compound_probability(destination.probability)
                        final_vals.extend([var_state])
                        
                    
            # Used to skip remaining edges
            if skip_edges:
                break

        return final_vals

    else:
        # There are no backward edges, must be a base location
        return [incoming_state]


## TODO: eval is a bad function to use, but it is needed here because I have to do string manipulation
## and then get it back to the momba datatype. If there is another way, that'd be great. For now, user input shouldn't
## be able to make it into the eval function in any way, so it may be safe.
def substitute_vals(var_values, destination, swap_pattern=re.compile(r":[^:]*>,", re.IGNORECASE)):
    new_var_values = dict(var_values)
    for assignment in destination.assignments:
        for var in new_var_values:
            temp = str(new_var_values[var])
            # When the conversion to string occurs, some extra stuff is added that doesn't
            # let it convert back into the proper datatype, so we have to remove it
            temp = temp.replace(str(assignment.target), str(assignment.value))
            temp = swap_pattern.sub(",", temp)
            temp = temp.replace('<', '')
            new_var_values[var] = eval(temp)  
    return new_var_values

def check_guard(values, guard, swap_pattern=re.compile(r":[^:]*>,", re.IGNORECASE)):
    guard = str(guard)

    # Swap out variables used in the guard for the values we know they are at this point
    for var in values:
        value = str(values[var])
        guard = guard.replace(str(var), str(value))
        guard = swap_pattern.sub(",", guard)
        guard = guard.replace('<', '')
    guard = eval(guard)


    # TODO: fold_constants needs to handle all different types of expressions, currently it only does some
    evaluated_guard = fold_constants(guard)

    # Check if the guard was able to be determined to be false
    if str(evaluated_guard) ==  'Value(value=False)':
        return False
    else:   
        return True





            

