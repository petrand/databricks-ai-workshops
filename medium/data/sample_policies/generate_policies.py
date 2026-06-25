#!/usr/bin/env python3
"""Generate realistic sample company policy PDFs for the Policy Compliance app.

These PDFs are used to test the upload + review-date/overdue features. Each PDF
contains a title, a metadata header block, and well-structured policy sections so
that browser-side text extraction yields meaningful content.

Review dates are deliberately varied relative to "today" = 2026-06-22 so the
dashboard exercises all three states:
    reviewDate < today                -> "Overdue"
    reviewDate within 90 days of today -> "Due soon"
    otherwise                          -> "Current"

Run with a venv that has reportlab installed, e.g.:
    uv run --with reportlab python generate_policies.py
"""

import os

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

ACCENT = HexColor("#1B3A57")
LIGHT = HexColor("#EEF2F6")
GREY = HexColor("#666666")


def styles():
    base = getSampleStyleSheet()
    s = {}
    s["title"] = ParagraphStyle(
        "title", parent=base["Title"], fontName="Helvetica-Bold",
        fontSize=20, textColor=ACCENT, spaceAfter=4, alignment=TA_LEFT,
    )
    s["subtitle"] = ParagraphStyle(
        "subtitle", parent=base["Normal"], fontName="Helvetica",
        fontSize=10, textColor=GREY, spaceAfter=12,
    )
    s["h2"] = ParagraphStyle(
        "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
        fontSize=12.5, textColor=ACCENT, spaceBefore=12, spaceAfter=4,
    )
    s["body"] = ParagraphStyle(
        "body", parent=base["Normal"], fontName="Helvetica",
        fontSize=10, leading=14, spaceAfter=6,
    )
    s["bullet"] = ParagraphStyle(
        "bullet", parent=base["Normal"], fontName="Helvetica",
        fontSize=10, leading=14, leftIndent=16, bulletIndent=4, spaceAfter=3,
    )
    s["meta"] = ParagraphStyle(
        "meta", parent=base["Normal"], fontName="Helvetica",
        fontSize=9.5, leading=13,
    )
    return s


