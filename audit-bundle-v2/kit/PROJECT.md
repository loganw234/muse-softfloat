# The project

## What Logan asked, verbatim (2026-10-23)

> I plan to take part in a hackathon hosted by Meta AI, the goal is to develop an IEEE-754 compliant softfloat for
> RP2040, for binary16/32/64. The math library is only one portion of the project, the other portion is testing how
> Meta models handle the methods and systems I use, along with heavy metrics tracking (cfts most recent work has been
> tracked the most I believe)

The rest of his request was about this kit. His answers since are in OWNER.md.

## What is fixed

- **The work:** "an IEEE-754 compliant softfloat for RP2040, for binary16/32/64".
- **The board:** a Pico, "constantly connected for debugging", whose access the lead controls (BOARD.md).
- **The web:** "Web access to read third-party code and solutions", with cft-fp256 off limits (CLEAN-ROOM.md).
- **The length:** ten days, 2026-10-26 to 2026-11-04.

## The standard

"It wont be included in the zip as its licensed to me, but I will also be giving the Meta lead the real IEEE 754
pdf for reference, so they will have the material needed in terms of the contract, but not necessarily how to
achieve it" (Logan, 2026-10-23). So:

- **The standard is the contract:** what conformance requires.
- **It is not the authority** of HonestFramework's [METHOD.md](method/honest/METHOD.md), section 1. The study names
  an executable authority, and its oracles, and Logan approves them.
- **The PDF is Logan's, under his licence.** It goes in no repository and no zip, and the record cites it by clause.
  That last rule is the kit's reading of "licensed to me", for Logan to confirm at kickoff.
- **Who besides the lead reads it** is the lead's decision. It may sit in a directory the lead gives that
  reader, outside every repository and every zip.

## The questions the study puts to Logan

Each goes to him with the lead's proposal beside it, and the kit proposes none. The kit's statements about the
standard below are from memory, so they are BELIEVED until the lead reads the PDF.

1. **The edition.** IEEE 754-2019 or 2008. The edition changes the required set: in 2008 minNum and maxNum are in
   clause 5, and in 2019 the minimum and maximum operations are recommended ones, in clause 9.
2. **The formats.** Each of binary16, binary32 and binary64 is either an arithmetic format or an interchange format
   only (binary16 can be either). An arithmetic format takes all of clause 5's operations. Among them are the
   conversions to and from decimal character sequences, which are a large piece of work. Clause 9's recommended
   operations (exp, log and the rest): in or out?
3. **Rounding.** roundTiesToEven and the three directed attributes are required. roundTiesToAway is required only for
   decimal formats. In or out here?
4. **Exceptions.**
   - Default handling, and the five flags.
   - Where the flag and mode state lives on a part with two cores: per core, per call, or global.
   - Clause 8's alternate exception handling: in or out?
5. **Tininess and NaNs.**
   - Tininess detected before or after rounding, one choice for every binary operation.
   - Payloads: whose NaN propagates, how signaling NaNs are treated, and whether there is a canonical NaN.
6. **The interface.**
   - A drop-in for the toolchain's runtime helpers, through pico-sdk's wrapping; an API of its own; or both.
   - binary16's storage type.
7. **Targets.**
   - Speed and size goals, and their yardstick: pico-sdk's float and double support, which uses the bootrom's
     routines (BELIEVED, for the survey to read).
   - Flash or RAM placement.
   - The language: C, Thumb assembly, or both.
8. **Dependencies and licence.**
   - pico-sdk's version, and the toolchain.
   - The output's licence.
   - Which third-party code may be copied, and which only read. Record each source's licence.
9. **The authority and the oracles.** The study proposes them, and Logan approves.
