"""Build the Kaggle writeup from PAPER.md and check the competition's limits. CPU only.

- drops the DRAFT note
- refuses to call the result final while a `[[placeholder]]` is left
- counts words the way the competition does: everything except the reference list and the figures
  (title, subtitle, abstract, tables and captions count)
- writes paper/kaggle_writeup.md and copies the figures next to it

Usage: python src/build_submission.py [--limit 3000]
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def count_words(md: str) -> int:
    body = md.split("### References")[0]
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)          # image tags are figures, not text
    body = re.sub(r"^\|[-| :]+\|$", " ", body, flags=re.M)     # table rulers
    body = re.sub(r"[|#*`>_]", " ", body)
    return len([w for w in body.split() if re.search(r"\w", w) or STRICT])


STRICT = True   # count every whitespace-separated token, including stand-alone symbols (=, −, →): the conservative count


def unwrap(md: str) -> str:
    """One line per paragraph and per list item: the Kaggle editor keeps the line breaks of a paragraph that
    contains inline HTML. Tables, headings, images and display formulas are left as they are."""
    out = []
    for block in md.split("\n\n"):
        lines = [l for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        first = lines[0].lstrip()
        if first.startswith(("|", "#", "![", "$$", "```")) or any(l.lstrip().startswith("|") for l in lines):
            out.append(block)
        elif all(re.match(r"\[\d+\] ", l) for l in lines):      # reference list: one paragraph per entry
            out.append("\n\n".join(lines))
        elif re.match(r"(\d+\.|[-*]) ", first):
            items = []
            for l in lines:
                if re.match(r"\s*(\d+\.|[-*]) ", l) or not items:
                    items.append(l.rstrip())
                else:
                    items[-1] += " " + l.strip()
            out.append("\n".join(items))
        else:
            out.append(" ".join(l.strip() for l in lines if l.strip()))
    return "\n\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=3000)
    args = ap.parse_args()
    md = (ROOT / "PAPER.md").read_text()
    md = re.sub(r"^> DRAFT.*?\n\n", "", md, flags=re.S | re.M)
    left = re.findall(r"\[\[.*?\]\]", md, flags=re.S)
    n = count_words(md)
    out = ROOT / "paper"
    out.mkdir(exist_ok=True)
    (out / "kaggle_writeup.md").write_text(md)
    (out / "figures").mkdir(exist_ok=True)
    for f in re.findall(r"!\[[^\]]*\]\((figures/[^)]+)\)", md):
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, out / f)
        else:
            print("MISSING FIGURE", f)
    # second copy whose images point at the public repository, so the text can be pasted without uploading figures
    RAW = "https://raw.githubusercontent.com/moncifem/null-edit/main/"
    (out / "kaggle_writeup_remote_images.md").write_text(re.sub(r"(!\[[^\]]*\]\()(figures/)", lambda m: m.group(1) + RAW + m.group(2), md))
    # body for the Kaggle editor: title and subtitle go into their own fields
    remote = (out / "kaggle_writeup_remote_images.md").read_text()
    (out / "kaggle_body.md").write_text(unwrap(remote[remote.index("### Abstract"):]))
    if (ROOT / "figures/thumbnail.png").exists():
        shutil.copy(ROOT / "figures/thumbnail.png", out / "thumbnail.png")
    required = ["### Abstract", "Introduction", "Method", "Experimental setup", "Results", "Related work", "### References"]
    print(f"words (excluding references and figures): {n} / {args.limit}  ->  {'OK' if n <= args.limit else 'OVER'}")
    print("sections:", ", ".join(f"{r.strip('# ')}={'yes' if r in md else 'NO'}" for r in required))
    print(f"placeholders left: {len(left)}")
    for p in left:
        print("   ", " ".join(p.split())[:90])
    print("written:", out / "kaggle_writeup.md")


if __name__ == "__main__":
    main()
