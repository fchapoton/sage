"""
Spaces of Distributions

"""
#*****************************************************************************
#       Copyright (C) 2012 Robert Pollack <rpollack@math.bu.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.modules.module import Module
from sage.structure.parent import Parent
from sage.rings.padics.factory import ZpCA, QpCR
from sage.rings.padics.padic_generic import pAdicGeneric
from sage.rings.rational_field import QQ
from sage.rings.integer_ring import ZZ
from sage.misc.cachefunc import cached_method
from sage.categories.modules import Modules
from sage.modular.pollack_stevens.dist import get_dist_classes # , Dist_long
from sage.structure.factory import UniqueFactory

import sage.rings.ring as ring

from sigma0 import _default_adjuster


class Distributions_factory(UniqueFactory):
    """
    Create a space of distributions.

    INPUT:

    - `k` -- nonnegative integer
    - `p` -- prime number or None
    - ``prec_cap`` -- positive integer or None
    - ``base`` -- ring or None
    - ``character`` -- a dirichlet character or None
    - ``adjuster`` -- None or callable that turns `2 \times 2` matrices into a 4-tuple
    - ``act_on_left`` -- bool (default: False)
    - ``dettwist`` -- integer or None (interpreted as 0)
    - ``act_padic`` -- whether monoid should allow p-adic coefficients
    - ``implementation`` -- string (default: None) Either None (for automatic), 'long', or 'vector'

    EXAMPLES::

        sage: D = Distributions(3, 11, 20)
        sage: D
        Space of 11-adic distributions with k=3 action and precision cap 20
        sage: v = D([1,0,0,0,0])
        sage: v.act_right([2,1,0,1])
        (8 + O(11^5), 4 + O(11^4), 2 + O(11^3), 1 + O(11^2), 6 + 4*11 + O(11))

    Note that we would expect something more p-adic, but fine...

        sage: D = Distributions(3, 11, 20, dettwist=1)
        sage: v = D([1,0,0,0,0])
        sage: v.act_right([2,1,0,1])
        (5 + 11 + O(11^5), 8 + O(11^4), 4 + O(11^3), 2 + O(11^2), 1 + O(11))
    """
    def create_key(self, k, p=None, prec_cap=None, base=None, character=None,
                   adjuster=None, act_on_left=False, dettwist=None,
                   act_padic=False, implementation=None):
        """
        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions
            sage: Distributions(20, 3, 10)              # indirect doctest
            Space of 3-adic distributions with k=20 action and precision cap 10
            sage: TestSuite(Distributions).run()
        """
        k = ZZ(k)

        if p is None:
            try:
                p = base.prime()
            except AttributeError:
                raise ValueError("You must specify a prime")
        else:
            p = ZZ(p)

        if base is None:
            if prec_cap is None:
                base = ZpCA(p)
            else:
                base = ZpCA(p, prec_cap)

        if prec_cap is None:
            try:
                prec_cap = base.precision_cap()
            except AttributeError:
                raise ValueError("You must specify a base or precision cap")

        if adjuster is None:
            adjuster = _default_adjuster()

        if dettwist is not None:
            dettwist = ZZ(dettwist)
            if dettwist == 0:
                dettwist = None

        return (k, p, prec_cap, base, character, adjuster, act_on_left,
                dettwist, act_padic, implementation)

    def create_object(self, version, key):
        """
        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: Distributions(0, 7, 5)              # indirect doctest
            Space of 7-adic distributions with k=0 action and precision cap 5
        """
        return Distributions_class(*key)


