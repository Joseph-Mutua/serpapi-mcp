"""Update the project, registry, bundle, and lockfile release versions."""

import argparse
import json
import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="New stable version, e.g. 2.0.0")
    args = parser.parse_args()

    if not re.fullmatch(r"(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*)){2}", args.version):
        parser.error("Expected a stable version in X.Y.Z format.")

    manifests = [ROOT / "server.json", ROOT / "mcpb/manifest.json"]
    originals = {
        path: path.read_bytes()
        for path in [ROOT / "pyproject.toml", ROOT / "uv.lock", *manifests]
    }
    documents = {path: json.loads(originals[path]) for path in manifests}

    try:
        subprocess.run(
            ["uv", "version", args.version, "--no-sync"],
            cwd=ROOT,
            check=True,
        )
        with (ROOT / "pyproject.toml").open("rb") as file:
            version = tomllib.load(file)["project"]["version"]

        for path, document in documents.items():
            document["version"] = version
            path.write_text(
                json.dumps(document, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    except (Exception, KeyboardInterrupt):
        # Restore all four files if locking or writing fails.
        for path, content in originals.items():
            path.write_bytes(content)
        raise

    print(f"All release versions updated to {version}.")


if __name__ == "__main__":
    main()
