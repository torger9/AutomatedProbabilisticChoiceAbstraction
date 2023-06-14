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



def make_new_model(model, context, initial_state, target_states, removable_vars_evaluated, cannot_remove_set):
    """
    Creates a new automata based on an existing one, but with a set of unnecessary variables removed,
    using their known values to preserve behavior
    """

    #Setup
    new_model = context.create_automaton(name="Abstracted")
    new_model.locations.clear()
    new_model.initial_locations.clear()
    new_model.edges.clear()

    #Variables for breadth first search
    location_queue = list()
    location_queue.append(initial_state)
    visited = set()
    visited.add(initial_state)

    
    new_model.add_location(initial_state, initial=True)
    new_model.initial_locations.add(initial_state)

    while len(location_queue) > 0:
        curr_location = location_queue.pop()

        # If the location is a target state, we have to use the known values of the variables to preserve behavior
        if curr_location in target_states:
            new_edge_set = evaluate_edges(model.get_outgoing_edges(curr_location), removable_vars_evaluated[curr_location], cannot_remove_set)
        else:
        #If it isn't a target state, we just remove the variables entirely and merge any edges that end up being the same
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


# TODO: This completely ignores guards, just maintaining them. It needs to be adapted in the case that the guards use variables that will be removed
def merge_edges(edge_set, cannot_remove_set):
    new_edges = set()
    for edge in edge_set:
        new_destinations = list()
        for destination in edge.destinations: 
            needed_assignments = set()
            # Keep only assignments that modify the variables we are keeping
            for assignment in destination.assignments:
                if assignment.target in cannot_remove_set:
                    needed_assignments.add(assignment)

            merged = False
            for i,d in enumerate(new_destinations):
                # If this new destination now matches one we already created, we merge the two into one,
                # summing their probabilities when we do
                if d.location == destination.location and frozenset(needed_assignments) == d.assignments:
                    merged = True
                    new_prob = ArithmeticBinary(ArithmeticBinaryOperator.ADD, d.probability, destination.probability)
                    new_destinations[i] = momba_model.Destination(d.location, new_prob, d.assignments)
                    break

            if not merged:
                new_destinations.append(momba_model.Destination(destination.location, destination.probability, frozenset(needed_assignments)))

        new_edge = momba_model.Edge(edge.location, frozenset(new_destinations), edge.action_pattern, edge.guard, edge.rate, edge.annotation, edge.observation)
        new_edges.add(new_edge)

        #TODO might need to see if new edges need to be checked for merging like the destinations were

    return new_edges


            

#Needs to be modified to work with guards
def evaluate_edges(edge_set, removable_vars_evaluated, cannot_remove_set):
    new_edges = set()

    # This first portion is the same as the merging method
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

            ## Here we determine what the guard would be for this possiblity
            new_guard = evaluate_guard(edge.guard, possibility)
            edge_merged = False
            ## We then merge any edges with guards that become the same
            for e in new_edges:
                if fold_constants(new_guard) == fold_constants(e.guard):
                    edge_merged = True
                    new_edges.remove(e)
                    new_edges.add(momba_model.Edge(e.location, merge_destinations(new_destinations, list(e.destinations)), e.action_pattern, e.guard, e.rate, e.annotation, e.observation))
                    break
            if not edge_merged:
                new_edge = momba_model.Edge(edge.location, frozenset(new_destinations), edge.action_pattern, new_guard, edge.rate, edge.annotation, edge.observation)
                new_edges.add(new_edge)
    
    # We then make sure that the edges all get merged properly with the removed variables.
    return merge_edges(new_edges, cannot_remove_set)

## TODO: Remove eval here using the method from CheckRemoval.py
## Swap in known variable values in the guard
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
                destinations1[i] = momba_model.Destination(dest1.location, ArithmeticBinary(ArithmeticBinaryOperator.ADD, dest1.probability, dest2.probability) , dest1.assignments)
                merged = True
                break
        if not merged:
            destinations1.append(dest2)
            
    return frozenset(destinations1)

