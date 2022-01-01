from momba import model as momba_model
from momba.model.expressions import ArithmeticBinary
from momba.model.expressions import IntegerConstant
from momba.model.operators import BooleanOperator
from momba.model.operators import ArithmeticBinaryOperator


class VariableState:
    """
    This class is used to keep track of information about a particular set of
    variable possibilities.
    """

    def __init__(self, var_values, probability=IntegerConstant(integer=1), guard=None):
        # If a VariableState object is passed, make a copy of it, but not referencing the original value
        # dictionary
        if isinstance(var_values, VariableState):
            var_state = var_values
            self.var_values = dict(var_state.var_values)
            self.probability = var_state.probability
            self.guard = var_state.guard

        else:
            self.var_values = var_values
            self.probability = probability
            self.guard = guard
        

    # Take the current probability of this set of values and multiply it by a new probability
    def compound_probability(self, prob):
        if self.probability == IntegerConstant(integer=1) or self.probability == None:
            self.probability = prob
        elif prob == None:
            return
        else:
            self.probability = ArithmeticBinary(ArithmeticBinaryOperator.MUL, self.probability, prob)

    

    ## Returns true if all variables have a value that does not include other variables
    def completely_resolved(self):
        for var in self.var_values:
            if not self.is_fully_evaluated(self.var_values[var]):
                return False

        return True

    ## This determines if an expressions still contains unresolved variables or not
    def is_fully_evaluated(self, expression):
        if len(expression.used_names) > 0:
            return False

        return True

    # Returns the set of variable that haven't been completely resolved
    def cannot_resolve_set(self):
        cannot_resolve = set()
        for var in self.var_values:
            if not self.is_fully_evaluated(var, self.var_values[var]):
                cannot_resolve.add(var)

        return cannot_resolve

    # This would simply and the old and new guard. I used this in an old implementation,
    # still not sure if it will be needed in the final version
    def conjuct_guard(self, guard):
        if self.guard == None:
            self.guard = guard
        else:   
            self.guard = ArithmeticBinary(BooleanOperator.AND, guard, self.guard)


    def remove_var(self, var):
        self.var_values.pop(var, None)
    
    def is_in(self, var):
        return var in self.var_values

    def __repr__(self):
        return f"Variable values: {self.var_values}\nProbability: {self.probability}\nGuard: {self.guard}\n"

