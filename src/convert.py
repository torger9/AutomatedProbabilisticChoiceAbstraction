

from momba import jani
from momba import model as momba_model
import sys
from backEdgesTargetLocations import add_backedges_find_target_loc
from Dependancies import get_location_dependancies
from CheckRemovals import evaluate_possibilities
from VariableState import VariableState
from NewModel import make_new_model

original_file = sys.argv[1]
new_file = sys.argv[2]

network = None
model = None
target_vars = [momba_model.expressions.Name('z')]
important_vars = [momba_model.expressions.Name('clk')]
with open(original_file, encoding='utf-8-sig') as jani_file:
    jani_string = jani_file.read()

    ## Here I assume only one instance in the JANI model
    network = jani.load_model(jani_string)
    model = network.instances.pop().automaton




if (len(model.initial_locations) > 1):
    print("Can't do multiple initial states yet")
    sys.exit(1)

## This is a hacky way to set the initial state variable without popping it out of the set
for init_state in model.initial_locations:
    initial_state = init_state 

# other_vars are all non-target or important vars
back_edges, target_locs, other_vars = add_backedges_find_target_loc(model, target_vars, initial_state)
other_vars.difference_update(target_vars + important_vars)
#for back in back_edges:
#    print(f"Source {back}")
#    for edge in back_edges[back]:
#        print(f"Dest {edge.location}")
print(f"Target Locations: {target_locs}")
for target in target_locs:
    
    #dependancies = get_location_dependancies(model, target, target_vars)
    #dependancies.difference_update(target_vars + important_vars)
    

    var_values = dict()
    for var in other_vars:
        var_values[var] = var
    #print(f"Original: {var_values}\n\n")
    print(var_values)
    var_state = VariableState(var_values, 1, None)
    final_vals = evaluate_possibilities(target, back_edges, var_values, set(), initial_state, target) 
    #for val in final_vals:
    #    print(val, '\n')
    cannot_remove_set = set()
    for val in final_vals:
        cannot_remove_set.update(val.cannot_resolve_set())
    
    for var in cannot_remove_set:
        for val in final_vals:
            val.remove_var(var)

    cannot_remove_set.update(target_vars)
    cannot_remove_set.update(important_vars)
    print(cannot_remove_set)
 

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

#Only works with 1 target state for now
new_model = make_new_model(model, new_context, initial_state, target_locs.pop(), final_vals, cannot_remove_set)
new_model.scope = momba_model.context.Scope(new_context, new_context.global_scope)




new_jani_string = jani.dump_model(new_network)

new_jani_string = new_jani_string.replace('"elements": []', '"elements": [{"automaton": "Abstracted"}]')
new_jani_string = new_jani_string.replace('"initial-locations": []', f'"initial-locations": [ "{new_model.initial_locations.pop().name}" ]')
syncs = '{"synchronise": [ "tick" ],"result": "tick"}'
new_jani_string = new_jani_string.replace('"syncs": []', f'"syncs": [ {syncs} ]')


with open(new_file, 'w') as new_file:
    new_file.write(new_jani_string)





