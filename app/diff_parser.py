"""
Unified diff parser.

Turns raw unified-diff text into a structured list of FileDiff objects,
each holding the file's path and its added ("+") lines together with
their line numbers in the NEW file.

We deliberately parse only what the mock provider rules need: added
lines and their new-file line numbers, plus the path. We do not need
removed-line content or old-file line numbers for this task.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


class DiffParseError(Exception):
    """Raised when the input cannot be parsed as a unified diff."""
    pass


@dataclass
class AddedLine:
    line_number: int   # line number in the NEW file
    content: str        # line content, WITHOUT the leading '+'


@dataclass
class FileDiff:
    path: str
    added_lines: List[AddedLine] = field(default_factory=list)


# Matches a hunk header like: @@ -38,6 +38,7 @@ optional trailing context
# We only care about the number right after the '+' (new-file start line).
_HUNK_HEADER_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def _extract_path_from_plus_line(line: str) -> Optional[str]:
    """
    Extracts the file path from a '+++ b/path/to/file' line.
    Returns None for '+++ /dev/null' (file was deleted).
    Strips the git-style 'b/' prefix when present.
    Handles an optional trailing tab + timestamp some diff tools add.
    """
    rest = line[4:].strip()
    # Some diffs append a tab and a timestamp after the path.
    rest = rest.split("\t")[0].strip()

    if rest == "/dev/null":
        return None
    if rest.startswith("b/"):
        rest = rest[2:]
    return rest


def parse_diff(diff_text: str) -> List[FileDiff]:
    """
    Parses unified diff text into a list of FileDiff objects.

    Raises DiffParseError if the text has no recognizable diff structure
    (e.g. no hunk headers found anywhere), or if it is structurally
    inconsistent (an added line appears outside any hunk).
    """
    if diff_text is None or diff_text.strip() == "":
        raise DiffParseError("Diff is empty.")

    lines = diff_text.splitlines()

    files: List[FileDiff] = []
    current_path: Optional[str] = None
    current_added_lines: List[AddedLine] = []
    new_line_counter: Optional[int] = None
    saw_any_hunk = False
    current_file_is_deletion = False

    def flush_current_file():
        if current_path is not None:
            files.append(FileDiff(path=current_path, added_lines=current_added_lines))

    for line in lines:
        if line.startswith("--- "):
            # A new file section is starting - close out the previous one.
            flush_current_file()
            current_path = None
            current_added_lines = []
            new_line_counter = None
            current_file_is_deletion = False

        elif line.startswith("+++ "):
            path = _extract_path_from_plus_line(line)
            if path is None:
                current_file_is_deletion = True
                current_path = None
            else:
                current_path = path
                current_added_lines = []

        elif line.startswith("@@"):
            match = _HUNK_HEADER_RE.match(line)
            if not match:
                raise DiffParseError(f"Malformed hunk header: {line!r}")
            new_line_counter = int(match.group(1))
            saw_any_hunk = True

        elif line.startswith("+"):
            # An added content line (the "+++ " header case was already
            # handled above, so reaching here means a real added line).
            if current_file_is_deletion:
                continue
            if current_path is None or new_line_counter is None:
                raise DiffParseError(
                    "Found an added line outside of any file/hunk context."
                )
            content = line[1:]
            current_added_lines.append(AddedLine(new_line_counter, content))
            new_line_counter += 1

        elif line.startswith("-"):
            # Removed content line (the "--- " header case was already
            # handled above). Does not exist in the new file, so the
            # new-file line counter does not advance.
            continue

        elif line.startswith("\\"):
            # e.g. "\ No newline at end of file" - not a content line.
            continue

        else:
            # Context line (starts with a space, or is blank) or an
            # unrelated header line (e.g. "diff --git ...", "index ...").
            # Context lines inside a hunk advance the new-file counter.
            if new_line_counter is not None and (line.startswith(" ") or line == ""):
                new_line_counter += 1

    flush_current_file()

    if not saw_any_hunk:
        raise DiffParseError("No valid hunk headers found - not a unified diff.")

    return files