# Architecture

```text
External prompts directory (read-only)
            |
            v
      PromptDiscovery
            |
            +-----------------------------+
            |                             |
            v                             v
  With-skill workspace           Without-skill workspace
 prompt + Creation Skill               prompt only
            |                             |
            v                             v
          Lab A                         Lab B
            |                             |
         LabValidator                 LabValidator
            \                             /
             \                           /
              +---- canonical correction
                    prompt + Checker Skill + schema
                         (no candidate access)
                            |
                  +---------+---------+
                  |                   |
                  v                   v
             Checker A           Checker B
                  |                   |
                  +---------+---------+
                            v
                      Pair comparator
                            |
                      Aggregate reports
```

## Trust boundaries

The two generation workspaces are separate filesystem trees. Creation Skill material is copied only to
`with_skill`. Canonical-correction workspace contains no candidate lab. Checker runs operate on copies in
`checker-run/labs/candidate`, preserving generated `source/` trees.

## Result semantics

- `passed`: checker completed and all checks passed.
- `failed`: checker completed and at least one check failed.
- `error`: technical/generation/validation/checker/report failure prevented a valid result.
- `INCOMPARABLE`: pairwise quality comparison is not methodologically valid (for example a checker did not complete).
