# Character Bible — recurring cast for Sean's engagement logs

Continuity matters. The same character drawn three different ways across a page doesn't read as one person — it reads as three random Sergio doodles. This file pins down how each recurring character should be drawn, so prompts stay consistent across an engagement (and across engagements).

When a new character enters Sean's work, add them here.

## Phaethon (Sean himself)

Sean's SOAK Ranger callsign is Phaethon. He is also the dev on every engagement log this skill ships against. He is **not** a Ranger Lead, despite having Lead-tier access on the soak-rangers app. Visual description for every Phaethon prompt:

> a stocky bearded man with round glasses (PHAETHON the Ranger, dark brown Ranger vest with name-patch PHAETHON)

Key traits:

- **Stocky build, not athletic.** Mad-magazine bulbous-nose energy, not action-hero proportions.
- **Beard.** Dark, full but not unkempt.
- **Round glasses.** Simple round frames, not aviators, not designer.
- **Dark brown Ranger vest.** Not khaki tan — Sean is a dirt-Ranger tier, vest is darker. The vest has two front pockets and a small name patch over the right breast that reads PHAETHON in block letters.
- **Often holding tech.** A Chromebook, a clipboard, a wrench, a paintbrush. He's always doing something with his hands.

What Phaethon is **not**:

- Not in a tan/khaki vest (that's the Khaki/OOH tier, not him)
- Not wearing a Ranger floppy hat with a stiff brim (those are for Khaki+ in this universe — Phaethon is hatless)
- Not muscle-bound or lean
- Not clean-shaven, not heavily bearded; medium fullness

## Lazareth

Sean's longtime Ranger friend; the README's "Hey Laz!" Chromebook walkthrough is for him. Most frequent bug-filer after Phaethon. Visual description:

> a Ranger in a dark brown Ranger vest with name-patch LAZARETH

Distinguishing traits beyond the base description aren't fully pinned yet — Grok generally renders him reasonably from the name-patch alone. If asked for a specific Lazareth scene (filing a bug, jabbing a button), keep him in the same dirt-Ranger brown vest as Phaethon and let the name patch do the identity work.

## Tugboat (Chuck Moran)

Khaki/OOH tier. Filed the heaviest single batch of structured feedback on the soak-rangers app (#16–#24, #50–#53). When Tugboat shows up in a panel, he's almost always *cataloguing* — pointing at things, X-ing out signs, writing notes on a clipboard:

> a Ranger in a tan/khaki Ranger vest with name-patch TUGBOAT, holding a fat red marker / clipboard / list

The tan vest visually separates him from Phaethon/Lazareth. Don't draw him in the dark brown.

## Malarkey

One of the four on the 3/20 SvelteKit-reframe call. Filed bugs #31, #32 (incident walkthroughs and must-reports). Generic ranger description with name patch — same approach as Lazareth, keep him in dark brown.

## Volcor

Production tier. Provided the schedule import format. When Volcor appears, he's in production garb — lilac-trimmed vest (the soak-rangers app uses lilac for Production):

> a Ranger in a Production vest with lilac trim, name-patch VOLCOR

## Heron · Nebula

Occasional bug-filers (#49 escalation, #59 assignment overlap). Use the generic Ranger description with their name patch. They don't appear in panels often enough to have a strong visual signature; Grok will render them generically based on the name patch alone.

## Neil Sampson (NWIOI engagement)

Different project. The therapist who was Sean's NWIOI Connect client. He's typically drawn as:

> a kindly therapist with glasses and short hair, holding a clipboard

For NWIOI panels specifically. He doesn't cross over into Ranger panels.

## "A ranger" (generic)

If a panel needs an unnamed Ranger (background crowd, etc.), use:

> a Ranger in a dark brown Ranger vest (no specific name)

This keeps them visually consistent with the named characters without forcing a specific identity.

## When you need a new character

1. Pick a vest color (matters — separates them tier-wise: dark brown = Ranger, tan = Khaki, lilac = Production, red = Lead).
2. Decide on 1–2 distinguishing physical traits (hat? beard? glasses? height?).
3. Give them a name-patch wording.
4. Write a one-sentence visual description in this file under a new heading.
5. Use that exact description every time the character appears in a prompt.

Don't trust Grok to "remember" a character across separate calls. Each `genimg.sh` call is a fresh request — full description every time.

## Why this matters

A page that mixes "Phaethon-the-bearded-glasses-guy" panels with "Phaethon-as-a-clean-shaven-blond" panels reads as a Grok failure, not as a story. Continuity is the difference between *art that tells an engagement's story* and *art that decorates an engagement's page*. Sean wants the former, always.