class Symk_factory(UniqueFactory):
    r"""
    Create the space of polynomial distributions of degree k (stored as a sequence of k + 1 moments).

    INPUT:

    - ``k`` (integer): the degree (degree `k` corresponds to weight `k + 2` modular forms)
    - ``base`` (ring, default None): the base ring (None is interpreted as `\QQ`)
    - ``character`` (Dirichlet character or None, default None) the character
    - ``adjuster`` (None or a callable that turns `2 \times 2` matrices into a 4-tuple, default None)
    - ``act_on_left`` (boolean, default False) whether to have the group acting
      on the left rather than the right.
    - ``dettwist`` (integer or None) -- power of determinant to twist by

    EXAMPLE::

        sage: D = Symk(4)
        sage: loads(dumps(D)) is D
        True
        sage: loads(dumps(D)) == D
        True
        sage: from sage.modular.pollack_stevens.distributions import Symk
        sage: Symk(5)
        Sym^5 Q^2
        sage: Symk(5, RR)
        Sym^5 (Real Field with 53 bits of precision)^2
        sage: Symk(5, oo.parent()) # don't do this
        Sym^5 (The Infinity Ring)^2
        sage: Symk(5, act_on_left = True)
        Sym^5 Q^2

    The ``dettwist`` attribute::

        sage: V = Symk(6)
        sage: v = V([1,0,0,0,0,0,0])
        sage: v.act_right([2,1,0,1])
        (64, 32, 16, 8, 4, 2, 1)
        sage: V = Symk(6, dettwist=-1)
        sage: v = V([1,0,0,0,0,0,0])
        sage: v.act_right([2,1,0,1])
        (32, 16, 8, 4, 2, 1, 1/2)
    """
    def create_key(self, k, base=None, character=None, adjuster=None,
                   act_on_left=False, dettwist=None, act_padic=False,
                   implementation=None):
        r"""
        Sanitize input.

        EXAMPLE::

            sage: from sage.modular.pollack_stevens.distributions import Symk
            sage: Symk(6) # indirect doctest
            Sym^6 Q^2

            sage: V = Symk(6, Qp(7))
            sage: TestSuite(V).run()
        """
        k = ZZ(k)
        if adjuster is None:
            adjuster = _default_adjuster()
        if base is None:
            base = QQ
        return (k, base, character, adjuster, act_on_left, dettwist,
                act_padic, implementation)

    def create_object(self, version, key):
        r"""
        EXAMPLE::

            sage: from sage.modular.pollack_stevens.distributions import Symk
            sage: Symk(6) # indirect doctest
            Sym^6 Q^2
        """
        return Symk_class(*key)

Distributions = Distributions_factory('Distributions')
Symk = Symk_factory('Symk')


