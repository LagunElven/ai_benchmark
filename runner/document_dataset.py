"""Offline document fixture generation with a small, deterministic rasterizer."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


@dataclass(frozen=True)
class DocumentSpec:
    document_id: str
    text: str
    ground_truth: dict[str, Any]
    page_width_inches: float = 8.5


@dataclass(frozen=True)
class Raster:
    width: int
    height: int
    pixels: bytes
    dpi: int


def load_document_spec(path: str | Path, schema_path: str | Path | None = None) -> DocumentSpec:
    source_path = Path(path)
    try:
        value = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read document source {source_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("Document source must be a JSON object")
    selected_schema = (
        Path(schema_path)
        if schema_path is not None
        else Path(__file__).resolve().parents[1] / "schemas" / "document-source.schema.json"
    )
    if selected_schema.is_file():
        try:
            schema = json.loads(selected_schema.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            message = f"Cannot read document source schema {selected_schema}: {exc}"
            raise ValueError(message) from exc
        errors = sorted(
            Draft202012Validator(schema).iter_errors(value),
            key=lambda error: list(error.path),
        )
        if errors:
            location = ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
            raise ValueError(f"Document source schema error at {location}: {errors[0].message}")
    document_id = value.get("id")
    text = value.get("text")
    ground_truth = value.get("ground_truth")
    if not isinstance(document_id, str) or not document_id:
        raise ValueError("Document source id must be a non-empty string")
    if not isinstance(text, str) or not text:
        raise ValueError("Document source text must be a non-empty string")
    if not isinstance(ground_truth, dict):
        raise ValueError("Document source ground_truth must be an object")
    width = value.get("page_width_inches", 8.5)
    if not isinstance(width, (int, float)) or isinstance(width, bool) or width <= 0:
        raise ValueError("page_width_inches must be a positive number")
    return DocumentSpec(document_id, text, ground_truth, float(width))


def _glyph(character: str, row: int) -> int:
    """Return one five-bit row of a compact deterministic bitmap font."""
    character = character.upper()
    glyphs = {
        "0": (14, 17, 19, 21, 25, 17, 14),
        "1": (4, 12, 4, 4, 4, 4, 14),
        "2": (14, 17, 1, 2, 4, 8, 31),
        "3": (30, 1, 1, 14, 1, 1, 30),
        "4": (2, 6, 10, 18, 31, 2, 2),
        "5": (31, 16, 16, 30, 1, 1, 30),
        "6": (6, 8, 16, 30, 17, 17, 14),
        "7": (31, 1, 2, 4, 8, 8, 8),
        "8": (14, 17, 17, 14, 17, 17, 14),
        "9": (14, 17, 17, 15, 1, 2, 28),
        "-": (0, 0, 0, 31, 0, 0, 0),
        ".": (0, 0, 0, 0, 0, 12, 12),
        ":": (0, 12, 12, 0, 12, 12, 0),
        "/": (1, 2, 4, 8, 16, 0, 0),
        "_": (0, 0, 0, 0, 0, 0, 31),
        "(": (2, 4, 8, 8, 8, 4, 2),
        ")": (8, 4, 2, 2, 2, 4, 8),
        "€": (14, 16, 16, 30, 16, 16, 14),
    }
    if character == " ":
        return 0
    if character in glyphs:
        return glyphs[character][row]
    if "A" <= character <= "Z":
        # A compact generated alphabet keeps the renderer dependency-free while
        # still giving every letter a stable, non-empty glyph.
        seed = ord(character) * 0x45D9F3B
        return ((seed ^ (seed >> (row + 1)) ^ (row * 0x1F1F)) & 0x1F) or 1
    return 1 << ((ord(character) + row) % 5)


def render_text(text: str, *, dpi: int, page_width_inches: float = 8.5) -> Raster:
    if dpi <= 0:
        raise ValueError("dpi must be positive")
    lines = text.splitlines() or [""]
    scale = max(1, dpi // 150)
    margin = 20 * scale
    character_width = 6 * scale
    line_height = 9 * scale
    content_width = margin * 2 + max(map(len, lines)) * character_width
    page_width = int(page_width_inches * dpi)
    width = max(margin * 2 + character_width, min(page_width, content_width))
    if content_width > page_width:
        width = content_width
    height = margin * 2 + len(lines) * line_height
    pixels = bytearray([255]) * (width * height)
    for line_index, line in enumerate(lines):
        top = margin + line_index * line_height
        for column, character in enumerate(line):
            left = margin + column * character_width
            bits = [_glyph(character, row) for row in range(7)]
            for glyph_row, bit_row in enumerate(bits):
                for glyph_column in range(5):
                    if not (bit_row & (1 << (4 - glyph_column))):
                        continue
                    for y in range(scale):
                        for x in range(scale):
                            destination = (
                                (top + glyph_row * scale + y) * width
                                + left
                                + glyph_column * scale
                                + x
                            )
                            pixels[destination] = 0
    return Raster(width, height, bytes(pixels), dpi)


def rotate(raster: Raster, angle: int) -> Raster:
    if angle not in {90, 180, 270}:
        raise ValueError("angle must be 90, 180 or 270 degrees")
    if angle == 180:
        pixels = bytes(reversed(raster.pixels))
        return Raster(raster.width, raster.height, pixels, raster.dpi)
    new_width, new_height = raster.height, raster.width
    output = bytearray(new_width * new_height)
    for y in range(raster.height):
        for x in range(raster.width):
            if angle == 90:
                destination_x, destination_y = raster.height - 1 - y, x
            else:
                destination_x, destination_y = y, raster.width - 1 - x
            destination = destination_y * new_width + destination_x
            output[destination] = raster.pixels[y * raster.width + x]
    return Raster(new_width, new_height, bytes(output), raster.dpi)


def add_noise(raster: Raster, *, seed: int, probability: float = 0.012) -> Raster:
    if not 0 <= probability <= 1:
        raise ValueError("probability must be between zero and one")
    generator = random.Random(seed)
    pixels = bytearray(raster.pixels)
    for index, value in enumerate(pixels):
        if generator.random() < probability:
            pixels[index] = 0 if value > 127 else 255
    return Raster(raster.width, raster.height, bytes(pixels), raster.dpi)


def compress(raster: Raster, *, levels: int = 4) -> Raster:
    """Apply deterministic lossy grayscale quantization as a codec-neutral stand-in."""
    if levels < 2 or levels > 256:
        raise ValueError("levels must be between 2 and 256")
    step = 255 / (levels - 1)
    pixels = bytes(round(round(value / step) * step) for value in raster.pixels)
    return Raster(raster.width, raster.height, pixels, raster.dpi)


def write_pgm(path: Path, raster: Raster) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"P5\n# dpi={raster.dpi}\n{raster.width} {raster.height}\n255\n".encode("ascii")
    path.write_bytes(header + raster.pixels)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_dataset(source: str | Path, output: str | Path, *, seed: int = 20260915) -> Path:
    spec = load_document_spec(source)
    destination = Path(output)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Output directory is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "source.txt").write_text(spec.text, encoding="utf-8", newline="")
    (destination / "ground-truth.json").write_text(
        json.dumps(spec.ground_truth, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="",
    )

    base_300 = render_text(spec.text, dpi=300, page_width_inches=spec.page_width_inches)
    base_150 = render_text(spec.text, dpi=150, page_width_inches=spec.page_width_inches)
    variants = [
        ("digital-300dpi", base_300, {"type": "identity"}),
        ("digital-150dpi", base_150, {"type": "identity"}),
        ("rotated-300dpi", rotate(base_300, 90), {"type": "rotation", "degrees": 90}),
        (
            "noisy-150dpi",
            add_noise(base_150, seed=seed),
            {"type": "salt_pepper", "probability": 0.012, "seed": seed},
        ),
        ("compressed-150dpi", compress(base_150), {"type": "quantization", "levels": 4}),
    ]
    manifest_variants = []
    for name, raster, transform in variants:
        path = destination / "rendered" / f"{name}.pgm"
        write_pgm(path, raster)
        manifest_variants.append(
            {
                "name": name,
                "path": path.relative_to(destination).as_posix(),
                "format": "pgm",
                "dpi": raster.dpi,
                "width": raster.width,
                "height": raster.height,
                "sha256": _sha256(path),
                "transform": transform,
            }
        )
    manifest = {
        "schema_version": "1.0",
        "document_id": spec.document_id,
        "source": "source.txt",
        "ground_truth": "ground-truth.json",
        "generator": {"name": "enterprise-llm-bench-rasterizer", "version": "1", "seed": seed},
        "variants": manifest_variants,
    }
    manifest_path = destination / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="",
    )
    return manifest_path
