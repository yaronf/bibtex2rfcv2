# Usage Guide

## Basic Usage

The basic command format is:
```bash
bibtex2rfcv2 convert INPUT_FILE OUTPUT_FILE
```

The tool accepts BibTeX files with any extension (e.g., .bib, .bibtex) and can process multiple entries in a single file. Command options can be specified before or after the arguments.

### Examples

1. Convert a BibTeX file to RFC XML:
```bash
bibtex2rfcv2 convert input.bib output.xml
```

2. Read from stdin and write to stdout:
```bash
cat input.bib | bibtex2rfcv2 convert - -
```

3. Read from stdin and write to a file:
```bash
cat input.bib | bibtex2rfcv2 convert - output.xml
```

4. Read from a file and write to stdout:
```bash
bibtex2rfcv2 convert input.bib -
```

## Command Options

### Global Options
- `--version`: Show version information
- `--help`: Show help message

### Convert Command Options
- `--progress/--no-progress`: Toggle progress bar (default: enabled)

Options can be specified in any order:
```bash
bibtex2rfcv2 --no-progress convert input.bib output.xml
bibtex2rfcv2 convert input.bib output.xml --no-progress
```

## Input Format

The tool accepts standard BibTeX entries. Field values can be enclosed in either curly braces `{}` or quotes `""`. Multiple authors should be separated by `and`. Here's an example:
```bibtex
@article{example2023,
  author = {John Doe and Jane Smith},
  title = {Example Title},
  journal = {Journal Name},
  year = {2023},
  volume = {1},
  number = {1},
  pages = {1--10},
  doi = {10.1234/example.2023}
}
```

## Output Format

The tool generates RFC-compliant XML references in xml2rfc v3 format. The output includes the proper XML namespace and handles multiple authors correctly. Example output:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<reference anchor="example2023" target="https://doi.org/10.1234/example.2023">
  <front>
    <title>Example Title</title>
    <author fullname="John Doe"/>
    <author fullname="Jane Smith"/>
    <date year="2023"/>
  </front>
  <seriesInfo name="Journal Name" value="1" pages="1--10"/>
  <format type="application/pdf" target="https://doi.org/10.1234/example.2023"/>
</reference>
```

## Supported BibTeX Entry Types

The tool supports all standard BibTeX entry types:
- article
- book
- inbook
- booklet
- conference
- inproceedings
- manual
- mastersthesis
- misc
- phdthesis
- proceedings
- techreport
- unpublished

## Field Mapping

Common BibTeX fields are automatically mapped to RFC XML elements. Field values are transformed as needed (e.g., LaTeX commands are converted to Unicode). Empty fields are omitted from the output.

- `author` → `<author fullname="...">` (multiple authors create multiple elements)
- `title` → `<title>` (LaTeX commands are converted)
- `year` → `<date year>`
- `journal` → `<seriesInfo name>`
- `booktitle` → `<seriesInfo name>` (for conference papers)
- `volume` → `<seriesInfo value>`
- `number` → `<seriesInfo number>`
- `pages` → `<seriesInfo pages>`
- `publisher` → `<publisher>`
- `doi` → `<format type="application/pdf" target="...">`
- `isbn` → `<format type="application/pdf" target="...">`
- `url` → `<format type="application/pdf" target="...">`

## Error Handling

The tool provides clear error messages for common issues:
- Missing required fields
- Invalid BibTeX syntax
- File access problems
- Encoding issues

## Progress Reporting

When processing multiple entries, a progress bar shows:
- Number of entries processed
- Current entry being processed
- Estimated time remaining

The progress bar format is:
```
Converting entries: 100%|██████████| 50/50 [00:02<00:00, 25.00it/s]
```

For very large files, the progress bar updates less frequently to maintain performance. The `--no-progress` option can be used to disable the progress bar entirely. 