class Distributions_abstract(Module):
    """
    Parent object for distributions. Not to be used directly, see derived
    classes :class:`Symk_class` and :class:`Distributions_class`.

    EXAMPLES::

        sage: from sage.modular.pollack_stevens.distributions import Distributions
        sage: Distributions(2, 17, 100)
        Space of 17-adic distributions with k=2 action and precision cap 100
    """
    def __init__(self, k, p=None, prec_cap=None, base=None, character=None,
                 adjuster=None, act_on_left=False, dettwist=None,
                 act_padic=False, implementation=None):
        """
        INPUT:

        - `k`             -- integer; k is the usual modular forms weight minus 2
        - `p`             -- None or prime
        - ``prec_cap``    -- None or positive integer
        - ``base``        -- None or TODO
        - ``character``   -- None or Dirichlet character
        - ``adjuster``    -- None or TODO
        - ``act_on_left`` -- bool (default: False)
        - ``dettwist``    -- None or integer (twist by determinant). Ignored for Symk spaces
        - ``act_padic``   -- bool (default: False) If true, will allow action by p-adic matrices.
        - ``implementation`` -- string (default: None) Either automatic (if None), 'vector' or 'long'.

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions
            sage: D = Distributions(2, 3, 5); D
            Space of 3-adic distributions with k=2 action and precision cap 5
            sage: type(D)
            <class 'sage.modular.pollack_stevens.distributions.Distributions_class_with_category'>

        p must be a prime, but p=6 below, which is not prime::

            sage: Distributions(k=0, p=6, prec_cap=10)
            Traceback (most recent call last):
            ...
            ValueError: p must be prime
        """
        if not isinstance(base, ring.Ring):
            raise TypeError("base must be a ring")
        from sage.rings.padics.pow_computer import PowComputer
        # should eventually be the PowComputer on ZpCA once that uses longs.
        Dist, WeightKAction = get_dist_classes(p, prec_cap, base,
                                               self.is_symk(), implementation)
        self.Element = Dist
        # if Dist is Dist_long:
        #     self.prime_pow = PowComputer(p, prec_cap, prec_cap, prec_cap)
        Parent.__init__(self, base, category=Modules(base))
        self._k = k
        self._p = p
        self._prec_cap = prec_cap
        self._character = character
        self._adjuster = adjuster
        self._dettwist = dettwist

        if self.is_symk() or character is not None:
            self._act = WeightKAction(self, character, adjuster, act_on_left,
                                      dettwist, padic=act_padic)
        else:
            self._act = WeightKAction(self, character, adjuster, act_on_left,
                                      dettwist, padic=True)

        self._populate_coercion_lists_(action_list=[self._act])

    def _element_constructor_(self, val):
        """
        Construct a distribution from data in ``val``

        EXAMPLES::

            sage: V = Symk(6)
            sage: v = V([1,2,3,4,5,6,7]); v
            (1, 2, 3, 4, 5, 6, 7)
        """
        return self.Element(val, self)

    def _coerce_map_from_(self, other):
        """
        Determine if self has a coerce map from other.

        EXAMPLES::

            sage: V = Symk(4)
            sage: W = V.base_extend(QQ[i])
            sage: W.has_coerce_map_from(V) # indirect doctest
            True

        Test some coercions::

            sage: v = V.an_element()
            sage: w = W.an_element()
            sage: v + w
            (0, 2, 4, 6, 8)
            sage: v == w
            True
        """
        return (isinstance(other, Distributions_abstract)
                and other._k == self._k
                and self._character == other._character
                and self.base_ring().has_coerce_map_from(other.base_ring())
                and (self.is_symk() or not other.is_symk()))

    def acting_matrix(self, g, M):
        r"""
        Return the matrix for the action of `g` on ``self``, truncated to
        the first `M` moments.

        EXAMPLE::

            sage: V = Symk(3)
            sage: from sage.modular.pollack_stevens.sigma0 import Sigma0
            sage: V.acting_matrix(Sigma0(1)([3,4,0,1]), 4)
            [27 36 48 64]
            [ 0  9 24 48]
            [ 0  0  3 12]
            [ 0  0  0  1]
        """
        # TODO: Add examples with a non-default action adjuster
        return self._act.acting_matrix(g, M)

    def prime(self):
        """
        Return prime `p` such that this is a space of `p`-adic distributions.

        In case this space is Symk of a non-padic field, we return 0.

        OUTPUT:

        - a prime

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Distributions(0, 7); D
            Space of 7-adic distributions with k=0 action and precision cap 20
            sage: D.prime()
            7
            sage: D = Symk(4, base=GF(7)); D
            Sym^4 (Finite Field of size 7)^2
            sage: D.prime()
            0

        But Symk of a `p`-adic field does work::

            sage: D = Symk(4, base=Qp(7)); D
            Sym^4 Q_7^2
            sage: D.prime()
            7
            sage: D.is_symk()
            True
        """
        return self._p

    def weight(self):
        """
        Return the weight of this distribution space.  The standard
        caveat applies, namely that the weight of `Sym^k` is
        defined to be `k`, not `k+2`.

        OUTPUT:

        - nonnegative integer

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Distributions(0, 7); D
            Space of 7-adic distributions with k=0 action and precision cap 20
            sage: D.weight()
            0
            sage: Distributions(389, 7).weight()
            389
        """
        return self._k

    def precision_cap(self):
        """
        Return the precision cap on distributions.

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Distributions(0, 7, 10); D
            Space of 7-adic distributions with k=0 action and precision cap 10
            sage: D.precision_cap()
            10
            sage: D = Symk(389, base=QQ); D
            Sym^389 Q^2
            sage: D.precision_cap()
            390
        """
        return self._prec_cap

    def lift(self, p=None, M=None, new_base_ring=None):
        """
        Return distribution space that contains lifts with given p,
        precision cap M, and base ring new_base_ring.

        INPUT:

        - `p` -- prime or None
        - `M` -- nonnegative integer or None
        - ``new_base_ring`` -- ring or None

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Symk(0, Qp(7)); D
            Sym^0 Q_7^2
            sage: D.lift(M=20)
            Space of 7-adic distributions with k=0 action and precision cap 20
            sage: D.lift(p=7, M=10)
            Space of 7-adic distributions with k=0 action and precision cap 10
            sage: D.lift(p=7, M=10, new_base_ring=QpCR(7,15)).base_ring()
            7-adic Field with capped relative precision 15
        """
        if self._character is not None:
            if self._character.base_ring() != QQ:
            # need to change coefficient ring for character
                raise NotImplementedError
        if M is None:
            M = self._prec_cap + 1

        # sanitize new_base_ring. Don't want it to end up being QQ!
        if new_base_ring is None:
            new_base_ring = self.base_ring()
        try:
            pp = new_base_ring.prime()
        except AttributeError:
            pp = None

        if p is None and pp is None:
            raise ValueError("You must specify a prime")
        elif pp is None:
            new_base_ring = QpCR(p, M)
        elif p is None:
            p = pp
        elif p != pp:
            raise ValueError("Inconsistent primes")
        return Distributions(k=self._k, p=p, prec_cap=M, base=new_base_ring, character=self._character, adjuster=self._adjuster, act_on_left=self._act.is_left())

    @cached_method
    def approx_module(self, M=None):
        """
        Return the M-th approximation module, or if M is not specified,
        return the largest approximation module.

        INPUT:

        - `M` -- None or nonnegative integer that is at most the precision cap

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions
            sage: D = Distributions(0, 5, 10)
            sage: D.approx_module()
            Ambient free module of rank 10 over the principal ideal domain 5-adic Ring with capped absolute precision 10
            sage: D.approx_module(1)
            Ambient free module of rank 1 over the principal ideal domain 5-adic Ring with capped absolute precision 10
            sage: D.approx_module(0)
            Ambient free module of rank 0 over the principal ideal domain 5-adic Ring with capped absolute precision 10

        Note that M must be at most the precision cap, and must be nonnegative::

            sage: D.approx_module(11)
            Traceback (most recent call last):
            ...
            ValueError: M (=11) must be less than or equal to the precision cap (=10)
            sage: D.approx_module(-1)
            Traceback (most recent call last):
            ...
            ValueError: rank (=-1) must be nonnegative
        """

