# Document datasets

Sources in this directory are small, deterministic JSON specifications. Generate
the rendered variants and manifest into a disposable directory with:

```powershell
python scripts/generate_document_dataset.py datasets/documents/invoice-001.json .tmp/invoice-001
```

The generator writes canonical text, versioned JSON ground truth and PGM raster
variants at 300/150 DPI, plus rotated, noisy and lossy-quantized variants. PGM
is intentionally dependency-free; a future OCR campaign may convert the same
pixels to PNG/PDF/JPEG when those codecs are provisioned.
