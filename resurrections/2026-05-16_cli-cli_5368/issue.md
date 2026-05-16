# Remove restrictions of `gh pr view --json files`

**Repository:** [cli/cli](https://github.com/cli/cli)
**Issue:** [cli/cli#5368](https://github.com/cli/cli/issues/5368)
**Reactions:** 6 👍
**Created:** 2022-03-28T16:25:49Z
**Last Activity:** 2026-01-21T17:35:41Z
**Labels:** bug, priority-2, help wanted, gh-pr

---

## Original Description

### Describe the feature or problem you’d like to solve

The query of `gh pr view --json files` is capped to 100 records now.

### Proposed solution

Remove the restrictions by some way, for example, adding option.

### Additional context

Discussed in https://github.com/cli/cli/discussions/5359

<div type='discussions-op-text'>

<sup>Originally posted by **SnowCait** March 26, 2022</sup>
I try to get files info which PR contains over 500 files.
But `gh` returns only 100 files info.
```
$ gh pr view $number --json changedFiles
{
  "changedFiles": 543
}

$ gh pr view $number --json files --jq '.files | length'
100
```

gh version is 2.6.0.

Is there any way to get all files info?</div>

---

*Resurrected by Resurrection Bot 🧬*
