# OCR Invoice Extractor

A bilingual Arabic/English OCR pipeline for extracting structured fields from invoice document images. Built with PaddleOCR and Flask, with a custom fuzzy keyword matcher and spatial line-reconstruction algorithm.

---

## What It Does

Given an image of an Arabic or bilingual invoice, the system extracts:

- **Invoice number** — detected via fuzzy keyword matching against Arabic invoice terms
- **Total amount** — extracted using positional logic relative to total/balance keywords
- **Confidence scores** — returned per extracted field for downstream validation

All results are returned as JSON via a REST API endpoint.

---

## How It Works

### 1. Dual-Language OCR Pass
The pipeline runs PaddleOCR twice on the same image — once for English, once for Arabic — collecting all detected words with their bounding box coordinates and confidence scores.

### 2. Spatial Line Reconstruction
Raw OCR output is an unordered list of bounding boxes. A custom y-threshold clustering algorithm groups detected words into lines based on vertical proximity, then sorts each line left-to-right by x-coordinate — reconstructing the document's reading order without any layout analysis library.

```
words → group by y-proximity → sort each line by x → structured lines
```

### 3. Fuzzy Arabic Keyword Matching
Arabic OCR output frequently produces character variants of the same word (e.g. `ىفاض` vs `يفاص`). A custom fuzzy matcher using **Longest Common Subsequence (LCS) dynamic programming** handles these variants without requiring exact string matches.

Target keyword groups:
- Invoice: `ةروتاف`, `دوك`
- Total/Balance: `يفاص`, `ةصلاخ`

### 4. Positional Field Extraction
Once keywords are located, invoice numbers (integers) and total amounts (floats) are extracted using multi-fallback positional logic — scanning adjacent cells and nearby lines when the primary position is empty.

---

## API

### `POST /`

Upload a document image and receive extracted fields.

**Request**
```
Content-Type: multipart/form-data
Body: image=<file>
```

**Response**
```json
{
  "v": [["12345", 0.98]],
  "va": [["1500.00", 0.95]]
}
```

| Field | Description |
|---|---|
| `v` | Extracted invoice numbers with confidence scores |
| `va` | Extracted total amounts with confidence scores |

---

## Tech Stack

- **Python** — core language
- **PaddleOCR** — bilingual OCR inference (Arabic + English)
- **Flask** — REST API layer
- **OpenCV** — image handling
- **Custom algorithms** — LCS fuzzy matching, y-threshold line clustering

---

## Installation

```bash
git clone https://github.com/Marioromeo7/ocr-invoice-extractor.git
cd ocr-invoice-extractor
pip install -r requirements.txt
```

> **Note:** PaddleOCR will download language model weights on first run. Requires ~500MB disk space.

---

## Running

```bash
python app.py
```

Server starts at `http://localhost:5000`

**Test with curl:**
```bash
curl -X POST http://localhost:5000/ \
  -F "image=@your_invoice.jpg"
```

---

## Project Structure

```
ocr-invoice-extractor/
├── app.py              # Flask REST API
├── o.py                # Core OCR pipeline and field extraction
├── y.py                # LCS fuzzy matcher test script
└── requirements.txt    # Dependencies
```

---

## Design Decisions

**Why dual-language OCR passes?**
PaddleOCR performs better per-language than in multilingual mode. Running separate passes and merging by spatial coordinates gives higher accuracy on mixed Arabic/English invoices.

**Why a custom LCS matcher instead of a library?**
Arabic OCR variants are subtle character-level differences. Standard string distance metrics (Levenshtein) penalize substitutions uniformly. LCS rewards shared subsequences, which better captures how OCR errors manifest in Arabic script.

**Why positional fallback logic for field extraction?**
Invoice layouts vary significantly across vendors. A rigid positional approach fails on format changes. The multi-fallback system scans a window of adjacent lines and positions, making extraction more robust across different invoice templates.

---

## Limitations

- Optimized for Egyptian Arabic invoice formats
- Performance depends on image quality and scan resolution
- y-threshold line grouping may misgroup words in heavily skewed scans
- Currently extracts invoice number and total amount only

---

## Author

**Mario Hossam Mitry George**
Backend Engineer · AI Systems Developer
[LinkedIn](https://linkedin.com/in/mario-george-5945a9296) · [GitHub](https://github.com/Marioromeo7)
