import re
import sys

from foldConstants import fold_constants

from momba import jani
from momba import model as momba_model
from momba.model.expressions import *
from momba.model.operators import *
from momba.model.operators import ArithmeticBinaryOperator
from momba.model.expressions import ArithmeticBinary
from momba.engine.values import Value

from VariableState import VariableState





def make_new_model(model, context, initial_state, target_state, removable_vars_evaluated, cannot_remove_set):
    new_model = context.create_automaton(name="Abstracted")
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
            for i,d in enumerate(new_destinations):
                if d.location == destination.location and frozenset(needed_assignments) == d.assignments:
                    merged = True
                    new_prob = ArithmeticBinary(ArithmeticBinaryOperator.ADD, d.probability, destination.probability)
                    new_destinations[i] = momba_model.Destination(d.location, new_prob, d.assignments)
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
    for possibility in removable_vars_evaluated:
        for edge in edge_set:
            new_destinations = list()
            for destination in edge.destinations: 
                needed_assignments = set()
                for assignment in destination.assignments:
                    if assignment.target in possibility.var_values:
                        needed_assignments.add(momba_model.Assignment(assignment.target, removable_vars_evaluated[assignment.target], assignment.index))
                    else:
                        needed_assignments.add(assignment)

                merged = False
                for i,d in enumerate(new_destinations):
                    if d.location == destination.location and frozenset(needed_assignments) == d.assignments:
                        merged = True
                        new_prob = ArithmeticBinary(ArithmeticBinaryOperator.ADD, d.probability, destination.probability)
                        new_destinations[i] = momba_model.Destination(d.location, new_prob, d.assignments)
                        break

                if not merged:
                    
                    new_destinations.append( momba_model.Destination(destination.location, (ArithmeticBinary(ArithmeticBinaryOperator.MUL, destination.probability, possibility.probability) if destination.probability else possibility.probability) , frozenset(needed_assignments)))

            new_guard = evaluate_guard(edge.guard, possibility)
            edge_merged = False
            for e in new_edges:
                if fold_constants(new_guard) == fold_constants(e.guard):
                    edge_merged = True
                    new_edges.remove(e)
                    new_edges.add(momba_model.Edge(e.location, merge_destinations(new_destinations, list(e.destinations)), e.action_pattern, e.guard, e.rate, e.annotation, e.observation))
                    break
            if not edge_merged:
                new_edge = momba_model.Edge(edge.location, frozenset(new_destinations), edge.action_pattern, new_guard, edge.rate, edge.annotation, edge.observation)
                new_edges.add(new_edge)
    return merge_edges(new_edges, cannot_remove_set)

def evaluate_guard(guard, removable_vars_evaluated, swap_pattern=re.compile(r":[^:]*>,", re.IGNORECASE)):
    string_guard = str(guard)
    for var in removable_vars_evaluated.var_values:
        string_guard = string_guard.replace(str(var), str(removable_vars_evaluated.var_values[var]))


    string_guard = swap_pattern.sub(",", string_guard)
    string_guard = string_guard.replace('<', '')
    return eval(string_guard)


def merge_destinations(destinations1, destinations2):

    for dest2 in destinations2:
        merged = False
        for i, dest1 in enumerate(destinations1):
            if dest1.assignments == dest2.assignments:
                #print(f"Probabilities {dest1.probability}, {dest2.probability}")
                destinations1[i] = momba_model.Destination(dest1.location, ArithmeticBinary(ArithmeticBinaryOperator.ADD, dest1.probability, dest2.probability) , dest1.assignments)
                merged = True
                break
        if not merged:
            destinations1.append(dest2)
            
    return frozenset(destinations1)

