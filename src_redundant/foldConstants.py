import dataclasses as d
import typing as t

import functools
from momba import model as momba_model

## This code was given by the momba creators as an example of contant folding, I am not entirely sure
## how it works
## TODO: It needs to work for all expression types. Right now it doesn't even work for 
## equality, only comparison

@d.dataclass(frozen=True)
class Value:
    value: t.Union[int, float, bool]


@functools.singledispatch
def fold_constants(expr: momba_model.Expression) -> t.Union[momba_model.Expression, Value]:
    # TODO: it would be nice to have a general API to
    # recursively fold over the AST of expressions
    return expr


@fold_constants.register
def _fold_boolean(
    expr: momba_model.expressions.BooleanConstant,
) -> t.Union[momba_model.Expression, Value]:
    return Value(expr.boolean)


@fold_constants.register
def _fold_integer(
    expr: momba_model.expressions.IntegerConstant,
) -> t.Union[momba_model.Expression, Value]:
    return Value(expr.integer)


@fold_constants.register
def _fold_real(
    expr: momba_model.expressions.RealConstant,
) -> t.Union[momba_model.Expression, Value]:
    return Value(expr.integer)


@fold_constants.register
def _fold_comparison(
    expr: momba_model.expressions.Comparison,
) -> t.Union[momba_model.Expression, Value]:
    left = fold_constants(expr.left)
    right = fold_constants(expr.right)
    if isinstance(left, Value) and isinstance(right, Value):
        # TODO: this should throw a proper exception
        assert not isinstance(left.value, bool) and not isinstance(
            right.value, bool
        ), "comparison is not defined for boolean values"
        return Value(expr.operator.native_function(left.value, right.value))
    return momba_model.expressions.Comparison(expr.operator, left, right)


def _shortcircuit_commutative_ops(
    expr: momba_model.expressions.Boolean, value: bool, other: momba_model.Expression
) -> t.Union[momba_model.Expression, Value]:
    if expr.operator is momba_model.operators.BooleanOperator.AND:
        if value:
            return other
        else:
            return Value(False)
    elif expr.operator is momba_model.operators.BooleanOperator.OR:
        if value:
            return Value(True)
        else:
            return other
    else:
        return expr


@fold_constants.register
def _fold_boolean(
    expr: momba_model.expressions.Boolean,
) -> t.Union[momba_model.Expression, Value]:
    left = fold_constants(expr.left)
    right = fold_constants(expr.right)
    if isinstance(left, Value) and isinstance(right, Value):
        # TODO: this should throw a proper exception
        assert isinstance(left.value, bool) and isinstance(
            right.value, bool
        ), "boolean operator is not defined for non-boolean values"
        return Value(expr.operator.native_function(left.value, right.value))
    elif isinstance(left, Value):
        # TODO: this should throw a proper exception
        assert isinstance(
            left.value, bool
        ), "boolean operator is not defined for non-boolean values"
        return _shortcircuit_commutative_ops(expr, left.value, right)
    elif isinstance(right, Value):
        # TODO: this should throw a proper exception
        assert isinstance(
            right.value, bool
        ), "boolean operator is not defined for non-boolean values"
        return _shortcircuit_commutative_ops(expr, right.value, left)
    return momba_model.expressions.Boolean(expr.operator, left, right)