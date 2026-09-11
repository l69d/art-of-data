# Art of Data

Goal and conventions: see `README.md`. Repo: github.com/l69d/art-of-data, served by GitHub Pages.

- Every change to data, scripts or a visualization updates that dataset's `README.md`
  and adds a dated line to the Log in the root `README.md`, in the same commit.
- A new visualization also gets a row in the root Gallery table.
- Run the dataset's `test_*.py` before committing.
- Visualization pages need their own `<!doctype html>` and meta tags, because Pages serves them as-is.
  If you republish one as an Artifact, strip those tags first.
