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

def evaluate_possibilities(location, back_edges, incoming_state, visited, initial_state, target_location, location_value_map, depth, workfile, datafile, solved, initialheap, heapobj):
    """
    This function recursively searches backward from a target location, evaluation all possible variable values
    in the target location
    """
    # TODO: This function gets tricky if edges come from multiple different locations into another
    # This would represent a case where both edges can result in reaching the location, and the guards
    # and probabilities are not mutually exclusive, which is what this function currently assumes.
    # It could be tricky to fix this, so it hasn't been attempted yet.
    
    # TODO: Currently runs under teh assumption that destinations off any given edge all lead to the
    # same location.
    # Were destinations able to lead to different locations, the probability would need to be readjusted
    # considering the "dead" path

    # Print utilization at beginning of each call
    print(f'\tRecursion depth {depth}')
    print(f'\t\tLocations solved: {len(location_value_map)}')
    workfile.write(f'\tRecursion depth {depth}\n')
    workfile.write(f'\t\tLocations solved: {len(location_value_map)}\n')


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
                break

            if dest.name in location_value_map:
                backwards_vals = location_value_map[dest.name]
            else:
                # Recurse down each path all the way first before doing the evaluations.
                # This allows the current variable values to be accesible when evaluating the proper
                # guards that should be considered true
                backwards_vals = evaluate_possibilities(dest, back_edges, incoming_state, visited, initial_state, target_location, location_value_map, depth+1, workfile, datafile, solved, initialheap, heapobj)
                location_value_map[dest.name] = backwards_vals

                heapsnap = heapobj.heap()
                stats = heapsnap.diff(initialheap)
                datafile.write(f'{len(solved)}\t{heapsnap.size}\t{stats.size}\t{stats.count}\t{heapobj.heapu().size}\t')
                for row in range(0,len(heapsnap),1):
                    if row > 2:
                        break
                    datafile.write(f'{heapsnap[row].size}\t{heapsnap[row].kind}\t')
                if len(heapsnap) < 3:
                    datafile.write(f'{0}\tN\A\t')
                if len(heapsnap) < 2:
                    datafile.write(f'{0}\tN\A\t')
                if len(heapsnap) < 1:
                    datafile.write(f'{0}\tN\A\t')
                if len(stats) < 1:
                    datafile.write(f'{0}\tN\A\t')
                else:
                    datafile.write(f'{heapsnap[0].size}\t{heapsnap[0].kind}\t')
                datafile.write("\n")

                if location.name not in solved:
                    solved.add(location.name)
                    
                    # print memory usage data to workfile for review
                    workfile.write(f'\t{len(solved)} locations solved : \n')
                    workfile.write(f'\t\tHeap Size : {convertSize(heapsnap.size)}\n')
                    workfile.write('\t\t\tIndex Count     Size                  Object Name\n')
                    workfile.write('\t\t\t  N/A  N/A%10s%40s\n' % (convertSize(heapobj.iso(final_vals).size),'final_vals'))
                    #for row in list(heapsnap.stat.get_rows())[:5]:
                    #    workfile.write("%5d%5d%8d%30s\n" %(row.index, row.count, convertSize(row.size), row.name))
                    for n in range(0,len(heapsnap),1):
                        if n > 4:
                            break
                        workfile.write("\t\t\t%5d%5d%10s%400s\n" %(n, heapsnap[n].count, convertSize(heapsnap[n].size), heapsnap[n].kind))
                    
                    workfile.write('\n\t\tChanges to heap since initial call\n')
                    workfile.write(f'\t\t\tTotal objects created : {stats.count}\n')
                    workfile.write(f'\t\t\tTotal size difference : {convertSize(stats.size)}\n')
                    workfile.write(f'\t\t\tNumber of entries : {stats.numrows}\n')
                    workfile.write('\t\t\tIndex Count     Size                  Object Name\n')
                    for count, row in enumerate(stats.get_rows()):
                        if count > 4:
                            break
                        workfile.write("\t\t\t%5d%5d%10s%40s\n" %(row.index, row.count, convertSize(row.size), row.name))

                    workfile.write(f'\n\t\tUnaccessable memory: {convertSize(heapobj.heapu().size)}\n')
                del stats
                del heapsnap
                
                #print(backwards_vals)
                #print(f"{len(location_value_map)}/77 locations solved")
                #if len(location_value_map) > 42:
                #    print(h.heap())
                print(f'\tRecursion depth {depth}')
                print(f'\t\tLocations solved: {len(location_value_map)}')
                workfile.write(f'\tRecursion depth {depth}\n')
                workfile.write(f'\t\tLocations solved: {len(location_value_map)}\n')
            

            # For each possible set of variable values
            for val in backwards_vals:        
                ## TODO: This check guard function doesn't work in a lot of cases:
                # 1. If the variables haven't been fully evaluated yet, it may not return false when expected,
                # resulting in possilby multiple guards being considered as true when in reality only one can
                # 2. If a target variable is compared to an evaluated variable, we can't say anything about the truth
                # value of the guard. So they will all be considered true, which is faulty behavior at this point 
                if check_guard(val.var_values, edge.guard):
                    for destination in edge.destinations:
                        var_state = VariableState(val)
                        # Apply this set of assignments to the variable values, along with the proper probability update
                        var_state.var_values = substitute_vals(var_state.var_values, destination)
                        var_state.compound_probability(destination.probability)
                        final_vals.extend([var_state])
            del backwards_vals
        return final_vals

    else:
        # There are no backward edges, must be a base location
        return [incoming_state]

def convertSize(size):
    # placeholder
    size_string = "a"

    if size < 1024:
        size_string = "%.0f  B" %(size)
    elif (size >= 1024) and (size < (1024*1024)):
        size_string = "%.2f KB" %(size/1024)
    elif (size >= (1024*1024)) and (size < (1024*1024*1024)):
        size_string = "%.2f MB" %(size/(1024*1024)) 
    else:
        size_string = "%.2f GB" %(size/(1024*1024*1024))

    return size_string

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
    








            

