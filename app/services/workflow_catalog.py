from app.schemas.workflow import Workflow, VerificationStatus


# Development fixtures only.
# These are NOT verified bank procedures.

WORKFLOWS = [
    Workflow(
        id="deposit-slip-demo",
        name="Deposit Slip Preparation",
        description="Prepare a sample cash deposit slip.",
        supported_languages=["en", "hi"],
        verification_status=VerificationStatus.SIMULATION,
        procedure_version="demo-1",
    ),
    Workflow(
        id="passbook-update-demo",
        name="Passbook Update Guidance",
        description="Practice using a simulated passbook kiosk.",
        supported_languages=["en", "hi"],
        verification_status=VerificationStatus.SIMULATION,
        procedure_version="demo-1",
    ),
    Workflow(
        id="debit-card-demo",
        name="Debit Card Request Guidance",
        description="Practice a sample debit card request journey.",
        supported_languages=["en", "hi"],
        verification_status=VerificationStatus.SIMULATION,
        procedure_version="demo-1",
    ),
]


def list_workflows(
    include_simulations: bool = False,
) -> list[Workflow]:
    if include_simulations:
        return WORKFLOWS.copy()

    return [
        workflow
        for workflow in WORKFLOWS
        if (
            workflow.verification_status
            == VerificationStatus.VERIFIED
            and workflow.source_reference is not None
            and workflow.verified_on is not None
        )
    ]
