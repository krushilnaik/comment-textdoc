import re
from difflib import SequenceMatcher
from pathlib import Path
from pprint import pprint


def clean_markdown(md: str):
    # Remove markdown formatting characters
    md = re.sub(r"[*_~#>`-]", "", md)
    # Replace [text](url) with just "text"
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    return md


def tokenize_lines(md: str):
    lines = md.splitlines()
    cleaned = [clean_markdown(line).strip().split() for line in lines if line.strip()]
    return cleaned


def get_diffs(md1: str, md2: str):
    lines1 = tokenize_lines(md1)
    lines2 = tokenize_lines(md2)
    result = []
    comments = []

    for line1, line2 in zip(lines1, lines2):
        sm = SequenceMatcher(None, line1, line2)
        merged = []

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            merged.append(
                {
                    "tag": tag,
                    "i1": i1,
                    "i2": i2,
                    "j1": j1,
                    "j2": j2,
                    "old": line1[i1:i2],
                    "new": line2[j1:j2],
                }
            )

        if not merged:
            continue

        # Merge nearby diffs (within one word in between)
        merged_blocks = []
        block = merged[0]
        for m in merged[1:]:
            print(f"before {block=}")
            print(f"\t{m=}")
            if m["i1"] <= block["i2"] + 1 and m["j1"] <= block["j2"] + 1:
                # Merge into current block
                print(line1)
                print(line2)
                block["i2"] = max(block["i2"], m["i2"])
                block["j2"] = max(block["j2"], m["j2"])
                block["old"].extend(line1[block["i1"] + 1 : m["i2"]])
                block["new"].extend(line2[block["j1"] + 1 : m["j2"]])
            else:
                merged_blocks.append(block)
                block = m
            print(f"after {block=}")
        merged_blocks.append(block)

        for b in merged_blocks:
            # Include one-word context on each side
            left_context = line1[b["i1"] - 1] if b["i1"] > 0 else ""
            right_context = line1[b["i2"]] if b["i2"] < len(line1) else ""

            change_line = ""
            pattern_line = ""
            comment_line = ""

            if left_context:
                change_line += f"{left_context} "
                pattern_line += f"{left_context} "

            change_line += f'**{" ".join(b["old"])}** → **{" ".join(b["new"])}**'
            pattern_line += " ".join(b["old"])
            comment_line = (
                "Consider changing '" + " ".join(b["old"]) + "' to '" + " ".join(b["new"]) + "'"
            )

            if right_context:
                change_line += f" {right_context}"
                pattern_line += f" {right_context}"

            result.append(change_line)
            comments.append(
                {
                    "pattern": re.escape(pattern_line),
                    "comment": comment_line,
                }
            )

    return comments


# Example usage
md_a = Path("./original.md").read_text(encoding="utf-8")
md_b = Path("./updated.md").read_text(encoding="utf-8")

# print(get_diffs(md_a, md_b))
pprint(get_diffs(md_a, md_b))
