# Third-party notices

## unslop

Several prose-check patterns in `scripts/academic_style.py` (significance inflation, `serves as a
cornerstone`-type copulas, vague attribution, synonym-cycling groups and the flat-paragraph rhythm
check) are adapted from unslop (https://github.com/MohamedAbdallah-14/unslop), used under the MIT
License:

```
MIT License

Copyright (c) 2026 Mohamed Abdallah

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Ideas (no code copied)

The academic writing mode also follows ideas from these projects; no code or text was copied:

- caveman (https://github.com/JuliusBrussee/caveman): re-inject the rules at SessionStart, including
  after compaction, and add a one-line reminder on every prompt; switch the mode from the chat.
- ponytail (https://github.com/dietrichgebert/ponytail): inject the rules into subagents at
  SubagentStart.
- humanizer (https://github.com/blader/humanizer) and stop-slop
  (https://github.com/hardikpandya/stop-slop): a pre-send self-check that no fact, number or
  citation was added or dropped; Bad/Good example pairs.
