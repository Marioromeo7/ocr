import re

from paddleocr import PaddleOCR


INVOICE_KEYWORDS = ["ةروتاف", "فاتورة", "دوك", "كود", "عيب", "بيع"]


def _ocr_words(img_path):
    words = []
    for lang in ["en", "arabic"]:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)
        result = ocr.ocr(img_path, cls=True)
        for block in result or []:
            for item in block or []:
                box = item[0]
                text, confidence = item[1]
                x = min(point[0] for point in box)
                y = min(point[1] for point in box)
                words.append(
                    {
                        "x": x,
                        "y": y,
                        "text": text.strip(),
                        "confidence": float(confidence),
                        "lang": lang,
                    }
                )
    return words


def _group_words_by_line(words, y_threshold=12):
    lines = []
    for word in sorted(words, key=lambda item: (item["y"], item["x"])):
        if not lines or abs(word["y"] - lines[-1]["y"]) >= y_threshold:
            lines.append({"y": word["y"], "items": [word]})
            continue

        lines[-1]["items"].append(word)
        lines[-1]["y"] = sum(item["y"] for item in lines[-1]["items"]) / len(
            lines[-1]["items"]
        )

    for line in lines:
        line["items"].sort(key=lambda item: item["x"])
    return lines


def _dedupe_words(words, x_threshold=8, y_threshold=8):
    deduped = []
    for word in sorted(words, key=lambda item: -item["confidence"]):
        duplicate = any(
            existing["text"] == word["text"]
            and abs(existing["x"] - word["x"]) <= x_threshold
            and abs(existing["y"] - word["y"]) <= y_threshold
            for existing in deduped
        )
        if not duplicate:
            deduped.append(word)
    return deduped


def _keyword_score(text, keyword):
    if keyword in text:
        return 1.0
    if not text or not keyword:
        return 0.0

    match_count = 0
    keyword_index = 0
    for char in text:
        if keyword_index >= len(keyword):
            break
        if char == keyword[keyword_index]:
            match_count += 1
            keyword_index += 1
    return match_count / max(len(keyword), 1)


def _matches_invoice_keyword(text):
    return max(_keyword_score(text, keyword) for keyword in INVOICE_KEYWORDS) >= 0.55


def _clean_number(text):
    number = re.sub(r"[^\d.]", "", text)
    if number.count(".") > 1:
        parts = number.split(".")
        number = "".join(parts[:-1]) + "." + parts[-1]
    return number


def _integer_candidate(word):
    number = _clean_number(word["text"])
    if number.isdigit() and 4 <= len(number) <= 10:
        return number
    return None


def _decimal_candidate(word):
    number = _clean_number(word["text"])
    if re.fullmatch(r"\d+\.\d+", number):
        return number
    return None


def _extract_invoice_id(lines):
    best = None
    for line in lines:
        keyword_items = [
            item for item in line["items"] if _matches_invoice_keyword(item["text"])
        ]
        if not keyword_items:
            continue

        candidates = []
        for item in line["items"]:
            number = _integer_candidate(item)
            if not number:
                continue
            nearest_keyword_distance = min(
                abs(item["x"] - keyword["x"]) for keyword in keyword_items
            )
            candidates.append((nearest_keyword_distance, -item["confidence"], number, item))

        if candidates:
            _, _, number, item = sorted(candidates)[0]
            current = [number, round(item["confidence"], 4)]
            if best is None or current[1] > best[1]:
                best = current
    return [best] if best else []


def _extract_total(lines):
    decimal_lines = []
    for line in lines:
        values = []
        for item in line["items"]:
            number = _decimal_candidate(item)
            if number:
                values.append((number, item))
        unique_values = _dedupe_amounts(values)
        if len(unique_values) >= 3:
            decimal_lines.append((line["y"], unique_values))

    if not decimal_lines:
        return []

    _, values = max(decimal_lines, key=lambda item: item[0])
    values = sorted(values, key=lambda item: item[1]["x"])

    # Egyptian invoice summaries in this dataset place net invoice after current
    # and previous balances: current, previous, net invoice, gross/other total.
    if len(values) >= 3:
        number, item = values[2]
    else:
        number, item = values[-1]
    return [[number, round(item["confidence"], 4)]]


def _dedupe_amounts(values, x_threshold=10):
    deduped = []
    for number, item in sorted(values, key=lambda pair: -pair[1]["confidence"]):
        duplicate = any(
            existing_number == number
            and abs(existing_item["x"] - item["x"]) <= x_threshold
            for existing_number, existing_item in deduped
        )
        if not duplicate:
            deduped.append((number, item))
    return sorted(deduped, key=lambda pair: pair[1]["x"])


def o(img_path):
    words = _dedupe_words(_ocr_words(img_path))
    lines = _group_words_by_line(words)
    return {
        "v": _extract_invoice_id(lines),
        "va": _extract_total(lines),
    }
