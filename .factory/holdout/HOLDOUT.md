# Holdout scenarios

Independent scenarios that combine Workshop Gen's behaviour in ways the journeys do
not. Each starts from a freshly started app with an empty database.
The executable holdout assertions are kept outside this repository and given only to
the verification environment.

## Two features, two modules, no leaking

1. Add `Purchase order approval` in module `Purchasing` and `Goods receipt` in module
   `Warehouse`.
2. Give `Purchase order approval` three preparation items and tick two of them. Give
   `Goods receipt` one preparation item and leave it unticked. Add one question only
   to `Goods receipt`.
3. The feature list shows each feature under its own module, `Purchase order approval`
   with `2 of 3 ready` and `Goods receipt` with `0 of 1 ready`.
4. Untick one item on `Purchase order approval`: it now shows `1 of 3 ready`, and
   `Goods receipt` is unchanged.
5. The brief for `Purchase order approval` contains none of `Goods receipt`'s items or
   its question.

## Hostile text stays text

1. Add a feature named `<script>alert(1)</script>` in module `<b>Sales</b>` with notes
   `"quotes" & <i>tags</i>`.
2. Add a question `</ul><h1>broken</h1>` to it.
3. The feature list, the feature page and the brief all show these values literally,
   as typed; none of them becomes markup or runs.
4. Opening a feature id that does not exist, or the id `abc`, answers 404, not 500.
