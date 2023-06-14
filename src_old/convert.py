# Import necessary packages
from momba import jani
from momba import model as momba_model
import sys
from ModelInfo import model_info
from Dependancies import get_location_dependancies
from CheckRemovals import evaluate_possibilities
from VariableState import VariableState
from NewModel import make_new_model
from guppy import hpy

# Open work and data files
workfile = open( 'workfile.txt', 'w', encoding = 'utf-8')
datafile = open( 'datafile.txt', 'w', encoding = 'utf-8')

# Desigate -i option for interactive mode
interactive_mode = (sys.argv[1] == '-i')

# Define proper function call
def usage(interactive_mode):
    print("\tUsage:")
    print("\tpython convert.py [-i] /path/to/original/jani/file /path/for/converted/jani")
    workfile.write("\tUsage:")
    workfile.write("\tpython convert.py [-i] /path/to/original/jani/file /path/for/converted/jani")

# Enforce proper call of convert.py
if interactive_mode:
    if len(sys.argv) < 4:
        print("\tYou did not provide the proper number of file names")
        workfile.write("\tYou did not provide the proper number of file names\n")
        usage(interactive_mode)
        sys.exit(1)
else:
    if len(sys.argv) < 3:
        print("\tYou did not provide the proper number of file names")
        workfile.write("\tYou did not provide the proper number of file names\n")
        usage(interactive_mode)
        sys.exit(1)


################################################################################
# Initialize some variables
if interactive_mode:
    original_file = sys.argv[2]
    new_file = sys.argv[3]
    print("Initializing...\n\tReading from " + sys.argv[2] + "\n\tWriting to " + sys.argv[3] + "\n")
    workfile.write("Initializing...\n\tReading from " + sys.argv[2] + "\n\tWriting to " + sys.argv[3] + "\n\n")
else:
    original_file = sys.argv[1]
    new_file = sys.argv[2]
    print("Initializing...\n\tReading from " + sys.argv[1] + "\n\tWriting to " + sys.argv[2] + "\n")
    workfile.write("Initializing...\n\tReading from " + sys.argv[1] + "\n\tWriting to " + sys.argv[2] + "\n\n")

network = None
model = None
target_vars = list()
important_vars = list()

# Collect list of target and important varialbes
# For interactive mode, variables are input at runtime
# for non-interactive mode, hardcode variables in "else" below
if interactive_mode:
    check = (input("\tAdd a target varialbe?: ").lower().startswith('y'))
    while check:
        target_vars.append(momba_model.expressions.Name(input("\t    name: ")))
        check = (input("\tAdd another varialbe?: ").lower().startswith('y'))
    check = (input("\tAdd an important varialbe?: ").lower().startswith('y'))
    while check:
        important_vars.append(momba_model.expressions.Name(input("\t    name: ")))
        check = (input("\tAdd another varialbe?: ").lower().startswith('y'))
    print("")
    workfile.write("\n")
else: 
    target_vars = [momba_model.expressions.Name('z')]
#    target_vars = [momba_model.expressions.Name('optimalRuns')]
    important_vars = [momba_model.expressions.Name('clk')]

print(f'\tTarget variables: {target_vars}')
workfile.write(f'\tTarget variables: {target_vars} {type(target_vars)}\n')
print(f'\tImportant variables: {important_vars}\n')
workfile.write(f'\tImportant variables: {important_vars}\n\n')

# Load the automatan from the jani file
with open(original_file, encoding='utf-8-sig') as jani_file:
    jani_string = jani_file.read()
    # The assumption is the network contains a single automaton
    network = jani.load_model(jani_string)
    model = network.instances.pop().automaton

# Enforce existance of a single initial state
# TODO: Can multiple initial states work at all?
if (len(model.initial_locations) > 1):
    print("Can't do multiple initial states yet")
    sys.exit(1)

# Obtain initial state from model
# To preserve model integrity, initial state should not be popped
for init_state in model.initial_locations:
    initial_state = init_state 
print(f'\tInitial state: {init_state}\n')
workfile.write(f'\tInitial state: {init_state}\n\n')

print("\tInitialization complete\n")
workfile.write("\tInitialization complete\n\n")


################################################################################
# Find target locations, variables, and back edges of model 
#back_edges, target_locs, all_vars = model_info(model, target_vars, initial_state, workfile)
back_edges, target_locs, all_vars = model_info(model, target_vars, initial_state, workfile)

# Other_vars is the set of variables that aren't target or other important vars
all_vars.difference_update(target_vars + important_vars)
other_vars = all_vars

# Dictionary maps each target location to its distributions of variable values
# key: target location, value: list(VariableState objects) *SET*
final_vals_map = dict()


cannot_remove_set = set()
for i, target in enumerate(target_locs):
    print(f"Target location {i+1} of {len(target_locs)}")
    workfile.write(f"Target location {i+1} of {len(target_locs)}\n")
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
    
    print("Evaluating possibilities...")
    workfile.write("Evaluating possibilities...\n")
    location_value_map = dict()
    
    heapobj = hpy()
    heapobj.setref()
    initialheap = heapobj.heap()
    final_vals = evaluate_possibilities(target, back_edges, VariableState(var_values), set(), initial_state, target, location_value_map, 0, workfile, datafile, set(), initialheap, heapobj)
    #final_vals = evaluate_possibilities(target, back_edges, VariableState(var_values), set(), initial_state, target, location_value_map) 

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
with open(new_file, 'w', encoding='utf-8-sig') as new_file:
    new_file.write(new_jani_string)
