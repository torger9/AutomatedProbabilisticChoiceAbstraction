from momba import model as momba_model
from momba.model.expressions import ArithmeticBinary
from momba.model.expressions import IntegerConstant
from momba.model.operators import BooleanOperator
from momba.model.operators import ArithmeticBinaryOperator


class VariableState:

    def __init__(self, var_values, probability=IntegerConstant(integer=1), guard=None):
        if isinstance(var_values, VariableState):
            var_state = var_values
            self.var_values = dict(var_state.var_values)
            self.probability = var_state.probability
            self.guard = var_state.guard

        else:
            self.var_values = var_values
            self.probability = probability
            self.guard = guard
        

    def compound_probability(self, prob):
        if self.probability == IntegerConstant(integer=1) or self.probability == None:
            self.probability = prob
        elif prob == None:
            return
        else:
            self.probability = ArithmeticBinary(ArithmeticBinaryOperator.MUL, self.probability, prob)

    def conjuct_guard(self, guard):
        if self.guard == None:
            self.guard = guard
        else:   
            self.guard = ArithmeticBinary(BooleanOperator.AND, guard, self.guard)

    ## Needs to be updated to work with guards
    def completely_resolved(self):
        for var in self.var_values:
            if not self.is_fully_evaluated(var, self.var_values[var]):
                return False

        return True

    ## This needs to be updated to work with the guard variables as well
    def is_fully_evaluated(self, target, expression):
        if len(expression.used_names) > 0:
            return False

        return True

    #This needs to be updated for a guard
    def cannot_resolve_set(self):
        no_resolve_set = set()
        for var in self.var_values:
            if not self.is_fully_evaluated(var, self.var_values[var]):
                no_resolve_set.add(var)

        return no_resolve_set

    def remove_var(self, var):
        self.var_values.pop(var, None)

    def is_in(self, var):
        return var in self.var_values

    def __repr__(self):
        return f"Variable values: {self.var_values}\nProbability: {self.probability}\nGuard: {self.guard}\n"

