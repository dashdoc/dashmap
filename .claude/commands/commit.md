If there are frontend changes, first run `npm run format` in the frontend. Then run `npm run build` and fix errors.
If there are backend changes, run `uv run ruff check backend/ --fix`

Then create a commit, fix the pre-commit errors and commit.