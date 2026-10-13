import json
from pathlib import Path

import cv2

from o import o


SOURCE_IMAGE = Path(r"C:\Users\mario\Desktop\worst_test.png")
OUTPUT_DIR = Path(".synthetic-eval")
EXPECTED = {
    "invoice_id": "206668",
    "total": "1095.9",
}


def _rotate(image, degrees):
    height, width = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), degrees, 1.0)
    return cv2.warpAffine(
        image,
        matrix,
        (width, height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )


def _adjust(image, alpha=1.0, beta=0):
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def _jpeg_copy(image, path, quality):
    cv2.imwrite(str(path), image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return cv2.imread(str(path))


def _variants(image):
    return {
        "original": image,
        "darker": _adjust(image, alpha=0.82, beta=-15),
        "brighter": _adjust(image, alpha=1.12, beta=20),
        "higher_contrast": _adjust(image, alpha=1.35, beta=-25),
        "lower_contrast": _adjust(image, alpha=0.72, beta=25),
        "blurred": cv2.GaussianBlur(image, (3, 3), 0),
        "rotated_left": _rotate(image, -2.0),
        "rotated_right": _rotate(image, 2.0),
    }


def _first_value(result, key):
    values = result.get(key) or []
    if not values:
        return None, None
    return values[0][0], values[0][1]


def main():
    image = cv2.imread(str(SOURCE_IMAGE))
    if image is None:
        raise FileNotFoundError(SOURCE_IMAGE)

    image_dir = OUTPUT_DIR / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for name, variant in _variants(image).items():
        extension = ".jpg" if name == "lower_contrast" else ".png"
        path = image_dir / f"{name}{extension}"
        if extension == ".jpg":
            variant = _jpeg_copy(variant, path, quality=60)
        else:
            cv2.imwrite(str(path), variant)

        result = o(str(path))
        invoice_id, invoice_confidence = _first_value(result, "v")
        total, total_confidence = _first_value(result, "va")
        invoice_correct = invoice_id == EXPECTED["invoice_id"]
        total_correct = total == EXPECTED["total"]
        rows.append(
            {
                "variant": name,
                "invoice_id": invoice_id,
                "invoice_confidence": invoice_confidence,
                "invoice_correct": invoice_correct,
                "total": total,
                "total_confidence": total_confidence,
                "total_correct": total_correct,
                "both_correct": invoice_correct and total_correct,
            }
        )

    total_cases = len(rows)
    summary = {
        "source_image": str(SOURCE_IMAGE),
        "expected": EXPECTED,
        "test_type": "synthetic single-sample stress test",
        "num_variants": total_cases,
        "invoice_exact_match": sum(row["invoice_correct"] for row in rows),
        "total_exact_match": sum(row["total_correct"] for row in rows),
        "both_fields_exact_match": sum(row["both_correct"] for row in rows),
    }
    summary["invoice_exact_match_rate"] = summary["invoice_exact_match"] / total_cases
    summary["total_exact_match_rate"] = summary["total_exact_match"] / total_cases
    summary["both_fields_exact_match_rate"] = (
        summary["both_fields_exact_match"] / total_cases
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "synthetic_eval.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, indent=2),
        encoding="utf-8",
    )

    print(json.dumps({"summary": summary, "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
