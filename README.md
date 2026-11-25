# A logarithmic loss in binary prefix coverage for prime reciprocals

**zslcz and 6.2Astra (AI assistant) · Research note · v0.1.0-draft**

[Read the proof (PDF)](note.pdf) · [LaTeX source](note.tex) · [Shell depths](data/shells.csv) · [First missing words](data/missing.csv)

How many leading digits can you prescribe in the reciprocal of a prime? In base π, for example, the second denominator shell is π < n ≤ π². Reading from the first nonzero digit, the prefix `10` occurs only for n = 8 and n = 9. Integer denominators realize that prefix, but there is no prime witness. The note gives a lower bound on how much coverage is lost in every sufficiently large shell.

## Result

Fix a real base β > 2. The first shell contains the integers greater than 1 and at most β. Multiplying both endpoints by β gives the next shell. For each denominator n in a shell, read the greedy expansion of 1/n from its first nonzero digit.

The **prime coverage depth** is the greatest length for which every word of zeros and ones beginning with 1 occurs as a prefix of some prime reciprocal in the shell. Different words may use different primes. If even the prefix 1 is missing, the depth is zero. For every sufficiently large shell index j, the prime coverage depth satisfies

$$D_{\mathbb P}(j)\le j-\log_\beta j+C_\beta.$$

The constant on the right depends only on the base. With all integer denominators available, every such word of length j − 1 occurs whenever j ≥ 2. Subtracting the prime depth from the integer depth therefore gives

$$D_{\mathbb N}(j)-D_{\mathbb P}(j)\ge \log_\beta j-O_\beta(1).$$

In particular, the number of digits lost tends to infinity. The proof leaves the optimal growth rate and a numerical threshold for the samples below undetermined.

The proof converts a word into an interval of possible denominators. Fourier decay for the reciprocal image of a self-similar measure places one such interval inside a run of composite integers. The external inputs are the prime number theorem and Theorem 3.1 of Mosquera and Shmerkin. Priority for this particular coverage bound remains undetermined. [Fourier decay theorem](https://www.acadsci.fi/mathematica/Vol43/vol43pp0823-0834.pdf) · [Related work on reciprocals in missing-digit sets](https://arxiv.org/abs/2604.11282)

## Reproduce the finite samples

Run the following commands from the repository root with Python 3.8 or later. The verifier uses the standard library. At the default denominator limit of 100 million, its odd-number sieve occupies about 50 MB.

```sh
python -m unittest -v
python verify.py --digits 50
python verify.py --digits 80
```

Each verification run recomputes both CSV files and compares them field by field with the bundled data. Expect **34 complete shells and 445 first missing words** at either precision. To generate a smaller sample in a separate directory, run `python verify.py --limit 10000 --write build/small`.

| Base | Complete shells | Integer depth in last shell | Prime depth in last shell |
| --- | ---: | ---: | ---: |
| π | 1–16 | 16 | 12 |
| e | 1–18 | 18 | 13 |

Each row in `data/shells.csv` gives both depths and the number of words missing at the first depth where prime coverage fails. In `data/missing.csv`, each such word has inclusive integer endpoints `first` and `last`. An empty window has `first > last`.

The verifier encloses π using Machin's formula and alternating arctangent series, and e using a factorial series with an explicit tail bound. It accepts an integer endpoint only when both rational bounds have the same floor. Boundary tests compare the interval method with exact, digit-by-digit greedy expansion in bases 3 and 5/2.

## Scope of the Lean proof

[Formal.lean](Formal.lean) uses the Lean 4.8.0 standard distribution. With elan installed, run

```sh
lean --version
lean -DwarningAsError=true Formal.lean
```

| Lemma | Statement checked by Lean |
| --- | --- |
| `existsPrimeDivisor` | Every natural number at least 2 has a prime divisor. |
| `compositeRun` | Adding any offset from 2 through L to a positive common multiple of the primes up to L gives a composite integer. |
| `missingWindow` | An integer interval inside that run contains no prime. |
| `missingNarrowWindow` | The middle-third and quarter-width inequalities in the proof suffice to exclude prime witnesses. |

The final lemma reports the axiom dependencies `propext`, `Classical.choice`, and `Quot.sound`. The greedy interval identity, Fourier analysis, prime number theorem, and asymptotic choice of a word in each shell are part of the written proof. A useful point for independent review is the uniform error in equation (2): the target interval shrinks as the shell index grows.

## Citation and review status

Suggested citation: **zslcz and 6.2Astra (AI assistant). *A logarithmic loss in binary prefix coverage for prime reciprocals*. Research note, v0.1.0-draft.** [Citation metadata](CITATION.cff)

zslcz posed the problem and directed the project. 6.2Astra is the project's byline credit for the AI assistant that helped with the derivation, literature search, code, and writing. This draft has not been independently peer reviewed. The choice of license for the manuscript, code, and data is pending.

To rebuild the PDF with TeX Live, run `xelatex note.tex` twice.
