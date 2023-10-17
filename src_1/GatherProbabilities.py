import sys
import re
from NewModel import evaluate_edges
from foldConstants import fold_constants
from momba import model as momba_model
from momba.model.expressions import *
from momba.model.operators import *
from VariableState import VariableState

#from guppy import hpy
#h = hpy()

def gather_probabilities (current_loc, target_loc, initial_loc, back_edges, path, possibilities, null_state, critical_vars, depth):
##########################################################################
#   begin at target location
#   for each path leading to the base location
#       find probability of path and assignment to target variable
#       combine duplicates and cumulate probability
#
#   current_loc     (current location)
#   target_loc      (target location)
#   initial_loc     (initial location)
#   back_edges      (dictionary of backward edges for each location)
#   path            (traced path from target location to initial location)
#   possibilities   (list of possible variable states and the probability)
#   null_state      (initial state of variables)
#   critical_vars   (target or important variables)
#   depth           (depth of recursion)
##########################################################################
    verbose = True
    debug = True
    
    #recursively layered indent
    indent = ''
    for i in range(depth + 1):
        indent = indent + '\t\t'
        
    if verbose: print(f'\n{indent}Recursion depth: {depth}')
    if debug: print(f'{indent}Current Location ({current_loc.name}): Back edges ({len(back_edges[current_loc])})\n{indent}Edge list:')
    for i, edge in enumerate(back_edges[current_loc]):
        previous_loc = edge.location
        if debug: print(f'{indent}\tEdge {i+1}: ({previous_loc.name}) --> ({current_loc.name})')

    # Ensure location to be explored has an origin in the model
    if current_loc in back_edges:

        # Depth first search through edges and destinations
        for i, edge in enumerate(back_edges[current_loc]):
            # Obtain previous location (next step from current to initial)
            # Accumulate path edge and destination for later use
            previous_loc = edge.location
            if debug: print(f'\n\t{indent}Edge {i+1}: ({previous_loc.name}) --> ({current_loc.name}) ({len(edge.destinations)} attached destinations)\n{indent}\tGuard {edge.guard}\n\t{indent}Destination list:')
            
            for j, destination in enumerate(edge.destinations):
                # Initial location has been reached, trace path from initial
                #   to target and accumulate variable states and probability 
                if debug: print(f'\n{indent}\t\tDestination {j+1}: ({edge.location.name}) --> ({destination.location.name})')
                path.append((edge,destination))
                
                if previous_loc == initial_loc: 
                    if debug: print(f'{indent}\t\tReached initial location')
                
                    possibility = VariableState(null_state)
                    if debug: 
                        print(f'{indent}\t\t\tInitialized variable values: ', end='')
                        for val in possibility.var_values:
                            print(val,end=', ')
                        print('')
                    
                    # Path stored as a list of tuples (edge, destination)
                    #   edge = step[0], destination = step[1]
                    for step in reversed(path):
                        if check_guard(possibility.var_values, step[0].guard):
                            possibility.var_values = substitute_vals(possibility.var_values, step[1])
                            possibility.compound_probability(step[1].probability)
                        else:
                            possibility.compound_probability(momba_model.expressions.IntegerConstant(0))
                            continue        
                    #if debug: print(f'{indent}\t\t\tObtained probability of path: {possibility.probability}\n{indent}\t\t\tType: {type(possibility.probability)}')
                    if debug: print(f'{indent}\t\t\tObtained probability of path: {parse_probability_expression(possibility.probability)}')
                            
                    #Remove non-target or important variables from destination assignment
                    for assignment in path[0][1].assignments:
                        if assignment.target not in critical_vars:
                            possibility.remove_var(assignment.target)
                    
                    #Remove non-target or important variables from varialbe distribution
                    to_remove = list()
                    for var in possibility.var_values:
                        if var not in critical_vars:
                            to_remove.append(var)
                    for var in to_remove:
                        possibility.remove_var(var)
                    del to_remove
                            
                    if parse_probability_expression(possibility.probability) != 0:
                        print(f'{indent}\t\t\tPossibility possible')
                        repeat = False
                        for item in possibilities:
                            if possibility.var_values == item.var_values:
                                repeat = True
                                
                        if repeat is True:
                            print(f'{indent}\t\t\tFound repeat possibility')
                            item.probability = ArithmeticBinary(ArithmeticBinaryOperator.ADD, item.probability, possibility.probability)
                        else:
                            print(f'{indent}\t\t\tFound new possibility')
                            possibilities.append(possibility)

                    else:
                        print(f'{indent}\t\t\tPossibility impossible')
                    
                    # Pop last tuple off path before return to continue search
                    path.pop()
                    continue
                
                # Looped around to target location, ignore path and continue search
                elif previous_loc == target_loc:
                    if debug: print(f'{indent}\t\tLooped around target location')
                    path.pop()
                    continue
                  
                # Looped around to current location, ignore path and continue search
                elif previous_loc == current_loc:
                    if debug: print(f'{indent}\t\t\tLooped around current location')
                    path.pop()
                    continue    
                    
                # Have not reached an end point, continue search
                else:
                    gather_probabilities(previous_loc, target_loc, initial_loc, back_edges, path, possibilities, null_state, critical_vars, depth+1) 
            

    # Location has no origin, print error message and exit
    else:
        print("\n***************************************************"\
            + "*************\nModel Error: Indeterminent Probability"\
            + "\n\tnon-initial precurser location " + {current_loc.name}\
            + "has no originating location\n************************"\
            + "****************************************")
        exit()
    
    if len(path) > 0:
        path.pop()  
    return

def parse_probability_expression(expression):
    if hasattr(expression, 'left'):
        left = parse_probability_expression(expression.left)
    else:
        return expression.as_float
        #return get_integer_value(expression)
        
    if hasattr(expression, 'right'):
        right = parse_probability_expression(expression.right)
    else:
        return expression.as_float
        #return get_integer_value(expression)
      
    if expression.operator == ArithmeticBinaryOperator.MUL:
        return left*right
    elif expression.operator == ArithmeticBinaryOperator.REAL_DIV:
        return left/right
    elif expression.operator == ArithmeticBinaryOperator.REAL_ADD:
        return left+right
    elif expression.operator == ArithmeticBinaryOperator.REAL_SUB:
        return left-right

def substitute_vals(var_values, destination):
    new_var_values = var_values
    old_values = dict()
    for assignment in destination.assignments:
        if assignment.target in new_var_values:
            old_values[assignment.target] = var_values[assignment.target]
            new_var_values[assignment.target] = replace_values(assignment.value, old_values, var_values)
    return new_var_values

def check_guard(values, guard):

    guard = replace_values_guard(guard, values)

    # TODO: fold_constants needs to handle all different types of expressions, currently it only does some
    evaluated_guard = fold_constants(guard)

    # Check if the guard was able to be determined to be false
    if str(evaluated_guard) ==  'Value(value=False)':
        return False
    else:   
        return True

def replace_values(expression, old_values, var_values): 
    
    if hasattr(expression, 'left'):
        return type(expression)(operator=expression.operator, left=replace_values(expression.left, old_values, var_values), right=replace_values(expression.right, old_values, var_values)) 
    else:
        if expression in old_values:
            return old_values[expression]
        elif expression in var_values:
            return var_values[expression]
        return expression

def replace_values_guard(expression, assignments):
    if hasattr(expression, 'left'):
        return type(expression)(operator=expression.operator, left=replace_values_guard(expression.left, assignments), right=replace_values_guard(expression.right, assignments)) 
    else:
        if expression in assignments:
            return assignments[expression]
        return expression