def meta_block(S, meta):
    rows = [
        ["Owner", meta["owner"], "Category", meta["category"]],
        ["Version", meta["version"], "Document Name", meta["docName"]],
        ["Effective Date", meta["effectiveDate"], "Review Date", meta["reviewDate"]],
    ]
    data = []
    for r in rows:
        data.append([
            Paragraph(f"<b>{r[0]}</b>", S["meta"]),
            Paragraph(r[1], S["meta"]),
            Paragraph(f"<b>{r[2]}</b>", S["meta"]),
            Paragraph(r[3], S["meta"]),
        ])
    t = Table(data, colWidths=[1.1 * inch, 2.15 * inch, 1.2 * inch, 2.05 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, ACCENT),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, HexColor("#C9D4DE")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def revision_table(S, rows):
    header = ["Version", "Date", "Author", "Summary of Changes"]
    data = [[Paragraph(f"<b>{h}</b>", S["meta"]) for h in header]]
    for r in rows:
        data.append([Paragraph(c, S["meta"]) for c in r])
    t = Table(data, colWidths=[0.8 * inch, 1.0 * inch, 1.6 * inch, 3.1 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#C9D4DE")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    # white text for header cells
    for i, h in enumerate(header):
        data[0][i] = Paragraph(
            f'<font color="#FFFFFF"><b>{h}</b></font>', S["meta"])
    return t


def build_pdf(meta, sections, revisions):
    S = styles()
    path = os.path.join(OUT_DIR, meta["file"])

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GREY)
        canvas.drawString(
            0.9 * inch, 0.5 * inch,
            f"{meta['docName']}  |  Version {meta['version']}  |  "
            f"Confidential — Internal Use Only")
        canvas.drawRightString(
            LETTER[0] - 0.9 * inch, 0.5 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc = BaseDocTemplate(
        path, pagesize=LETTER,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        topMargin=0.9 * inch, bottomMargin=0.8 * inch,
        title=meta["title"], author=meta["owner"],
        subject=meta["category"],
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="all", frames=frame, onPage=footer)])

    flow = []
    flow.append(Paragraph(meta["title"], S["title"]))
    flow.append(Paragraph(
        f"{meta['company']} &middot; Corporate Policy &middot; "
        f"{meta['category']}", S["subtitle"]))
    flow.append(meta_block(S, meta))
    flow.append(Spacer(1, 10))

    for heading, paras in sections:
        flow.append(Paragraph(heading, S["h2"]))
        for p in paras:
            if isinstance(p, tuple) and p[0] == "ul":
                for item in p[1]:
                    flow.append(Paragraph(item, S["bullet"], bulletText="•"))
            else:
                flow.append(Paragraph(p, S["body"]))

    flow.append(Paragraph("Revision History", S["h2"]))
    flow.append(revision_table(S, revisions))

    doc.build(flow)
    return path


COMPANY = "Northwind Global Technologies, Inc."

POLICIES = []

# 1. Information Security Policy — OVERDUE (reviewDate 2025-08-15)
POLICIES.append((
    {
        "file": "information_security_policy.pdf",
        "company": COMPANY,
        "title": "Information Security Policy",
        "docName": "POL-SEC-001 Information Security Policy",
        "category": "Security",
        "owner": "Chief Information Security Officer (CISO)",
        "version": "3.2",
        "effectiveDate": "2024-08-15",
        "reviewDate": "2025-08-15",
    },
    [
        ("1. Purpose", [
            "This policy establishes the principles and minimum requirements for "
            "protecting the confidentiality, integrity, and availability of "
            f"{COMPANY} information assets. It ensures that information is "
            "safeguarded against unauthorized access, disclosure, modification, "
            "or destruction, whether accidental or deliberate.",
        ]),
        ("2. Scope", [
            "This policy applies to all employees, contractors, consultants, and "
            "third parties who access company information systems, networks, or "
            "data, regardless of location or device. It covers all information "
            "assets owned, leased, or managed by the company, including cloud and "
            "on-premises environments.",
        ]),
        ("3. Policy Statements", [
            ("ul", [
                "Information must be classified as Public, Internal, Confidential, "
                "or Restricted, and handled according to its classification.",
                "All systems must enforce multi-factor authentication for remote "
                "and privileged access.",
                "Passwords must be at least 14 characters and managed through the "
                "approved enterprise password manager.",
                "Data at rest and in transit must be encrypted using AES-256 or a "
                "stronger approved algorithm.",
                "Access follows the principle of least privilege and is reviewed "
                "quarterly by system owners.",
                "Security patches rated Critical must be applied within 14 days of "
                "release.",
            ]),
        ]),
        ("4. Responsibilities", [
            "The CISO owns this policy and the overall security program. System "
            "owners are accountable for access reviews and patch compliance. All "
            "users are responsible for completing annual security awareness "
            "training and reporting suspected incidents promptly.",
        ]),
        ("5. Enforcement", [
            "Violations of this policy may result in disciplinary action up to and "
            "including termination of employment or contract, and may carry civil "
            "or criminal liability. Exceptions require documented risk acceptance "
            "approved by the CISO.",
        ]),
    ],
    [
        ["1.0", "2019-07-01", "J. Okafor", "Initial release."],
        ["2.0", "2021-09-01", "J. Okafor", "Added cloud and MFA requirements."],
        ["3.0", "2023-08-15", "L. Martinez", "Restructured to ISO 27001 controls."],
        ["3.2", "2024-08-15", "L. Martinez", "Updated patching SLAs and encryption standards."],
    ],
))

# 2. Remote Work Policy — OVERDUE (reviewDate 2026-03-01)
POLICIES.append((
    {
        "file": "remote_work_policy.pdf",
        "company": COMPANY,
        "title": "Remote Work Policy",
        "docName": "POL-HR-014 Remote Work Policy",
        "category": "HR",
        "owner": "VP, People Operations",
        "version": "2.1",
        "effectiveDate": "2025-03-01",
        "reviewDate": "2026-03-01",
    },
    [
        ("1. Purpose", [
            "This policy defines the expectations, eligibility, and obligations "
            "for employees who perform their duties remotely, on a hybrid "
            "schedule, or from a location other than a company office. It aims to "
            "support flexibility while maintaining productivity, security, and "
            "team cohesion.",
        ]),
        ("2. Scope", [
            "This policy applies to all regular full-time and part-time employees "
            "whose roles are designated as remote-eligible or hybrid. It does not "
            "apply to roles requiring on-site presence, such as facilities, lab, "
            "or front-desk functions.",
        ]),
        ("3. Policy Statements", [
            "Remote work arrangements must be approved by the employee's manager "
            "and documented in the HR system.",
            ("ul", [
                "Employees must be reachable and available during their agreed "
                "core working hours in the company's primary time zone.",
                "A safe, ergonomic, and private workspace appropriate for handling "
                "company information must be maintained.",
                "Company-issued devices must be used for all work involving "
                "Confidential or Restricted data.",
                "Hybrid employees are expected on-site a minimum of two days per "
                "week unless otherwise agreed.",
                "Employees must not perform work from a country not approved by "
                "Legal and People Operations.",
            ]),
        ]),
        ("4. Responsibilities", [
            "Managers approve and periodically review remote arrangements and "
            "ensure equitable treatment of remote staff. People Operations "
            "maintains this policy and resolves disputes. Employees are "
            "responsible for safeguarding equipment and reporting any change in "
            "work location.",
        ]),
        ("5. Enforcement", [
            "Failure to comply may result in revocation of remote-work privileges "
            "and, in serious cases, disciplinary action. Reimbursement of home-"
            "office expenses is governed by the Expense & Travel Policy.",
        ]),
    ],
    [
        ["1.0", "2020-04-15", "S. Kim", "Emergency remote-work guidance."],
        ["2.0", "2023-02-20", "S. Kim", "Formalized hybrid model and core hours."],
        ["2.1", "2025-03-01", "D. Fernandes", "Clarified cross-border work approvals."],
    ],
))

# 3. Data Retention & Privacy Policy — DUE SOON (reviewDate 2026-07-30)
POLICIES.append((
    {
        "file": "data_retention_privacy_policy.pdf",
        "company": COMPANY,
        "title": "Data Retention & Privacy Policy",
        "docName": "POL-DG-007 Data Retention & Privacy Policy",
        "category": "Data Governance",
        "owner": "Data Protection Officer (DPO)",
        "version": "4.0",
        "effectiveDate": "2025-07-30",
        "reviewDate": "2026-07-30",
    },
    [
        ("1. Purpose", [
            "This policy governs how personal and business data is collected, "
            "stored, retained, and disposed of, ensuring compliance with "
            "applicable data protection laws including GDPR and CCPA, and "
            "minimizing risk from over-retention of data.",
        ]),
        ("2. Scope", [
            "This policy applies to all structured and unstructured data held by "
            f"{COMPANY}, including customer records, employee records, and "
            "operational data, across all storage systems and jurisdictions.",
        ]),
        ("3. Policy Statements", [
            ("ul", [
                "Personal data must be processed lawfully, fairly, and only for "
                "the purposes for which it was collected.",
                "Data must be retained only as long as necessary; default "
                "retention is 7 years for financial records and 24 months for "
                "marketing data.",
                "Data subject requests for access, correction, or erasure must be "
                "fulfilled within 30 days.",
                "Records scheduled for disposal must be securely and "
                "irreversibly destroyed.",
                "Cross-border transfers require an approved transfer mechanism such "
                "as Standard Contractual Clauses.",
            ]),
            "A data retention schedule is maintained as Appendix A and reviewed "
            "annually by the DPO and Legal.",
        ]),
        ("4. Responsibilities", [
            "The DPO owns this policy and oversees compliance. Data owners "
            "classify data and apply retention rules. IT operations implement "
            "automated retention and deletion controls. All staff must report "
            "personal-data breaches within 24 hours of discovery.",
        ]),
        ("5. Enforcement", [
            "Non-compliance may expose the company to regulatory fines and "
            "reputational harm and may result in disciplinary action. Exceptions "
            "to retention periods require legal-hold authorization.",
        ]),
    ],
    [
        ["1.0", "2018-05-25", "R. Ahmed", "Initial GDPR-aligned release."],
        ["2.0", "2020-01-01", "R. Ahmed", "Added CCPA provisions."],
        ["3.0", "2023-07-30", "M. Cho", "Introduced automated deletion controls."],
        ["4.0", "2025-07-30", "M. Cho", "Updated retention schedule and breach SLAs."],
    ],
))

# 4. Code of Conduct — CURRENT (reviewDate 2027-01-15)
POLICIES.append((
    {
        "file": "code_of_conduct.pdf",
        "company": COMPANY,
        "title": "Code of Conduct",
        "docName": "POL-COMP-002 Code of Conduct",
        "category": "Compliance",
        "owner": "Chief Compliance Officer",
        "version": "5.0",
        "effectiveDate": "2026-01-15",
        "reviewDate": "2027-01-15",
    },
    [
        ("1. Purpose", [
            "The Code of Conduct sets out the ethical standards and behaviors "
            f"expected of everyone who works for or on behalf of {COMPANY}. It "
            "reflects our commitment to integrity, fairness, and lawful conduct in "
            "all business dealings.",
        ]),
        ("2. Scope", [
            "This Code applies to all directors, officers, employees, and "
            "contractors worldwide. Business partners and suppliers are expected "
            "to uphold equivalent standards.",
        ]),
        ("3. Policy Statements", [
            ("ul", [
                "We treat colleagues, customers, and partners with respect and do "
                "not tolerate harassment or discrimination of any kind.",
                "We avoid conflicts of interest and disclose any actual or "
                "potential conflict to our manager and Compliance.",
                "We never offer, give, solicit, or accept bribes or improper "
                "payments, including facilitation payments.",
                "We protect company assets, confidential information, and "
                "intellectual property.",
                "We compete fairly and comply with all applicable competition and "
                "anti-trust laws.",
                "We keep accurate books and records and never falsify any document "
                "or report.",
            ]),
        ]),
        ("4. Responsibilities", [
            "The Chief Compliance Officer maintains the Code and the ethics "
            "hotline. Managers model ethical behavior and support those who raise "
            "concerns. Every individual is responsible for reading, understanding, "
            "and acting in accordance with the Code.",
        ]),
        ("5. Enforcement", [
            "Reports may be made anonymously through the confidential ethics "
            "hotline, and retaliation against good-faith reporters is strictly "
            "prohibited. Breaches of the Code may lead to disciplinary action up "
            "to and including termination, and referral to authorities where "
            "warranted.",
        ]),
    ],
    [
        ["1.0", "2015-03-01", "Board of Directors", "Initial adoption."],
        ["3.0", "2020-06-01", "P. Nguyen", "Added anti-bribery and hotline."],
        ["4.0", "2024-01-15", "P. Nguyen", "Refreshed conflict-of-interest rules."],
        ["5.0", "2026-01-15", "A. Walsh", "Expanded anti-retaliation protections."],
    ],
))

# 5. Expense & Travel Policy — CURRENT (reviewDate 2027-05-01)
POLICIES.append((
    {
        "file": "expense_and_travel_policy.pdf",
        "company": COMPANY,
        "title": "Expense & Travel Policy",
        "docName": "POL-FIN-021 Expense & Travel Policy",
        "category": "Finance",
        "owner": "VP, Corporate Finance",
        "version": "2.3",
        "effectiveDate": "2026-05-01",
        "reviewDate": "2027-05-01",
    },
    [
        ("1. Purpose", [
            "This policy defines the rules for incurring, approving, and "
            "reimbursing business travel and expenses. It ensures spending is "
            "reasonable, necessary, properly documented, and compliant with tax "
            "requirements.",
        ]),
        ("2. Scope", [
            "This policy applies to all employees and contractors who incur "
            "business expenses or travel on company business, and to anyone who "
            "approves such expenses.",
        ]),
        ("3. Policy Statements", [
            ("ul", [
                "All expenses must have a valid business purpose and an itemized "
                "receipt for any amount of USD 25 or more.",
                "Air travel should be booked at least 14 days in advance in "
                "economy class for flights under 6 hours.",
                "Hotel stays must not exceed the per-diem cap for the destination "
                "city as published in Appendix B.",
                "Meals are reimbursed up to the daily per-diem; alcohol is not "
                "reimbursable.",
                "Expense reports must be submitted within 30 days of the expense "
                "being incurred.",
                "Personal travel combined with business travel must be clearly "
                "separated and is not reimbursable.",
            ]),
        ]),
        ("4. Responsibilities", [
            "Corporate Finance owns this policy and the expense system. Managers "
            "review and approve reports for their teams and are accountable for "
            "budget adherence. Employees must submit accurate, timely, and "
            "complete expense claims.",
        ]),
        ("5. Enforcement", [
            "Late or non-compliant claims may be rejected or delayed. Falsifying "
            "an expense claim is considered fraud and will result in disciplinary "
            "action up to and including termination. Approvers who knowingly "
            "approve improper claims are equally accountable.",
        ]),
    ],
    [
        ["1.0", "2017-02-01", "H. Schmidt", "Initial release."],
        ["2.0", "2022-05-01", "H. Schmidt", "Introduced per-diem structure."],
        ["2.3", "2026-05-01", "T. Owens", "Updated per-diem caps and submission window."],
    ],
))

# 6. Incident Response Policy — OVERDUE (reviewDate 2026-04-10)
POLICIES.append((
    {
        "file": "incident_response_policy.pdf",
        "company": COMPANY,
        "title": "Incident Response Policy",
        "docName": "POL-SEC-009 Incident Response Policy",
        "category": "Security",
        "owner": "Director, Security Operations",
        "version": "1.4",
        "effectiveDate": "2025-04-10",
        "reviewDate": "2026-04-10",
    },
    [
        ("1. Purpose", [
            "This policy establishes a consistent and effective approach to "
            "detecting, responding to, and recovering from information security "
            "incidents in order to limit damage, reduce recovery time and cost, "
            "and meet legal and contractual obligations.",
        ]),
        ("2. Scope", [
            "This policy applies to all security incidents affecting company "
            f"systems, data, or services across {COMPANY}, and to all personnel "
            "involved in detecting, reporting, or responding to such incidents.",
        ]),
        ("3. Policy Statements", [
            "Incidents are classified by severity (SEV-1 through SEV-4) based on "
            "business impact and data sensitivity.",
            ("ul", [
                "Suspected incidents must be reported to the Security Operations "
                "Center (SOC) immediately and no later than 1 hour after "
                "discovery.",
                "The incident response lifecycle follows: Preparation, "
                "Identification, Containment, Eradication, Recovery, and Lessons "
                "Learned.",
                "SEV-1 incidents require activation of the incident bridge and "
                "executive notification within 30 minutes.",
                "Evidence must be preserved using approved forensic procedures to "
                "maintain chain of custody.",
                "Regulatory and customer breach notifications must be coordinated "
                "with Legal and the DPO.",
            ]),
        ]),
        ("4. Responsibilities", [
            "The Director of Security Operations owns this policy and the response "
            "playbooks. The on-call Incident Commander leads response activities. "
            "All staff are responsible for prompt reporting and for cooperating "
            "fully with investigations.",
        ]),
        ("5. Enforcement", [
            "A post-incident review is mandatory for all SEV-1 and SEV-2 incidents "
            "and corrective actions are tracked to closure. Failure to report or "
            "respond appropriately may result in disciplinary action.",
        ]),
    ],
    [
        ["1.0", "2021-11-01", "C. Rivera", "Initial release."],
        ["1.2", "2023-10-01", "C. Rivera", "Added severity matrix and SOC SLAs."],
        ["1.4", "2025-04-10", "C. Rivera", "Aligned playbooks to NIST 800-61r2."],
    ],
))


def main():
    created = []
    for meta, sections, revisions in POLICIES:
        path = build_pdf(meta, sections, revisions)
        created.append((path, meta))
        print(f"Created: {path}")
    print(f"\nTotal: {len(created)} PDFs in {OUT_DIR}")


if __name__ == "__main__":
    main()
