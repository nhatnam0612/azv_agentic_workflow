from azv_workflow.models import AZVAssessment, InvoiceExtraction, InvoiceLine


def test_invoice_schema():
    invoice = InvoiceExtraction(
        invoice_number="001234-20",
        lines=[InvoiceLine(goa_number="1040", service="Professionelle Zahnreinigung")],
    )
    assert invoice.lines[0].goa_number == "1040"


def test_assessment_confidence_validation():
    assessment = AZVAssessment(
        classification="UNKLAR",
        confidence=0.5,
        human_review_required=True,
    )
    assert assessment.human_review_required is True
