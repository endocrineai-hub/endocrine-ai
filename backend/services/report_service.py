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
