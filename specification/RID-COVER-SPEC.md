# `rid-cover/1` neutral specification

- **Specification version:** `rid-cover/1-spec.1`
- **Status:** Complete
- **Completed:** 2026-10-08
- **Source version:** `bence-hervay/nopert-rid` commit `802a3ded09535c4a99cef1371ce0d0277c433fa8`
- **Version hash:** See [`VERSION.json`](VERSION.json)

## Summary

This document defines the `rid-cover/1` data format and its mathematical meaning.
It contains no upstream source code.
The attached tables fix every vertex, domain inequality, cover, zoom, and zoom root.

## Implementation Checklist

- [x] Define vertex indices `0` through `59`.
- [x] Define domain inequality indices `0` through `72`.
- [x] Define coordinate systems and affine-map orientation.
- [x] Define every zoom family, name, order, root, and variable order.
- [x] Bind point-cover radii to signed faces.
- [x] Define the cell-tree grammar and leaf association.
- [x] Define witness fields, polynomials, support checks, and signs.
- [x] Define delegated hand-over and zero-window behaviour.
- [x] Define the pentagon extension rule.
- [x] Define the complete JSON encoding and semantic validation rules.
- [x] Record source provenance and a specification version hash.

## 1. Normative files

The specification bundle contains these normative files:

- [`RID-COVER-SPEC.md`](RID-COVER-SPEC.md), this document;
- [`vertices.json`](vertices.json), the exact 60-row vertex table;
- [`domain-inequalities.json`](domain-inequalities.json), the exact 73-row polynomial table;
- [`cover-inventory.json`](cover-inventory.json), all 38 covers and 334 zoom roots;
- [`rid-cover.schema.json`](rid-cover.schema.json), the structural JSON Schema;
- [`PROVENANCE.json`](PROVENANCE.json), definition-level source provenance.

[`SHA256SUMS`](SHA256SUMS) authenticates those files.
[`VERSION.json`](VERSION.json) gives the SHA-256 identifier of that checksum manifest.

The article remains normative for the proof of the zoom lemmas.
This specification is normative for the data encoding and all index bindings.

## 2. Exact numbers

Let

\[
K=\mathbb Q(\sqrt5)=\{a+b\sqrt5:a,b\in\mathbb Q\}.
\]

A rational is a JSON string in one of these forms:

- `n`, for an integer;
- `n/d`, for a non-integer in lowest terms, with `d > 1`.

The numerator uses decimal digits with one optional leading minus sign.
The encoding forbids a leading plus sign, leading zeroes, `-0`, and a negative denominator.
It also forbids reducible fractions and fractions that represent integers.

An element \(a+b\sqrt5\) is the two-element JSON array `[a,b]`.
Each element is a canonical rational string.

All arithmetic, comparisons, interval endpoints, substitutions, divisions, and Bernstein coefficients are exact.

## 3. Vertex numbering

The RID has 60 vertices in the order given by [`vertices.json`](vertices.json).
Each coordinate uses the \(K\) encoding from Section 2.

The following deterministic rule produces the same order.

1. Start with these three arrays of integer pairs:

   \[
   ((2,0),(2,0),(4,2)),
   \quad ((3,1),(1,1),(2,2)),
   \quad ((5,1),(0,0),(3,1)).
   \]

2. Interpret a pair \((a,b)\) as \((a+b\sqrt5)/2\).
3. Apply every independent sign choice to the three pairs.
4. Apply the three cyclic left shifts to the coordinate array.
5. Remove duplicates.
6. Sort the integer-pair arrays lexicographically.
   Compare \(a\) before \(b\), then coordinates `0`, `1`, and `2`.
7. Number the resulting 60 arrays from `0`.

This is a lexical sort of the integer codes.
It is not a numerical sort of the values in \(K\).

An unordered pair of vertices is an RID edge exactly when its squared Euclidean distance is \(4\).
There are 120 such pairs.

## 4. Domain-inequality numbering

The standard configuration variables have this order:

\[
(s,t,r_1,r_2,r_3).
\]

Every domain polynomial is named \(q_i\).
The representative domain requires

\[
q_i\leq 0\qquad(0\leq i\leq72).
\]

[`domain-inequalities.json`](domain-inequalities.json) gives every polynomial as exact nonzero terms.
An exponent vector `[e0,e1,e2,e3,e4]` denotes

