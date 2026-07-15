# Lesson integration

Discover lesson materials read-only. Start with `rg --files` and narrow the results to coordination files, teleprompters, slides, and source files. Do not rename, rewrite, move, or generate files during discovery.

For each proposed clip:

1. Link it to the relevant coordination passage, teleprompter passage, slide, or source file.
2. Reuse the lesson's terminology, notation, examples, and conceptual order.
3. Record the source paths or links in the storyboard and generated manifest.
4. Keep every source unchanged unless the user separately requests an edit.

Default generated files to the next unused `animations/<topic>/vNNN/` path, starting with `v001` and incrementing the numeric suffix. Inspect existing version directories, then present the exact proposed path and require the user to choose explicitly between:

1. Write to that new versioned path.
2. Force-overwrite an exact existing output path named by the user.

Do not write until the user chooses one option. Generic approval, including storyboard approval, does not make this choice. Apply force-overwrite only to the named output path, never to lesson sources. Record the selected output path and choice in the manifest.
