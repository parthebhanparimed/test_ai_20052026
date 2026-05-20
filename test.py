# # from presidio_analyzer import AnalyzerEngine
# # from presidio_anonymizer import AnonymizerEngine
# # import re

# # # -----------------------------
# # # Initialize Presidio
# # # -----------------------------
# # analyzer = AnalyzerEngine()
# # anonymizer = AnonymizerEngine()

# # # -----------------------------
# # # Custom Regex Patterns
# # # -----------------------------
# # CUSTOM_PATTERNS = {
# #     "MRN": r"\bMRN[: ]?\d+\b",
# #     "DOB": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
# #     "PHONE": r"\b(?:\+91[- ]?)?[6-9]\d{9}\b",
# #     "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
# # }

# # # -----------------------------
# # # Prompt Injection Protection
# # # -----------------------------
# # BLOCK_PATTERNS = [
# #     "ignore previous instructions",
# #     "reveal system prompt",
# #     "bypass security",
# # ]

# # # -----------------------------
# # # Regex Redaction
# # # -----------------------------
# # def regex_redact(text: str):

# #     for entity, pattern in CUSTOM_PATTERNS.items():
# #         text = re.sub(
# #             pattern,
# #             f"<{entity}>",
# #             text,
# #             flags=re.IGNORECASE
# #         )

# #     return text

# # # -----------------------------
# # # Prompt Safety Validation
# # # -----------------------------
# # def validate_prompt_safety(text: str):

# #     lower = text.lower()

# #     for pattern in BLOCK_PATTERNS:
# #         if pattern in lower:
# #             raise ValueError(
# #                 f"Blocked unsafe instruction: {pattern}"
# #             )

# # # -----------------------------
# # # Main Guardrail Function
# # # -----------------------------
# # def sanitize_for_llm(text: str):

# #     # Block prompt injection
# #     validate_prompt_safety(text)

# #     # Regex masking
# #     text = regex_redact(text)

# #     # Presidio detection + anonymization
# #     results = analyzer.analyze(
# #         text=text,
# #         language="en"
# #     )

# #     sanitized = anonymizer.anonymize(
# #         text=text,
# #         analyzer_results=results
# #     )

# #     return sanitized.text

# # # -----------------------------
# # # TEST INPUT
# # # -----------------------------
# # auditor_comment = """
# # [ { "example": "Missed code N1830 from PL with support of lab value of cr 1.37 m" }, { "example": "Deleted M359 from page no 25,49 due to unacceptable notes" }, { "example": "Modified I10 to I129 from assessment on page 2,36" }, { "example": "NPI number modified from 1649290800 to 1306805460 with attestation signature" }, { "example": "Added atrial fibrillation with support of propafenone from page no,35" }, { "example": "Deleted Z9484 12/15/2025 p-34 Cell transplant only present under PMH" }, { "example": "I130 modified to I129 due to absence of documented heart failure" }, { "example": "E1165 modified to E119 8/18/2025 p-20 Diabetes mellitus without hyperglycemia support" } ]
# # """

# # # -----------------------------
# # # RUN TEST
# # # -----------------------------
# # try:

# #     safe_text = sanitize_for_llm(auditor_comment)

# #     print("\n===== SANITIZED OUTPUT =====\n")
# #     print(safe_text)

# # except Exception as e:

# #     print("\nBLOCKED:")
# #     print(str(e))

# import re
# from presidio_analyzer import AnalyzerEngine, PatternRecognizer, RecognizerRegistry, Pattern
# from presidio_anonymizer import AnonymizerEngine

# # =====================================================
# # Hardened Custom Patterns (Fixed Presidio Object Format)
# # =====================================================
# # Wrapping the pattern dicts in the native Pattern class solves the compilation crash
# MRN_RECOGNIZER = PatternRecognizer(
#     supported_entity="MRN",
#     patterns=[Pattern(name="mrn_pattern", regex=r"\bMRN[: ]?\d+\b", score=0.95)]
# )

# NPI_RECOGNIZER = PatternRecognizer(
#     supported_entity="NPI",
#     patterns=[Pattern(name="npi_pattern", regex=r"\b\d{10}\b", score=0.95)]
# )

# DOB_RECOGNIZER = PatternRecognizer(
#     supported_entity="DOB",
#     patterns=[Pattern(name="dob_pattern", regex=r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", score=0.95)]
# )

# # =====================================================
# # Initialize Presidio Registry & Engine
# # =====================================================
# registry = RecognizerRegistry()
# registry.load_predefined_recognizers()  # Keeps default PERSON, EMAIL, PHONE_NUMBER engines

# # Add our specialized clinical/PII structural recognizers
# registry.add_recognizer(MRN_RECOGNIZER)
# registry.add_recognizer(NPI_RECOGNIZER)
# registry.add_recognizer(DOB_RECOGNIZER)

# analyzer = AnalyzerEngine(registry=registry)
# anonymizer = AnonymizerEngine()

