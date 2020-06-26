 - [x] 
> Lemma 1 is not understandable to me. I cannot recognize what are the initial assumptions and what is a statement that is to be proved by the lemma. There are no motives, nor examples, discussed to justify the main idea of this lemma. And finally, each lemma is to be formally proved. However, there is no proof in the paper.

> Why did you choose the designation "Lemma" for "Lemma 1"?

> Lines 86-88 — please justify better the claim

 - [x] 
> “The basic premise is that expressions can generate a special data type: Music.” --> Remark: How expressions in formal languages can generate any data type? It is strange to me. I guess that the right formulation can be that expressions are interpreted (or calculated) in some type space, i.e. they can be generated as expressions of some type!

 - [x] 
 > “A musical Event can be one of many things, such as a note, a chord, or even more implementation-specific events like MIDI messages” --> Remark: I am not quite sure if it is a correct formulation of the notion of Event. Is the Event a concept of the PIM or PSM level of abstraction? I would suggest here strong differentiating between platform independent (PIM) and platform-specific (PSM) concepts.

 - [x] 
> L122: smaallest ->smallest 

 - [x]
> In the end of the paper the reader has a vague idea of the syntax and elements of the language built from the multiple examples, but a formal specification of the DSL is never presented. For example, do I have and if-then-else or while-do like statements?
> Does the language allow recursiveness? If it does, how to finish it?

PMS: Instead of packing this paper with even more content describing a full specification of the language, I fell it is better to simple link to the documentation where a full picture can more clearly be seen.

 - [x] Line 70 (listing 2) — explain the syntax for times/duration

 - [x] Line 261 — my brain did not parse it… ;)

 - [x] Line 266 — first reference to regular and musical-emmiting functions

 - [x] Line 269 — first reference to return statements

 - [x] Line 277 — what is the effect of the "stretch" function? Was it defined elsewhere or is part of the DSL basic statements?

 - [x] 

> Line 275-289 — some aid mapping this example to the music sheet below would be great

> The authors should help the reader map the "program specification" to the music sheet, facilitating the comprehension, usefulness and application of the DSL features.

 - [-] Line 348 — the semantics of the operators is unclear! E.g., what about conflicts in unions?

PMS: I really don't feel like it is needed to explicitly explain every detail of the operations provided by keyboards in this paper. A more fitting place to include them would certainly be a documentation, and it would be better in my opinion to just include a link to said documentation at the beginning of the paper.

 - [x]
> I believe there are cases where laziness can be harmful and variable contents should be immediately evaluated, although it may cause problems with infinite sequences.

 - [x] 
> Related Work is completely missing.

> Despite a very timely critical analysis section, there is no related work nor a state of the art section, and no conclusion. There is indeed a reasonable amount of related work that deserve to be cited and explored here,.

> My major concern with this paper is the lack of a explicit discussion relating this works is other work already available in the literature, from a quick search on the web it seems that there are already some languages used for representing music, why another one? Or why a complete new DSL instead of enriching an already existing one? The authors decided to adopt a subset of ABC to describe notes, that seems reasonable, but a more broader discussion comparing of highlighting the necessity of a new approach needs to be included. This discussion seems required to sustain the authors' claim of not being "reinventing the wheel".

> Although I'm not an expert in "music DSLs", I believe there are some, and it is not reasonable for this paper to leave out the related work. The absence of a related work section is a "big no no" for me, hence my grade as "borderline paper" (otherwise I would have gone to the "weak accept" or even "accept" grades). For example, although with a totally different objective, I can see some relations between the proposed DSL with the LaTeX extensions to typeset music sheets, such as the lazy evaluation, whatever is not kept in a variable is sent to the output, etc.

> Overall the paper lacks some detail and some clearer discussion on some specific points There are some minor issues with the text itself, and there are some confusing sections, a review of the text is advised, also making clearer the issues concerning: the boundary between specification and implementation, integration of a DSL in a more generic programming language. And include the discussion around related work.

 - [x] Lines 207-210 (listing 4) — lots of elements that are used were never introduced
 
 - [x] 
