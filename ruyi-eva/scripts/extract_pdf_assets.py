#!/usr/bin/env python3
"""Extract catalogue evidence locally. Requires pypdf, pypdfium2 and Pillow."""
import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader
import pypdfium2 as pdfium


def extract(source: Path, output: Path):
    source = source.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Use a new empty output directory to preserve existing evidence")
    for folder in ("images", "web-images", "pages", "sheets"):
        (output / folder).mkdir()
    reader = PdfReader(source)
    renderer = pdfium.PdfDocument(str(source))
    assets, by_hash, pages = [], {}, []
    for number, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        preview = f"pages/page-{number:03}.jpg"
        rendered = renderer[number - 1]
        bitmap = rendered.render(scale=1.25)
        image = bitmap.to_pil().convert("RGB")
        image.save(output / preview, quality=88)
        image.close()
        bitmap.close()
        rendered.close()
        occurrences = []
        for item in page.images:
            digest = hashlib.sha256(item.data).hexdigest()
            asset = by_hash.get(digest)
            if asset is None:
                identifier = f"img-{len(assets) + 1:04}"
                with Image.open(io.BytesIO(item.data)) as decoded:
                    image_format = decoded.format
                    width, height = decoded.size
                extension = {"JPEG": ".jpg", "JPEG2000": ".jp2", "PNG": ".png", "TIFF": ".tif"}.get(image_format, Path(item.name).suffix or ".bin")
                relative = f"images/{identifier}{extension}"
                (output / relative).write_bytes(item.data)
                asset = dict(id=identifier, file=relative, sha256=digest,
                             format=image_format, width=width, height=height, occurrences=[])
                # PDF JPEG2000 may be named .jpg by pypdf but Chrome cannot decode it.
                # Preserve the original bytes; create a lossless, browser-compatible derivative.
                if image_format not in ("JPEG", "PNG"):
                    browser_file = f"web-images/{identifier}.png"
                    with Image.open(output / relative) as decoded:
                        decoded.convert("RGBA" if "A" in decoded.getbands() else "RGB").save(output / browser_file)
                    asset["browserFile"] = browser_file
                by_hash[digest] = asset
                assets.append(asset)
            asset["occurrences"].append(dict(pdfPage=number, name=item.name))
            occurrences.append(asset["id"])
        pages.append(dict(pdfPage=number, preview=preview, text=text, imageIds=occurrences))
    renderer.close()
    for start in range(0, len(assets), 40):
        subset = assets[start:start + 40]
        sheet = Image.new("RGB", (1200, ((len(subset) + 4) // 5) * 180), "#e8e8e8")
        draw = ImageDraw.Draw(sheet)
        for index, asset in enumerate(subset):
            x, y = (index % 5) * 240, (index // 5) * 180
            with Image.open(output / asset["file"]) as original:
                thumb = original.convert("RGBA")
                thumb.thumbnail((228, 145))
                sheet.paste(thumb, (x + (240 - thumb.width) // 2, y), thumb)
            page_numbers = sorted({item["pdfPage"] for item in asset["occurrences"]})
            draw.text((x + 5, y + 148), f'{asset["id"]} {asset["width"]}x{asset["height"]}', fill="black")
            draw.text((x + 5, y + 162), "PDF p." + ",".join(map(str, page_numbers)), fill="black")
        sheet.save(output / f"sheets/images-{start // 40 + 1:02}.jpg", quality=90)
    manifest = dict(source=str(source), sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                    pageCount=len(pages), uniqueImageCount=len(assets), images=assets, pages=pages)
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (output / "text.txt").write_text("\n\n".join(f'=== PDF page {p["pdfPage"]} ===\n{p["text"]}' for p in pages))
    print(json.dumps(dict(pages=len(pages), uniqueImages=len(assets), output=str(output.resolve()))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    extract(args.source, args.output)
