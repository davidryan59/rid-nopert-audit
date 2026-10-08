# Clean-room zoom-cover specification

## Summary

The article specifies the zoom lemma and the geometry of all 38 covers.
The copied JSON files contain the terminal cells and compact witness references.
The public material does not specify enough of the JSON encoding to reconstruct those witnesses uniquely.
The strict clean-room audit must stop before it assigns mathematical meaning to the ambiguous fields.

## Implementation Checklist

- [x] Record the five configuration coordinates and the adapted coordinate systems.
- [x] Record every cover root domain and zoom family from the article.
- [x] Record the no-fit sets, witnesses, support tests, distance factors, and sign tests.
- [x] Record the binary subdivision and cover-completeness obligations.
- [x] Record the hand-over and pentagon extension obligations.
- [x] Map each visible JSON field where the article gives an explicit meaning.
- [x] List every missing serialization definition that blocks an independent check.
- [ ] Interpret the compact witness references. This needs the missing index tables and field semantics.
- [ ] Interpret the subdivision strings. This needs the missing "rid-cover/1" grammar.
- [ ] Check the five zoom obligations on all terminal cells. The preceding items block this work.

## Permitted basis

This specification uses only these sources before the freeze:

- Hervay's "paper/article.pdf" at commit "802a3ded09535c4a99cef1371ce0d0277c433fa8";
- the 30 copied "local" JSON files;
- the eight copied "exotic" JSON files;
- the project front door, which disclosed aggregate prior results.

No checker source, test, report, manifest, log, figure source, or audit document informed this specification.

## Exact scalars

Section 5.1 defines the coefficient field

\[
  \mathbb Q(\sqrt5)=\{a+b\sqrt5:a,b\in\mathbb Q\}.
\]

Addition is componentwise. Multiplication is

\[
  (a+b\sqrt5)(c+d\sqrt5)=(ac+5bd)+(ad+bc)\sqrt5.
\]

For a nonzero element, inversion is

\[
  (a+b\sqrt5)^{-1}=\frac{a-b\sqrt5}{a^2-5b^2}.
\]

The sign is exact.
If the rational parts have opposite signs, compare \(a^2\) with \(5b^2\), while retaining the sign of \(a\).

The JSON files visibly use strings such as "3/64" for rationals.
They visibly use two-element arrays such as ["-2", "1"] for field elements.
The article says that field coefficients use the pair \(a,b\), but it does not define the JSON schema.

## Configuration coordinates

### Standard coordinates

Sections 2.3 and 3 use

\[
  c=[s,t,r_1,r_2,r_3],\qquad u=(s,t,1),\qquad r=(r_1,r_2,r_3).
\]

The homogeneous form permits any positive multiple of \(u\), as stated before Definition 7.1.
The rotation denominator and numerator are

\[
  d=1+r\mathbin\cdot r,
\]

\[
  \bar R_P(r)x=(1-r\mathbin\cdot r)x+2r(r\mathbin\cdot x)+2r\mathbin\times x.
\]

The screen map is Equation (2.4):

\[
  L_{s,t}(x_1,x_2,x_3)=(x_1-sx_3,x_2-tx_3).
\]

Equation (2.1) defines the RID vertex set as all independent sign choices and cyclic coordinate permutations of

\[
  (1,1,\phi^3),\quad(\phi^2,\phi,2\phi),\quad(2+\phi,0,\phi^2),
\]

where \(\phi=(1+\sqrt5)/2\).
This definition produces an unordered set of 60 vertices.

### Pentagon coordinates

Section 8.2, Equations (8.3) and (8.4), define

\[
  \eta=s+\bar\phi t,\qquad \xi=s+\phi t+\bar\phi,
  \qquad \bar\phi=1-\phi.
\]

The inverse map is

\[
  s=\frac{-5+3\sqrt5}{10}+\frac{\phi\eta-\bar\phi\xi}{\sqrt5},
  \qquad
  t=\frac{5-\sqrt5}{10}+\frac{\xi-\eta}{\sqrt5}.
\]

