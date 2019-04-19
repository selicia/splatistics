# :squid: Splatistics :octopus:

## Summary

This project seeks to optimize ability slot usage for loadouts by maximizing the
net increase for all stats.

This project uses a genetic algorithm where fitness points are by the net
increase of a player's stats. (Checkout the links at the bottom of this README
for further info)

## Getting Started

This project currently has no external dependencies outside of a Python 3
interpreter. The main entrypoint is in the `optimizer/optimize.py` script, so to
execute:

```
python optimizer/optimize.py
```

The current script is optimizing a loadout for the Vanilla .96 Gal during
development.

## Current Limitations

The following are to-do's being addressed:

- Abilities that simultaneously amplify multiple paramters have a bias
- Main Power Up is not being accounted for currently

## Useful Links

The following are documents, pages, and tidbits, that describe the background
material used in development of this software:

- [Genetic Algorithms Wiki Page](https://en.wikipedia.org/wiki/Genetic_algorithm)
- [Crossover Wiki Page](https://en.wikipedia.org/wiki/Crossover_(genetic_algorithm))
- [Mutation Wiki Page](https://en.wikipedia.org/wiki/Mutation_(genetic_algorithm))
- [Leanny's Ability Write-Up](http://leanny.github.io/paper/abilities.pdf)
- [Selicia's Early Methodology Explanation](https://github.com/selicia/splatistics/issues/1#issuecomment-483960004)
