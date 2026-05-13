#!/usr/bin/env python3
"""Import SciX/ADS publications into Hugo Blox publication pages.

The SciX web UI is backed by the ADS API. Create an API token at SciX/ADS and
export it as SCIX_TOKEN or ADS_DEV_KEY before running this script.

Example:
  SCIX_TOKEN=... python3 scripts/import_scixplorer_publications.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_QUERY = 'author:"Gough-Kelly, Steven"'
DEFAULT_SORT = "date desc"
DEFAULT_FIELDS = [
    "abstract",
    "author",
    "bibcode",
    "date",
    "doi",
    "doctype",
    "esources",
    "identifier",
    "links_data",
    "pub",
    "pubdate",
    "property",
    "title",
    "year",
]


def api_get_json(url: str, token: str, params: dict[str, Any] | None = None) -> Any:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, token: str | None = None) -> bytes:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"&", " and ", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:80] or "publication"


def author_year_slug(record: dict[str, Any]) -> str:
    authors = record.get("author") or []
    first_author = first(authors, "unknown")
    surname = first_author.split(",", 1)[0].strip() or first_author.split()[0]
    year = first(record.get("year"), normalized_date(record)[:4])
    return slugify(f"{surname}-{year}")


def unique_bundle_dir(output_dir: Path, base_slug: str, bibcode: str, overwrite: bool) -> Path:
    candidate = output_dir / base_slug
    if overwrite or not candidate.exists():
        return candidate

    existing_index = candidate / "index.md"
    if existing_index.exists() and bibcode in existing_index.read_text(encoding="utf-8"):
        return candidate

    suffix = slugify(bibcode)[-8:]
    candidate = output_dir / f"{base_slug}-{suffix}"
    counter = 2
    while candidate.exists():
        existing_index = candidate / "index.md"
        if existing_index.exists() and bibcode in existing_index.read_text(encoding="utf-8"):
            return candidate
        candidate = output_dir / f"{base_slug}-{suffix}-{counter}"
        counter += 1
    return candidate


def yaml_scalar(value: Any) -> str:
    if value is None:
        return '""'
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def yaml_block(value: str, indent: int = 0) -> str:
    padding = " " * indent
    body = textwrap.indent(value.strip() or "", padding + "  ")
    return f"|-\n{body}"


def first(value: Any, default: str = "") -> str:
    if isinstance(value, list):
        return str(value[0]) if value else default
    return str(value) if value is not None else default


def normalized_date(record: dict[str, Any]) -> str:
    for key in ("date", "pubdate", "year"):
        value = first(record.get(key))
        if value:
            break
    else:
        return "1900-01-01"

    if re.fullmatch(r"\d{4}", value):
        return f"{value}-01-01"
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return f"{value}-01"
    return value[:10]


def publication_type(record: dict[str, Any]) -> str:
    doctypes = record.get("doctype") or []
    if isinstance(doctypes, str):
        doctypes = [doctypes]
    joined = " ".join(doctypes).lower()
    if "eprint" in joined:
        return "preprint"
    if "inproceedings" in joined or "proceedings" in joined:
        return "paper-conference"
    if "techreport" in joined or "report" in joined:
        return "report"
    if "phdthesis" in joined or "mastersthesis" in joined:
        return "thesis"
    return "article-journal"


def doi_for(record: dict[str, Any]) -> str:
    doi = first(record.get("doi"))
    return doi.removeprefix("https://doi.org/").removeprefix("http://doi.org/")


def arxiv_id(record: dict[str, Any]) -> str:
    for ident in record.get("identifier") or []:
        ident = str(ident)
        if ident.lower().startswith("arxiv:"):
            return ident.split(":", 1)[1]
    return ""


def scix_url(bibcode: str) -> str:
    return f"https://scixplorer.org/abs/{urllib.parse.quote(bibcode)}/abstract"


def link_from_links_data(item: Any) -> tuple[str, str] | None:
    if isinstance(item, str):
        try:
            item = json.loads(item)
        except json.JSONDecodeError:
            return None
    if not isinstance(item, dict):
        return None

    for nested_key in ("instances", "links", "records"):
        nested = item.get(nested_key)
        if isinstance(nested, list):
            for nested_item in nested:
                parsed = link_from_links_data(nested_item)
                if parsed:
                    return parsed

    url = item.get("url") or item.get("link") or item.get("href")
    title = item.get("title") or item.get("name") or item.get("type") or "Full text"
    if not url:
        return None
    return str(title), str(url)


def links_from_links_data(item: Any) -> list[tuple[str, str]]:
    if isinstance(item, str):
        try:
            item = json.loads(item)
        except json.JSONDecodeError:
            return []
    if isinstance(item, list):
        links: list[tuple[str, str]] = []
        for child in item:
            links.extend(links_from_links_data(child))
        return links
    if not isinstance(item, dict):
        return []

    found: list[tuple[str, str]] = []
    parsed = link_from_links_data(item)
    if parsed:
        found.append(parsed)
    for nested_key in ("instances", "links", "records"):
        nested = item.get(nested_key)
        if isinstance(nested, list):
            for child in nested:
                found.extend(links_from_links_data(child))
    return found


def collect_links(record: dict[str, Any]) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(name: str, url: str, kind: str | None = None) -> None:
        if not url or url in seen:
            return
        seen.add(url)
        item = {"url": url}
        if kind:
            item["type"] = kind
        else:
            item["name"] = name
        links.append(item)

    add("SciX", scix_url(record["bibcode"]))

    doi = doi_for(record)
    if doi:
        add("DOI", f"https://doi.org/{doi}")

    arxiv = arxiv_id(record)
    if arxiv:
        add("arXiv", f"https://arxiv.org/abs/{arxiv}", "source")
        add("PDF", f"https://arxiv.org/pdf/{arxiv}", "pdf")

    for raw_link in record.get("links_data") or []:
        for title, url in links_from_links_data(raw_link):
            add(title, url)

    return links


def discover_graphics(api_base: str, token: str, bibcode: str) -> list[dict[str, Any]]:
    """Return graphics metadata when SciX/ADS exposes it.

    The graphics endpoint is not available for every record. Keep this optional
    so metadata import still works when no figures are indexed.
    """

    url = f"{api_base.rstrip('/')}/graphics/{urllib.parse.quote(bibcode)}"
    try:
        data = api_get_json(url, token)
    except urllib.error.HTTPError as exc:
        if exc.code in {400, 404, 405}:
            return []
        raise
    except urllib.error.URLError:
        return []

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("figures", "graphics", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def best_figure_url(figures: list[dict[str, Any]]) -> str:
    def walk(value: Any) -> str:
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            return value
        if isinstance(value, dict):
            for preferred in ("thumbnail", "thumb", "image", "url", "href"):
                found = walk(value.get(preferred))
                if found:
                    return found
            for child in value.values():
                found = walk(child)
                if found:
                    return found
        if isinstance(value, list):
            for child in value:
                found = walk(child)
                if found:
                    return found
        return ""

    for figure in figures:
        for key in ("thumbnail", "thumb", "image", "url"):
            found = walk(figure.get(key))
            if found:
                return found
        found = walk(figure)
        if found:
            return found
    return ""


def write_featured_image(
    out_dir: Path,
    image_url: str,
    token: str,
    dry_run: bool,
) -> str:
    if not image_url:
        return ""

    suffix = Path(urllib.parse.urlparse(image_url).path).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        suffix = ".jpg"
    filename = f"featured{suffix}"
    if dry_run:
        return filename

    try:
        content = download(image_url, token=None)
    except urllib.error.URLError:
        content = download(image_url, token=token)
    (out_dir / filename).write_bytes(content)
    return filename


def front_matter(record: dict[str, Any], links: list[dict[str, str]], figure_caption: str) -> str:
    title = first(record.get("title"), "Untitled publication")
    authors = [str(author) for author in record.get("author") or []]
    publication = first(record.get("pub"))
    abstract = first(record.get("abstract"))
    date = normalized_date(record)
    doi = doi_for(record)
    summary = abstract[:240].rstrip()
    if len(abstract) > len(summary):
        summary += "..."

    lines = [
        "---",
        f"title: {yaml_scalar(title)}",
        "authors:",
    ]
    if authors:
        for author in authors:
            author_value = "me" if "gough-kelly" in author.lower() else author
            lines.append(f"  - {yaml_scalar(author_value)}")
    else:
        lines.append("  - me")
    lines.extend(
        [
            f"date: {yaml_scalar(date)}",
            f"publishDate: {yaml_scalar(date)}",
            f"bibcode: {yaml_scalar(record.get('bibcode', ''))}",
            f"publication_types: [{yaml_scalar(publication_type(record))}]",
            f"publication: {yaml_scalar(publication)}",
            'publication_short: ""',
        ]
    )
    if doi:
        lines.append(f"doi: {yaml_scalar(doi)}")
    lines.extend(
        [
            f"abstract: {yaml_block(abstract)}",
            f"summary: {yaml_block(summary)}",
            "tags: []",
            "featured: true",
            "links:",
        ]
    )
    if links:
        for link in links:
            lines.append(f"  - url: {yaml_scalar(link['url'])}")
            if "type" in link:
                lines.append(f"    type: {yaml_scalar(link['type'])}")
            else:
                lines.append(f"    name: {yaml_scalar(link.get('name', 'Link'))}")
    else:
        lines.append("  []")
    lines.extend(
        [
            "image:",
            f"  caption: {yaml_scalar(figure_caption)}",
            '  focal_point: "Center"',
            "  preview_only: false",
            "projects: []",
            'slides: ""',
            "---",
            "",
        ]
    )
    return "\n".join(lines)


def write_publication(
    record: dict[str, Any],
    output_dir: Path,
    api_base: str,
    token: str,
    overwrite: bool,
    dry_run: bool,
) -> Path:
    slug = author_year_slug(record)
    pub_dir = unique_bundle_dir(output_dir, slug, record["bibcode"], overwrite)

    if pub_dir.exists() and not overwrite:
        return pub_dir
    if not dry_run:
        pub_dir.mkdir(parents=True, exist_ok=True)

    links = collect_links(record)
    figures = discover_graphics(api_base, token, record["bibcode"])
    figure_caption = first(figures[0].get("caption"), "") if figures else ""
    image_url = best_figure_url(figures)
    write_featured_image(pub_dir, image_url, token, dry_run)

    if not dry_run:
        (pub_dir / "index.md").write_text(
            front_matter(record, links, figure_caption),
            encoding="utf-8",
        )
    return pub_dir


def fetch_records(
    api_base: str,
    token: str,
    query: str,
    sort: str,
    rows: int,
    max_records: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    start = 0
    while len(records) < max_records:
        batch_size = min(rows, max_records - len(records))
        data = api_get_json(
            f"{api_base.rstrip('/')}/search/query",
            token,
            {
                "q": query,
                "sort": sort,
                "rows": batch_size,
                "start": start,
                "fl": ",".join(DEFAULT_FIELDS),
            },
        )
        docs = data.get("response", {}).get("docs", [])
        if not docs:
            break
        records.extend(docs)
        start += len(docs)
        if len(docs) < batch_size:
            break
        time.sleep(0.2)
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pull publications from SciX/ADS and write Hugo Blox publication posts."
    )
    parser.add_argument("--query", default=DEFAULT_QUERY, help="SciX/ADS search query.")
    parser.add_argument("--sort", default=DEFAULT_SORT, help="SciX/ADS sort expression.")
    parser.add_argument("--rows", type=int, default=25, help="API page size.")
    parser.add_argument("--max-records", type=int, default=100, help="Maximum records to import.")
    parser.add_argument(
        "--output-dir",
        default="content/publications",
        type=Path,
        help="Directory where publication page bundles are written.",
    )
    parser.add_argument(
        "--api-base",
        default=os.environ.get("SCIX_API_BASE", "https://api.adsabs.harvard.edu/v1"),
        help="SciX/ADS API base URL.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing bundles.")
    parser.add_argument("--dry-run", action="store_true", help="Print intended output only.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = os.environ.get("SCIX_TOKEN") or os.environ.get("ADS_DEV_KEY")
    if not token:
        print(
            "Missing API token. Set SCIX_TOKEN or ADS_DEV_KEY before running.",
            file=sys.stderr,
        )
        return 2

    records = fetch_records(
        args.api_base,
        token,
        args.query,
        args.sort,
        args.rows,
        args.max_records,
    )
    if not records:
        print("No publications found.")
        return 0

    written: list[Path] = []
    for record in records:
        if "bibcode" not in record:
            continue
        path = write_publication(
            record,
            args.output_dir,
            args.api_base,
            token,
            args.overwrite,
            args.dry_run,
        )
        written.append(path)

    action = "Would write" if args.dry_run else "Wrote"
    print(f"{action} {len(written)} publication bundles:")
    for path in written:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