\[
s^{e_0}t^{e_1}r_1^{e_2}r_2^{e_3}r_3^{e_4}.
\]

The coefficient is an element of \(K\).

Let

\[
\phi=\frac{1+\sqrt5}{2},\qquad u=(s,t,1).
\]

The index rules are:

- `0`:
  \[
  q_0=\phi s+\phi^2t-1.
  \]
- `1` through `12`: put \(k=i-1\), \(a=\lfloor k/4\rfloor\), and use rotation indices modulo three.
  The four sign pairs for each \(a\) are `(-,-)`, `(-,+)`, `(+,-)`, `(+,+)`.
  For signs \(\epsilon_1,\epsilon_2\in\{-1,+1\}\),
  \[
  q_i=\epsilon_1r_{a+1}+\epsilon_2(\phi-1)r_{((a+1)\bmod3)+1}+\phi-2.
  \]
- `13` through `72`: index \(i=13+j\) uses symmetry quaternion \(g_j=(g_0,\vec g)\).
  Its exact expanded affine polynomial is row \(i\) of the table.

For a general homogeneous view \(u=(u_1,u_2,u_3)\), define

\[
A_g(u,r)=\vec g\mathbin\cdot u+
 r\mathbin\cdot\bigl(g_0u+\vec g\mathbin\times u\bigr).
\]

Then the homogeneous forms are

\[
q_0(u,r)=\phi u_1+\phi^2u_2-u_3,
\]

the rotation inequalities above, independent of \(u\), and

\[
q_{13+j}(u,r)=A_{g_j}(u,r)^2-u\mathbin\cdot u.
\]

Their homogeneous degrees in the view are respectively `1`, `0`, and `2`.
The table records this degree for every row.

## 5. Coordinate and affine-map conventions

Three vectors must remain distinct:

- \(x=(x_0,\ldots,x_4)\), the selected adapted coordinates;
- \(z=(z_0,\ldots,z_4)\), the cover coordinates;
- \(y=(y_0,\ldots,y_4)\), the variables of one zoom.

The JSON fields `centre` and `map` mean

\[
x_i=c_i+\sum_{j=0}^4 M_{ij}z_j.
\]

The first index of `map` is the output row \(i\).
The second index is the cover-coordinate column \(j\).
Thus `map` is `[row][column]`.

The first \(k\) cover coordinates form `z_base`.
The remaining \(5-k\) coordinates form `z_offset`.
The shape determines \(k\).

### 5.1 Configuration coordinates

The JSON value `"configuration"` means

\[
x=(s,t,r_1,r_2,r_3),\qquad u=(s,t,1).
\]

The no-fit set is \(r_1=r_2=r_3=0\).

Local and square covers use \(x=z\).

The pentagon cover uses

\[
z=(\eta,\xi,r_1,r_2,r_3),
\]

where

\[
\eta=s+(1-\phi)t,
\qquad
\xi=s+\phi t+1-\phi.
\]

Its stored centre and matrix give the inverse:

\[
s=\frac{-5+3\sqrt5}{10}
  +\frac{5+\sqrt5}{10}\eta
  +\frac{5-\sqrt5}{10}\xi,
\]

\[
t=\frac{5-\sqrt5}{10}
  -\frac{\sqrt5}{5}\eta
  +\frac{\sqrt5}{5}\xi.
\]

### 5.2 Arc-plane coordinates

The JSON value `{"arc-plane":"plus"}` uses \(\sigma=+1\).
The value `{"arc-plane":"minus"}` uses \(\sigma=-1\).

In either case,

\[
x=(e,v,\theta,\zeta_1,\zeta_3).
\]

Define

\[
a_1=\frac{-5+3\sqrt5}{10},
\qquad
a_3=\frac{-5+\sqrt5}{10},
\]

\[
r_A=(a_1,0,a_3),
\qquad
w_\sigma=(\sigma a_3,1,-\sigma a_1).
\]

The configuration is

\[
u=(1-2e,v,2+e),
\]

\[
r=\sigma r_A+\theta w_\sigma+(\zeta_1,0,\zeta_3).
\]

The corresponding affine view is \(s=u_1/u_3\), \(t=u_2/u_3\).
Every checked cell must prove \(u_3>0\).

For \(s>-2\), the inverse is

