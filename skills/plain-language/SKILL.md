---
name: plain-language
description: Rewrite, review, or write text in plain language, following the US federal plain language guidelines (digital.gov, Plain Writing Act of 2010), so readers can find what they need, understand it, and act on it the first time they read it. Use when the user says "plain language", "make this easier to understand", "simplify this", "too jargony", "rewrite for a general audience", "ELI5 this doc", or asks for a plain-language review of docs, emails, policies, error messages, READMEs, or UI copy.
---

# Plain language

Plain language is content that is clear and easy for its intended audience to understand. Readers should be able to find what they need, understand it, and use it the first time they read it. It is not about oversimplifying. Match the audience's knowledge and comfort level. Keep every fact, requirement, and caveat that matters.

The rules below come from the federal Plain Language Guide on digital.gov, which replaced plainlanguage.gov. The Plain Writing Act of 2010 requires US federal agencies to follow it.

## Modes

Work out which one the user wants. If it's unclear, rewrite.

- **Rewrite**: return the revised text, then a short list of the main changes.
- **Review**: don't rewrite. Return findings ordered by impact. For each one, quote the original, name the problem, and suggest a fix.
- **Write**: draft new text that follows the rules below from the start.

## Process

1. **Identify the reader and what they need to do.** People only want to know what applies to them. If the text doesn't say who the audience is and the user didn't either, state your assumption in one line and continue. If the text serves several audiences, separate their material instead of mixing it.
2. **Find the main point.** Say it in one or two sentences. If you can't, fix the structure before touching any words.
3. **Organize.** Put the most important information first and background (if needed) toward the end. Put general information before exceptions, conditions, and special cases. List steps in the order they happen.
4. **Apply the rules below**, from structure down to individual words.
5. **Check** the result against the checklist, and confirm the meaning hasn't changed. Flag anything ambiguous instead of guessing.
6. **Recommend testing** when the text matters, for example a public page, form, or policy. See "Test with real readers".

## Rules

### Structure and design
- Put key information at the top. Frame content around the reader's goal: "If you want a research grant, here's what you have to do."
- Use clear, descriptive headings, and use heading levels consistently. For long documents, add a table of contents or links to the headings.
- Keep sections short so readers can skim and scan. Dense sections with no white space push readers away.
- Cover one topic in each paragraph, and start each one with a topic sentence. Keep paragraphs to about 150 words or less, in 3–8 sentences, and never more than 250 words. A one-sentence paragraph is fine now and then.
- Use lists to make content easy to scan, and tables to make complex relationships clear.
- For emphasis, use bold or italics, and use them sparingly. Don't underline (readers expect underlined text to be a link) and don't use all caps.
- Write link text that says where the link goes. Never use "click here" or "read more".
- Don't use an FAQ in place of clear main content. If you add one, base it on real questions from readers.

### Sentences
- Keep sentences short, with one idea in each. Avoid sentences loaded with dependent clauses and exceptions.
- Use active voice to make it clear who must do what: "You must do it", not "It must be done." Passive voice is fine when there is no clear actor, such as when describing a legal consequence.
- Use present tense unless another tense is needed for accuracy.
- Speak directly to the reader as "you".
- Use **must** for requirements, **must not** for prohibitions, **may** when something is optional, and **should** for recommendations. Don't use **shall**, which is ambiguous.
- Turn hidden verbs back into verbs. Watch for nouns ending in -ment, -tion, -sion, or -ance, and for verbs like achieve, effect, make, and take. "Analyze", not "conduct an analysis of".
- Use positive wording and avoid double negatives: "You must get approval", not "No approval may be implied." Watch for words like unless, fail to, notwithstanding, and except.
- Use transition words (this, however, therefore) to link ideas.

### Words
- Choose the familiar word over the unusual one. See `references/word-swaps.md` for replacements.
- Avoid jargon, but keep technical terms the audience needs, and explain them. Specialist terms are fine for specialist readers.
- Use one term for each concept and stick to it. Don't swap in synonyms for variety.
- Keep abbreviations to no more than 3 in a document. Prefer a short nickname ("the Act") to an acronym. Define an abbreviation the first time you use it, unless everyone knows it (FBI, PhD).
- Use examples to explain complex ideas. Write "for example" and "that is" instead of "e.g." and "i.e."
- Cut unnecessary words, including modifiers (absolutely, actually, completely, really, quite, totally, very) and doublets ("cease and desist" → "stop", "due and payable" → "due").
- Avoid noun strings, where three or more nouns are stacked together. Break them up with prepositions or cut the non-essential ones.
- Avoid slashes. Decide whether "and/or" means "and" or "or".

### Definitions
- Define words by their normal meaning. Never define a word to mean something else.
- Avoid long definition sections. If you need one, put it at the end and list the terms alphabetically, without numbers. Don't define terms the document never uses.

## What not to do

- Don't remove legally or technically required content. Rephrase it, or add a plain summary above it.
- Don't talk down to readers or oversimplify for an expert audience.
- Don't change code, commands, identifiers, quoted text, or product names.
- Don't treat a readability score as proof that text is clear. Scores can't tell whether readers can act on it. (This point is my own judgment; the federal guide doesn't cover readability formulas.)

## Test with real readers

The federal guide says to test and fix, then test again, at least twice. An agent can't do this itself, so suggest one of these methods to the user when the content matters:

- **Paraphrase testing**: individual interviews where readers explain the text in their own words. Best for short pages, short documents, and survey questions.
- **Usability testing**: individual interviews where readers try to complete tasks. Best for longer documents, websites, and forms.
- **Controlled comparative studies**: large studies that collect statistics on responses. Run smaller tests first.

Focus groups are better for learning about the audience before you write than for testing what you wrote.

## Checklist

- [ ] The most important information or action comes first, and background comes last
- [ ] Each audience can find the material that applies to them
- [ ] Headings are descriptive and let a reader skim
- [ ] Each paragraph has one topic, starts with a topic sentence, and is 150 words or less
- [ ] Each sentence has one idea
- [ ] Active voice, present tense, "you" for the reader
- [ ] must / must not / may / should used correctly, with no "shall"
- [ ] No hidden verbs, noun strings, slashes, double negatives, or "e.g."/"i.e."
- [ ] Jargon is replaced or explained, with no more than 3 abbreviations
- [ ] The same term is used for the same thing throughout
- [ ] Link text is meaningful
- [ ] No facts, requirements, or caveats were lost in the rewrite

## Sources

- Federal Plain Language Guide (digital.gov): https://digital.gov/guides/plain-language
  - Principles: https://digital.gov/guides/plain-language/principles
  - Writing: https://digital.gov/guides/plain-language/writing
  - Design: https://digital.gov/guides/plain-language/design
  - Testing: https://digital.gov/guides/plain-language/test
- Plain Writing Act of 2010: https://digital.gov/resources/plain-writing-act
