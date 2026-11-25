import Lean

/-! Arithmetic step of the proof. Only Lean's standard distribution is used.
The real-variable existence of a trapped prefix interval is a paper proof. -/
namespace PrimeCoverage

/-- The usual divisor definition of a prime natural number. -/
def IsPrime (n : Nat) : Prop :=
  2 ≤ n ∧ ∀ d : Nat, d ∣ n → d = 1 ∨ d = n

theorem existsPrimeDivisor (n : Nat) (hn : 2 ≤ n) :
    ∃ p, IsPrime p ∧ p ∣ n := by
  induction n using Nat.strongInductionOn with
  | _ n ih =>
    by_cases prime : IsPrime n
    · exact ⟨n, prime, Nat.dvd_refl n⟩
    · have bad : ¬ (∀ d : Nat, d ∣ n → d = 1 ∨ d = n) :=
        fun h => prime ⟨hn, h⟩
      apply Classical.byContradiction
      intro none
      apply bad
      intro d divides
      by_cases one : d = 1
      · exact Or.inl one
      · apply Or.inr
        apply Classical.byContradiction
        intro different
        have pos : 0 < d := by
          cases d with
          | zero =>
            obtain ⟨k, hk⟩ := divides
            simp at hk
            omega
          | succ _ => omega
        have upper : d ≤ n := Nat.le_of_dvd (by omega) divides
        obtain ⟨p, hp, hpd⟩ := ih d (by omega) (by omega)
        exact none ⟨p, hp, Nat.dvd_trans hpd divides⟩

/-- base is a positive multiple of a modulus containing all primes up to L.
Every offset from 2 through L gives a composite integer. -/
theorem compositeRun {base q L t : Nat} (hbase : 0 < base) (hqbase : q ∣ base)
    (hq : ∀ p, IsPrime p → p ≤ L → p ∣ q) (ht : 2 ≤ t) (hL : t ≤ L) :
    ¬ IsPrime (base + t) := by
  obtain ⟨p, prime, hpt⟩ := existsPrimeDivisor t ht
  have hle : p ≤ t := Nat.le_of_dvd (by omega) hpt
  have hpb : p ∣ base := Nat.dvd_trans (hq p prime (by omega)) hqbase
  intro contra
  have alternatives := contra.2 p (Nat.dvd_add hpb hpt)
  have hp := prime.1
  omega

/-- A nonempty or empty discrete cylinder lying in the certified run has
no prime witness. The hypothesis on q is satisfied by the paper's primorial. -/
theorem missingWindow {base q L first last : Nat} (hbase : 0 < base)
    (hqbase : q ∣ base) (hq : ∀ p, IsPrime p → p ≤ L → p ∣ q)
    (left : base + 2 ≤ first) (right : last ≤ base + L) :
    ¬ ∃ p, first ≤ p ∧ p ≤ last ∧ IsPrime p := by
  intro witness
  obtain ⟨p, hfirst, hlast, prime⟩ := witness
  let t := p - base
  have ht : 2 ≤ t := by dsimp [t]; omega
  have hL : t ≤ L := by dsimp [t]; omega
  have identity : base + t = p := by dsimp [t]; omega
  exact compositeRun hbase hqbase hq ht hL (identity.symm ▸ prime)

/-- Integer version of the middle-third / quarter-width step. In the proof
center can be floor (12 * B / U). Taking floors in inequalities with integer
shifts gives the hypotheses below for every integer p in the cylinder. -/
theorem missingNarrowWindow {base q L center first last : Nat}
    (hbase : 0 < base) (hqbase : q ∣ base)
    (hq : ∀ p, IsPrime p → p ≤ L → p ∣ q) (large : 24 ≤ L)
    (lower : 12 * base + 4 * L ≤ center) (upper : center ≤ 12 * base + 8 * L)
    (narrow : ∀ p, first ≤ p → p ≤ last →
      center ≤ 12 * p + 3 * L ∧ 12 * p ≤ center + 3 * L) :
    ¬ ∃ p, first ≤ p ∧ p ≤ last ∧ IsPrime p := by
  intro witness
  obtain ⟨p, hfirst, hlast, prime⟩ := witness
  obtain ⟨lo, hi⟩ := narrow p hfirst hlast
  have left : base + 2 ≤ p := by omega
  have right : p ≤ base + L := by omega
  exact missingWindow hbase hqbase hq left right ⟨p, Nat.le_refl _, Nat.le_refl _, prime⟩

#print axioms missingNarrowWindow
end PrimeCoverage
