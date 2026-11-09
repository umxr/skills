# Evals

Test cases for the skills in `skills/`, kept here rather than inside each skill folder so that installing a skill copies only the skill: no fixture repos, no graders for the model to find, and none of the fake credentials some fixtures plant on purpose.

```
evals/<skill-name>/<case-name>/
  prompt.md        # run settings, then the user's prompt
  case.yaml        # what a good result looks like
  graders/         # one assertion per file
  files/           # the fixture repo the case runs against
  place-files.sh   # copies files/ into the run's workspace
```

The layout is the one `claude plugin eval` reads.

## Running them

```sh
evals/run.sh inspect                                   # every case, with and without the skill
evals/run.sh inspect --case python-service-focused --runs 1
```

`run.sh` links `evals/<skill-name>/` into the skill as `evals/` for the duration of the run (`claude plugin eval` only looks there) and removes the link afterwards. Extra arguments go straight to `claude plugin eval`. These are real, billed model runs.

## Fixtures

Some fixture repos contain production-looking secrets (a committed `.env`, hard-coded keys). They are fake and exist to test that a skill masks them. Don't "fix" them.
