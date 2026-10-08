"""Exact boxes, interval products, and corner bounds."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Callable, Iterable, Sequence

from exact import Q5
from polynomial import Polynomial


def as_q5(value: Q5 | Fraction | int) -> Q5:
    return value if isinstance(value, Q5) else Q5.rational(value)


@dataclass(frozen=True)
class Interval:
    lower: Q5
    upper: Q5

    def __init__(self, lower: Q5 | Fraction | int, upper: Q5 | Fraction | int):
        lower_q5 = as_q5(lower)
        upper_q5 = as_q5(upper)
        if lower_q5 > upper_q5:
            raise ValueError("interval endpoints are reversed")
        object.__setattr__(self, "lower", lower_q5)
        object.__setattr__(self, "upper", upper_q5)

    def contains(self, value: Q5 | Fraction | int) -> bool:
        point = as_q5(value)
        return self.lower <= point <= self.upper

    def contains_interval(self, other: Interval) -> bool:
        return self.lower <= other.lower and other.upper <= self.upper

    def midpoint(self) -> Q5:
        return (self.lower + self.upper) / 2

    def split(self) -> tuple[Interval, Interval]:
        middle = self.midpoint()
        return Interval(self.lower, middle), Interval(middle, self.upper)

    def product(self, other: Interval) -> Interval:
        candidates = [
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper,
        ]
        return Interval(min(candidates), max(candidates))


@dataclass(frozen=True)
class Box:
    intervals: tuple[Interval, ...]

    def __init__(self, intervals: Sequence[Interval]):
        object.__setattr__(self, "intervals", tuple(intervals))

    @property
    def dimension(self) -> int:
        return len(self.intervals)

    def contains_box(self, other: Box) -> bool:
        return self.dimension == other.dimension and all(
            target.contains_interval(candidate)
            for target, candidate in zip(self.intervals, other.intervals)
        )

    def corners(self) -> Iterable[tuple[Q5, ...]]:
        return product(*((interval.lower, interval.upper) for interval in self.intervals))

    def split(self, axis: int) -> tuple[Box, Box]:
        if axis < 0 or axis >= self.dimension:
            raise IndexError("split axis outside box")
        lower_interval, upper_interval = self.intervals[axis].split()
        left = list(self.intervals)
        right = list(self.intervals)
        left[axis] = lower_interval
        right[axis] = upper_interval
        return Box(left), Box(right)


def corner_range(function: Callable[[Sequence[Q5]], Q5], box: Box) -> Interval:
    """Exact range for a function known to be multi-affine."""
    values = [function(corner) for corner in box.corners()]
    if not values:
        value = function(())
        return Interval(value, value)
    return Interval(min(values), max(values))


def polynomial_corner_range(polynomial: Polynomial, box: Box) -> Interval:
    if polynomial.nvars != box.dimension:
        raise ValueError("polynomial and box dimensions differ")
    if any(degree > 1 for degree in polynomial.degrees()):
        raise ValueError("corner minimisation needs a multi-affine polynomial")
    return corner_range(polynomial.evaluate, box)


def map_bounds(coordinates: Sequence[Polynomial], domain: Box) -> Box:
    """Bound a multi-affine coordinate map by its exact corner ranges."""
    if any(coordinate.nvars != domain.dimension for coordinate in coordinates):
        raise ValueError("map and domain dimensions differ")
    return Box([polynomial_corner_range(coordinate, domain) for coordinate in coordinates])


def map_is_contained(coordinates: Sequence[Polynomial], domain: Box, target: Box) -> bool:
    if len(coordinates) != target.dimension:
        return False
    return target.contains_box(map_bounds(coordinates, domain))