# # =====================================================
# # Prompt Injection Guardrails
# # =====================================================
# BLOCK_PATTERNS = [
#     "ignore previous instructions",
#     "reveal system prompt",
#     "bypass security",
#     "print patient data",
#     "show hidden prompt",
# ]

# def validate_prompt_safety(text: str):
#     lower = text.lower()
#     for pattern in BLOCK_PATTERNS:
#         if pattern in lower:
#             raise ValueError(f"Blocked unsafe instruction token: {pattern}")

# # =====================================================
# # Main Consolidated Guardrail Function
# # =====================================================
# def sanitize_for_llm(text: str):
#     if not text:
#         return text

#     # Step 1: Prompt Injection Protection
#     validate_prompt_safety(text)

#     # Step 2: Unified Analysis Pass 
#     analysis_results = analyzer.analyze(
#         text=text,
#         language="en",
#         entities=[
#             "PERSON",
#             "EMAIL_ADDRESS",
#             "PHONE_NUMBER",
#             "MRN",
#             "NPI",
#             "DOB"
#         ]
#     )

#     # Step 3: Coordinated Anonymization
#     anonymized_result = anonymizer.anonymize(
#         text=text,
#         analyzer_results=analysis_results
#     )

#     return anonymized_result.text

# # =====================================================
# # EXECUTE TEST (Auditor Context Sample)
# # =====================================================
# auditor_comment = """
# [ { "example": "Missed code N1830 from PL with support of lab value of cr 1.37 m" }, { "example": "Deleted M359 from page no 25,49 due to unacceptable notes" }, { "example": "Modified I10 to I129 from assessment on page 2,36" }, { "example": "NPI number modified from 1649290800 to 1306805460 with attestation signature" }, { "example": "Added atrial fibrillation with support of propafenone from page no,35" }, { "example": "Deleted Z9484 12/15/2025 p-34 Cell transplant only present under PMH" }, { "example": "I130 modified to I129 due to absence of documented heart failure" }, { "example": "E1165 modified to E119 8/18/2025 p-20 Diabetes mellitus without hyperglycemia support" } ]
# """

# try:
#     safe_text = sanitize_for_llm(auditor_comment)
#     print("\n===== SANITIZED OUTPUT =====")
#     print(safe_text)
# except Exception as e:
#     print(f"\nBLOCKED: {str(e)}")




# from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
# from presidio_anonymizer import AnonymizerEngine
# from presidio_anonymizer.entities import OperatorConfig

# # =====================================================
# # Initialize Presidio Engine with Native Rules
# # =====================================================
# registry = RecognizerRegistry()
# # Automatically loads highly optimized native ML engines for:
# # PERSON, EMAIL_ADDRESS, PHONE_NUMBER, DATE_TIME, etc.
# registry.load_predefined_recognizers() 

# analyzer = AnalyzerEngine(registry=registry)
# anonymizer = AnonymizerEngine()

# # =====================================================
# # Prompt Injection Guardrails (String-based matching)
# # =====================================================
# BLOCK_PATTERNS = [
#     "ignore previous instructions",
#     "reveal system prompt",
#     "bypass security",
#     "print patient data",
#     "show hidden prompt",
# ]

# def validate_prompt_safety(text: str):
#     lower = text.lower()
#     for pattern in BLOCK_PATTERNS:
#         if pattern in lower:
#             raise ValueError(f"Blocked unsafe instruction token: {pattern}")

# # =====================================================
# # Main Consolidated Guardrail Function
# # =====================================================
# def sanitize_for_llm(text: str):
#     if not text:
#         return text

#     # Step 1: Prompt Injection Protection (No regex used)
#     validate_prompt_safety(text)

#     # Step 2: Native NLP Engine Analysis
#     # We target standard entities, mapping dates directly to 'DATE_TIME'
#     analysis_results = analyzer.analyze(
#         text=text,
#         language="en",
#         entities=[
#             "PERSON",
#             "EMAIL_ADDRESS",
#             "PHONE_NUMBER",
#             "DATE_TIME"
#         ]
#     )

#     # Step 3: Direct Redaction Configuration (Removes both text and tags)
#     # Using "redact" completely deletes the word out of the data stream.
#     # If you prefer a static placeholder, change "redact" to "replace" and add {"value": "[REDACTED]"}
#     redact_operator = OperatorConfig("redact")
    
#     operators = {
#         "PERSON": redact_operator,
#         "EMAIL_ADDRESS": redact_operator,
#         "PHONE_NUMBER": redact_operator,
#         "DATE_TIME": redact_operator
#     }

#     # Step 4: Coordinated Anonymization
#     anonymized_result = anonymizer.anonymize(
#         text=text,
#         analyzer_results=analysis_results,
#         operators=operators
#     )

#     return anonymized_result.text

