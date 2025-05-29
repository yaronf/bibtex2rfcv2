import os
import sys
from pathlib import Path
import bibtexparser

# Usage: python split_bibtex_entries.py <input_bibtex> <output_dir>
def main():
    if len(sys.argv) != 3:
        print("Usage: python split_bibtex_entries.py <input_bibtex> <output_dir>")
        sys.exit(1)
    input_bib = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    with input_bib.open(encoding="utf-8") as f:
        bib_database = bibtexparser.load(f)

    for i, entry in enumerate(bib_database.entries, 1):
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [entry]
        entry_str = bibtexparser.dumps(db)
        out_file = output_dir / f"entry{i}.bibtex"
        with out_file.open("w", encoding="utf-8") as out:
            out.write(entry_str)
    print(f"Wrote {len(bib_database.entries)} entries to {output_dir}")

if __name__ == "__main__":
    main() 