# Exact Cost Model for the Shared Gap-Alphabet Stream

## Definitions

Let a byte stream of length \(N\) be partitioned into \(B\) blocks. Block \(i\)
has \(n_i\) bytes and a reduced Zeckendorf gap sequence of length \(k_i\).
The stream alphabet is

\[
\mathcal A=\bigcup_{i=1}^{B}\{g:g\text{ occurs in block }i\},
\qquad a=|\mathcal A|,
\qquad w=\lceil\log_2 a\rceil,
\]

with \(w=0\) when \(a\leq1\). Let

\[
u(x)=
\begin{cases}
1,&x=0,\\
\lfloor\log_{128}x\rfloor+1,&x>0
\end{cases}
\]

be the byte length of unsigned LEB128, and let

\[
q_i=\left\lceil\frac{k_iw}{8}\right\rceil
\]

be the packed identifier length.

The candidate transformed payload for block \(i\) has exact length

\[
p_i=u(k_i)+u(q_i)+q_i.
\]

The block selector uses the transformed payload exactly when \(p_i<n_i\).
Define

\[
s_i=\min(n_i,p_i).
\]

## Exact stream condition

The raw FISA stream has length

\[
L_{\mathrm{raw}}=6+u(N)+N.
\]

The complete shared-alphabet candidate has length

\[
\begin{split}
L_{\mathrm{shared}}={}&6+u(N)+u(b)+u(B)+u(a)+1\\
&+\sum_{g\in\mathcal A}u(g)
+\sum_{i=1}^{B}\left[1+u(n_i)+u(s_i)+s_i\right],
\end{split}
\]

where \(b\) is the nominal block size. The constants include the four-byte
magic, one-byte format identifier, stream mode, and one-byte symbol width.

Therefore the shared representation is selected if and only if

\[
\boxed{
u(b)+u(B)+u(a)+1+\sum_{g\in\mathcal A}u(g)
+\sum_{i=1}^{B}\left[1+u(n_i)+u(s_i)+s_i\right]
<N
}
\]

because the outer magic, format identifier, stream mode, and original-length
field cancel in the comparison.

This is a necessary and sufficient condition for the implemented FISA 1.0
selector. It includes all alphabet values, all length fields, all mode bytes,
and byte padding.

## Per-block sufficient threshold

Let the global metadata cost be

\[
C_{\mathcal A}=u(b)+u(B)+u(a)+1+\sum_{g\in\mathcal A}u(g).
\]

For a full block of \(n\) bytes, a sufficient condition under equal
amortization is

\[
1+u(n)+u(p(k))+p(k)+\left\lceil\frac{C_{\mathcal A}}{B}\right\rceil<n,
\]

where

\[
p(k)=u(k)+u\left(\left\lceil\frac{kw}{8}\right\rceil\right)
+\left\lceil\frac{kw}{8}\right\rceil.
\]

The corresponding computable threshold is

\[
k^\star(n,w,C_{\mathcal A},B)=
\max\left\{k\geq0:
1+u(n)+u(p(k))+p(k)
+\left\lceil\frac{C_{\mathcal A}}{B}\right\rceil<n
\right\}.
\]

Unlike a threshold based only on Zeckendorf weight, this expression accounts
for identifier width, byte alignment, length coding, and amortized alphabet
metadata. It is sufficient per block; the exact stream condition remains less
restrictive because savings may be distributed unevenly across blocks.

## Entropy-rate statement

For a single discrete random variable \(X\), an invertible transform \(R\)
satisfies \(H(R(X))=H(X)\). For a stochastic block process
\((X_t)_{t\geq1}\), componentwise invertibility also preserves the joint
entropy and entropy rate:

\[
H(R(X_1),\ldots,R(X_m))=H(X_1,\ldots,X_m).
\]

It does not preserve a restricted model's empirical order, factorization, or
coding redundancy. A transform can expose dependencies that are cheaper for a
particular finite-context or alphabet model even though the source entropy
rate is unchanged. The shared alphabet exploits this modelling effect rather
than claiming entropy destruction.