#        print "Calling approx_module with self = ",self," and M = ",M
        if M is None:
            M = self._prec_cap
        elif M > self._prec_cap:
            raise ValueError("M (=%s) must be less than or equal to the precision cap (=%s)" % (M, self._prec_cap))
        elif M < self._prec_cap and self.is_symk():
            raise ValueError("Sym^k objects do not support approximation "
                             "modules")
        return self.base_ring() ** M

    def random_element(self, M=None, **args):
        """
        Return a random element of the M-th approximation module with
        non-negative valuation.

        INPUT:

        - `M` -- None or a nonnegative integer

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions
            sage: D = Distributions(0, 5, 10)
            sage: D.random_element()
            (..., ..., ..., ..., ..., ..., ..., ..., ..., ...)
            sage: D.random_element(0)
            ()
            sage: D.random_element(5)
            (..., ..., ..., ..., ...)
            sage: D.random_element(-1)
            Traceback (most recent call last):
            ...
            ValueError: rank (=-1) must be nonnegative
            sage: D.random_element(11)
            Traceback (most recent call last):
            ...
            ValueError: M (=11) must be less than or equal to the precision cap (=10)
        """
        if M is None:
            M = self.precision_cap()
        R = self.base_ring()
        return self((R ** M).random_element(**args))
##        return self(self.approx_module(M).random_element())

    def clear_cache(self):
        """
        Clear some caches that are created only for speed purposes.

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Distributions(0, 7, 10)
            sage: D.clear_cache()
        """
        self.approx_module.clear_cache()
        self._act.clear_cache()

    @cached_method
    def basis(self, M=None):
        """
        Return a basis for this space of distributions.

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Distributions(0, 7, 4); D
            Space of 7-adic distributions with k=0 action and precision cap 4
            sage: D.basis()
            [(1 + O(7^4), O(7^3), O(7^2), O(7)),
             (O(7^4), 1 + O(7^3), O(7^2), O(7)),
             (O(7^4), O(7^3), 1 + O(7^2), O(7)),
             (O(7^4), O(7^3), O(7^2), 1 + O(7))]            
            sage: D = Symk(3, base=QQ); D
            Sym^3 Q^2
            sage: D.basis()
            [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
        """
        V = self.approx_module(M)
        return [self(v) for v in V.basis()]

    def _an_element_(self):
        """
        Return a typical element of self.

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions
            sage: D = Distributions(0, 7, 4); D
            Space of 7-adic distributions with k=0 action and precision cap 4
            sage: D.an_element() # indirect doctest
            (2 + O(7^2), 1 + O(7))
        """
        if self._prec_cap > 1:
            return self([2, 1])
        else:
            return self([1])


