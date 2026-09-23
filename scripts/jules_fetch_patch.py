"""Fetch the final change-set patch from a Jules session's activities.

Usage: python3 scripts/jules_fetch_patch.py SESSION_ID OUT_PATCH_PATH
Reads JULES_CODER_API_KEY from env, falls back to parsing ~/.bashrc.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path


def get_key():
    key = os.environ.get("JULES_CODER_API_KEY")
    if key:
        return key
    for line in Path.home().joinpath(".bashrc").read_text().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[len("export "):]
        if line.startswith("JULES_CODER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("JULES_CODER_API_KEY not found in env or ~/.bashrc")


def fetch_activities(session_id):
    key = get_key()
    url = f"https://jules.googleapis.com/v1alpha/sessions/{session_id}/activities?pageSize=100"
    req = urllib.request.Request(url, headers={"X-Goog-Api-Key": key})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read()).get("activities", [])


def main():
    session_id, out_path = sys.argv[1], sys.argv[2]
    activities = fetch_activities(session_id)
    patch = None
    n_changesets = 0
    for a in activities:
        for art in a.get("artifacts", []):
            cs = art.get("changeSet")
            if cs and cs.get("gitPatch", {}).get("unidiffPatch"):
                patch = cs["gitPatch"]["unidiffPatch"]  # keep the LAST one
                n_changesets += 1
    if not patch:
        raise SystemExit(f"no changeSet patch found in {len(activities)} activities")
    filtered_lines = []
    in_batches = False
    for line in patch.splitlines(True):
        if line.startswith("diff --git a/batches/"):
            in_batches = True
            filtered_lines.append(line)
        elif line.startswith("diff --git a/"):
            in_batches = False
        elif in_batches:
            filtered_lines.append(line)
    if filtered_lines:
        patch = "".join(filtered_lines)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(patch)
    print(f"fetched {n_changesets} changeSets; final patch = {len(patch)} chars -> {out_path}")


if __name__ == "__main__":
    main()
