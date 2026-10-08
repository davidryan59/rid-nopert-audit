"""Small sparse multivariate polynomials over Q(sqrt(5))."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Iterable, Mapping, Sequence, Tuple

from exact import ONE, Q5, ZERO


Exponent = Tuple[int, ...]


class MonomialDivisionError(ValueError):
    pass


class Polynomial:
    """A sparse polynomial with a fixed number of variables."""

    def __init__(self, nvars: int, terms: Mapping[Exponent, Q5] | None = None):
        if not isinstance(nvars, int) or nvars < 0:
            raise ValueError("nvars must be a nonnegative integer")
        cleaned: dict[Exponent, Q5] = {}
        for exponent, coefficient in (terms or {}).items():
            if len(exponent) != nvars:
                raise ValueError("monomial has the wrong dimension")
            if any(not isinstance(value, int) or value < 0 for value in exponent):
                raise ValueError("monomial exponents must be nonnegative integers")
            q5 = coefficient if isinstance(coefficient, Q5) else Q5.rational(coefficient)
            if not q5.is_zero():
                cleaned[tuple(exponent)] = cleaned.get(tuple(exponent), ZERO) + q5
                if cleaned[tuple(exponent)].is_zero():
                    del cleaned[tuple(exponent)]
        self.nvars = nvars
        self._terms = cleaned

    @classmethod
    def zero(cls, nvars: int) -> Polynomial:
        return cls(nvars)

    @classmethod
    def constant(cls, nvars: int, coefficient: Q5 | Fraction | int) -> Polynomial:
        q5 = coefficient if isinstance(coefficient, Q5) else Q5.rational(coefficient)
        if q5.is_zero():
            return cls.zero(nvars)
        return cls(nvars, {(0,) * nvars: q5})

    @classmethod
    def variable(cls, nvars: int, index: int) -> Polynomial:
        if index < 0 or index >= nvars:
            raise IndexError("variable index outside polynomial dimension")
        exponent = [0] * nvars
        exponent[index] = 1
        return cls(nvars, {tuple(exponent): ONE})

    @property
    def terms(self) -> dict[Exponent, Q5]:
        return dict(self._terms)

    def is_zero(self) -> bool:
        return not self._terms

    def coefficient(self, exponent: Sequence[int]) -> Q5:
        return self._terms.get(tuple(exponent), ZERO)

    def degrees(self) -> tuple[int, ...]:
        if not self._terms:
            return (0,) * self.nvars
        return tuple(max(exponent[index] for exponent in self._terms) for index in range(self.nvars))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Polynomial) and self.nvars == other.nvars and self._terms == other._terms

    def __repr__(self) -> str:
        return f"Polynomial({self.nvars}, {self._terms!r})"

    def _coerce_polynomial(self, other: Polynomial | Q5 | Fraction | int) -> Polynomial:
        if isinstance(other, Polynomial):
            if other.nvars != self.nvars:
                raise ValueError("polynomial dimensions differ")
            return other
        if isinstance(other, (Q5, Fraction, int)):
            return Polynomial.constant(self.nvars, other)
        return NotImplemented

    def __add__(self, other: Polynomial | Q5 | Fraction | int) -> Polynomial:
        rhs = self._coerce_polynomial(other)
        if rhs is NotImplemented:
            return NotImplemented
        terms = self.terms
        for exponent, coefficient in rhs._terms.items():
            terms[exponent] = terms.get(exponent, ZERO) + coefficient
            if terms[exponent].is_zero():
                del terms[exponent]
        return Polynomial(self.nvars, terms)

    __radd__ = __add__

    def __neg__(self) -> Polynomial:
        return Polynomial(self.nvars, {exponent: -coefficient for exponent, coefficient in self._terms.items()})

    def __sub__(self, other: Polynomial | Q5 | Fraction | int) -> Polynomial:
        rhs = self._coerce_polynomial(other)
        if rhs is NotImplemented:
            return NotImplemented
        return self + (-rhs)

    def __rsub__(self, other: Polynomial | Q5 | Fraction | int) -> Polynomial:
        rhs = self._coerce_polynomial(other)
        if rhs is NotImplemented:
            return NotImplemented
        return rhs - self

    def __mul__(self, other: Polynomial | Q5 | Fraction | int) -> Polynomial:
        rhs = self._coerce_polynomial(other)
        if rhs is NotImplemented:
            return NotImplemented
        terms: dict[Exponent, Q5] = {}
        for left_exponent, left_coefficient in self._terms.items():
            for right_exponent, right_coefficient in rhs._terms.items():
                exponent = tuple(a + b for a, b in zip(left_exponent, right_exponent))
                terms[exponent] = terms.get(exponent, ZERO) + left_coefficient * right_coefficient
                if terms[exponent].is_zero():
                    del terms[exponent]
        return Polynomial(self.nvars, terms)

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> Polynomial:
        if not isinstance(exponent, int) or exponent < 0:
            raise ValueError("polynomial exponent must be a nonnegative integer")
        result = Polynomial.constant(self.nvars, ONE)
        base = self
        power = exponent
        while power:
            if power & 1:
                result *= base
            base *= base
            power //= 2
        return result

    def evaluate(self, values: Sequence[Q5 | int]) -> Q5:
        if len(values) != self.nvars:
            raise ValueError("evaluation point has the wrong dimension")
        qvalues = [value if isinstance(value, Q5) else Q5.rational(value) for value in values]
        result = ZERO
        for exponent, coefficient in self._terms.items():
            term = coefficient
            for value, power in zip(qvalues, exponent):
                term *= value**power
            result += term
        return result

    def substitute(self, replacements: Sequence[Polynomial]) -> Polynomial:
        """Substitute arbitrary polynomial coordinate maps exactly."""
        if len(replacements) != self.nvars:
            raise ValueError("one replacement is required for each source variable")
        if not replacements:
            return Polynomial(0, self._terms)
        target_nvars = replacements[0].nvars
        if any(replacement.nvars != target_nvars for replacement in replacements):
            raise ValueError("replacement dimensions differ")
        result = Polynomial.zero(target_nvars)
        for exponent, coefficient in self._terms.items():
            term = Polynomial.constant(target_nvars, coefficient)
            for replacement, power in zip(replacements, exponent):
                term *= replacement**power
            result += term
        return result

    def affine_substitute(
        self,
        centre: Sequence[Q5],
        matrix: Sequence[Sequence[Q5]],
    ) -> Polynomial:
        """Substitute x_i = centre_i + sum_j matrix[i][j] y_j."""
        if len(centre) != self.nvars or len(matrix) != self.nvars:
            raise ValueError("affine map has the wrong source dimension")
        target_nvars = len(matrix[0]) if matrix else 0
        if any(len(row) != target_nvars for row in matrix):
            raise ValueError("affine matrix rows have different lengths")
        variables = [Polynomial.variable(target_nvars, index) for index in range(target_nvars)]
        replacements: list[Polynomial] = []
        for constant, row in zip(centre, matrix):
            replacement = Polynomial.constant(target_nvars, constant)
            for coefficient, variable in zip(row, variables):
                replacement += variable * coefficient
            replacements.append(replacement)
        return self.substitute(replacements)

    def divisible_by_monomial(self, exponents: Sequence[int]) -> bool:
        divisor = tuple(exponents)
        if len(divisor) != self.nvars or any(not isinstance(value, int) or value < 0 for value in divisor):
            raise ValueError("invalid monomial divisor")
        return all(
            all(term_power >= divisor_power for term_power, divisor_power in zip(exponent, divisor))
            for exponent in self._terms
        )

    def divide_monomial(self, exponents: Sequence[int]) -> Polynomial:
        divisor = tuple(exponents)
        if not self.divisible_by_monomial(divisor):
            raise MonomialDivisionError(f"polynomial is not divisible by x^{divisor}")
        return Polynomial(
            self.nvars,
            {
                tuple(term_power - divisor_power for term_power, divisor_power in zip(exponent, divisor)): coefficient
                for exponent, coefficient in self._terms.items()
            },
        )

    def multiply_monomial(self, exponents: Sequence[int]) -> Polynomial:
        multiplier = tuple(exponents)
        if len(multiplier) != self.nvars or any(
            not isinstance(value, int) or value < 0 for value in multiplier
        ):
            raise ValueError("invalid monomial multiplier")
        return Polynomial(
            self.nvars,
            {
                tuple(term_power + extra for term_power, extra in zip(exponent, multiplier)): coefficient
                for exponent, coefficient in self._terms.items()
            },
        )

    def all_exponents(self) -> Iterable[Exponent]:
        return self._terms.keys()


def monomial(
    nvars: int,
    exponents: Sequence[int],
    coefficient: Q5 | Fraction | int = ONE,
) -> Polynomial:
    exponent = tuple(exponents)
    if len(exponent) != nvars:
        raise ValueError("monomial dimension mismatch")
    return Polynomial(nvars, {exponent: coefficient if isinstance(coefficient, Q5) else Q5.rational(coefficient)})


def dense_exponents(degrees: Sequence[int]) -> Iterable[Exponent]:
    return product(*(range(degree + 1) for degree in degrees))
