import csv
import io
from typing import Iterable


def assessments_to_csv(rows: Iterable[dict]) -> str:
    output = io.StringIO()
    fieldnames = [
        "id",
        "created_at",
        "patient_name",
        "age",
        "gender",
        "bmi",
        "thyroid_risk",
        "diabetes_risk",
        "pcos_risk",
        "adrenal_risk",
        "metabolic_risk",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in fieldnames})
    return output.getvalue()


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def assessments_to_pdf_bytes(rows: Iterable[dict]) -> bytes:
    lines = ["Endocrine Risk Assessments Report", ""]
    for idx, row in enumerate(rows, start=1):
        lines.append(
            f"{idx}. {row.get('created_at','')} | {row.get('patient_name','Anonymous')} | "
            f"Thyroid {row.get('thyroid_risk','')} | Diabetes {row.get('diabetes_risk','')} | "
            f"Risk Score {row.get('risk_score','')}"
        )
    if len(lines) == 2:
        lines.append("No assessments available.")

    escaped_lines = [_pdf_escape(line) for line in lines]

    content_parts = ["BT", "/F1 11 Tf", "50 780 Td", "14 TL"]
    for i, line in enumerate(escaped_lines):
        if i == 0:
            content_parts.append(f"({line}) Tj")
        else:
            content_parts.append("T*")
            content_parts.append(f"({line}) Tj")
    content_parts.append("ET")
    content = "\n".join(content_parts).encode("latin-1", errors="replace")

    offsets = []
    pdf = bytearray(b"%PDF-1.4\n")

    def add_obj(obj_bytes: bytes) -> None:
        offsets.append(len(pdf))
        obj_num = len(offsets)
        pdf.extend(f"{obj_num} 0 obj\n".encode("ascii"))
        pdf.extend(obj_bytes)
        pdf.extend(b"\nendobj\n")

    add_obj(b"<< /Type /Catalog /Pages 2 0 R >>")
    add_obj(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    add_obj(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>")
    add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    add_obj(b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream")

    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)+1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets:
        pdf.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            "trailer\n"
            f"<< /Size {len(offsets)+1} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref_pos}\n"
            "%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)
