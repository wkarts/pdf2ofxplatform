from __future__ import annotations

import argparse
import json
from pathlib import Path
from uuid import uuid4

from pdf2ofx.application.processor import ConversionProcessor
from pdf2ofx.settings import get_settings
from pdf2ofx.storage.job_store import JobStore


def main() -> int:
    parser = argparse.ArgumentParser(prog="pdf2ofx")
    subparsers = parser.add_subparsers(dest="command", required=True)

    cleanup = subparsers.add_parser("cleanup", help="Remove jobs expirados.")
    cleanup.set_defaults(command="cleanup")

    convert = subparsers.add_parser("convert", help="Converte um PDF local.")
    convert.add_argument("input", type=Path)
    convert.add_argument("output", type=Path)
    convert.add_argument("--bank", default="auto")

    args = parser.parse_args()
    settings = get_settings()
    store = JobStore(settings.data_dir, settings.job_ttl_hours)

    if args.command == "cleanup":
        count = store.cleanup_expired()
        print(json.dumps({"removed": count}))
        return 0

    job_id = str(uuid4())
    store.create(job_id, args.input.name, args.bank, "ofx_102")
    store.input_path(job_id).write_bytes(args.input.read_bytes())
    result = ConversionProcessor(settings, store).process(job_id, args.bank)
    args.output.write_bytes(store.output_path(job_id).read_bytes())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
