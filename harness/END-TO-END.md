# Runtime scenarios

The journeys a consultant takes through Workshop Gen. Each one starts from a freshly
started app with an empty database and goes only through the pages.
Shared runtime verification owns execution and evidence.

## J1: A consultant adds a feature

1. Open the feature list and add a feature named `Goods receipt` in module
   `Warehouse` with the notes `Scan the delivery note, then book the pallets.`
2. The feature list shows `Goods receipt` under a `Warehouse` heading, with
   `0 of 0 ready`.
3. Opening it shows the name, the module and the notes exactly as typed.

**What would make this fail:** the feature is missing from the list, sits under the
wrong module, or its notes are lost or altered.

## J2: A consultant prepares the brief parts

1. On the `Goods receipt` page, add the preparation items `Print sample delivery note`
   and `Create test pallets`.
2. Add the scenario steps `Scan the delivery note`, `Check quantities` and
   `Book to stock`, in that order.
3. Add the questions `Who books partial deliveries?` and `Do you label pallets?`.
4. All seven entries appear on the page; the steps are numbered 1, 2, 3 in the order
   they were added.
5. Tick `Create test pallets`: it shows as ticked and the other item does not.
6. Untick it: it shows as not ticked again.

**What would make this fail:** an entry lands in the wrong list, the steps are out of
order or unnumbered, or ticking one item changes another.

## J3: A consultant prints the brief

1. With `Print sample delivery note` ticked and `Create test pallets` not ticked, open
   the brief page for `Goods receipt`.
2. It shows the title, the module `Warehouse`, the notes, both checklist items with
   their tick state, the three steps numbered 1-3, and both questions.
3. It has no site navigation.
4. The feature list shows `Goods receipt` with `1 of 2 ready`.

**What would make this fail:** any part is missing from the brief, the navigation is
printed with it, or the progress count disagrees with the ticks.

## J4: Bad input is refused

1. Submit the add-feature form with an empty name.
2. The form comes back with an error message (status 400), not a crash.
3. The feature list has no new entry.

**What would make this fail:** a blank feature is saved, or the app answers 500.
