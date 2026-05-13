"""Generate synthetic EduPath Academy policy documents.

This script creates markdown policy documents in a specified output directory.
Used by the 01_quickstart_setup notebook to produce content for the Vector Search index.
"""

import os


EDU_POLICY_DOCS = {
    "academic_integrity.md": """# Academic Integrity Policy

EduPath Academy is committed to fostering an environment of honesty, trust, and intellectual rigor. All students, faculty, and staff share responsibility for upholding the highest standards of academic conduct.

## Definition of Academic Integrity

Academic integrity means presenting your own work honestly and giving proper credit to the ideas and contributions of others. It is the foundation of meaningful learning and the value of your degree.

## Prohibited Conduct

### Plagiarism
Submitting work that is not your own, including:
- Copying text from sources without proper citation
- Paraphrasing ideas without attribution
- Submitting AI-generated content as your own without disclosure
- Reusing your own prior submissions without instructor approval (self-plagiarism)

### Cheating
- Using unauthorized materials, devices, or notes during examinations
- Sharing exam content with students who have not yet taken the assessment
- Obtaining advance copies of exams or assignments

### Unauthorized Collaboration
- Working with others on assignments designated as individual work
- Sharing code, solutions, or lab reports beyond what the instructor permits
- Using external tutoring services that complete work on a student's behalf

## Consequences

Violations are adjudicated by the Academic Integrity Board. Sanctions include:
- First offense: Zero on the assignment and a formal warning
- Second offense: Failure in the course
- Third offense: Suspension or expulsion from EduPath Academy

## Reporting

Faculty who suspect violations should submit a report through the Academic Integrity Portal within 5 business days of discovery. Students may also report suspected violations anonymously.

## Appeals

Students may appeal decisions within 14 calendar days by submitting a written statement to the Provost's Office.
""",
    "attendance_policy.md": """# Attendance Policy

Regular attendance and active participation are essential to academic success at EduPath Academy. This policy applies to all credit-bearing courses across all campuses and modalities.

## Expectations

Students are expected to attend all scheduled class sessions, arrive on time, and remain for the full duration. For online synchronous courses, students must have cameras enabled unless accommodations have been approved.

## Absence Categories

### Excused Absences
The following are considered excused with proper documentation:
- Illness or medical appointments (doctor's note required for 3+ consecutive days)
- Family emergencies (bereavement, hospitalization of immediate family)
- University-approved activities (athletics, conferences, field trips)
- Religious observances (notify instructor within first week of term)
- Jury duty or court appearances

### Unexcused Absences
All absences not meeting the above criteria are unexcused. This includes:
- Vacation or personal travel during the academic term
- Work schedule conflicts (unless part of an approved co-op program)
- Transportation issues or oversleeping

## Attendance Thresholds

- Missing more than 15% of class sessions results in a half-letter grade reduction
- Missing more than 25% of class sessions may result in automatic course failure
- Instructors may set stricter requirements with advance notice in the syllabus

## Notification Requirements

Students must notify instructors of anticipated absences at least 24 hours in advance when possible. For unexpected absences, notification should occur within 24 hours of the missed class.

## Make-Up Work

Students with excused absences may request make-up assignments within 3 business days of returning. Instructors are not obligated to provide make-up opportunities for unexcused absences.
""",
    "grading_policy.md": """# Grading Policy

EduPath Academy uses a transparent, standards-based grading system to evaluate student performance and provide meaningful feedback on learning outcomes.

## Grading Scale

| Letter Grade | Percentage | GPA Points |
|---|---|---|
| A  | 93-100% | 4.0 |
| A- | 90-92%  | 3.7 |
| B+ | 87-89%  | 3.3 |
| B  | 83-86%  | 3.0 |
| B- | 80-82%  | 2.7 |
| C+ | 77-79%  | 2.3 |
| C  | 73-76%  | 2.0 |
| C- | 70-72%  | 1.7 |
| D  | 60-69%  | 1.0 |
| F  | Below 60% | 0.0 |

## Standard Grade Components

Unless otherwise specified in the course syllabus:
- Assignments and Projects: 40%
- Examinations (midterm and final): 35%
- Class Participation and Attendance: 15%
- Quizzes and In-Class Activities: 10%

Instructors may adjust these weights with approval from the department chair.

## Grade Posting

Instructors must post grades for assignments within 10 business days of the submission deadline. Final grades are due within 72 hours of the final exam period.

## Incomplete Grades

An Incomplete (I) may be granted when a student has completed at least 70% of coursework satisfactorily but cannot finish due to documented extenuating circumstances. Incomplete work must be submitted within 60 days of the term end.

## Grade Appeals

Students may appeal final grades within 14 calendar days of grade posting. The appeal process is:
1. Discuss with the instructor directly
2. If unresolved, submit written appeal to the department chair
3. Final appeal to the Academic Standards Committee

## Academic Standing

- Good Standing: Cumulative GPA of 2.0 or above
- Academic Probation: GPA below 2.0 for one term
- Academic Suspension: GPA below 2.0 for two consecutive terms
""",
    "course_enrollment.md": """# Course Enrollment Policy

This policy governs the registration, addition, and withdrawal from courses at EduPath Academy.

## Registration Periods

- Priority Registration: 4 weeks before term start (seniors and students with accommodations)
- General Registration: 3 weeks before term start (all degree-seeking students)
- Open Registration: 2 weeks before term start (non-degree and visiting students)
- Late Registration: First week of classes (requires instructor and advisor approval)

## Course Load

- Full-time undergraduate: 12-18 credit hours per term
- Part-time undergraduate: 1-11 credit hours per term
- Overload (19+ credits): Requires GPA of 3.5+ and dean's approval
- Graduate students: 9-12 credit hours per term

## Prerequisites and Corequisites

Students must satisfy all listed prerequisites before enrolling. The system enforces prerequisite checks automatically. Override requests must be submitted to the department offering the course.

## Add/Drop Period

- Add courses: Within the first 2 weeks of the term (no notation on transcript)
- Drop courses: Before the midterm date (W notation on transcript)
- After midterm: Withdrawal only with documented extenuating circumstances

## Waitlists

When a course reaches capacity, students may join the waitlist. Waitlisted students are enrolled automatically as seats become available, in waitlist order. Students are notified via email and have 24 hours to confirm.

## Course Cancellations

EduPath Academy reserves the right to cancel courses with fewer than 8 enrolled students. Affected students receive priority registration for alternative sections.

## Repeating Courses

Students may repeat a course once to improve their grade. Both attempts appear on the transcript, but only the higher grade counts toward GPA. Financial aid may not cover repeated courses.
""",
    "student_conduct.md": """# Student Conduct Policy

EduPath Academy expects all community members to conduct themselves with respect, responsibility, and regard for the rights of others. This policy applies on all campuses, at university-sponsored events, and in online learning environments.

## Community Standards

All students are expected to:
- Treat others with dignity and respect regardless of background or identity
- Maintain a safe and productive learning environment
- Comply with all university policies and applicable laws
- Report safety concerns promptly

## Prohibited Behaviors

### Harassment and Discrimination
- Verbal, physical, or electronic harassment based on protected characteristics
- Creating a hostile environment through persistent unwelcome conduct
- Retaliating against individuals who report misconduct

### Disruptive Conduct
- Interfering with instruction or university operations
- Unauthorized use of recording devices in classrooms
- Being under the influence of drugs or alcohol during academic activities

### Property and Safety Violations
- Damaging or stealing university or personal property
- Unauthorized access to buildings, systems, or restricted areas
- Possessing weapons on campus (exceptions for authorized security personnel)
- Violating fire safety regulations including tampering with equipment

### Technology Misuse
- Unauthorized access to university systems or data
- Using university networks for illegal activities
- Cyberbullying or online harassment of community members

## Reporting Incidents

Incidents should be reported to the Dean of Students Office within 30 days. Reports can be filed:
- Online through the Student Conduct Portal
- In person at the Dean of Students Office (Building 3, Room 201)
- By phone at the campus safety hotline (available 24/7)

## Adjudication Process

1. Initial review by the Dean of Students (within 5 business days)
2. Investigation and evidence gathering (within 15 business days)
3. Hearing before the Student Conduct Board (if charges are sustained)
4. Decision and sanctions communicated in writing

## Sanctions

Sanctions range from written warnings to expulsion, depending on severity and prior history.
""",
    "tuition_refund.md": """# Tuition Refund Policy

This policy outlines the refund schedule for students who withdraw from courses or from EduPath Academy entirely.

## Refund Schedule for Course Withdrawal

| Withdrawal Timing | Tuition Refund | Fees Refund |
|---|---|---|
| Before classes begin | 100% | 100% |
| Week 1 of classes | 100% | 50% |
| Week 2 of classes | 75% | 25% |
| Week 3 of classes | 50% | 0% |
| Week 4 of classes | 25% | 0% |
| After Week 4 | 0% | 0% |

## Complete Withdrawal

Students withdrawing from all courses follow the same schedule above, calculated from the official last date of attendance.

## How to Request a Refund

1. Submit the official Course Withdrawal Form through the Registrar's Office or Student Portal
2. Refund calculations are based on the date the form is received, not the last date of attendance
3. Refunds are processed within 14 business days of approval
4. Refunds are returned to the original payment method when possible

## Financial Aid Adjustments

Students receiving financial aid should consult the Financial Aid Office before withdrawing. Federal regulations (Return of Title IV Funds) may require the return of a portion of financial aid, which could result in a balance owed to the university.

## Exceptions

Refund exceptions may be granted for:
- Documented medical emergencies requiring extended absence
- Military deployment orders
- Death of an immediate family member
- University-initiated course cancellations (100% refund regardless of timing)

Exception requests must be submitted in writing to the Bursar's Office with supporting documentation within 30 days of the withdrawal date.

## Tuition Insurance

EduPath Academy offers optional tuition insurance through our partner provider. Students who purchase this coverage may be eligible for refunds beyond the standard schedule. Enrollment in tuition insurance must occur before the term start date.
""",
    "privacy_policy.md": """# Student Privacy Policy

EduPath Academy is committed to protecting the privacy of student educational records in compliance with the Family Educational Rights and Privacy Act (FERPA) and applicable state privacy laws.

## Scope

This policy applies to all student educational records maintained by EduPath Academy, including:
- Academic records (transcripts, grades, enrollment history)
- Financial records (tuition payments, financial aid)
- Disciplinary records
- Health and counseling records (additional protections apply)
- Digital learning activity data

## Student Rights Under FERPA

Students have the right to:
- Inspect and review their educational records within 45 days of request
- Request amendment of records believed to be inaccurate or misleading
- Consent to disclosure of personally identifiable information (with exceptions)
- File a complaint with the U.S. Department of Education

## Directory Information

The following is designated as directory information and may be disclosed without consent:
- Name, email address, and phone number
- Major field of study and enrollment status
- Dates of attendance and degrees awarded
- Participation in officially recognized activities

Students may opt out of directory information disclosure by submitting a request to the Registrar's Office within the first two weeks of each term.

## Data Security

EduPath Academy maintains administrative, technical, and physical safeguards to protect student records, including:
- Encryption of data in transit and at rest
- Role-based access controls for all information systems
- Regular security assessments and penetration testing
- Mandatory privacy training for all employees handling student data

## Third-Party Disclosures

Student records may be disclosed without consent to:
- University officials with legitimate educational interest
- Other institutions where the student seeks enrollment
- Authorized federal and state agencies for audit or compliance purposes
- Parties in connection with financial aid
- Organizations conducting studies on behalf of the university

## Data Retention

Academic transcripts are retained permanently. Other records are retained according to the university's Records Retention Schedule, typically 5-7 years after the student's last enrollment.

## Requests and Questions

Privacy-related requests should be directed to the Registrar's Office or the University Privacy Officer at privacy@edupath.edu.
""",
}


def generate_docs(output_dir: str) -> str:
    """Write all policy documents to output_dir and return the path."""
    os.makedirs(output_dir, exist_ok=True)
    for filename, content in EDU_POLICY_DOCS.items():
        with open(os.path.join(output_dir, filename), "w") as f:
            f.write(content.strip())
    return output_dir


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "data", "edu_policy_docs")
    generate_docs(target)
    print(f"Created {len(EDU_POLICY_DOCS)} policy documents in: {target}")
