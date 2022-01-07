

from momba import jani
from momba import model as momba_model
import sys
from ModelInfo import model_info
from Dependancies import get_location_dependancies
from CheckRemovals import evaluate_possibilities
from VariableState import VariableState
from NewModel import make_new_model

def usage():

    print("Usage:")
    print("python convert.py /path/to/original/jani/file /path/for/converted/jani")

if len(sys.argv) < 3:
    print("You did not provide the proper number of file names")
    usage()

original_file = sys.argv[1]
new_file = sys.argv[2]

# Initialize some variables
network = None
model = None

# TODO: Make it so the target/important variables can be chosen by the user instead of hardcoded
target_vars = [momba_model.expressions.Name('optimalRuns')]
important_vars = [momba_model.expressions.Name('clk')]

## Load the automatan from the jani file
with open(original_file, encoding='utf-8-sig') as jani_file:
    jani_string = jani_file.read()

    ## Here I assume only one instance in the JANI model
    network = jani.load_model(jani_string)
    model = network.instances.pop().automaton

# TODO: Can multiple initial states work at all?
if (len(model.initial_locations) > 1):
    print("Can't do multiple initial states yet")
    sys.exit(1)

## This is a hacky way to set the initial state variable without popping it out of the set
## We don't want to pop it because we want to preserve the integrity of the model variable
for init_state in model.initial_locations:
    initial_state = init_state 

# Get the necessary info about the model
back_edges, target_locs, all_vars = model_info(model, target_vars, initial_state)


## other_vars is the set of variables that aren't target or other important vars
all_vars.difference_update(target_vars + important_vars)
other_vars = all_vars


# This dictionary maps a target location to the distribution of 
# variable values at that particular location
final_vals_map = dict()

cannot_remove_set = set()
for i, target in enumerate(target_locs):
    print(f"{i} of {len(target_locs)}")
    # TODO: I wrote this code to find dependancies. I think in the future we will need to use
    # it to better determine which variables can actually be removed. For now it isn't used the way
    # I have currently written the code.
    #dependancies = get_location_dependancies(model, target, target_vars)
    #dependancies.difference_update(target_vars + important_vars)
    
    # This dictionary keeps track of the value (or distribution of values) of all 
    # variables at this target location. Each variable is initialized to itself,
    # i.e. Name(identifier= 'x') = Name(identifier= 'x')
    var_values = dict()
    for var in other_vars:
        var_values[var] = var


    # Final_vals is a list of all the possible values (a distribution) the variables
    # could be at this location, with their associated probability
    location_value_map = dict()
    #print("Evaluating possibilities")
    final_vals = evaluate_possibilities(target, back_edges, VariableState(var_values), set(), initial_state, target, location_value_map) 
    print(final_vals)
    ## Any variables that we can't fully resolve (for any of the possiblities)
    ## can't be removed from the model as part of the abstraction

    for val in final_vals:
        cannot_remove_set.update(val.cannot_resolve_set())
    
    


    # Store this set of possibilities
    final_vals_map[target] = final_vals


cannot_remove_set.update(target_vars)
cannot_remove_set.update(important_vars)

for target in final_vals_map:
    for var in cannot_remove_set:
            for val in final_vals_map[target]:
                val.remove_var(var)

 
## Do the setup for creating a new model
new_context = momba_model.context.Context(momba_model.context.ModelType.DTMC)
new_context.global_scope = model.scope.parent
new_context.global_scope.ctx = new_context

for action in model.ctx.action_types:
    action = model.ctx.get_action_type_by_name(action)
    new_context.create_action_type(action.label, parameters=action.parameters)

for property in model.ctx.properties:
    property = model.ctx.get_property_definition_by_name(property)
    new_context.define_property(property.name, expression= property.expression)

new_network = new_context.create_network(name="Abstracted")

# This function actually builds the new model, eliminating variables we previously
# found to be unnecessary, and using the values we evaluated for them to preserve target 
# variable behavior
new_model = make_new_model(model, new_context, initial_state, target_locs, final_vals_map, cannot_remove_set)

## Set the variable scope
new_model.scope = momba_model.context.Scope(new_context, new_context.global_scope)


# Dump the model to a jani string 
new_jani_string = jani.dump_model(new_network)
# TODO: I had to add all these replace functions for things tow work right. 
# I would greatly prefer to get all these elements correct in the actual automata object rather than messing with the strings,
# but I don't know how at this point
new_jani_string = new_jani_string.replace('"elements": []', '"elements": [{"automaton": "Abstracted"}]')
new_jani_string = new_jani_string.replace('"initial-locations": []', f'"initial-locations": [ "{new_model.initial_locations.pop().name}" ]')

# TODO: Currently the 'tick' synchronization is hard-coded, so nothing else would work
syncs = '{"synchronise": [ "tick" ],"result": "tick"}'
new_jani_string = new_jani_string.replace('"syncs": []', f'"syncs": [ {syncs} ]')

# Export the jani to a file
with open(new_file, 'w') as new_file:
    new_file.write(new_jani_string)