The pentagon configuration is \((\eta,\xi,r)=(0,0,0)\).
The reduced-domain viewing inequality is exactly \(\xi\leq0\).

### Arc-plane coordinates

Section 9.1 defines

\[
  a_1=\frac{-5+3\sqrt5}{10},\qquad
  a_3=\frac{-5+\sqrt5}{10},\qquad
  r_A=(a_1,0,a_3),
\]

and \(w_\sigma=(\sigma a_3,1,-\sigma a_1)\) for \(\sigma\in\{-1,1\}\).
Equation (9.3) defines

\[
  e=\frac{1-2s}{2+s},\qquad v=\frac{5t}{2+s},\qquad \theta=r_2,
\]

\[
  \zeta_1=r_1-\sigma(a_1+a_3\theta),\qquad
  \zeta_3=r_3-\sigma(a_3-a_1\theta).
\]

The inverse homogeneous viewing vector and rotation are

\[
  u=(1-2e,v,2+e),
\]

\[
  r=\sigma r_A+\theta w_\sigma+(\zeta_1,0,\zeta_3).
\]

The arc planes are \(v=\zeta_1=\zeta_3=0\).
The first touch arc is \(\theta=0\), with \(0\leq e\leq e_*=\sqrt5-2\).
The second touch arc is \(\theta=-e\) on the same interval.

## No-fit sets

Definition 7.1 and Sections 7 to 10 use two no-fit sets.

1. The aligned set \(r=0\). The plug and hole shadows are identical, so no strict fit exists.
2. Each plane \(\Pi_\sigma\) from Equation (9.1). Lemma 9.1 proves equal plug and hole support in direction \(e_2\).

An independent checker should recompute Lemma 9.1's finite support equality from the 60 coordinates.
This set-level check does not require the missing vertex index order.

## Generic zoom maps

Definitions 7.2, Lemma 7.4, and Lemma 8.1 specify two families.

### Tube zoom

Let base coordinates satisfy \(z_b\in\Sigma_b\).
Let the offset direction \(\hat f\) lie on a face \(F\) of the sign box \(\Phi\).
For \(0\leq\delta\leq\delta_{\max}\), set

\[
  z_o=\delta\hat f.
\]

Every point in \(\Sigma_b\times\delta_{\max}\Phi\) either has zero offset or belongs to a face zoom.

### Point zoom, family A

Let \(\hat b\) lie on a face \(G\) of \(\Sigma\), and let \(\hat f\) lie on a face \(F\) of \(\Phi\).
For \(0\leq\mu\leq\mu_{\max}\) and \(0\leq\rho\leq\rho_0\), set

\[
  z_b=\mu\hat b,\qquad z_o=\rho\mu\hat f.
\]

Both \(\mu\) and \(\rho\) are distance coordinates.

### Point zoom, family B

For \(0\leq\delta\leq\delta_{\max}\), put

\[
  z_b=\delta b,\qquad z_o=\delta\hat f,
\]

where \(b\) lies in the cone of \(\Sigma\) and satisfies \(\lVert b\rVert_\infty\leq1/\rho_0\).
The distance coordinate is \(\delta\).

### Crossing sheared family

