# API Spec

## POST /api/assess
- Input: patient_name, profile, optional lab_report_text
- Output: status, extracted_markers, assessment

## POST /api/extract-markers
- Input: lab_report_text
- Output: status, extracted_markers

## POST /api/chat
- Input: message, optional assessment
- Output: status, reply, disclaimer

## GET /api/admin/assessments
- Auth: admin session
- Output: assessments list
