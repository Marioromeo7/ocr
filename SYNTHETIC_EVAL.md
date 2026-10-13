# Synthetic OCR Evaluation

This is a synthetic single-sample stress test, not a dataset-level accuracy claim.

Source image:

```text
C:\Users\mario\Desktop\worst_test.png
```

Ground truth used for the test:

| Field | Expected value |
|---|---:|
| Invoice number | 206668 |
| Total | 1095.9 |

The source image was transformed into 8 controlled variants: original, darker,
brighter, higher contrast, lower contrast with JPEG compression, blurred,
rotated left, and rotated right.

## Result

| Metric | Result |
|---|---:|
| Invoice number exact match | 7 / 8 = 87.5% |
| Total exact match | 7 / 8 = 87.5% |
| Both fields exact match | 7 / 8 = 87.5% |

On the original image, the extractor returned:

```json
{
  "v": [["206668", 0.9967]],
  "va": [["1095.9", 0.9975]]
}
```

## Per-Variant Results

| Variant | Invoice number | Invoice confidence | Total | Total confidence | Both correct |
|---|---:|---:|---:|---:|---|
| original | 206668 | 0.9967 | 1095.9 | 0.9975 | yes |
| darker | 206668 | 0.9970 | 1095.9 | 0.9977 | yes |
| brighter | 206668 | 0.9967 | 1095.9 | 0.9974 | yes |
| higher_contrast | 206668 | 0.9966 | 1095.9 | 0.9975 | yes |
| lower_contrast | 206668 | 0.9955 | 1095.9 | 0.9974 | yes |
| blurred | 206668 | 0.9972 | 1095.9 | 0.9983 | yes |
| rotated_left | 20668 | 0.7370 | 21.359 | 0.8526 | no |
| rotated_right | 206668 | 0.9970 | 1095.9 | 0.9972 | yes |

## Shareable Wording

In a synthetic stress test generated from one labeled invoice image, the OCR
extractor correctly identified both the invoice number and total in 7 of 8
controlled variants, for an exact-match rate of 87.5%. On the original sample,
it extracted invoice number `206668` with 99.67% OCR confidence and total
`1095.9` with 99.75% OCR confidence.

Because this test is based on one invoice and synthetic transformations, it
should be described as a single-sample stress test rather than real production
accuracy.