\[
e=\frac{1-2s}{2+s},
\qquad
v=\frac{5t}{2+s},
\qquad
\theta=r_2,
\]

\[
\zeta_1=r_1-\sigma(a_1+a_3\theta),
\qquad
\zeta_3=r_3-\sigma(a_3-a_1\theta).
\]

The no-fit set is \(v=\zeta_1=\zeta_3=0\).

The arc covers use

\[
z=(e,v/2,\theta,\zeta_1,\zeta_3).
\]

The endpoint covers use

\[
z=(e-(\sqrt5-2),v/2,\theta,\zeta_1,\zeta_3).
\]

The crossing covers use

\[
z=(e,4v/5,\theta,\zeta_1,\zeta_3).
\]

Their sheared family uses a temporary offset coordinate \(\theta'\) with

\[
\theta=\theta'-e.
\]

## 6. Signed faces and radii

A unit-box axis is one of `[-1,0]`, `[0,1]`, or `[-1,1]`.
A face is `{"axis":a,"side":s}` with \(s=-1\) or \(+1\).

Enumerate faces as follows:

1. Visit axes in increasing order.
2. Visit the lower endpoint before the upper endpoint.
3. Emit an endpoint only when it is nonzero.

Thus `[-1,1]` emits the negative face and then the positive face.
`[0,1]` emits only the positive face.
`[-1,0]` emits only the negative face.

For a point shape, `radii[p]` belongs to base face `faces(base)[p]`.
If that face is `(axis,side)`, the corresponding cover bound is `side*radii[p]`.

The offset bounds are `radius * offset`.
For a tube, the base bounds are the stored rational intervals.

## 7. Zoom inventory, names, and order

[`cover-inventory.json`](cover-inventory.json) gives the required ordered zoom list for every cover.
Each entry records the exact name, family, faces, root, variable roles, and distance-variable positions.

The following rules generate that inventory.

Let `OF = faces(offset)` and, for point shapes, `BF = faces(base)`.

- A tube has one `T` zoom for each face in `OF` order.
- A point shape first has every `A` zoom.
  The base-face loop is outer and the offset-face loop is inner.
- All `B` zooms follow, one per offset face in `OF` order.
- Sheared `A'` zooms follow all `B` zooms.
  The outer loop uses `window.faces` in its stored order.
  The inner loop uses `OF` order.

Names use zero-based local axes:

- `T o{axis}{side}`;
- `A b{axis}{side} o{axis}{side}`;
- `B o{axis}{side}`;
- `A' b{axis}{side} o{axis}{side}`.

The side is `-` or `+`.
`b` axes are local to the base unit box.
`o` axes are local to the offset unit box.

The cover counts are:

| Covers | Roots per cover | Order |
|---|---:|---|
| Local `0` through `29` | 6 | six `T` roots |
| `square` | 18 | 12 `A`, then 6 `B` |
| `pentagon` | 24 | 18 `A`, then 6 `B` |
| `arc+`, `arc-` | 7 | seven `T` roots |
| `endpoint+`, `endpoint-` | 21 | 14 `A`, then 7 `B` |
| `crossing+`, `crossing-` | 28 | 14 `A`, 7 `B`, then 7 `A'` |

The total is 334 roots.

## 8. Zoom variables and maps

For a face \(F=(a,s)\), `unit(U,F,free)` inserts \(s\) at axis \(a\).
It takes every other component from `free`, in increasing axis order.

All root intervals are closed.
The exact intervals for each root appear in [`cover-inventory.json`](cover-inventory.json).

### 8.1 Tube family

Let the base dimension be \(k\), with offset dimension \(m=5-k\).
For offset face \(F\), the variables are

\[
y=(z_{b,0},\ldots,z_{b,k-1},\delta,
   \widehat f_{\mathrm{free}}).
\]

Their order is base axes, then \(\delta\), then free offset axes.
Their bounds are the stored base intervals, \([0,\texttt{radius}]\), and the corresponding unit-box intervals.

The map is

\[
z_b=(y_0,\ldots,y_{k-1}),
\qquad
z_o=\delta\widehat f.
\]

The sole distance variable is \(y_k=\delta\).

### 8.2 Point family A

For base face \(G\) and offset face \(F\), the variables are

\[
y=(\mu,\rho,\widehat b_{\mathrm{free}},
   \widehat f_{\mathrm{free}}).
\]

Free base axes precede free offset axes.
Each group uses increasing local axis order.

If `radii[p]` belongs to \(G\), the root bounds are

\[
0\leq\mu\leq\texttt{radii[p]},
\qquad
0\leq\rho\leq\texttt{ratio}.
\]

The free variables use their unit-box bounds.
The map is

\[
z_b=\mu\widehat b,
\qquad
z_o=\rho\mu\widehat f.
\]

Both \(y_0=\mu\) and \(y_1=\rho\) are distance variables.

### 8.3 Point family B

For offset face \(F\), the variables are

\[
y=(\delta,b_0,\ldots,b_{k-1},
   \widehat f_{\mathrm{free}}).
\]

Their bounds are

\[
0\leq\delta\leq\texttt{radius},
\qquad
\frac{U_{b,j}^{\rm lo}}{\texttt{ratio}}
\leq b_j\leq
\frac{U_{b,j}^{\rm hi}}{\texttt{ratio}}.
\]

The map is

\[
z_b=\delta b,
\qquad
z_o=\delta\widehat f.
\]

The sole distance variable is \(y_0=\delta\).

### 8.4 Sheared family A-prime

The variable order matches family A:

\[
y=(\mu,\rho',\widehat b_{\mathrm{free}},
   \widehat f'_{\mathrm{free}}).
\]

The \(\mu\) bound uses the base-face radius.
The \(\rho'\) bound is `[0,window.radius]`.

Let \(S\) be `window.shear`, with one row per offset coordinate.
In the original cover coordinates,

\[
z_b=\mu\widehat b,
\qquad
z_o=\rho'\mu\widehat f'-S(\mu\widehat b).
\]

Both \(y_0=\mu\) and \(y_1=\rho'\) are distance variables.

For the crossing covers, \(S=(0,1,0,0)^T\).
This gives \(\theta=\theta'-e\).

### 8.5 Factor vectors

A leaf factor is `[a0,a1,a2,a3,a4]`.
It denotes

\[
y_0^{a_0}y_1^{a_1}y_2^{a_2}y_3^{a_3}y_4^{a_4}.
\]

Every exponent is an integer from `0` through `255`.
A positive exponent is permitted only at a distance-variable position for that zoom.

## 9. Cell-tree grammar

The grammar is recursive:

```text
tree := "." | digit tree tree
digit := "0" | "1" | "2" | "3" | "4"
```

A digit \(j\) bisects variable \(y_j\) at its exact midpoint.
For interval \([l,h]\), the children are

\[
[l,(l+h)/2]
\quad\text{and}\quad
[(l+h)/2,h].
\]

Both children are closed.
The string is a preorder traversal.
The lower child appears before the upper child.
A period is a leaf.

The whole string must parse as exactly one tree.
Early termination, invalid bytes, and trailing bytes fail.

Enumerate leaf cells when their periods occur in preorder.
`leaves[i]` describes leaf cell \(i\) in that same order.
The two arrays must have equal lengths.

## 10. Witness semantics

Let \(v_i\in K^3\) be vertex \(i\).
Let

\[
d(r)=1+r\mathbin\cdot r,
\]

\[
\widehat R(r)=(1-r\mathbin\cdot r)I+2rr^T+2[r]_\times.
\]

Then \(\widehat R(r)=d(r)R(r)\).

Every stored witness denotes a necessary inequality \(g\geq0\) for a weak containment.
The checker proves that its divided pullback is strictly negative.

### 10.1 Ordered-edge gap

The form is

```json
{"edge":[from,to],"vertex":plug}
```

`from` and `to` are vertex indices.
Their unordered pair must be an RID edge.
The order remains significant.

Define

\[
v_h=v_{\rm from},
\qquad
v_p=v_{\rm plug},
\qquad
n(u)=u\mathbin\times(v_{\rm to}-v_{\rm from}).
\]

The hole contact vertex is `from`.
The witness polynomial is

\[
g(u,r)=d(r)n(u)\mathbin\cdot v_h
       -n(u)\mathbin\cdot\widehat R(r)v_p.
\]

Reversing the edge reverses the normal and changes the witness.

### 10.2 Fixed-direction gap

The form is

```json
{"direction":[[a1,b1],[a2,b2]],"contact":h,"vertex":plug}
```

The planar screen normal is

\[
(n_1,n_2)=(a_1+b_1\sqrt5,a_2+b_2\sqrt5).
\]

It must be nonzero.
`contact` is the hole vertex \(h\).
`vertex` is the plug vertex \(p\).

For \(u=(u_1,u_2,u_3)\), define

\[
n(u)=(n_1u_3,n_2u_3,-n_1u_1-n_2u_2).
\]

Use the same gap polynomial

\[
g(u,r)=d(r)n(u)\mathbin\cdot v_h
       -n(u)\mathbin\cdot\widehat R(r)v_p.
\]

### 10.3 Domain witness

The form is

```json
{"inequality":i}
```

It denotes

\[
g(u,r)=-q_i(u,r).
\]

This witness is valid only for a cover whose `scope` is `"domain"`.

### 10.4 Support validity

At every required corner view, prove \(u_3>0\).
For a gap witness, prove

\[
n(u)\mathbin\cdot(v_h-v_w)\geq0
\qquad\text{for every }w=0,\ldots,59.
\]

The view map is multilinear, so exact corner checks cover the cell.
A corner where \(n(u)=0\) contributes only equalities and may be skipped.
A domain witness needs no support test.

### 10.5 Division and Bernstein sign

Pull the witness back through the complete zoom map:

\[
G(y)=g(u(y),r(y)).
\]

Divide every monomial exactly by the stored factor \(y^a\).
Failure of exact divisibility rejects the leaf.

Let

\[
N(y)=G(y)/y^a.
\]

Every tensor-product Bernstein coefficient of \(N\) on the closed leaf cell must be strictly negative.
Zero fails.

Equivalently, one may use \(p=-g\) and require strictly positive coefficients.
The canonical convention in this specification is \(g\geq0\) with strictly negative coefficients.

## 11. Delegated hand-over

Only an unsheared family-A leaf may contain the JSON value `"delegated"`.
Its base face must occur in `window.faces`.

Reconstruct \(\widehat b\) and \(\widehat f\) from the leaf's source zoom variables.
Let \(S\) be `window.shear`.
Define the window vector

\[
w=\rho\widehat f+S\widehat b.
\]

For the whole delegated cell, each coordinate must satisfy

\[
\texttt{window.radius}\,U_{o,l}^{\rm lo}
\leq w_l\leq
\texttt{window.radius}\,U_{o,l}^{\rm hi}.
\]

The exact range uses interval arithmetic.
Each term \(\rho\widehat f_l\) is independent of the base-free terms.

For a point in the cell, compute the offset-box gauge of \(w\):

\[
\rho'=\max_l |w_l|.
\]

Only signs permitted by the one-sided or two-sided unit-box axis are eligible.
On a tie, choose the first eligible axis in increasing axis order.

If \(w=0\), the point lies in the no-fit set.
No target zoom is needed.

Otherwise, let \(F'\) be the selected offset face.
The target is the unique sheared zoom with the source base face \(G\) and offset face \(F'\).
Its variables are

\[
y'=(\mu,\rho',\widehat b_{\mathrm{free}},
    (w/\rho')_{\mathrm{free}}).
\]

The target variables must lie in that target zoom's closed root.
The source and target zoom maps must give exactly the same adapted coordinates \(x\).

The identity follows from

\[
\rho'\widehat f'-S\widehat b
=\rho\widehat f.
\]

## 12. Pentagon extension

`beyond` is either `null` or

```json
{"axis":a,"inequality":i}
```

Let \(U_a\) be the upper bound of cover coordinate \(z_a\).
The declaration is valid only if the exact identity

\[
q_i(c+Mz)=\kappa(z_a-U_a)
\]

holds as a polynomial for a constant \(\kappa>0\).
No other monomial may remain.

The covered set then has no upper bound on \(z_a\).
It keeps the lower bound on \(z_a\) and both bounds on every other coordinate.
Any point with \(z_a>U_a\) violates \(q_i\leq0\).

The pentagon file has

```json
{"axis":1,"inequality":0}
```

Here \(z_1=\xi\), \(U_1=0\), and

\[
q_0=\phi\xi.
\]

Thus \(\kappa=\phi>0\).

## 13. JSON structure

[`rid-cover.schema.json`](rid-cover.schema.json) gives the structural schema.
The rules below complete the semantic schema.

### 13.1 Top-level object

Every field is required and appears in this order:

1. `format`: exactly `"rid-cover/1"`;
2. `name`: a string;
3. `scope`: `"all"` or `"domain"`;
4. `parameters`: a parameters object;
5. `witnesses`: an array of witnesses;
6. `zooms`: an array of zoom entries.

For the required catalogue:

- `local/0.json` through `local/29.json` have matching decimal names and scope `"all"`;
- the eight exotic paths and names appear in [`cover-inventory.json`](cover-inventory.json);
- every exotic cover has scope `"domain"`;
- every `parameters` value equals the matching inventory value;
- every ordered zoom name and root equals the matching inventory value.

### 13.2 Parameters

Every parameters object contains, in order:

1. `coordinates`;
2. `centre`, exactly five \(K\) numbers;
3. `map`, exactly five rows of five \(K\) numbers;
4. `shape`;
5. `beyond`, present as an object or `null`.

The matrix must be nonsingular.

A tube shape contains `base`, `offset`, and `radius` in that order.
A point shape contains `base`, `offset`, `radii`, `radius`, `ratio`, and `window` in that order.
The `window` field is required and may be `null`.
A non-null window contains `faces`, `shear`, and `radius` in that order.
A face contains `axis` and `side` in that order.
A `beyond` object contains `axis` and `inequality` in that order.

Both base and offset dimensions are positive and sum to five.
Every required radius, ratio, and interval width is strictly positive.

For a point shape:

- `radii.length` equals `faces(base).length`;
- a window shear has one row per offset axis and one column per base axis;
- `window.faces` is nonempty, contains no duplicate, and contains only base faces;
- `window.radius` is positive.

### 13.3 Witness objects

A witness has exactly one of these field sets and field orders:

- `edge`, `vertex`;
- `direction`, `contact`, `vertex`;
- `inequality`.

Vertex indices range from `0` through `59`.
An inequality index ranges from `0` through `72`.
The edge must pass the exact edge test from Section 3.

### 13.4 Zoom entries and leaves

A zoom entry contains `name`, `tree`, and `leaves` in that order.
Its position, name, and root must match the inventory.

A leaf is either:

- `{"witness":{"index":i,"factor":[a0,a1,a2,a3,a4]}}`; or
- the string `"delegated"`.

The witness index must be below `witnesses.length`.
Every factor exponent ranges from `0` through `255`.
The tree and leaf rules from Sections 8 and 9 apply.

`scope:"all"` forbids domain witnesses.
Delegation must satisfy Section 11.

### 13.5 Unknown, missing, repeated, and null fields

Every object rejects unknown fields.
Every listed field is required.
Repeated object keys fail.
`null` is valid only for the required `beyond` and `window` fields.

### 13.6 Canonical bytes

A file is accepted only when parsing and canonical reserialisation reproduce the input bytes exactly.
The canonical encoding has:

- UTF-8 JSON;
- the field orders stated above;
- compact separators, with no insignificant whitespace;
- canonical rational strings;
- decimal JSON integers with no leading plus sign or redundant zero;
- `null` spelled exactly as shown;
- one final line-feed byte;
- no other trailing byte.

Strings use double quotes.
Escape quote and backslash as `\"` and `\\`.
Use `\b`, `\t`, `\n`, `\f`, and `\r` for those five control characters.
Encode every other `U+0000` through `U+001F` character as lowercase `\u00xx`.
Encode all remaining Unicode characters directly as UTF-8.
Do not escape `/`.

The 38 supplied files are canonical examples of this encoding.

## 14. Complete verification obligations

A conforming checker must perform all of these checks.

1. Parse the canonical JSON and reject every schema violation.
2. Match the required cover name, scope, parameters, zoom order, names, and roots.
3. Reconstruct every tree and bind every `leaves[]` entry to its cell.
4. Check that every root's leaf cells tile the root exactly.
5. Validate every witness index, support, factor, and scope.
6. Pull back the exact witness polynomial and divide by the exact factor.
7. Prove \(u_3>0\), support validity, and strict Bernstein negativity.
8. Validate every delegated cell and its sheared hand-over.
9. Validate every `beyond` identity and its remaining containment bounds.

The checker must fail closed.
An unknown value, ambiguous binding, failed identity, or zero Bernstein coefficient rejects the proof.