class Symk_class(Distributions_abstract):

    def __init__(self, k, base, character, adjuster, act_on_left, dettwist,
                 act_padic, implementation):
        r"""
        EXAMPLE::

            sage: D = sage.modular.pollack_stevens.distributions.Symk(4); D
            Sym^4 Q^2
            sage: TestSuite(D).run() # indirect doctest
        """
        if hasattr(base, 'prime'):
            p = base.prime()
        else:
            p = ZZ(0)
        Distributions_abstract.__init__(self, k, p, k + 1, base, character,
                                        adjuster, act_on_left, dettwist,
                                        act_padic, implementation)

    def _an_element_(self):
        r"""
        Return a representative element of ``self``.

        EXAMPLE::

            sage: from sage.modular.pollack_stevens.distributions import Symk
            sage: D = Symk(3, base=QQ); D
            Sym^3 Q^2
            sage: D.an_element()                  # indirect doctest
            (0, 1, 2, 3)
        """
        return self(range(self.weight() + 1))

    def _repr_(self):
        """
        EXAMPLES::

            sage: Symk(6)
            Sym^6 Q^2
            sage: Symk(6,dettwist=3)
            Sym^6 Q^2 * det^3
            sage: Symk(6,character=DirichletGroup(7,QQ).0)
            Sym^6 Q^2 twisted by Dirichlet character modulo 7 of conductor 7 mapping 3 |--> -1
            sage: Symk(6,character=DirichletGroup(7,QQ).0,dettwist=3)
            Sym^6 Q^2 * det^3 twisted by Dirichlet character modulo 7 of conductor 7 mapping 3 |--> -1

        """
        if self.base_ring() is QQ:
            V = 'Q^2'
        elif self.base_ring() is ZZ:
            V = 'Z^2'
        elif isinstance(self.base_ring(), pAdicGeneric) and self.base_ring().degree() == 1:
            if self.base_ring().is_field():
                V = 'Q_%s^2' % self._p
            else:
                V = 'Z_%s^2' % self._p
        else:
            V = '(%s)^2' % self.base_ring()
        s = "Sym^%s %s" % (self._k, V)
        if self._dettwist is not None and self._dettwist != 0:
            s += " * det^%s" % self._dettwist
        if self._character is not None:
            s += " twisted by %s" % self._character
        return s

    def is_symk(self):
        """
        Whether or not this distributions space is Sym^k (ring).

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Distributions(4, 17, 10); D
            Space of 17-adic distributions with k=4 action and precision cap 10
            sage: D.is_symk()
            False
            sage: D = Symk(4); D
            Sym^4 Q^2
            sage: D.is_symk()
            True
            sage: D = Symk(4, base=GF(7)); D
            Sym^4 (Finite Field of size 7)^2
            sage: D.is_symk()
            True
        """
        return True

    def change_ring(self, new_base_ring):
        """
        Return a Symk with the same k but a different base ring.

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Distributions(0, 7, 4); D
            Space of 7-adic distributions with k=0 action and precision cap 4
            sage: D.base_ring()
            7-adic Ring with capped absolute precision 4
            sage: D2 = D.change_ring(QpCR(7)); D2
            Space of 7-adic distributions with k=0 action and precision cap 4
            sage: D2.base_ring()
            7-adic Field with capped relative precision 20
        """
        return Symk(k=self._k, base=new_base_ring, character=self._character, adjuster=self._adjuster, act_on_left=self._act.is_left())

    def base_extend(self, new_base_ring):
        r"""
        Extend scalars to a new base ring.

        EXAMPLE::

            sage: Symk(3).base_extend(Qp(3))
            Sym^3 Q_3^2
        """
        if not new_base_ring.has_coerce_map_from(self.base_ring()):
            raise ValueError("New base ring (%s) does not have a coercion from %s" % (new_base_ring, self.base_ring()))
        return self.change_ring(new_base_ring)


