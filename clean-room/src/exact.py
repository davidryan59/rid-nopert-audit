"""Exact arithmetic in Q(sqrt(5)).

This module follows Article Section 5.1.  It has no dependency on the
upstream implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any


def parse_fraction(value: Any) -> Fraction:
    """Parse the deliberately small rational syntax used by this checker."""
    if isinstance(value, bool):
        raise ValueError("booleans are not rationals")
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str) or not value:
        raise ValueError(f"expected an integer or rational string, got {value!r}")
    if value.strip() != value:
        raise ValueError("rational strings may not contain surrounding whitespace")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(f"invalid rational {value!r}") from error
    # Fraction accepts decimal strings.  The proof-data syntax observed in the
    # permitted files uses only signed integers and one optional slash.
    pieces = value.split("/")
    if len(pieces) > 2 or any(not piece for piece in pieces):
        raise ValueError(f"invalid rational grammar {value!r}")
    for position, piece in enumerate(pieces):
        signed = position == 0
        digits = piece[1:] if signed and piece[:1] in "+-" else piece
        if not digits.isdigit():
            raise ValueError(f"invalid rational grammar {value!r}")
    return result


def _coerce(value: Q5 | Fraction | int) -> Q5:
    if isinstance(value, Q5):
        return value
    if isinstance(value, (Fraction, int)) and not isinstance(value, bool):
        return Q5(Fraction(value), Fraction(0))
    return NotImplemented


@dataclass(frozen=True)
class Q5:
    """The exact number a + b*sqrt(5), with rational a and b."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "a", Fraction(self.a))
        object.__setattr__(self, "b", Fraction(self.b))

    @classmethod
    def from_json(cls, value: Any) -> Q5:
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError("a Q(sqrt(5)) value must be a two-element array")
        return cls(parse_fraction(value[0]), parse_fraction(value[1]))

    @classmethod
    def rational(cls, value: Fraction | int) -> Q5:
        return cls(Fraction(value), Fraction(0))

    def to_json(self) -> list[str]:
        return [_fraction_text(self.a), _fraction_text(self.b)]

    def __add__(self, other: Q5 | Fraction | int) -> Q5:
        other_q5 = _coerce(other)
        if other_q5 is NotImplemented:
            return NotImplemented
        return Q5(self.a + other_q5.a, self.b + other_q5.b)

    __radd__ = __add__

    def __neg__(self) -> Q5:
        return Q5(-self.a, -self.b)

    def __sub__(self, other: Q5 | Fraction | int) -> Q5:
        other_q5 = _coerce(other)
        if other_q5 is NotImplemented:
            return NotImplemented
        return self + (-other_q5)

    def __rsub__(self, other: Q5 | Fraction | int) -> Q5:
        other_q5 = _coerce(other)
        if other_q5 is NotImplemented:
            return NotImplemented
        return other_q5 - self

    def __mul__(self, other: Q5 | Fraction | int) -> Q5:
        other_q5 = _coerce(other)
        if other_q5 is NotImplemented:
            return NotImplemented
        return Q5(
            self.a * other_q5.a + 5 * self.b * other_q5.b,
            self.a * other_q5.b + self.b * other_q5.a,
        )

    __rmul__ = __mul__

    def reciprocal(self) -> Q5:
        if self.is_zero():
            raise ZeroDivisionError("division by zero in Q(sqrt(5))")
        denominator = self.a * self.a - 5 * self.b * self.b
        # Irrationality of sqrt(5) makes this nonzero for a nonzero pair.
        if denominator == 0:
            raise ArithmeticError("impossible rational square root of 5")
        return Q5(self.a / denominator, -self.b / denominator)

    def __truediv__(self, other: Q5 | Fraction | int) -> Q5:
        other_q5 = _coerce(other)
        if other_q5 is NotImplemented:
            return NotImplemented
        return self * other_q5.reciprocal()

    def __rtruediv__(self, other: Q5 | Fraction | int) -> Q5:
        other_q5 = _coerce(other)
        if other_q5 is NotImplemented:
            return NotImplemented
        return other_q5 / self

    def __pow__(self, exponent: int) -> Q5:
        if not isinstance(exponent, int):
            return NotImplemented
        if exponent < 0:
            return (self.reciprocal()) ** (-exponent)
        result = Q5.rational(1)
        base = self
        power = exponent
        while power:
            if power & 1:
                result *= base
            base *= base
            power //= 2
        return result

    def is_zero(self) -> bool:
        return self.a == 0 and self.b == 0

    def sign(self) -> int:
        """Return -1, 0, or 1 without floating point."""
        if self.a == 0:
            return _rational_sign(self.b)
        if self.b == 0:
            return _rational_sign(self.a)
        sign_a = _rational_sign(self.a)
        sign_b = _rational_sign(self.b)
        if sign_a == sign_b:
            return sign_a
        square_comparison = self.a * self.a - 5 * self.b * self.b
        if square_comparison == 0:
            raise ArithmeticError("impossible rational cancellation with sqrt(5)")
        return sign_a * _rational_sign(square_comparison)

    def __lt__(self, other: Q5 | Fraction | int) -> bool:
        other_q5 = _coerce(other)
        if other_q5 is NotImplemented:
            return NotImplemented
        return (self - other_q5).sign() < 0

    def __le__(self, other: Q5 | Fraction | int) -> bool:
        other_q5 = _coerce(other)
        if other_q5 is NotImplemented:
            return NotImplemented
        return (self - other_q5).sign() <= 0

    def __gt__(self, other: Q5 | Fraction | int) -> bool:
        other_q5 = _coerce(other)
        if other_q5 is NotImplemented:
            return NotImplemented
        return (self - other_q5).sign() > 0

    def __ge__(self, other: Q5 | Fraction | int) -> bool:
        other_q5 = _coerce(other)
        if other_q5 is NotImplemented:
            return NotImplemented
        return (self - other_q5).sign() >= 0

    def __bool__(self) -> bool:
        return not self.is_zero()


ZERO = Q5.rational(0)
ONE = Q5.rational(1)
SQRT5 = Q5(Fraction(0), Fraction(1))


def _rational_sign(value: Fraction) -> int:
    return (value > 0) - (value < 0)


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"
