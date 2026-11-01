# Coach: brain breaks unconnected to the manuscript (proposed)

**Status: proposed, not admitted.** Written 2026-10-30 for fleet card AP-LRN-3. Its dependency, OCA-A6
(the syllabus dry run), landed 2026-10-29.

**Owner direction (2026-10-29):** build both exercise kinds: manuscript-connected (the structural prompt
library) and totally novel brain breaks.

**Done bar:**
- a brain-break prompt kind, keyed to the same craft concepts;
- offered for ruts and pressure blocks, alongside manuscript-connected prompts;
- depletion stays a no-prompt zone;
- the writer does the writing.

## The one real change: firewall test 1

Every prompt today must pass the 5-part firewall in `revision-coach/references/structural-prompt-library.md`.
Test 1, **state-grounded**, fails any prompt that "could have been given to almost any writer on almost
any project". A brain break is that by design: it steps away from the book. So this spec gives brain
breaks their own test 1 and keeps tests 2 to 5 unchanged.

- **Test 1 for a brain break: concept-grounded.** The prompt exercises one named craft concept (a
  syllabus lesson's concept, such as stakes, a scene turn or compression) on material the writer invents
  on the spot. It must not touch the manuscript, its characters or its argument.
- **Tests 2 to 5 still apply:**
  - constraint-based: a structural requirement, never an event or outcome;
  - plural-solution;
  - aesthetic-open: the writer supplies every person, place, fact and line;
  - self-evaluative: it ends with a check on the concept.

This keeps the Firewall's purpose (the writer does the writing, and the coach never supplies content)
while dropping the link to the diagnosis that brain breaks exist to escape.

## Where it goes

All the changes are prose, in two files (a third if owner call 1 is a yes).

1. **`structural-prompt-library.md`, a new "Brain breaks" section:**
   - the test 1 variant above;
   - how to make one: take a family (Constraint, Inversion, Isolation, Scale-Shift, Perspective, Deletion,
     Temporal) and a lesson concept, and apply it to invented material. For example, Deletion with
     compression: "Write 150 words about anyone doing anything. Then cut a third without losing what the
     reader needs. Check: what did the cut make clearer?";
   - two worked examples (one passing, one failing on test 4, because it names the scenario);
   - the delivery rules below.
2. **`writers-block-taxonomy.md`, one line per block type that offers one:**
   - **Type 2, Motivational / Avoidance:** beside the exercise library, as an off-project warm-up.
   - **Type 6, Aesthetic / Execution Gap:** practise the skill without the book's stakes. The taxonomy
     already treats this type as closer to craft instruction.
   - **The Perfectionism Modifier:** a brain break is disposable by nature, which is the modifier's whole
     point.
   - **Not offered:**
     - Type 3, depletion (the done bar, and an existing No-Prompt Zone);
     - Type 7, feedback saturation (an existing No-Prompt Zone);
     - any other No-Prompt Zone except "state file missing" (owner call 1).

## Delivery

- **One choice, never a list.** Where a block type allows both, offer one manuscript-connected prompt or
  one brain break, and the writer picks. That keeps the library's "one prompt per corridor, never an
  array" rule.
- **Framing:** low-stakes and disposable. The clinamen clause still applies ("if you find a better
  move by breaking the constraint, that counts").
- **No storage:** nothing is saved. The writer's brain-break text never enters the manuscript, the
  state files or a finding.

## Owner calls

1. **No state file:** may a writer with no `Diagnostic_State.md` or `Argument_State.md` get a brain break?
   Today `/coach stuck` already offers such a writer a state-less run before routing to `/start`
   (`commands/coach.md`; `SKILL.md` §2 "State-less run"). That run skips steps 4 to 6, which include
   prompt generation, and it writes nothing. The library's "state file missing" No-Prompt Zone also
   applies. The proposal is yes, and it adds a third file to the scope. In `SKILL.md` §2's state-less
   paragraph, after the conversation, the coach may offer one brain break in the conversation itself,
   under the same Type 2, Type 6 and perfectionism conditions. Nothing is written, as now. The No-Prompt
   Zone gains "except a brain break in the state-less run". With a no, brain breaks need a state file,
   like every other prompt.
2. **Learning Mode:** may it offer a brain break as the lesson's exercise when the writer hasn't named a
   passage? Today the exercise is grounded in a passage the writer names.

## Not in scope

- Lesson doors and the map (AP-LRN-1, apodictic#418) and see-also links (AP-LRN-2, apodictic#417).
- New prompt families, and any validator: the firewall is applied by the coach, as now.