class Distributions_class(Distributions_abstract):
    r"""
    EXAMPLES::

        sage: from sage.modular.pollack_stevens.distributions import Distributions
        sage: D = Distributions(0, 5, 10)
        sage: TestSuite(D).run()
    """

    def _repr_(self):
        """
        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: Distributions(0, 5, 10)._repr_()
            'Space of 5-adic distributions with k=0 action and precision cap 10'
            sage: Distributions(0, 5, 10)
            Space of 5-adic distributions with k=0 action and precision cap 10

        Examples with twists::

            sage: Distributions(0,3,4)
            Space of 3-adic distributions with k=0 action and precision cap 4
            sage: Distributions(0,3,4,dettwist=-1)
            Space of 3-adic distributions with k=0 action and precision cap 4 twistted by det^-1
            sage: Distributions(0,3,4,character=DirichletGroup(3).0)
            Space of 3-adic distributions with k=0 action and precision cap 4 twistted by (Dirichlet character modulo 3 of conductor 3 mapping 2 |--> -1)
            sage: Distributions(0,3,4,character=DirichletGroup(3).0,dettwist=-1)
            Space of 3-adic distributions with k=0 action and precision cap 4 twistted by det^-1 * (Dirichlet character modulo 3 of conductor 3 mapping 2 |--> -1)
        """
        s = "Space of %s-adic distributions with k=%s action and precision cap %s" % (self._p, self._k, self._prec_cap)
        twiststuff = []
        if self._dettwist is not None:
            twiststuff.append("det^%s" % self._dettwist)
        if self._character is not None:
            twiststuff.append("(%s)" % self._character)
        if twiststuff:
            s += " twistted by " + " * ".join(twiststuff)
        return s

    def is_symk(self):
        """
        Whether or not this distributions space is Sym^k (ring).

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Distributions(4, 17, 10); D
            Space of 17-adic distributions with k=4 action and precision cap 10
            sage: D.is_symk()
            False
            sage: D = Symk(4); D
            Sym^4 Q^2
            sage: D.is_symk()
            True
            sage: D = Symk(4, base=GF(7)); D
            Sym^4 (Finite Field of size 7)^2
            sage: D.is_symk()
            True
        """
        return False

    def change_ring(self, new_base_ring):
        """
        Return space of distributions like this one, but with the base ring changed.

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Distributions(0, 7, 4); D
            Space of 7-adic distributions with k=0 action and precision cap 4
            sage: D.base_ring()
            7-adic Ring with capped absolute precision 4
            sage: D2 = D.change_ring(QpCR(7)); D2
            Space of 7-adic distributions with k=0 action and precision cap 4
            sage: D2.base_ring()
            7-adic Field with capped relative precision 20
        """
        return Distributions(k=self._k, p=self._p, prec_cap=self._prec_cap, base=new_base_ring, character=self._character, adjuster=self._adjuster, act_on_left=self._act.is_left())

    def specialize(self, new_base_ring=None):
        """
        Return distribution space got by specializing to Sym^k, over
        the new_base_ring.  If new_base_ring is not given, use current
        base_ring.

        EXAMPLES::

            sage: from sage.modular.pollack_stevens.distributions import Distributions, Symk
            sage: D = Distributions(0, 7, 4); D
            Space of 7-adic distributions with k=0 action and precision cap 4
            sage: D.is_symk()
            False
            sage: D2 = D.specialize(); D2
            Sym^0 Z_7^2
            sage: D2.is_symk()
            True
            sage: D2 = D.specialize(QQ); D2
            Sym^0 Q^2
        """
        if self._character is not None:
            raise NotImplementedError
        if new_base_ring is None:
            new_base_ring = self.base_ring()
        return Symk(k=self._k, base=new_base_ring, adjuster=self._adjuster, act_on_left=self._act.is_left())