# # =====================================================
# # EXECUTE TEST (Auditor Context Sample)
# # =====================================================
# auditor_comment = """
# [ { "example": "Missed code N1830 from PL with support of lab value of cr 1.37 m" }, { "example": "Deleted M359 from page no 25,49 due to unacceptable notes" }, { "example": "Modified I10 to I129 from assessment on page 2,36" }, { "example": "NPI number modified from 1649290800 to 1306805460 with attestation signature" }, { "example": "Added atrial fibrillation with support of propafenone from page no,35" }, { "example": "Deleted Z9484 12/15/2025 p-34 Cell transplant only present under PMH" }, { "example": "I130 modified to I129 due to absence of documented heart failure" }, { "example": "E1165 modified to E119 8/18/2025 p-20 Diabetes mellitus without hyperglycemia support" } ]
# """

# try:
#     safe_text = sanitize_for_llm(auditor_comment)
#     print("\n===== SANITIZED OUTPUT =====")
#     print(safe_text)
# except Exception as e:
#     print(f"\nBLOCKED: {str(e)}")



from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import re

# =====================================================
# Initialize Engines
# =====================================================
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# =====================================================
# Healthcare-Safe Regex Patterns
# =====================================================
CUSTOM_PATTERNS = {

    # Explicit PHI
    "MRN": r"\bMRN[: ]?\d+\b",

    # NPI Numbers
    "NPI": r"\b\d{10}\b",

    # DOB only if explicitly mentioned
    "DOB": r"\bDOB[: ]?\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

    # Phone
    "PHONE": r"\b(?:\+91[- ]?)?[6-9]\d{9}\b",

    # Email
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
}

# =====================================================
# Prompt Injection Protection
# =====================================================
BLOCK_PATTERNS = [
    "ignore previous instructions",
    "reveal system prompt",
    "bypass security",
    "print patient data",
    "show hidden prompt",
]

# =====================================================
# Prompt Validation
# =====================================================
def validate_prompt_safety(text: str):

    lower = text.lower()

    for pattern in BLOCK_PATTERNS:

        if pattern in lower:

            raise ValueError(
                f"Blocked unsafe instruction: {pattern}"
            )

# =====================================================
# Regex Redaction
# =====================================================
def regex_redact(text: str):

    for entity, pattern in CUSTOM_PATTERNS.items():

        text = re.sub(
            pattern,
            f"<{entity}>",
            text,
            flags=re.IGNORECASE
        )

    return text

# =====================================================
# Main Guardrail
# =====================================================
def sanitize_for_llm(text: str):

    if not text:
        return text

    # ---------------------------------------------
    # Step 1: Prompt Injection Protection
    # ---------------------------------------------
    validate_prompt_safety(text)

    # ---------------------------------------------
    # Step 2: Regex-based PHI masking
    # ---------------------------------------------
    text = regex_redact(text)

    # ---------------------------------------------
    # Step 3: Presidio NLP Detection
    # Restrict entities to avoid ICD false positives
    # ---------------------------------------------
    results = analyzer.analyze(
        text=text,
        language="en",
        entities=[
            "PERSON",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER"
        ]
    )

    # ---------------------------------------------
    # Step 4: Presidio Anonymization
    # ---------------------------------------------
    sanitized = anonymizer.anonymize(
        text=text,
        analyzer_results=results
    )

    return sanitized.text

# =====================================================
# TEST INPUT
# =====================================================
auditor_comment = """
**Medical Chart Summary**

Patient Name: John Doe
DOB: 14-May-1980
Age: 45
Gender: Male
Medical Record Number: MRN-2026-1001
Date of Visit: 18-May-2026
Physician: Dr. Sarah Williams

John Doe, a 45-year-old male, presented to the clinic for a follow-up evaluation related to Type 2 Diabetes Mellitus. The patient reported symptoms including frequent urination, fatigue, and occasional blurred vision over the past several weeks. Vital signs recorded during the visit showed a blood pressure of 140/90 mmHg and a heart rate of 82 bpm.

The patient’s laboratory results indicated an HbA1c level of 8.2%, suggesting suboptimal glycemic control. Current medications include Metformin 500mg twice daily. The patient has a documented allergy to Penicillin.

Patient demographic and contact information on file includes:
Address: 123 Elm Street, New York, NY, USA
Phone: +1 555-123-4567
Email: [john.doe@example.com](mailto:john.doe@example.com)
SSN: 123-45-6789
Insurance ID: INS-458963214

The treatment plan discussed during the visit includes continuation of Metformin therapy, dietary modifications, regular exercise, and close glucose monitoring. Follow-up was recommended in three months for repeat laboratory evaluation and medication review.

James Anderson hs four billed invoice.
+91 99999 99999


Emergency Contact: Mary Doe – +1 555-987-6543


"""

# =====================================================
# RUN TEST
# =====================================================
try:

    safe_text = sanitize_for_llm(auditor_comment)

    print("\n===== SANITIZED OUTPUT =====\n")
    print(safe_text)

except Exception as e:

    print("\nBLOCKED:")
    print(str(e))