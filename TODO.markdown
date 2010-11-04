Operators
* Implement ROLLUP
* Implement DRILLDOWN
* Implement STORE (stores the result of the query in a table with a
  user-defined name.)
 * Maybe have this be implicit, like
     R = Q.narrow("day = 28")
   rather than
     STORE(Q.narrow("day = 28"), R)
     
* Implement RELATE
 * How should JOIN type be done? Default to natural join, but other than
   that, possibly:
       Q.relate(R, "Q.a = R.a", OUTER)
   would do an outer join on Q.a = R.a.
