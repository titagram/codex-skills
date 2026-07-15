# Lesson integration

Discover lesson materials read-only. Start with `rg --files` and narrow the results to coordination files, teleprompters, slides, and source files. Do not rename, rewrite, move, or generate files during discovery.

For each proposed clip:

1. Link it to the relevant coordination passage, teleprompter passage, slide, or source file.
2. Reuse the lesson's terminology, notation, examples, and conceptual order.
3. Record the source paths or links in the storyboard and generated manifest.
4. Keep every source unchanged unless the user separately requests an edit.

Default generated files to `animations/<topic>/`. Treat that directory as new output: inspect it before writing, and never overwrite an existing source or output without explicit approval.