Section 10.2 defines \(\theta'=\theta+e\).
The seven sheared \(A'\) zooms use the positive base face \(e=\mu\).
They use \(\theta'\) in place of \(\theta\) and \(0\leq\rho'\leq1/4\).
The actual coordinate is \(\theta=\theta'-e\).

## Root domains of the 38 covers

### Local covers 0 through 29

Section 7.4 and Appendix B, Table 3, specify six tube zooms per cover.
Their base is the listed rectangle in \((s,t)\), enlarged by \(1/1024\) on every side.
The result is clipped to \([0,2/3]\times[0,2/5]\).
Their offset is \(r\in\delta_{\max}[-1,1]^3\).
Each face of the cube supplies one root zoom.

The copied JSON files repeat these enlarged bounds and radii in "parameters.shape.tube".
The article's Table 3 is the authority for the intended mathematical roots.

| Cover | Raw \(s\) interval | Raw \(t\) interval | \(\delta_{\max}\) |
|---:|---:|---:|---:|
| 0 | \(1/12,1/6\) | \(0,1/10\) | \(1/96\) |
| 1 | \(0,1/6\) | \(1/10,1/5\) | \(1/80\) |
| 2 | \(1/6,1/3\) | \(0,1/10\) | \(1/50\) |
| 3 | \(1/6,1/4\) | \(1/10,1/5\) | \(1/50\) |
| 4 | \(1/4,1/3\) | \(1/10,3/20\) | \(1/50\) |
| 5 | \(1/4,1/3\) | \(3/20,1/5\) | \(1/50\) |
| 6 | \(0,1/12\) | \(1/5,3/10\) | \(1/50\) |
| 7 | \(1/12,1/8\) | \(1/5,9/40\) | \(1/50\) |
| 8 | \(1/12,1/8\) | \(9/40,1/4\) | \(1/50\) |
| 9 | \(1/8,1/6\) | \(1/5,1/4\) | \(1/200\) |
| 10 | \(1/12,1/8\) | \(1/4,3/10\) | \(1/50\) |
| 11 | \(1/8,7/48\) | \(1/4,11/40\) | \(1/50\) |
| 12 | \(7/48,1/6\) | \(1/4,21/80\) | \(1/200\) |
| 13 | \(7/48,5/32\) | \(21/80,11/40\) | \(1/50\) |
| 14 | \(5/32,31/192\) | \(21/80,43/160\) | \(1/200\) |
| 15 | \(1/8,1/6\) | \(11/40,3/10\) | \(1/50\) |
| 16 | \(0,1/6\) | \(3/10,2/5\) | \(1/50\) |
| 17 | \(1/6,5/24\) | \(1/5,9/40\) | \(1/50\) |
| 18 | \(1/6,3/16\) | \(9/40,1/4\) | \(1/200\) |
| 19 | \(3/16,5/24\) | \(9/40,1/4\) | \(1/50\) |
| 20 | \(5/24,1/4\) | \(1/5,9/40\) | \(1/50\) |
| 21 | \(5/24,1/4\) | \(9/40,1/4\) | \(1/200\) |
| 22 | \(1/6,3/16\) | \(1/4,21/80\) | \(1/200\) |
| 23 | \(3/16,5/24\) | \(1/4,21/80\) | \(1/200\) |
| 24 | \(5/24,11/48\) | \(1/4,11/40\) | \(1/200\) |
| 25 | \(1/4,1/3\) | \(1/5,1/4\) | \(1/50\) |
| 26 | \(1/3,1/2\) | \(0,1/10\) | \(1/50\) |
| 27 | \(1/3,1/2\) | \(1/10,1/5\) | \(1/50\) |
| 28 | \(1/2,7/12\) | \(0,1/10\) | \(1/50\) |
| 29 | \(7/12,5/8\) | \(0,1/20\) | \(1/20\) |

### Square cover

Section 8.1 specifies \(\Sigma=[0,1]^2\), \(\Phi=[-1,1]^3\), \(\mu_{\max}=\delta_{\max}=1/8\), and \(\rho_0=1\).
There are 12 family-A roots and six family-B roots.

### Pentagon cover

Section 8.2 specifies \(\Sigma=[-1,1]\times[-1,0]\), \(\Phi=[-1,1]^3\), \(\mu_{\max}=1/32\), \(\delta_{\max}=1/16\), and \(\rho_0=2\).
There are 18 family-A roots and six family-B roots.

### Arc covers

Section 9.2 specifies a tube base \(e\in[3/64,3/16]\).
The offset coordinates are \((v/2,\theta,\zeta_1,\zeta_3)\).
The sign box is \([0,1]\times[-1,1]^3\), and \(\delta_{\max}=1/32\).
Each sign of \(\sigma\) has seven roots.

### Endpoint covers

Section 10.1 specifies base \(e-e_*\), offset \((v/2,\theta,\zeta_1,\zeta_3)\), and the same sign box.
The negative base face has radius \(1/16\), and the positive base face has radius \(1/32\).
The offset radius is \(1/32\), and \(\rho_0=1\).
Each sign has 14 family-A roots and seven family-B roots.

### Crossing covers

Section 10.2 specifies base \(e\), offset \((4v/5,\theta,\zeta_1,\zeta_3)\), and the same sign box.
Both radii are \(1/16\), and \(\rho_0=5/4\).
Each sign has 14 family-A roots, seven family-B roots, and seven sheared roots.

## Witness polynomials

### Gap witness

Equation (6.6) defines, for a plug vertex \(v_p\), a hole contact vertex \(v_h\), and support direction \(n(u)\),

\[
  p(u,r)=n(u)\mathbin\cdot\left(\bar R_P(r)v_p-dv_h\right).
\]

One support form uses an ordered edge \((v_a,v_b)\):

\[
  n(u)=\sigma u\mathbin\times(v_b-v_a).
\]

The other uses a fixed screen direction \((n_1,n_2)\):

\[
  n(u)=(u_3n_1,u_3n_2,-u_1n_1-u_2n_2).
\]

The JSON witness objects visibly have either "edge" and "vertex", or "direction", "contact", and "vertex".
The article does not state that these field names have the meanings above.

### Domain witness

Definition 7.1 permits any defining inequality \(q\leq0\) of \(D\), using \(q\) as a witness.
The square cover uses the fold inequality associated with the half-turn \(k\).
The arc, endpoint, and crossing covers also use the tie inequality from Equation (9.2).
The JSON represents a domain witness as {"inequality": n}, but no public table maps \(n\) to a polynomial.

## Support conditions

Equation (7.2) requires

\[
  n(u)\mathbin\cdot(w-v_h)\leq0
\]

for every one of the 60 hole vertices \(w\).
The checker must evaluate all 60 conditions at all \(2^5\) cell corners.
Equality is permitted.
The multi-affine corner rule then proves each condition throughout the cell.

## Distance factors and exact division

Definition 7.2 permits a monomial in designated nonnegative distance coordinates:

\[
  y^a=\prod_j y_j^{a_j}.
\]

Each leaf visibly stores a five-entry "factor" exponent vector.
The checker must substitute the complete zoom map into the witness polynomial.
Every resulting monomial exponent must dominate the claimed exponent vector.
The quotient must be computed by exact monomial division.

The article does not define which serialized coordinate each exponent position denotes.
This prevents exact division from being attached to a mathematical leaf.

## Bernstein obligation

Section 5.2 defines the tensor Bernstein basis.
For one variable on \([l,h]\), first substitute \(x=l+(h-l)y\).
For power coefficients \(a_k\) and degree \(n\), Equation (5.2) gives

\[
  b_r=\sum_{k=0}^r\frac{\binom r k}{\binom n k}a_k.
\]

Apply this conversion one variable at a time.
Lemma 7.3 requires every coefficient of the divided quotient to be strictly positive.
Zero fails.

## Five cell obligations

For each interpreted terminal cell, an independent checker must prove all of these statements.

1. Each designated distance coordinate is nonnegative throughout the cell.
2. The zero set of each distance coordinate maps into the stated no-fit set.
3. The pulled-back witness is exactly divisible by the claimed distance monomial.
4. Every support condition holds at every required cell corner.
5. Every tensor Bernstein coefficient of the quotient is strictly positive.

It must also prove \(u_3>0\) throughout each root and every cell.
For domain witnesses, it must identify the selected polynomial as a defining \(q\leq0\) inequality of \(D\).

## Subdivision and completeness

Section 7.3 says that each root is bisected in one coordinate at a time.
Both closed midpoint children are retained.
Induction then proves that the terminal cells cover the root.

A checker must reconstruct every root-to-leaf path and midpoint box.
It must reject missing children, extra children, duplicate paths, malformed children, and non-prefix-free leaves.
It must prove that every mathematical root zoom expected for the cover occurs exactly once.

Valid leaves alone do not prove a cover.
Completeness needs the subdivision-tree proof for each root, plus Lemma 7.4 or Lemma 8.1 across all required faces.

The JSON "tree" values are compact strings of digits and dots.
The article does not define their grammar, traversal order, child order, or association with the "leaves" array.
Therefore the copied inputs do not provide an independently interpretable completeness certificate.

## Hand-over obligation

For a crossing family-A cell on the positive base face, Section 10.2 defines

\[
  o(y)=\rho\hat f+(0,1,0,0).
\]

Lemma 10.2 requires

\[
  o(y)\in\tfrac14\Phi
\]

throughout the cell.
Each coordinate is a product of two zoom coordinates plus a constant.
Exact interval products give its range.

A handed cell must map into the no-fit second arc or into a checked sheared root.
The JSON uses the string "delegated", but it contains no target reference.
The article does not define how the marker binds to a sheared root or leaf set.

## Pentagon extension obligation

The ordinary point cover reaches \(|\eta|\leq1/32\), \(-1/32\leq\xi\leq0\), and \(\lVert r\rVert_\infty\leq1/16\).
Section 8.2 extends its acceptance region by dropping the upper bound \(\xi\leq0\).
This is sound because every point with \(\xi>0\) violates the viewing-triangle inequality and lies outside \(D\).

The checker must establish the exact identity

\[
  \phi\xi=\phi s+\phi^2t-1.
\]

It must also prove exact containment in all remaining bounds.
The JSON stores "beyond": {"axis": 1, "inequality": 0}, whose encoding is not defined by the article.

## Visible JSON field inventory

All 38 files visibly use these top-level fields:

- "format";
- "name";
- "scope";
- "parameters";
- "witnesses";
- "zooms".

The visible parameter fields are "coordinates", "centre", "map", "shape", and "beyond".
Point shapes can also contain "window" data for crossing hand-overs.
Each zoom visibly has "name", "tree", and "leaves".
An ordinary leaf visibly contains a witness index and factor vector.
Crossing data also contain the string leaf "delegated".

These observations describe syntax only.
They do not supply the missing mathematical semantics.

## Blocking omissions in the public specification

The following omissions independently prevent a strict clean-room result.

1. **Vertex numbering.** Equation (2.1) defines a set, but JSON witnesses use integers for vertices and contacts.
2. **Domain-inequality numbering.** The article defines inequality families, but JSON witnesses use one integer without an index table.
3. **Tree grammar.** The article does not define the digit-and-dot encoding, traversal order, child order, or leaf-array association.
4. **Zoom-name grammar.** Names such as "A b0+ o1-" and "A' b0+ o1-" have no normative public grammar.
5. **Zoom coordinate order.** The article does not bind the five serialized coordinates to factor positions and tree split digits.
6. **Affine field semantics.** The article does not state the matrix orientation or how "centre" and "map" compose with adapted coordinates.
7. **Witness field semantics.** The article does not normatively define "edge", "direction", "contact", "vertex", and "inequality".
8. **Face-radius order.** The article gives face-dependent radii, but it does not bind JSON "radii" entries to signed faces.
9. **Delegation binding.** A "delegated" leaf contains no target, and the article does not define its implicit target rule.
10. **Pentagon extension encoding.** The mathematics is clear, but the "beyond.axis" and "beyond.inequality" indices are undefined.
11. **Schema and rejection rules.** "rid-cover/1" has no public schema for types, fields, integer ranges, or unknown fields.

Guessing these conventions from familiar programming patterns would cross the stated clean-room rule.
Several guesses can produce internally consistent but different polynomials or cells.
The checker must fail closed until a neutral declarative specification supplies these definitions.

## Required neutral specification

A separate specification session can inspect the implementation and publish a source-provenance table.
That table must define all eleven items above without copying algorithms.
A new implementation session can then receive that table, the article, and the 38 JSON files.
It must not receive the original checker source.