>  are some references to expressions like "integrating musical <something>" throughout the paper, this was a bit confusing at first for me, given my background in the design of development of new languages when I read the term "integrate" I usually think on something of merging two "things" where one is a programming language, this usually entails creating mechanisms that allows using this new "thing" inside a already know programming language. And when started reading this paper, this was the gist I had understood from the authors discussion, only much later it seemed that actually my first impression was not correct, the goal seems to write programs in a DSL, out-of-scope of any generalist programming environment, which is of course acceptable my I think this needs to be clearer in the paper from the beginning. Another detail that could help is to better describe the code listings, add more text to the caption saying what things really are, "code written using our DSL"!
or similar, it may be obvious for the authors' but not for the readers. Another example of expression that makes things confusing: "regular data in a programming language".

 - [x] 
> Figures and Listings are to be referenced explicitly in the text and discussed in details.

- [x] 
> The introduction is well written, and interesting, following the previous comment I think a more clear discussion right on the first paragraph, about the DSL should make things clearer. There are many details to be addressed when creating a compiler/interpreter for a new language, although some of these are introduced in this section, others are missing, e.g. generic architecture, parser generator, etc. Also, I understand the goal of the authors' is to create a new DSL, but I think the paper would benefit for defining an explicit research question for guiding the discussion. Still in the Introduction, its' not mandatory bu please consider including a last paragraph with a summary of the papers' remaining section, it helps the reader to organize ideas.

- [x]
> [x] Section 2 describes how to address the problem, but it's not clear which actual problem are we talking about. Also this section needs a detailed review, there are some confusing sentences, and the beginning its' hard to read. Laziness is not a only used in functional programming languages; also, please rephrase: "Because of that, the events must always be sorted already", too confusing. Another example " sequence could be potentially infinite" (correct, makes sense), [x] "... to stop this arrangement sooner or later", later than infinite? [x] Finally consider renaming this section, many details are discussed in this section besides goals and requirements, and the jump between goals and requirements is a bit messy, its' hard for me to see laziness as a requirement, but a goal yes, in fact the authors' have laziness as a requirement and as a goal, note that a requirement is not the same thing as a goal. [x] Another example of confusing sentences "expressions can generate a special data t!
ype", why this data type special? Cant' we treat is a another data type in the context of programming languages? I wouldn't call the 3 paragraphs in this section title "Data Model" a proper discussion about the data types used, and their description, a more elaborated discussion should be included. An expression is one concept, a data type is other, it seems some things are being confused. [x] Another element this section is missing is an overall description of the language. It contains variables (that look like...), expressions, functions, .... one expressions ends with ; or not, a function is defined as ..., something like this. [x] Also please include in the captions list in which language the the snippet of code is being written.

 - [x] 
> Operators, Grids, Keyboards, Lines 118 – 168 --> Remark: all those concepts are to be clearly introduced. The syntax rules given in this segment of the text are to be introduced in the form of listings, and each listing is to be discussed and explained clearly in the text. Otherwise, this segment of the text prevents clear understanding the rest of the paper.

> Both in the examples and, once in a while, in the main text, new concepts, operators/functions of syntactic figures are introduced without any previous introduction. This leaves the reader "guessing" what are they.

- [x]
> The implementation section includes many discussion details that are inherent to the language itself, not the implementation, I think a more clear boundary between the definition of the language (sometimes called the specification) and implementation details should enhance the clarity of the discussion. Often is better to discuss fewer concepts but in a clearer way. The examples used to illustrate the operators and others are rich, well chosen and interesting, and help to enrich the paper. Note that some of the language important language concepts, for example, a function are only illustrated as examples.

 - [x] 
> Finally, some form of the proof of concept or concept evaluation is to be announced in the paper, at least as a future work in Conclusion.

> Some of the discussion in the last section feels like a conclusion, and since there is no explicit conclusion section, please consider updating this section title to e.g. "Results Discussion and Conclusion" or similar. And the references needs a major revamp, consider using footnotes for the URLs for example, and the overall lack of references is a side effect of the missing discussion about related work, some of the references are not properly defined. A lot of references are missing throughout the text, in particular related with the design and implementation of programming languages, this is related with my previous remarks in my comments about Section 2.
-----



