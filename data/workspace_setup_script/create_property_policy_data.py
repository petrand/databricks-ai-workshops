# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "1"
# ///
# MAGIC %md
# MAGIC # Retail Property Management — Company Policies (Synthetic Data)
# MAGIC
# MAGIC This notebook generates **100 synthetic company policies** for a retail property
# MAGIC management company (example company: **Vicinity Centres**) and writes them to a Unity
# MAGIC Catalog table — **one row per policy**, each policy formatted as Markdown and well under
# MAGIC two pages.
# MAGIC
# MAGIC **Output table:** `${catalog}.${schema}.${table}` (defaults: `dev` / `policies` / `policy_docs`)
# MAGIC
# MAGIC The data is fictional and intended for demos, Genie/RAG, and testing. Set the widgets at
# MAGIC the top, then **Run All**.

# COMMAND ----------

# MAGIC %md ## 1. Configuration

# COMMAND ----------

dbutils.widgets.text("catalog", "dev", "Target catalog")
dbutils.widgets.text("schema", "policies", "Target schema")
dbutils.widgets.text("table", "policy_docs", "Target table")
dbutils.widgets.dropdown("write_mode", "overwrite", ["overwrite", "append"], "Write mode")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
TABLE = dbutils.widgets.get("table")
WRITE_MODE = dbutils.widgets.get("write_mode")
FQN = f"{CATALOG}.{SCHEMA}.{TABLE}"
print(f"Target table: {FQN}  (mode={WRITE_MODE})")

# COMMAND ----------

# MAGIC %md ## 2. Company metadata & document renderer

# COMMAND ----------

COMPANY = "Vicinity Centres"
SHORT = "Vicinity"
DOMAIN = "vicinity.example.com"

def doc(p):
    """Render the full Markdown content for a policy from its fields."""
    header = (
        f"# {p['title']}\n\n"
        f"**Company:** {COMPANY} ({SHORT})  \n"
        f"**Policy ID:** {p['id']}  \n"
        f"**Category:** {p['category']}  \n"
        f"**Owner:** {p['owner']}  \n"
        f"**Version:** {p['ver']}  \n"
        f"**Effective date:** {p['eff']}  \n"
        f"**Next review:** {p['rev']}\n\n"
    )
    return header + p["body"].strip() + "\n"

# COMMAND ----------

# MAGIC %md ## 3. Policy definitions (100 policies)

# COMMAND ----------

# COMMAND ----------

POLICIES = [
{
 "id":"POL-001","doc_name":"tenant_onboarding_policy","category":"Tenant & Leasing",
 "title":"Tenant Onboarding & Handover Policy","eff":"2024-07-01","rev":"2026-07-01",
 "owner":"Leasing & Tenancy Coordination","ver":"3.2",
 "body":"""
## Purpose
This policy establishes a consistent process for onboarding new retail tenants into Vicinity-managed
centres, ensuring tenants are trading-ready, compliant, and supported from lease execution through to
their first day of trade.

## Scope
Applies to all new tenancies, relocations, and assignments across all Vicinity-managed shopping centres,
and to all Centre Management, Leasing, and Operations staff involved in handover.

## Policy Statements
1. A signed lease or agreement to lease must be in place before any handover of premises.
2. The incoming tenant must provide, prior to fit-out access:
   - Certificate of currency for public liability insurance (minimum $20M).
   - Workers' compensation insurance evidence.
   - Approved fit-out drawings (see Tenant Fit-Out & Construction Policy).
   - Trading name, ABN, and emergency contact details.
3. Centre Management must complete a documented premises condition report (with photos) at handover.
4. A welcome pack covering centre rules, trading hours, loading dock procedures, waste management,
   and key contacts must be issued at handover.
5. Tenant inductions covering WHS, emergency procedures, and centre access must be completed before
   the tenant or its contractors commence work on site.

## Onboarding Checklist
| Step | Responsible | Timing |
|------|-------------|--------|
| Lease executed | Leasing | Pre-handover |
| Insurance verified | Tenancy Coordination | Pre-access |
| Condition report | Centre Management | At handover |
| WHS & emergency induction | Operations | Before fit-out |
| Services connected (power, comms) | Tenant | Before trade |
| Trading-ready inspection | Centre Manager | Before opening |

## Roles & Responsibilities
- **Leasing** secures executed documentation and commercial terms.
- **Tenancy Coordination** verifies compliance documents and schedules handover.
- **Centre Management** conducts inspections and issues the welcome pack.

## Non-Compliance
Premises will not be released and trade will not be authorised until all mandatory items are complete.
Questions: tenancy@vicinity.example.com.
"""
},
{
 "id":"POL-002","doc_name":"lease_administration_policy","category":"Tenant & Leasing",
 "title":"Lease Administration Policy","eff":"2024-05-15","rev":"2026-05-15",
 "owner":"Leasing & Tenancy Coordination","ver":"2.4",
 "body":"""
## Purpose
To ensure accurate, timely administration of all lease documentation, critical dates, and obligations
across the Vicinity portfolio, protecting the interests of landlords and maintaining compliance with retail
leasing legislation.

## Scope
All retail, casual mall leasing (CML), storage, and ancillary agreements managed by Vicinity.

## Policy Statements
1. Every executed lease must be registered in the property management system within five business days
   of execution, with all critical dates captured (commencement, expiry, option, rent review, bank
   guarantee expiry).
2. Disclosure statements must be issued to tenants within the statutory timeframe applicable in the
   relevant jurisdiction before lease entry.
3. Bank guarantees and security deposits must be recorded, held securely, and reviewed at each rent
   review to maintain the required number of months' cover.
4. Critical date reports must be produced monthly and circulated to Centre Managers and Leasing.
5. Lease variations, assignments, and surrenders must follow the delegated authority matrix and be
   documented in writing.

## Critical Date Management
The system must trigger alerts at 180, 90, and 30 days before each critical date. Option exercise
windows must be actioned by Leasing to avoid unintended holdovers or lapses.

## Records
All lease documents are retained for a minimum of seven years after expiry. Electronic copies are the
system of record; originals are stored in fire-rated storage.

## Roles & Responsibilities
- **Tenancy Coordination** maintains the lease register and critical date integrity.
- **Leasing** manages negotiations, options, and variations.
- **Finance** reconciles security holdings.

Contact: leaseadmin@vicinity.example.com.
"""
},
{
 "id":"POL-003","doc_name":"rent_review_policy","category":"Tenant & Leasing",
 "title":"Rent Review & Outgoings Policy","eff":"2024-09-01","rev":"2026-09-01",
 "owner":"Leasing & Finance","ver":"1.9",
 "body":"""
## Purpose
To govern the consistent and lawful conduct of rent reviews and the recovery of outgoings across
Vicinity-managed centres.

## Scope
All leases containing rent review and/or outgoings recovery provisions.

## Rent Review Principles
1. Reviews are conducted strictly in accordance with the mechanism in each lease (fixed, CPI, market,
   or ratchet where permitted by jurisdiction).
2. Market reviews must be supported by current comparable evidence and, where required, an independent
   valuation by an accredited specialist retail valuer.
3. Review notices must be issued within the timeframe and form prescribed by the lease and applicable
   retail leasing legislation.
4. Tenants must be given the disclosure and dispute rights required by law.

## Outgoings Recovery
- Annual outgoings estimates must be provided to tenants before the start of each accounting period.
- Audited or certified outgoings statements must be issued within the statutory period after year-end.
- Management fees and capital expenditure must only be recovered where expressly permitted by the lease.
- Outgoings must be apportioned on a fair and consistent basis (typically GLA-weighted).

## Disputes
Disputes are managed under the Tenant Dispute Resolution Policy and relevant small business commissioner
processes. Recovery of disputed amounts is suspended pending resolution where legally required.

## Roles & Responsibilities
- **Leasing** issues review notices and negotiates market reviews.
- **Finance** prepares outgoings budgets, reconciliations, and statements.
- **Centre Management** supports with operational expenditure context.

Contact: finance-outgoings@vicinity.example.com.
"""
},
{
 "id":"POL-004","doc_name":"casual_mall_leasing_policy","category":"Tenant & Leasing",
 "title":"Casual Mall Leasing (CML) Policy","eff":"2024-08-01","rev":"2026-08-01",
 "owner":"Centre Marketing & Leasing","ver":"2.1",
 "body":"""
## Purpose
To manage short-term and casual leasing of common area space (kiosks, pop-ups, promotional sites,
display vehicles, and ATMs) in a way that maximises income while protecting permanent tenants,
shopper amenity, and safety.

## Scope
All casual and short-term licences in common areas of Vicinity-managed centres.

## Policy Statements
1. CML operators must hold current public liability insurance ($20M minimum) before occupying any site.
2. Sites must not obstruct fire egress, sight lines to permanent tenants, or accessible paths of travel.
3. Product and service categories that directly compete with an adjacent specialty tenant should be
   avoided where a lease grants exclusivity or where it would unreasonably impact trade.
4. All licences are documented, with defined trading hours, site dimensions, and conduct rules.
5. Electrical leads and structures must be tagged, tested, and approved by Operations.

## Prohibited Without Approval
- Cooking or open flame, helium/gas cylinders, animals, and amplified sound.
- Distribution of food samples without food safety compliance.
- Charity and political solicitation outside designated guidelines.

## Revenue & Reporting
CML income targets are set annually. Bookings, occupancy, and income are reported monthly to the asset
owner. Discounting beyond delegated authority requires approval.

## Roles & Responsibilities
- **Centre Marketing** sources and books operators.
- **Operations** approves structures, power, and safety compliance.
- **Centre Manager** has final authority over site suitability.

Contact: cml@vicinity.example.com.
"""
},
{
 "id":"POL-005","doc_name":"tenant_dispute_resolution_policy","category":"Tenant & Leasing",
 "title":"Tenant Dispute Resolution Policy","eff":"2024-06-01","rev":"2026-06-01",
 "owner":"Risk & Compliance","ver":"1.5",
 "body":"""
## Purpose
To provide a fair, consistent, and legally compliant approach to resolving disputes with retail tenants,
minimising escalation, cost, and reputational risk.

## Scope
All disputes between Vicinity (as manager/landlord agent) and tenants, including disputes over rent,
outgoings, repairs, trading hours, and lease interpretation.

## Principles
1. Disputes are handled promptly, respectfully, and in good faith.
2. All communications are documented and factual.
3. Staff must not threaten lockouts, distraint, or termination except strictly in accordance with the
   lease and law, and only with senior and legal approval.

## Process
1. **Acknowledge** the dispute in writing within three business days.
2. **Investigate** by gathering relevant lease clauses, ledgers, and correspondence.
3. **Discuss** directly with the tenant to seek a commercial resolution.
4. **Escalate** unresolved matters to the Centre Manager and, if needed, to Legal.
5. **Refer** to mediation or the relevant retail tenancy/small business commissioner where required
   before any formal proceedings.

## Records & Reporting
All disputes are logged in the disputes register with status and value at risk. Matters exceeding
defined thresholds are reported to the asset owner and Risk Committee monthly.

## Roles & Responsibilities
- **Centre Management** is the first point of contact and seeks early resolution.
- **Risk & Compliance** maintains the register and ensures legal process is followed.
- **Legal** advises on rights and represents Vicinity in formal proceedings.

Contact: disputes@vicinity.example.com.
"""
},
{
 "id":"POL-006","doc_name":"trading_hours_policy","category":"Tenant & Leasing",
 "title":"Centre Trading Hours Policy","eff":"2024-04-01","rev":"2026-04-01",
 "owner":"Centre Management","ver":"2.0",
 "body":"""
## Purpose
To set core trading hours for Vicinity-managed centres and govern tenant obligations to trade, ensuring a
consistent, attractive offer for shoppers.

## Scope
All tenants with a lease obligation to trade and all Centre Management staff.

## Core Trading Hours
Centres publish core trading hours by location. Tenants must open for the full core hours unless an
approved exemption applies. Extended hours apply during peak periods (e.g., Christmas) and are notified
in advance.

## Tenant Obligations
1. Trade during all core hours with the premises staffed, lit, and stocked.
2. Obtain written approval before closing early, opening late, or ceasing trade temporarily.
3. Display approved signage for any approved variation to hours.

## Public Holidays
Trading on public holidays is determined by local legislation and centre direction. Tenants are notified
of public holiday trading at least 14 days in advance where practicable.

## Exemptions
Exemptions may be granted for refurbishment, stocktake, or genuine hardship, subject to Centre Manager
approval and not unreasonably impacting the centre. Persistent failure to trade is a lease breach and is
managed under the Tenant Dispute Resolution Policy.

## Roles & Responsibilities
- **Centre Management** sets and communicates hours and approves exemptions.
- **Marketing** aligns campaigns and signage with trading hours.

Contact: centreops@vicinity.example.com.
"""
},
{
 "id":"POL-007","doc_name":"tenant_signage_policy","category":"Tenant & Leasing",
 "title":"Tenant Signage & Shopfront Presentation Policy","eff":"2024-03-15","rev":"2026-03-15",
 "owner":"Operations & Design","ver":"1.7",
 "body":"""
## Purpose
To maintain a high-quality, consistent, and safe presentation of tenant shopfronts and signage across
Vicinity centres.

## Scope
All tenant signage, shopfront displays, window graphics, and digital screens within leased premises and
visible to common areas.

## Standards
1. All new or altered signage requires written approval and must comply with the centre's design
   guidelines and any landlord design criteria in the lease.
2. Signage must be professionally manufactured, well maintained, and illuminated where specified.
3. Hand-written signs, peeling decals, and temporary printed signs taped to glass are not permitted in
   shopper-facing areas.
4. Sale and promotional signage must be neat and limited to the proportion of window area set in the
   design guidelines.
5. Digital screens must not display content that is offensive, flashing at unsafe rates, or excessively
   loud.

## Safety
Signage must be securely fixed, electrically tested and tagged, and must not obstruct egress or
emergency signage. Projecting and suspended signs require engineering certification.

## Enforcement
Centre Management may issue a rectification notice for non-compliant signage. Unsafe signage may be made
safe or removed at the tenant's cost where the tenant fails to act.

## Roles & Responsibilities
- **Operations & Design** reviews and approves signage applications.
- **Centre Management** monitors presentation and issues notices.

Contact: design@vicinity.example.com.
"""
},
{
 "id":"POL-008","doc_name":"retail_mix_policy","category":"Tenant & Leasing",
 "title":"Retail Mix & Exclusivity Management Policy","eff":"2024-10-01","rev":"2026-10-01",
 "owner":"Leasing Strategy","ver":"1.3",
 "body":"""
## Purpose
To guide leasing decisions so that each centre maintains an optimal, balanced retail mix that meets
shopper needs and maximises sustainable income, while properly managing exclusivity and permitted-use
commitments.

## Scope
All leasing, renewal, and remixing decisions across the Vicinity portfolio.

## Principles
1. Each centre maintains a remix plan aligned to its catchment, positioning, and anchor strategy.
2. New tenancies are assessed for category contribution, covenant strength, and impact on existing
   tenants.
3. Exclusivity and restricted-use clauses are granted sparingly, recorded centrally, and checked before
   any new lease or permitted-use change is approved.

## Exclusivity Register
A portfolio exclusivity register must be maintained. Before signing a new tenant or approving a use
change, Leasing must confirm no conflict with existing exclusivities. Potential conflicts are referred
to Legal.

## Permitted Use
Permitted-use clauses must be specific. Material changes of use require landlord consent and a review of
exclusivity, parking, services capacity, and WHS implications.

## Roles & Responsibilities
- **Leasing Strategy** maintains remix plans and approves category decisions.
- **Tenancy Coordination** maintains the exclusivity register.
- **Legal** advises on enforceability and drafting.

Contact: leasingstrategy@vicinity.example.com.
"""
},
{
 "id":"POL-009","doc_name":"tenant_arrears_policy","category":"Tenant & Leasing",
 "title":"Tenant Arrears Management Policy","eff":"2024-02-01","rev":"2026-02-01",
 "owner":"Finance & Credit Control","ver":"2.6",
 "body":"""
## Purpose
To manage tenant arrears consistently and lawfully, minimising bad debt while supporting genuine tenants
through temporary difficulty.

## Scope
All tenant accounts across Vicinity-managed centres.

## Arrears Process
| Days Overdue | Action |
|--------------|--------|
| 1-7 | Automated reminder and account review |
| 8-14 | Direct contact by Credit Control; payment confirmation requested |
| 15-30 | Formal letter; Centre Manager engaged; payment plan considered |
| 31-60 | Breach notice considered per lease and law; security may be drawn |
| 60+ | Legal referral and recovery action per delegated authority |

## Principles
1. All recovery action complies with the lease and applicable retail tenancy law.
2. Default interest and recovery costs are charged only where the lease permits.
3. Payment plans must be documented and approved within delegated authority.
4. Drawing on bank guarantees or bonds requires senior approval and must be replenished by the tenant.

## Hardship
Genuine hardship requests are assessed case by case with reference to trading performance and history.
Any rent relief or deferral must be documented and approved by the asset owner.

## Reporting
An aged arrears report is produced weekly and reviewed monthly with the asset owner.

## Roles & Responsibilities
- **Credit Control** drives day-to-day recovery.
- **Centre Management** supports tenant engagement.
- **Legal** manages formal recovery.

Contact: creditcontrol@vicinity.example.com.
"""
},
{
 "id":"POL-010","doc_name":"lease_renewal_policy","category":"Tenant & Leasing",
 "title":"Lease Renewal & Holdover Policy","eff":"2024-11-01","rev":"2026-11-01",
 "owner":"Leasing","ver":"1.4",
 "body":"""
## Purpose
To manage lease expiries, renewals, options, and holdovers proactively to protect income continuity and
the centre's retail mix.

## Scope
All leases approaching expiry or in holdover across the Vicinity portfolio.

## Policy Statements
1. Expiry management begins at least 12 months before expiry, informed by the centre remix plan.
2. Tenants are notified of renewal intentions within the timeframe required by the lease and law.
3. Where a tenant holds an option, the option process and notice requirements must be followed precisely
   to avoid disputes.
4. Holdovers are minimised; where unavoidable, terms (including ongoing rent and termination notice) must
   be documented in writing.
5. Renewal terms align with current market and the asset's strategy; incentives follow the delegated
   authority matrix.

## Statutory Considerations
Minimum-term, disclosure, and notice obligations under retail leasing legislation must be met. Failure to
provide a required renewal or relocation notice in time can create unintended obligations and must be
escalated immediately.

## Roles & Responsibilities
- **Leasing** manages negotiations and documentation.
- **Tenancy Coordination** tracks expiries, options, and notice deadlines.
- **Centre Management** provides tenant performance input.

Contact: leasing@vicinity.example.com.
"""
},
{
 "id":"POL-011","doc_name":"planned_preventive_maintenance_policy","category":"Operations & Maintenance",
 "title":"Planned Preventive Maintenance Policy","eff":"2024-07-15","rev":"2026-07-15",
 "owner":"Centre Operations","ver":"2.2",
 "body":"""
## Purpose
To ensure all centre plant, equipment, and building fabric is maintained proactively to maximise
reliability, safety, asset life, and compliance.

## Scope
All base-building assets in Vicinity-managed centres, including HVAC, vertical transport, fire systems,
electrical, hydraulic, BMS, and structure.

## Policy Statements
1. Every centre maintains an asset register with criticality ratings and a planned preventive
   maintenance (PPM) schedule.
2. PPM tasks are scheduled in the maintenance management system with statutory and manufacturer
   frequencies as the minimum.
3. Statutory inspections (fire, lifts, pressure vessels, backflow, etc.) must never lapse; certificates
   are stored centrally.
4. Reactive works are logged, prioritised by a defined response matrix, and trended to identify recurring
   failures.
5. Contractors performing maintenance must comply with the Contractor Management Policy.

## Prioritisation Matrix
| Priority | Example | Target Response |
|----------|---------|-----------------|
| P1 Safety/critical | Fire system fault, lift entrapment | Immediate |
| P2 Major | HVAC failure in summer, water leak | 4 hours |
| P3 Minor | Lighting outage, door adjustment | 2 business days |
| P4 Cosmetic | Minor finishes | Next scheduled visit |

## Reporting
Maintenance KPIs (PPM completion %, reactive volume, statutory compliance) are reported monthly to the
asset owner.

## Roles & Responsibilities
- **Operations Manager** owns the PPM schedule and contractor performance.
- **Facilities Coordinator** logs and dispatches reactive works.

Contact: operations@vicinity.example.com.
"""
},
{
 "id":"POL-012","doc_name":"building_compliance_policy","category":"Operations & Maintenance",
 "title":"Essential Safety Measures & Building Compliance Policy","eff":"2024-06-15","rev":"2026-06-15",
 "owner":"Centre Operations & Risk","ver":"1.8",
 "body":"""
## Purpose
To ensure all centres maintain their essential safety measures (ESM) and meet building and fire safety
obligations.

## Scope
All Vicinity-managed centres and the essential safety/fire safety measures within them.

## Policy Statements
1. Each centre maintains a current schedule of essential safety measures and their required maintenance
   frequencies and performance standards.
2. Annual statements (Annual Fire Safety Statement / Annual Essential Safety Measures Report, as
   applicable to jurisdiction) must be issued on time by an accredited person.
3. Any defect to an essential safety measure is treated as a priority and rectified promptly; interim
   controls (e.g., fire watch) are implemented where a system is impaired.
4. Building occupancy limits and accessibility provisions must be maintained.
5. Records of inspections, tests, and certificates are retained for the life of the asset.

## Impairments
Any isolation or impairment of fire systems requires a permit, notification to the monitoring service,
and compensating controls until restored.

## Roles & Responsibilities
- **Operations** schedules and verifies ESM maintenance.
- **Risk & Compliance** tracks statutory statements and accreditation.

Contact: compliance@vicinity.example.com.
"""
},
{
 "id":"POL-013","doc_name":"hvac_energy_operations_policy","category":"Operations & Maintenance",
 "title":"HVAC & Building Services Operations Policy","eff":"2024-05-01","rev":"2026-05-01",
 "owner":"Centre Operations","ver":"1.5",
 "body":"""
## Purpose
To operate heating, ventilation, air conditioning, and related building services to deliver shopper and
tenant comfort, indoor air quality, and energy efficiency.

## Scope
All base-building mechanical services and building management systems (BMS) in Vicinity centres.

## Operating Standards
1. Common-area temperatures are maintained within the centre comfort band during trading hours.
2. BMS schedules align plant operation to trading hours plus appropriate pre-cool/pre-heat periods only.
3. Outside-air and filtration regimes meet indoor air quality standards; cooling towers are managed under
   the Water Hygiene & Legionella Policy.
4. Energy performance is monitored; anomalies and after-hours plant runtime are investigated.

## After-Hours Conditioning
Tenants requiring after-hours air conditioning must request it through the centre; usage is metered and
charged per the lease/outgoings arrangements.

## Roles & Responsibilities
- **Operations** manages BMS schedules and contractor tuning.
- **Sustainability** reviews energy performance and improvement opportunities.

Contact: operations@vicinity.example.com.
"""
},
{
 "id":"POL-014","doc_name":"water_hygiene_legionella_policy","category":"Operations & Maintenance",
 "title":"Water Hygiene & Legionella Control Policy","eff":"2024-03-01","rev":"2026-03-01",
 "owner":"Centre Operations & Risk","ver":"1.2",
 "body":"""
## Purpose
To control the risk of Legionella and other waterborne hazards arising from cooling towers, warm water
systems, and water features in Vicinity centres.

## Scope
All cooling towers, warm and hot water systems, decorative water features, and associated infrastructure.

## Policy Statements
1. Each relevant system has a documented risk management plan and monitoring program meeting the
   applicable public health regulation.
2. Cooling towers are registered with the relevant authority and serviced, tested, and disinfected at
   required intervals.
3. Microbial and chemical testing is conducted at required frequencies; exceedances trigger immediate
   corrective action and notification where mandated.
4. All results and corrective actions are recorded and retained.

## Exceedance Response
On a confirmed exceedance, the system is treated, re-tested, and where required reported to the health
authority. Decorative features may be shut down pending clearance.

## Roles & Responsibilities
- **Operations** oversees the testing contractor and remediation.
- **Risk & Compliance** ensures registration and notification compliance.

Contact: compliance@vicinity.example.com.
"""
},
{
 "id":"POL-015","doc_name":"asset_lifecycle_capex_policy","category":"Operations & Maintenance",
 "title":"Asset Lifecycle & Capital Works Policy","eff":"2024-09-15","rev":"2026-09-15",
 "owner":"Asset Management","ver":"1.6",
 "body":"""
## Purpose
To plan and govern capital works and asset replacement so that centres remain safe, compliant, and
competitive while delivering value to owners.

## Scope
All capital expenditure (capex) on base-building assets and centre improvements.

## Policy Statements
1. Each centre maintains a rolling 10-year capital plan informed by asset condition assessments.
2. Capex proposals require a business case covering scope, cost, benefit, risk, and owner approval per
   the delegated authority matrix.
3. Lifecycle replacement decisions balance condition, reliability, energy performance, and
   obsolescence.
4. Projects are delivered under the Project & Contractor Management policies with defined budgets and
   handover requirements.

## Condition Assessments
Independent condition assessments are refreshed at least every three years and feed the capital plan and
maintenance strategy.

## Roles & Responsibilities
- **Asset Management** owns the capital plan and business cases.
- **Operations** provides condition and reliability input and manages delivery.
- **Finance** validates budgets and tracks spend.

Contact: assetmanagement@vicinity.example.com.
"""
},
{
 "id":"POL-016","doc_name":"loading_dock_logistics_policy","category":"Operations & Maintenance",
 "title":"Loading Dock & Deliveries Policy","eff":"2024-04-15","rev":"2026-04-15",
 "owner":"Centre Operations","ver":"1.3",
 "body":"""
## Purpose
To manage loading docks and deliveries safely and efficiently, minimising congestion, noise, and risk to
people and property.

## Scope
All loading docks, service corridors, and goods lifts in Vicinity centres, and all tenants, carriers, and
contractors using them.

## Rules
1. Delivery vehicles must use designated docks and follow posted speed limits and traffic management.
2. Reversing requires care; spotters are used where sight lines are restricted.
3. Goods must be moved promptly; docks and corridors must be kept clear of stock and rubbish.
4. Pallet jacks, cages, and trolleys must be used safely and stored correctly.
5. After-hours and oversized deliveries must be booked with the centre.

## Safety
Dock plates, edge protection, and bollards must be maintained. Spills are cleaned immediately and
reported. Idling engines in enclosed docks are not permitted.

## Roles & Responsibilities
- **Operations** maintains dock infrastructure and manages bookings.
- **Tenants** ensure their carriers comply with dock rules.

Contact: operations@vicinity.example.com.
"""
},
{
 "id":"POL-017","doc_name":"pest_management_policy","category":"Operations & Maintenance",
 "title":"Integrated Pest Management Policy","eff":"2024-02-15","rev":"2026-02-15",
 "owner":"Centre Operations","ver":"1.1",
 "body":"""
## Purpose
To prevent and control pests across centres using an integrated, low-toxicity approach that protects
shoppers, tenants (particularly food retailers), and the building.

## Scope
All common areas, base-building voids, food courts, waste areas, and grease management systems.

## Policy Statements
1. Each centre has a scheduled pest management program by a licensed contractor, with documented service
   reports and bait station maps.
2. Food retailers must maintain their own in-store pest control and cooperate with centre-wide programs.
3. Treatments prioritise prevention (proofing, hygiene, waste management) before chemical control.
4. Sightings are logged and trended; hot spots trigger additional inspection and proofing.

## Coordination With Tenants
Food court and food retail tenants are included in coordinated treatment windows to prevent harbourage
migrating between tenancies.

## Roles & Responsibilities
- **Operations** manages the contractor and common-area program.
- **Tenancy** ensures food tenants meet their obligations.

Contact: operations@vicinity.example.com.
"""
},
{
 "id":"POL-018","doc_name":"lifts_escalators_policy","category":"Operations & Maintenance",
 "title":"Vertical Transport (Lifts & Escalators) Policy","eff":"2024-08-15","rev":"2026-08-15",
 "owner":"Centre Operations","ver":"1.4",
 "body":"""
## Purpose
To keep lifts, escalators, and travelators safe, reliable, and compliant for shoppers and tenants.

## Scope
All vertical transport assets in Vicinity-managed centres.

## Policy Statements
1. All units are maintained by a licensed contractor under a comprehensive agreement, with statutory
   inspections kept current.
2. Entrapment and breakdown responses meet the agreed response times; entrapments are treated as P1.
3. Units with safety defects are taken out of service and barricaded until repaired.
4. Escalator and travelator safety signage, comb plates, and emergency stops are inspected regularly.
5. Incident data is trended to inform refurbishment and replacement planning.

## Shopper Safety
Clear signage advises holding handrails, supervising children, and not using escalators with prams or
trolleys where prohibited. Incidents involving injury follow the Incident Management Policy.

## Roles & Responsibilities
- **Operations** manages the maintenance contract and statutory compliance.
- **Security** assists with incident response and crowd control.

Contact: operations@vicinity.example.com.
"""
},
{
 "id":"POL-019","doc_name":"common_area_maintenance_standards_policy","category":"Operations & Maintenance",
 "title":"Common Area Presentation & Maintenance Standards Policy","eff":"2024-01-15","rev":"2026-01-15",
 "owner":"Centre Operations","ver":"2.0",
 "body":"""
## Purpose
To define the presentation and maintenance standards for common areas so every centre is clean, safe,
well-presented, and welcoming.

## Scope
All common areas including malls, food courts, amenities, car parks, landscaping, and external areas.

## Standards
1. Floors are clean, dry, and free of trip hazards; spills are attended to immediately.
2. Amenities (restrooms, parents' rooms) are cleaned to schedule and stocked at all times during trade.
3. Furniture, planters, signage, and finishes are maintained in good repair.
4. Lighting is fully operational; failed lamps are replaced within defined timeframes.
5. Landscaping is maintained healthy and tidy; external areas are free of litter and graffiti.

## Inspections
Centre Management conducts documented presentation walks at least daily during trade, logging defects for
rectification.

## Roles & Responsibilities
- **Operations** maintains base-building presentation.
- **Cleaning Contractor** delivers daily standards per the Cleaning & Hygiene Policy.

Contact: operations@vicinity.example.com.
"""
},
{
 "id":"POL-020","doc_name":"after_hours_works_permit_policy","category":"Operations & Maintenance",
 "title":"After-Hours Works & Hot Works Permit Policy","eff":"2024-10-15","rev":"2026-10-15",
 "owner":"Centre Operations & WHS","ver":"1.7",
 "body":"""
## Purpose
To control higher-risk works (after-hours, hot works, confined space, working at height, isolations) so
they are performed safely and without disrupting trade or impairing safety systems.

## Scope
All such works performed by contractors or tenants in Vicinity centres.

## Permit Requirements
1. A permit to work must be issued and signed before commencing hot works, confined space entry, work at
   height, electrical isolation, or roof access.
2. Hot works require a fire watch, suitable extinguishers, and isolation/monitoring of affected detection
   with a documented fire impairment.
3. After-hours works must be booked and inducted; noise and dust controls protect adjacent tenants.
4. On completion, the area is made safe, systems are restored, and the permit is closed out.

## Verification
Security/Operations verify permit conditions during the works and at fire-system reinstatement.

## Roles & Responsibilities
- **Operations/WHS** issues and audits permits.
- **Contractors** comply with all permit conditions.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-021","doc_name":"whs_management_policy","category":"Work Health & Safety",
 "title":"Work Health & Safety Management Policy","eff":"2024-01-01","rev":"2026-01-01",
 "owner":"WHS","ver":"3.0",
 "body":"""
## Purpose
Vicinity Centres is committed to providing a safe and healthy environment for employees, contractors,
tenants, and shoppers. This policy sets the framework for managing work health and safety (WHS) across
the portfolio.

## Scope
All Vicinity employees, contractors, and visitors, and all activities at managed centres and offices.

## Commitments
1. Comply with all applicable WHS legislation, regulations, and codes of practice as a minimum standard.
2. Identify hazards and assess and control risks using the hierarchy of controls.
3. Consult with workers and stakeholders on matters affecting their health and safety.
4. Provide information, training, instruction, and supervision.
5. Report, investigate, and learn from incidents and near misses.
6. Set measurable WHS objectives and review performance.

## Responsibilities
- **Officers** (as defined in WHS law) exercise due diligence.
- **Managers** implement WHS in their area and lead by example.
- **Workers** take reasonable care, follow procedures, and report hazards.

## Consultation
WHS committees and toolbox talks provide structured consultation. Workers may raise issues without fear
of reprisal.

## Review
This policy is reviewed at least every two years or after significant change. WHS performance is reported
to the Board Risk Committee.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-022","doc_name":"hazard_risk_assessment_policy","category":"Work Health & Safety",
 "title":"Hazard Identification & Risk Assessment Policy","eff":"2024-02-01","rev":"2026-02-01",
 "owner":"WHS","ver":"1.6",
 "body":"""
## Purpose
To ensure hazards are systematically identified and risks are assessed and controlled before they cause
harm.

## Scope
All workplaces, tasks, plant, and substances under Vicinity's management or control.

## Process
1. **Identify** hazards through inspections, task analysis, consultation, and incident data.
2. **Assess** risk by likelihood and consequence using the corporate risk matrix.
3. **Control** using the hierarchy: elimination, substitution, isolation, engineering, administrative,
   then PPE.
4. **Document** in a risk register or safe work method statement (SWMS) for high-risk work.
5. **Review** controls after incidents, changes, or at scheduled intervals.

## High-Risk Work
High-risk construction work requires a SWMS before commencement. Plant and hazardous chemicals require
specific risk assessments and registers.

## Roles & Responsibilities
- **Managers** ensure assessments are completed and controls implemented.
- **WHS** provides tools, training, and assurance.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-023","doc_name":"incident_management_policy","category":"Work Health & Safety",
 "title":"Incident Management & Notifiable Incidents Policy","eff":"2024-03-01","rev":"2026-03-01",
 "owner":"WHS & Risk","ver":"2.3",
 "body":"""
## Purpose
To ensure all incidents and near misses are reported, managed, investigated, and used to prevent
recurrence, and that notifiable incidents are reported to the regulator.

## Scope
All incidents involving employees, contractors, tenants, shoppers, or property at managed sites.

## Reporting
1. All incidents and near misses must be reported in the incident system as soon as possible and within
   24 hours.
2. Serious injuries, dangerous incidents, and fatalities are **notifiable**: the site must be preserved
   (so far as is safe) and the regulator notified immediately by the authorised person.
3. Injured persons receive first aid or medical care as the first priority.

## Investigation
Incidents are investigated proportionate to actual and potential severity, using root cause analysis.
Corrective actions are assigned, tracked, and verified for effectiveness.

## Privacy
Personal and medical information is handled confidentially under the Privacy Policy.

## Roles & Responsibilities
- **First responders** make safe and provide care.
- **Managers** report and support investigation.
- **WHS/Risk** manages notifications, investigation quality, and trends.

Contact: incidents@vicinity.example.com.
"""
},
{
 "id":"POL-024","doc_name":"contractor_whs_policy","category":"Work Health & Safety",
 "title":"Contractor WHS & Permit Policy","eff":"2024-04-01","rev":"2026-04-01",
 "owner":"WHS","ver":"1.9",
 "body":"""
## Purpose
To ensure contractors performing work at Vicinity centres do so safely and in compliance with WHS law and
centre requirements.

## Scope
All contractors and subcontractors engaged to work at managed sites.

## Requirements
1. Contractors must be prequalified, including insurances, licences, and a WHS management system
   appropriate to their risk.
2. Site-specific inductions must be completed before work commences.
3. SWMS or safe work procedures are required for high-risk work and reviewed on site.
4. Permits to work apply to hot works, confined spaces, electrical isolation, and working at height.
5. Contractor performance is monitored; serious or repeated breaches lead to stand-down or removal.

## Sign-In & Supervision
Contractors sign in/out, display identification, and work only within approved areas and hours. Site
representatives verify controls are in place.

## Roles & Responsibilities
- **Procurement** manages prequalification.
- **Operations/WHS** manages inductions, permits, and on-site compliance.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-025","doc_name":"slips_trips_falls_policy","category":"Work Health & Safety",
 "title":"Slips, Trips & Falls Prevention Policy","eff":"2024-05-01","rev":"2026-05-01",
 "owner":"WHS & Operations","ver":"1.2",
 "body":"""
## Purpose
To reduce the risk of slips, trips, and falls — the most common cause of injury to shoppers and workers
in retail centres.

## Scope
All common areas, back-of-house, car parks, and external areas of managed centres.

## Controls
1. Spills and wet areas are attended to immediately with appropriate signage and cleaning.
2. Wet-weather mats and warning signage are deployed at entries during rain.
3. Floor surfaces are maintained with appropriate slip resistance; defects (lifted tiles, damaged
   thresholds) are rectified promptly.
4. Cleaning is scheduled to minimise wet floors during peak shopper periods where possible.
5. Lighting levels are maintained, especially on stairs, ramps, and car parks.

## Inspections & Records
Documented presentation/safety walks identify hazards. Cleaning wet-floor logs and inspection records are
retained to demonstrate diligence.

## Roles & Responsibilities
- **Cleaning Contractor** delivers immediate spill response and signage.
- **Operations** maintains surfaces and lighting.
- **All staff** report hazards immediately.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-026","doc_name":"working_at_heights_policy","category":"Work Health & Safety",
 "title":"Working at Heights Policy","eff":"2024-06-01","rev":"2026-06-01",
 "owner":"WHS","ver":"1.4",
 "body":"""
## Purpose
To prevent falls from height during maintenance, cleaning, signage, and construction activities.

## Scope
All work performed at height (roofs, plant platforms, atria, elevated work platforms, ladders) at managed
sites.

## Requirements
1. Work at height is eliminated where possible (e.g., design out, work from ground level).
2. Where unavoidable, fall prevention (guardrails, EWPs) is preferred over fall arrest.
3. A permit and SWMS are required for roof access and other high-risk height work.
4. Anchor points and height safety systems are certified and inspected at required intervals.
5. Workers are trained and competent; fall-arrest users are trained in rescue.

## Atrium & Void Work
Work over voids, atria, or public areas requires exclusion zones, edge protection, and tool tethering to
prevent dropped objects.

## Roles & Responsibilities
- **Operations/WHS** manage permits, anchor certification, and verification.
- **Contractors** provide competent workers and compliant equipment.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-027","doc_name":"hazardous_substances_policy","category":"Work Health & Safety",
 "title":"Hazardous Chemicals & Dangerous Goods Policy","eff":"2024-07-01","rev":"2026-07-01",
 "owner":"WHS","ver":"1.3",
 "body":"""
## Purpose
To manage the safe storage, handling, and use of hazardous chemicals and dangerous goods at centres.

## Scope
All hazardous chemicals used or stored by Vicinity and its contractors (cleaning chemicals, pool/water
treatment, fuels, gases). Tenant chemicals are managed by tenants but must not create base-building risk.

## Requirements
1. A chemical register and current safety data sheets (SDS) are maintained for all hazardous chemicals.
2. Storage meets segregation, bunding, ventilation, and quantity requirements for the dangerous goods
   class.
3. Manifests and placarding are maintained where threshold quantities are exceeded.
4. Spill kits, PPE, and emergency information are available where chemicals are used or stored.
5. Workers are trained in safe handling and emergency response.

## Spills
Spills are contained, cleaned, and reported. Significant spills follow the Emergency and Environmental
Incident procedures.

## Roles & Responsibilities
- **Operations/WHS** maintain registers, storage, and training.
- **Contractors** provide SDS and comply with handling rules.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-028","doc_name":"first_aid_policy","category":"Work Health & Safety",
 "title":"First Aid & Medical Response Policy","eff":"2024-08-01","rev":"2026-08-01",
 "owner":"WHS & Centre Management","ver":"1.1",
 "body":"""
## Purpose
To ensure prompt and appropriate first aid and medical response for workers and shoppers.

## Scope
All managed centres and offices.

## Provisions
1. Each centre maintains first aid kits, trained first aiders, and accessible automated external
   defibrillators (AEDs).
2. First aid rooms or designated areas are provided where required by the centre's size and risk.
3. AEDs are signed, maintained, and ready; pads and batteries are checked at intervals.
4. Trained first aiders are rostered during trading hours; security officers commonly hold first aid
   qualifications.
5. Serious medical events are escalated to emergency services and managed under the Incident Management
   Policy.

## Records & Hygiene
First aid treatments are recorded confidentially. Sharps and biohazards are managed per infection control
procedures.

## Roles & Responsibilities
- **WHS** sets requirements and tracks first aider numbers and currency.
- **Centre Management/Security** deliver response on site.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-029","doc_name":"fatigue_lone_worker_policy","category":"Work Health & Safety",
 "title":"Fatigue & Lone Worker Safety Policy","eff":"2024-09-01","rev":"2026-09-01",
 "owner":"WHS","ver":"1.0",
 "body":"""
## Purpose
To manage the risks associated with fatigue and with employees who work alone or in isolation,
particularly during after-hours operations.

## Scope
All workers whose roles involve shift work, extended hours, on-call duty, or working alone (e.g., security
patrols, after-hours operations).

## Fatigue Controls
1. Rosters are designed to provide adequate rest breaks and recovery between shifts.
2. Excessive overtime and back-to-back shifts are avoided and monitored.
3. Workers must not undertake safety-critical tasks when impaired by fatigue.

## Lone Worker Controls
1. Lone and isolated work is risk-assessed; communication and check-in procedures are established.
2. Personal duress and check-in technology is provided where the risk warrants.
3. Escalation procedures apply if a worker fails to check in.

## Roles & Responsibilities
- **Managers** design safe rosters and monitor fatigue and check-ins.
- **Workers** report fatigue and follow check-in procedures.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-030","doc_name":"mental_health_wellbeing_policy","category":"Work Health & Safety",
 "title":"Psychological Health & Wellbeing Policy","eff":"2024-10-01","rev":"2026-10-01",
 "owner":"People & Culture / WHS","ver":"1.2",
 "body":"""
## Purpose
To protect and promote the psychological health of workers and to manage psychosocial hazards as part of
Vicinity's WHS obligations.

## Scope
All Vicinity employees and, where relevant, contractors at managed sites.

## Commitments
1. Identify and control psychosocial hazards (high job demands, low control, poor support, bullying,
   exposure to traumatic events such as serious incidents in centre).
2. Provide an Employee Assistance Program (EAP) accessible to all staff and immediate family.
3. Offer support and debriefing after critical incidents (e.g., armed robbery, serious injury, death in
   centre).
4. Foster a respectful workplace free from bullying, harassment, and discrimination.

## Support Pathways
EAP is confidential and free. Managers are trained to recognise distress and refer to support. Reasonable
adjustments are considered for affected workers.

## Roles & Responsibilities
- **People & Culture** manages EAP, training, and support.
- **Managers** monitor workloads and provide support.
- **WHS** integrates psychosocial risk into risk management.

Contact: wellbeing@vicinity.example.com.
"""
},
{
 "id":"POL-031","doc_name":"emergency_management_policy","category":"Security & Emergency",
 "title":"Emergency Management & Evacuation Policy","eff":"2024-01-01","rev":"2026-01-01",
 "owner":"Security & Risk","ver":"3.1",
 "body":"""
## Purpose
To protect life and property by ensuring every centre has effective emergency planning, response, and
evacuation capability.

## Scope
All managed centres, their occupants, and emergency situations including fire, bomb threat, armed
offender, medical emergency, severe weather, and infrastructure failure.

## Requirements
1. Each centre maintains an emergency plan and emergency procedures consistent with the applicable
   planning-for-emergencies standard.
2. An Emergency Planning Committee (EPC) and trained Emergency Control Organisation (ECO) — chief and
   area wardens — are established and current.
3. Emergency procedures are practised through exercises at least annually; evacuation diagrams are
   displayed and current.
4. Detection, alarm, communication, and emergency lighting systems are maintained per the Building
   Compliance Policy.
5. Tenants must participate in emergency training and follow warden directions.

## Activation
On alarm or warden direction, occupants evacuate via the nearest safe exit to the assembly area.
Re-entry occurs only when authorised by emergency services or the chief warden.

## Roles & Responsibilities
- **Chief Warden** leads on-site response.
- **Security** supports detection, communication, and crowd management.
- **Risk** maintains plans and training compliance.

Contact: security@vicinity.example.com.
"""
},
{
 "id":"POL-032","doc_name":"security_operations_policy","category":"Security & Emergency",
 "title":"Centre Security Operations Policy","eff":"2024-02-01","rev":"2026-02-01",
 "owner":"Security","ver":"2.5",
 "body":"""
## Purpose
To provide a safe and secure environment for shoppers, tenants, and staff through professional,
risk-based security operations.

## Scope
All security services at managed centres, whether in-house or contracted.

## Policy Statements
1. Security resourcing is based on a documented risk assessment for each centre and adjusted for peak
   periods and events.
2. Security officers must be licensed, inducted, and trained in customer service, conflict de-escalation,
   first aid, and emergency response.
3. Patrols, incident response, and access control follow documented post orders and assignment
   instructions.
4. Use of force is a last resort, reasonable and proportionate, and always documented; officers do not
   pursue offenders beyond safe limits.
5. All incidents are recorded in the security/incident system.

## Conduct
Officers act lawfully, impartially, and respectfully, and comply with anti-discrimination obligations.
Detentions follow lawful citizen's-arrest limits and are handed to police promptly.

## Roles & Responsibilities
- **Security Manager** sets risk-based resourcing and supervises performance.
- **Officers** deliver services per post orders.

Contact: security@vicinity.example.com.
"""
},
{
 "id":"POL-033","doc_name":"cctv_policy","category":"Security & Emergency",
 "title":"CCTV & Surveillance Policy","eff":"2024-03-01","rev":"2026-03-01",
 "owner":"Security & Privacy","ver":"1.8",
 "body":"""
## Purpose
To operate CCTV lawfully and effectively to deter crime, support safety and investigations, and protect
privacy.

## Scope
All CCTV and surveillance systems in common areas, car parks, and back-of-house of managed centres.

## Principles
1. CCTV is used for safety, security, and asset protection — not for monitoring employee productivity.
2. Signage notifies shoppers and staff that CCTV is in operation, consistent with privacy and surveillance
   laws.
3. Cameras are not installed in areas with a high expectation of privacy (e.g., toilets, change rooms,
   parents' rooms).
4. Footage access is restricted to authorised personnel and logged.
5. Footage is retained for a defined period (typically 30-90 days) then securely overwritten, unless held
   for an investigation or legal request.

## Disclosure
Footage is released to police or in response to lawful requests through a controlled process, recorded in
a disclosure register. Personal requests are handled under the Privacy Policy.

## Roles & Responsibilities
- **Security** operates and maintains the system and access controls.
- **Privacy Officer** ensures lawful use and handles disclosure requests.

Contact: security@vicinity.example.com.
"""
},
{
 "id":"POL-034","doc_name":"access_control_keys_policy","category":"Security & Emergency",
 "title":"Access Control & Key Management Policy","eff":"2024-04-01","rev":"2026-04-01",
 "owner":"Security & Operations","ver":"1.5",
 "body":"""
## Purpose
To control physical access to centre areas and to manage keys, swipe cards, and credentials securely.

## Scope
All access points, keys, master key systems, and electronic access credentials at managed centres.

## Policy Statements
1. Access is granted on a least-privilege basis and recorded in an access register.
2. Keys and access cards are issued against signature, tracked, and returned on role change or departure.
3. Master and restricted keys are held securely with strict issue controls; lost master keys trigger a
   risk assessment and possible re-keying.
4. Electronic access events are logged; access rights are reviewed periodically and revoked promptly when
   no longer required.
5. After-hours access by tenants and contractors is controlled and recorded.

## Lost/Compromised Credentials
Lost cards or keys are reported immediately and deactivated. Tailgating into back-of-house areas is
prohibited.

## Roles & Responsibilities
- **Security** administers credentials and the access register.
- **Operations** maintains hardware and master key systems.

Contact: security@vicinity.example.com.
"""
},
{
 "id":"POL-035","doc_name":"crowd_event_safety_policy","category":"Security & Emergency",
 "title":"Crowd & Event Safety Policy","eff":"2024-05-01","rev":"2026-05-01",
 "owner":"Security & Marketing","ver":"1.3",
 "body":"""
## Purpose
To manage the safety of high-attendance events and peak trading periods (e.g., celebrity appearances,
product launches, sales events, Christmas) where crowd density creates risk.

## Scope
All promotional events and peak periods in managed centres expected to draw significant crowds.

## Requirements
1. Events likely to draw large crowds require a documented event safety plan and risk assessment.
2. Crowd capacity, queue management, barriers, and additional security/medical resources are determined
   in advance.
3. Egress routes and emergency access must remain clear at all times.
4. A go/no-go and crowd-control escalation (including event suspension) procedure is defined.
5. High-risk events are notified to police and emergency services as appropriate.

## Coordination
Marketing and the event promoter coordinate with Security and Operations. The Centre Manager has authority
to modify or stop an event on safety grounds.

## Roles & Responsibilities
- **Marketing** plans events and engages promoters.
- **Security** leads crowd safety planning and response.

Contact: security@vicinity.example.com.
"""
},
{
 "id":"POL-036","doc_name":"lost_property_policy","category":"Security & Emergency",
 "title":"Lost & Found Property Policy","eff":"2024-06-01","rev":"2026-06-01",
 "owner":"Centre Management & Security","ver":"1.0",
 "body":"""
## Purpose
To manage lost and found property fairly, securely, and in line with legal obligations.

## Scope
All property found in common areas of managed centres and handed to centre staff.

## Process
1. Found items are recorded in the lost property register with date, location, description, and finder.
2. Items are stored securely; high-value items, wallets, phones, and IDs receive enhanced security.
3. Cash and items suspected of being stolen or related to a crime are referred to police.
4. Owners reclaiming items must provide reasonable proof of ownership and sign on collection.
5. Unclaimed items are held for a defined period, then donated, returned to finder, or disposed of per
   law and policy.

## Perishables & Hazards
Perishable items are disposed of promptly. Suspicious or hazardous items are not handled and are reported
to Security.

## Roles & Responsibilities
- **Centre Management/Security** maintain the register and storage.

Contact: centremanagement@vicinity.example.com.
"""
},
{
 "id":"POL-037","doc_name":"trespass_antisocial_behaviour_policy","category":"Security & Emergency",
 "title":"Trespass & Anti-Social Behaviour Policy","eff":"2024-07-01","rev":"2026-07-01",
 "owner":"Security","ver":"1.4",
 "body":"""
## Purpose
To manage anti-social behaviour, trespass, and banning fairly and lawfully while keeping centres safe and
welcoming.

## Scope
All persons in managed centres exhibiting anti-social, threatening, or unlawful behaviour.

## Principles
1. Centres are private property open to the public for lawful purposes; entry may be refused or withdrawn
   for unacceptable conduct.
2. Responses are graduated: verbal warning, formal warning, temporary ban, then longer ban, proportionate
   to the behaviour.
3. Bans are documented with evidence (incident reports, CCTV) and a defined duration and scope.
4. Officers act without discrimination and consider vulnerability (e.g., youth, mental health,
   homelessness) and refer to support services where appropriate.
5. Serious or criminal conduct is reported to police.

## Records
Banning notices and supporting evidence are retained securely and reviewed for fairness and consistency.

## Roles & Responsibilities
- **Security** issues and enforces notices.
- **Centre Manager** approves longer bans and reviews appeals.

Contact: security@vicinity.example.com.
"""
},
{
 "id":"POL-038","doc_name":"counter_terrorism_policy","category":"Security & Emergency",
 "title":"Counter-Terrorism & Hostile Threat Preparedness Policy","eff":"2024-08-01","rev":"2026-08-01",
 "owner":"Security & Risk","ver":"1.1",
 "body":"""
## Purpose
To enhance preparedness for hostile threats, including armed offender and vehicle-as-a-weapon scenarios,
in line with national protective security guidance for crowded places.

## Scope
All managed centres, with depth of measures proportionate to each centre's risk profile.

## Measures
1. Each higher-risk centre completes a crowded-places risk assessment and self-assessment aligned to
   national guidance.
2. Protective measures may include hostile vehicle mitigation, CCTV analytics, staff awareness, and
   relationships with police.
3. Staff are trained in "see something, say something", and in armed-offender response (escape, hide,
   tell) and lockdown procedures.
4. Suspicious items and behaviours are reported and managed under defined procedures.
5. Information sharing with law enforcement is maintained through established channels.

## Sensitivity
Detailed protective security information is confidential and shared on a need-to-know basis.

## Roles & Responsibilities
- **Security/Risk** maintain assessments and police liaison.
- **All staff** complete awareness training and report concerns.

Contact: security@vicinity.example.com.
"""
},
{
 "id":"POL-039","doc_name":"severe_weather_policy","category":"Security & Emergency",
 "title":"Severe Weather & Natural Hazard Policy","eff":"2024-09-01","rev":"2026-09-01",
 "owner":"Operations & Risk","ver":"1.2",
 "body":"""
## Purpose
To prepare for and respond to severe weather and natural hazards (storms, flooding, heatwave, bushfire
smoke, earthquake) to protect people and property and maintain continuity.

## Scope
All managed centres, with site-specific plans reflecting local hazards.

## Preparedness
1. Each centre identifies its exposure to natural hazards and maintains response actions in its emergency
   plan.
2. Roof drainage, sump pumps, and storm-water systems are maintained ahead of storm seasons.
3. Triggers and actions are defined for warnings (e.g., securing outdoor furniture, closing affected
   areas, evacuation, or shelter-in-place).
4. Heatwave and air-quality events trigger HVAC and amenity responses for shopper welfare.

## Response & Recovery
Damage is assessed and made safe; affected areas are isolated. Business continuity and insurance
procedures are activated for significant events.

## Roles & Responsibilities
- **Operations** maintains protective infrastructure and leads make-safe.
- **Risk** coordinates continuity and insurance.

Contact: operations@vicinity.example.com.
"""
},
{
 "id":"POL-040","doc_name":"business_continuity_policy","category":"Security & Emergency",
 "title":"Business Continuity & Crisis Management Policy","eff":"2024-10-01","rev":"2026-10-01",
 "owner":"Risk","ver":"1.6",
 "body":"""
## Purpose
To ensure Vicinity can respond to and recover from disruptive events while protecting people, assets,
reputation, and continuity of trade.

## Scope
All centres and corporate functions, covering disruptions such as major incidents, utility outages,
cyber incidents, pandemics, and supply failures.

## Framework
1. Business impact analyses identify critical functions and recovery priorities and time objectives.
2. Each centre and key function maintains a business continuity plan (BCP) with response roles and
   workarounds.
3. A crisis management team (CMT) is established with clear activation criteria and authority.
4. Plans are tested at least annually through exercises and updated after tests and incidents.
5. Crisis communications follow the Communications Policy with a single source of truth.

## Activation
The CMT is activated for events exceeding normal incident response. Decisions and actions are logged.

## Roles & Responsibilities
- **Risk** owns the BCP framework and exercise program.
- **CMT** leads response and recovery during a crisis.

Contact: risk@vicinity.example.com.
"""
},
{
 "id":"POL-041","doc_name":"delegations_of_authority_policy","category":"Finance & Procurement",
 "title":"Delegations of Authority Policy","eff":"2024-01-15","rev":"2026-01-15",
 "owner":"Finance","ver":"2.1",
 "body":"""
## Purpose
To define who may approve expenditure, contracts, and commitments on behalf of Vicinity and managed
assets, ensuring proper financial control and accountability.

## Scope
All financial and contractual commitments by employees across the business and managed centres.

## Principles
1. Authority is delegated by role and value through a Delegations of Authority (DoA) matrix.
2. No person approves their own expenditure, claim, or a transaction in which they have a conflict.
3. Commitments above a delegate's limit require escalation to a higher delegate or the asset owner.
4. Delegations require segregation of duties between requisition, approval, and payment.
5. Emergency expenditure to protect life or property may proceed and be ratified promptly afterwards.

## Operating Within Owner Mandates
For managed assets, delegations also respect each owner's management agreement and any owner-specific
approval thresholds.

## Roles & Responsibilities
- **Finance** maintains and communicates the DoA matrix.
- **Managers** approve only within their delegated limits.

Contact: finance@vicinity.example.com.
"""
},
{
 "id":"POL-042","doc_name":"procurement_policy","category":"Finance & Procurement",
 "title":"Procurement & Purchasing Policy","eff":"2024-02-15","rev":"2026-02-15",
 "owner":"Procurement","ver":"1.9",
 "body":"""
## Purpose
To ensure goods and services are procured ethically, competitively, and in the best interests of Vicinity
and the owners whose assets it manages.

## Scope
All procurement of goods, services, and works across the business and managed centres.

## Principles
1. Procurement achieves value for money considering whole-of-life cost, quality, risk, and
   sustainability — not lowest price alone.
2. Competitive processes apply based on value thresholds (quotes, tenders) defined in the procurement
   framework.
3. Suppliers are selected fairly and transparently; conflicts of interest must be declared and managed.
4. Approved contracts and purchase orders precede the supply of goods or services.
5. Modern slavery, WHS, and sustainability criteria are considered in supplier selection.

## Thresholds
| Value (indicative) | Minimum Process |
|--------------------|-----------------|
| Low | One written quote |
| Medium | Three written quotes |
| High | Formal tender / panel |

## Roles & Responsibilities
- **Procurement** sets the framework and runs major sourcing.
- **Budget holders** initiate within delegation and the DoA matrix.

Contact: procurement@vicinity.example.com.
"""
},
{
 "id":"POL-043","doc_name":"accounts_payable_policy","category":"Finance & Procurement",
 "title":"Accounts Payable & Payments Policy","eff":"2024-03-15","rev":"2026-03-15",
 "owner":"Finance","ver":"1.7",
 "body":"""
## Purpose
To ensure supplier invoices are validated, approved, and paid accurately, on time, and with strong
controls against fraud and error.

## Scope
All supplier payments across the business and managed centres.

## Controls
1. Invoices are matched to an approved purchase order and evidence of receipt (three-way match) before
   payment.
2. Payment approvals follow the DoA matrix with segregation of duties.
3. New suppliers and bank-account changes are independently verified by call-back to a known contact to
   prevent payment-redirection fraud.
4. Payment runs are reviewed and approved by an authorised officer.
5. Duplicate, unusual, or urgent payments are scrutinised before release.

## Supplier Terms
Standard payment terms are applied; small-business suppliers are paid within shortened terms where
applicable. Early-payment requests follow approval.

## Roles & Responsibilities
- **Accounts Payable** validates and processes invoices.
- **Finance** verifies banking details and approves payment runs.

Contact: ap@vicinity.example.com.
"""
},
{
 "id":"POL-044","doc_name":"trust_accounting_policy","category":"Finance & Procurement",
 "title":"Trust Accounting & Owner Funds Policy","eff":"2024-04-15","rev":"2026-04-15",
 "owner":"Finance","ver":"1.4",
 "body":"""
## Purpose
To manage funds held on behalf of property owners in strict compliance with trust-account and real estate
agency legislation.

## Scope
All money received and held on behalf of owners for managed properties, including rent, outgoings, and
bonds where applicable.

## Requirements
1. Owner funds are held in designated trust accounts separate from Vicinity's own funds.
2. Trust accounts are reconciled monthly and audited as required by the relevant agency legislation.
3. Disbursements to owners and suppliers follow authorised instructions and the management agreement.
4. Receipts and payments are recorded promptly and accurately; no co-mingling of funds is permitted.
5. Interest and handling of trust money comply with the applicable legislation.

## Controls & Audit
Segregation of duties applies to receipting, reconciliation, and disbursement. External trust audits are
completed within statutory deadlines.

## Roles & Responsibilities
- **Finance/Trust Accounting** maintains and reconciles trust accounts.
- **Licensee-in-charge** ensures statutory compliance.

Contact: trustaccounts@vicinity.example.com.
"""
},
{
 "id":"POL-045","doc_name":"budgeting_reporting_policy","category":"Finance & Procurement",
 "title":"Budgeting & Financial Reporting Policy","eff":"2024-05-15","rev":"2026-05-15",
 "owner":"Finance","ver":"1.5",
 "body":"""
## Purpose
To provide accurate, timely budgets and financial reporting to owners and management to support sound
decisions.

## Scope
All managed centres and corporate cost centres.

## Requirements
1. Annual operating and capital budgets are prepared for each centre and approved by the owner before the
   financial year.
2. Monthly management reporting compares actuals to budget with variance commentary and a reforecast.
3. Outgoings budgets and reconciliations follow the Rent Review & Outgoings Policy.
4. Reporting follows applicable accounting standards and owner reporting requirements.
5. Period-end close follows a defined timetable with reconciliations and review.

## Forecasting
Reforecasts incorporate leasing, arrears, and capital timing. Material risks and opportunities are
flagged to owners promptly.

## Roles & Responsibilities
- **Finance Business Partners** prepare budgets and reporting.
- **Centre Managers** own operational performance against budget.

Contact: finance@vicinity.example.com.
"""
},
{
 "id":"POL-046","doc_name":"expense_travel_policy","category":"Finance & Procurement",
 "title":"Employee Expense & Travel Policy","eff":"2024-06-15","rev":"2026-06-15",
 "owner":"Finance","ver":"2.0",
 "body":"""
## Purpose
To ensure business expenses and travel are reasonable, necessary, and properly approved and substantiated.

## Scope
All employees incurring business expenses or travelling on Vicinity business.

## Rules
1. Expenses must be business-related, reasonable, and within policy limits, and supported by a valid tax
   receipt.
2. Travel is booked through approved channels; the lowest practical fare and standard accommodation apply
   unless approved otherwise.
3. Corporate cards are for business use only and reconciled monthly; personal use is prohibited.
4. Entertainment and gifts comply with the Gifts & Hospitality and Anti-Bribery policies.
5. Claims are approved by the employee's manager (one-up) within the DoA matrix.

## Prohibited
Alcohol in excess, fines, personal items, and expenses lacking documentation are not reimbursable.

## Roles & Responsibilities
- **Employees** submit accurate, substantiated claims promptly.
- **Managers** review and approve.
- **Finance** audits and processes reimbursements.

Contact: expenses@vicinity.example.com.
"""
},
{
 "id":"POL-047","doc_name":"fraud_control_policy","category":"Finance & Procurement",
 "title":"Fraud & Corruption Control Policy","eff":"2024-07-15","rev":"2026-07-15",
 "owner":"Risk & Finance","ver":"1.3",
 "body":"""
## Purpose
To prevent, detect, and respond to fraud and corruption affecting Vicinity, its people, owners, and
suppliers.

## Scope
All employees, contractors, and third parties, and all fraud and corruption risks (internal and external).

## Commitments
1. Vicinity has zero tolerance for fraud and corruption.
2. Controls include segregation of duties, approvals, supplier verification, reconciliations, and data
   analytics.
3. Suspected fraud must be reported (see Whistleblower Policy) and is investigated independently.
4. Confirmed fraud may result in dismissal, recovery action, and referral to police.
5. Fraud risk is assessed periodically and controls improved.

## Common Schemes Addressed
Payment-redirection (BEC), fake suppliers, false claims, theft of cash/stock, and conflicts of interest.

## Roles & Responsibilities
- **Risk** owns the fraud control framework and investigations.
- **Finance** maintains preventive controls.
- **All staff** report suspicions.

Contact: ethics@vicinity.example.com.
"""
},
{
 "id":"POL-048","doc_name":"cash_handling_policy","category":"Finance & Procurement",
 "title":"Cash Handling & Banking Policy","eff":"2024-08-15","rev":"2026-08-15",
 "owner":"Finance & Security","ver":"1.1",
 "body":"""
## Purpose
To manage centre cash (e.g., car park revenue, CML, vending, coin/charity collections) securely and
accurately.

## Scope
All cash received or handled at managed centres.

## Controls
1. Cash is counted by two people where practicable and reconciled to system records.
2. Cash is stored in secure safes; floats and holdings are kept to the minimum necessary.
3. Cash-in-transit is performed by a licensed carrier; staff do not transport significant cash.
4. Discrepancies are investigated and reported; persistent variances are escalated.
5. Access to safes and cash areas is restricted and logged.

## Security
Cash handling areas are covered by CCTV and access control. Robbery response is covered by the Security
and Wellbeing policies.

## Roles & Responsibilities
- **Centre Administration** performs counts and reconciliations.
- **Security** secures cash areas and manages CIT logistics.

Contact: finance@vicinity.example.com.
"""
},
{
 "id":"POL-049","doc_name":"tax_compliance_policy","category":"Finance & Procurement",
 "title":"Tax Compliance & GST Policy","eff":"2024-09-15","rev":"2026-09-15",
 "owner":"Finance / Tax","ver":"1.0",
 "body":"""
## Purpose
To ensure Vicinity and the entities it manages meet their tax obligations accurately and on time.

## Scope
All tax obligations relevant to the business and managed assets, including GST, income tax, FBT, payroll
tax, and land tax recoveries.

## Principles
1. Tax positions are based on the law and professional advice; aggressive or artificial schemes are not
   used.
2. GST is correctly applied, recorded, and reported; tax invoices meet legal requirements.
3. Returns and payments are lodged by statutory deadlines.
4. Land tax and other statutory outgoings are recovered from tenants only where the lease and law permit.
5. Records supporting tax positions are retained for the required periods.

## Advice & Governance
Material or uncertain tax matters are referred to the tax function and external advisers. The tax risk
position is reviewed periodically.

## Roles & Responsibilities
- **Tax/Finance** manages compliance, advice, and lodgements.
- **Centre Finance** ensures accurate transaction coding.

Contact: tax@vicinity.example.com.
"""
},
{
 "id":"POL-050","doc_name":"insurance_claims_finance_policy","category":"Finance & Procurement",
 "title":"Insurance Recoveries & Claims Finance Policy","eff":"2024-10-15","rev":"2026-10-15",
 "owner":"Risk & Finance","ver":"1.2",
 "body":"""
## Purpose
To manage the financial aspects of insurance — premium recovery, excess management, and claims proceeds —
across managed assets.

## Scope
All insurance arrangements for managed centres and the financial flows arising from claims.

## Requirements
1. Insurance premiums recoverable from tenants are recovered only as permitted by the lease and disclosed
   in outgoings.
2. Claims are lodged promptly with full documentation (see Risk & Insurance policies).
3. Excesses and uninsured costs are coded correctly and, where recoverable, charged to the responsible
   party.
4. Claim proceeds are applied to reinstatement or to the owner per the management agreement.
5. Subrogation and recovery from at-fault third parties are pursued where viable.

## Reporting
Open claims, reserves, and recoveries are reported to owners and the Risk Committee.

## Roles & Responsibilities
- **Risk** manages the insurance program and claims.
- **Finance** manages recoveries, coding, and proceeds.

Contact: insurance@vicinity.example.com.
"""
},
{
 "id":"POL-051","doc_name":"contractor_management_policy","category":"Vendor & Contractor",
 "title":"Contractor Engagement & Management Policy","eff":"2024-01-20","rev":"2026-01-20",
 "owner":"Procurement & Operations","ver":"2.2",
 "body":"""
## Purpose
To ensure contractors are competent, compliant, and managed throughout their engagement at Vicinity
centres.

## Scope
All contractors and subcontractors engaged to provide services or works at managed sites.

## Lifecycle
1. **Prequalification:** insurances, licences, WHS system, financial viability, and modern-slavery checks.
2. **Engagement:** written contract or purchase order with scope, KPIs, and safety requirements.
3. **Mobilisation:** site induction, SWMS review, and permits before work starts.
4. **Performance:** monitoring against KPIs, audits, and incident review.
5. **Offboarding:** access revoked, keys returned, and performance recorded for future selection.

## Compliance Verification
Insurances and licences are verified at onboarding and monitored for expiry. Lapsed compliance results in
suspension of access.

## Roles & Responsibilities
- **Procurement** owns prequalification and contracts.
- **Operations** manages day-to-day performance and safety.

Contact: contractors@vicinity.example.com.
"""
},
{
 "id":"POL-052","doc_name":"supplier_code_of_conduct_policy","category":"Vendor & Contractor",
 "title":"Supplier Code of Conduct Policy","eff":"2024-02-20","rev":"2026-02-20",
 "owner":"Procurement","ver":"1.4",
 "body":"""
## Purpose
To set the minimum standards of ethics, labour, safety, and environmental conduct expected of all
suppliers to Vicinity.

## Scope
All suppliers, contractors, and their subcontractors.

## Expectations
1. **Ethics:** comply with laws, compete fairly, and reject bribery, corruption, and facilitation
   payments.
2. **Labour & human rights:** no child, forced, or bonded labour; lawful wages and hours; freedom of
   association; safe accommodation where provided.
3. **Health & safety:** maintain safe systems of work and comply with WHS obligations.
4. **Environment:** minimise environmental harm and comply with environmental law.
5. **Confidentiality & privacy:** protect Vicinity and shopper information.

## Compliance & Audit
Suppliers must allow reasonable audits and cooperate with investigations. Breaches may lead to corrective
action or termination.

## Roles & Responsibilities
- **Procurement** communicates and enforces the Code.
- **Suppliers** cascade requirements to their subcontractors.

Contact: procurement@vicinity.example.com.
"""
},
{
 "id":"POL-053","doc_name":"modern_slavery_policy","category":"Vendor & Contractor",
 "title":"Modern Slavery & Human Rights Policy","eff":"2024-03-20","rev":"2026-03-20",
 "owner":"Risk & Procurement","ver":"1.2",
 "body":"""
## Purpose
To identify, assess, and address modern slavery risks in Vicinity's operations and supply chains, and to
meet modern slavery reporting obligations.

## Scope
Vicinity's operations and its suppliers, with focus on higher-risk categories such as cleaning, security,
catering, construction, and goods not for resale.

## Commitments
1. Assess modern slavery risk in procurement and supplier onboarding.
2. Require suppliers to comply with the Supplier Code of Conduct and applicable labour laws.
3. Provide grievance channels for workers and respond to credible reports.
4. Train relevant staff to recognise and escalate indicators of modern slavery.
5. Publish an annual modern slavery statement describing risks and actions.

## Remediation
Where modern slavery is identified, Vicinity prioritises remediation for affected workers over simply
terminating the supplier, where appropriate.

## Roles & Responsibilities
- **Risk** coordinates assessment and the annual statement.
- **Procurement** embeds requirements in sourcing.

Contact: humanrights@vicinity.example.com.
"""
},
{
 "id":"POL-054","doc_name":"cleaning_contract_management_policy","category":"Vendor & Contractor",
 "title":"Cleaning & Hygiene Services Management Policy","eff":"2024-04-20","rev":"2026-04-20",
 "owner":"Operations","ver":"1.3",
 "body":"""
## Purpose
To ensure contracted cleaning services deliver consistently high standards of cleanliness and hygiene
safely and sustainably.

## Scope
All contracted cleaning and hygiene services at managed centres.

## Standards
1. Cleaning specifications define tasks, frequencies, and outcome standards for each area type.
2. Restroom servicing, spill response, and food court cleaning meet defined response times.
3. Chemicals are managed under the Hazardous Chemicals Policy; safe systems protect cleaners and the
   public (wet-floor signage, equipment safety).
4. Cleaning staff are inducted, fairly engaged (modern slavery), and supervised.
5. Performance is measured by audits and shopper feedback; results drive corrective action.

## Sustainability
Water- and energy-efficient methods and lower-toxicity chemicals are preferred where effective.

## Roles & Responsibilities
- **Operations** manages the contract, audits, and standards.
- **Contractor** rosters trained staff and meets the specification.

Contact: operations@vicinity.example.com.
"""
},
{
 "id":"POL-055","doc_name":"security_contract_management_policy","category":"Vendor & Contractor",
 "title":"Security Services Contract Management Policy","eff":"2024-05-20","rev":"2026-05-20",
 "owner":"Security & Procurement","ver":"1.2",
 "body":"""
## Purpose
To govern the engagement and management of contracted security providers to deliver safe, lawful, and
professional services.

## Scope
All contracted security services at managed centres.

## Requirements
1. Providers and individual officers hold current security licences appropriate to their duties.
2. Post orders, rosters, and assignment instructions are documented and maintained.
3. Officers are vetted, inducted, and trained (customer service, de-escalation, first aid, emergency
   response).
4. Use-of-force, detention, and reporting comply with the Security Operations Policy and law.
5. Provider performance, incident response, and complaints are reviewed regularly.

## Subcontracting & Fair Work
Subcontracting requires approval; providers must pay lawful wages and comply with modern slavery and fair
work obligations.

## Roles & Responsibilities
- **Security** manages operational performance and post orders.
- **Procurement** manages the contract and compliance.

Contact: security@vicinity.example.com.
"""
},
{
 "id":"POL-056","doc_name":"vendor_insurance_compliance_policy","category":"Vendor & Contractor",
 "title":"Vendor Insurance & Licence Compliance Policy","eff":"2024-06-20","rev":"2026-06-20",
 "owner":"Risk & Procurement","ver":"1.1",
 "body":"""
## Purpose
To ensure all vendors and contractors hold and maintain the insurances and licences required for their
work at managed sites.

## Scope
All vendors and contractors engaged by Vicinity or working at managed centres.

## Requirements
1. Minimum insurances by risk category (public liability, workers' compensation, professional indemnity,
   plant) are defined and verified before work begins.
2. Certificates of currency and licences are stored centrally with expiry tracking.
3. Work is suspended automatically if cover or licences lapse.
4. High-risk works require evidence of specific cover (e.g., higher liability limits).
5. Periodic audits confirm ongoing compliance.

## Verification
Compliance is checked via a vendor management system; reminders are issued before expiry.

## Roles & Responsibilities
- **Procurement/Risk** maintain the compliance register and verify documents.
- **Operations** ensure non-compliant vendors do not work on site.

Contact: vendorcompliance@vicinity.example.com.
"""
},
{
 "id":"POL-057","doc_name":"conflict_of_interest_procurement_policy","category":"Vendor & Contractor",
 "title":"Conflicts of Interest in Procurement Policy","eff":"2024-07-20","rev":"2026-07-20",
 "owner":"Procurement & Risk","ver":"1.0",
 "body":"""
## Purpose
To identify and manage conflicts of interest in supplier selection and management so procurement decisions
are fair and defensible.

## Scope
All staff involved in sourcing, evaluating, awarding, or managing supplier contracts.

## Requirements
1. Actual, potential, and perceived conflicts (e.g., personal relationships, financial interests, prior
   employment) must be declared before involvement in a procurement.
2. Conflicted individuals are excluded from evaluation and decision-making for the affected sourcing.
3. Evaluation criteria and scoring are documented to demonstrate fairness.
4. Gifts and hospitality from suppliers follow the Gifts & Hospitality Policy and never influence
   decisions.
5. Declarations are recorded in a conflicts register and reviewed.

## Roles & Responsibilities
- **Staff** declare conflicts proactively.
- **Procurement/Risk** assess and manage declared conflicts.

Contact: procurement@vicinity.example.com.
"""
},
{
 "id":"POL-058","doc_name":"contractor_swms_permit_compliance_policy","category":"Vendor & Contractor",
 "title":"Contractor SWMS & Site Compliance Policy","eff":"2024-08-20","rev":"2026-08-20",
 "owner":"WHS & Operations","ver":"1.3",
 "body":"""
## Purpose
To ensure contractors plan and perform work safely on site through safe work method statements (SWMS),
permits, and supervision.

## Scope
All contractor works at managed centres, particularly high-risk construction work.

## Requirements
1. A SWMS is prepared, reviewed, and available on site for high-risk construction work before it starts.
2. Permits (hot works, confined space, height, isolation) are obtained per the After-Hours & Hot Works
   Permit Policy.
3. Work areas are isolated from the public with appropriate hoarding, signage, and dust/noise controls.
4. Plant and equipment are tested, tagged, and operated by competent persons.
5. Site reps verify compliance and may stop unsafe work.

## Stop-Work
Any person may stop work that poses an imminent risk. Work resumes only when the hazard is controlled.

## Roles & Responsibilities
- **Contractors** prepare SWMS and comply with permits.
- **Operations/WHS** verify and audit compliance.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-059","doc_name":"vendor_performance_review_policy","category":"Vendor & Contractor",
 "title":"Vendor Performance & Contract Review Policy","eff":"2024-09-20","rev":"2026-09-20",
 "owner":"Procurement","ver":"1.1",
 "body":"""
## Purpose
To manage supplier performance against contracted standards and drive continuous improvement and value.

## Scope
All material service contracts at managed centres and corporate level.

## Requirements
1. Key contracts have defined KPIs and service levels with measurement methods.
2. Performance is reviewed at scheduled business reviews; underperformance triggers corrective action
   plans.
3. Persistent underperformance may lead to penalties (where contracted), retendering, or termination.
4. Contract expiry and renewal are planned ahead to maintain competitive tension and continuity.
5. Lessons and supplier ratings inform future sourcing.

## Records
Performance data and review minutes are retained and inform the approved supplier list.

## Roles & Responsibilities
- **Contract Owners** manage day-to-day performance.
- **Procurement** governs reviews, renewals, and ratings.

Contact: procurement@vicinity.example.com.
"""
},
{
 "id":"POL-060","doc_name":"goods_not_for_resale_policy","category":"Vendor & Contractor",
 "title":"Goods & Services Not For Resale (GNFR) Policy","eff":"2024-10-20","rev":"2026-10-20",
 "owner":"Procurement","ver":"1.0",
 "body":"""
## Purpose
To manage the procurement of goods and services not for resale (GNFR) — such as consumables, equipment,
uniforms, and office supplies — efficiently and sustainably.

## Scope
All GNFR procurement across the business and managed centres.

## Principles
1. GNFR is sourced through approved suppliers and catalogues to control cost and quality.
2. Demand is aggregated where possible to gain value and reduce administrative effort.
3. Sustainability and modern-slavery criteria apply to GNFR categories.
4. Maverick (off-contract) spend is minimised and monitored.
5. Inventory of high-use consumables is managed to avoid waste and stockouts.

## Catalogues & Cards
Low-value GNFR may be purchased via approved cards or catalogues within the DoA matrix and reconciled
under the Expense Policy.

## Roles & Responsibilities
- **Procurement** maintains catalogues and approved suppliers.
- **Budget holders** purchase within policy and delegation.

Contact: procurement@vicinity.example.com.
"""
},
{
 "id":"POL-061","doc_name":"sustainability_policy","category":"Sustainability & ESG",
 "title":"Sustainability & Climate Policy","eff":"2024-01-10","rev":"2026-01-10",
 "owner":"Sustainability","ver":"2.0",
 "body":"""
## Purpose
To embed sustainability across the portfolio, reduce environmental impact, build resilience to climate
change, and create long-term value for owners and communities.

## Scope
All managed centres and corporate operations.

## Commitments
1. Pursue emissions reduction toward net-zero targets, including energy efficiency and renewable energy.
2. Improve building ratings (e.g., NABERS, Green Star) where applicable to each asset.
3. Reduce potable water use and improve waste diversion from landfill.
4. Assess and manage physical and transition climate risks in asset planning.
5. Report performance transparently in line with recognised frameworks.

## Implementation
Each centre has sustainability targets and an action plan integrated with capital and operating plans.
Performance is monitored through metering and analytics.

## Roles & Responsibilities
- **Sustainability** sets strategy, targets, and reporting.
- **Operations** delivers efficiency and waste outcomes on site.

Contact: sustainability@vicinity.example.com.
"""
},
{
 "id":"POL-062","doc_name":"energy_management_policy","category":"Sustainability & ESG",
 "title":"Energy Management Policy","eff":"2024-02-10","rev":"2026-02-10",
 "owner":"Sustainability & Operations","ver":"1.4",
 "body":"""
## Purpose
To manage energy use efficiently, reduce cost and emissions, and improve resilience across the portfolio.

## Scope
All base-building energy use at managed centres; tenant energy is addressed through engagement and green
leasing.

## Policy Statements
1. Energy is metered and monitored; consumption is benchmarked and anomalies investigated.
2. Efficiency measures (LED, HVAC optimisation, controls tuning) are prioritised in capital planning.
3. On-site renewables (e.g., solar PV) and renewable electricity procurement are pursued where viable.
4. Peak demand and tariffs are managed to reduce cost and grid stress.
5. Energy performance feeds building ratings and sustainability reporting.

## Tenant Engagement
Green lease provisions and tenant programs encourage efficient tenant energy use and data sharing.

## Roles & Responsibilities
- **Sustainability** sets targets and analyses performance.
- **Operations** implements efficiency and tuning.

Contact: sustainability@vicinity.example.com.
"""
},
{
 "id":"POL-063","doc_name":"waste_recycling_policy","category":"Sustainability & ESG",
 "title":"Waste & Recycling Management Policy","eff":"2024-03-10","rev":"2026-03-10",
 "owner":"Operations & Sustainability","ver":"1.6",
 "body":"""
## Purpose
To manage centre waste safely and to maximise diversion from landfill through recycling and resource
recovery.

## Scope
All waste generated in common areas and base-building operations, and the shared waste systems used by
tenants.

## Requirements
1. Waste streams are separated (general, cardboard, organics, glass, e-waste, etc.) using clear signage
   and infrastructure.
2. Tenants must use the centre's waste systems correctly and may be charged for contamination or excess.
3. Compactors, balers, and grease traps are maintained and serviced safely.
4. Hazardous and regulated wastes are disposed of through licensed contractors with documentation.
5. Waste and diversion data are tracked and reported.

## Food Court & Organics
Food tenants follow organics separation and grease management to reduce contamination and odours.

## Roles & Responsibilities
- **Operations** manages waste infrastructure and contractors.
- **Tenants** segregate waste correctly.

Contact: operations@vicinity.example.com.
"""
},
{
 "id":"POL-064","doc_name":"environmental_compliance_policy","category":"Sustainability & ESG",
 "title":"Environmental Compliance & Incident Policy","eff":"2024-04-10","rev":"2026-04-10",
 "owner":"Risk & Operations","ver":"1.2",
 "body":"""
## Purpose
To ensure centres comply with environmental laws and respond effectively to environmental incidents.

## Scope
All managed centres, covering trade waste, stormwater, air emissions, contaminated land, and refrigerant
and ozone-depleting substances.

## Requirements
1. Relevant environmental licences, permits, and trade-waste agreements are maintained and complied with.
2. Stormwater is protected from contamination; spills are contained and prevented from entering drains.
3. Refrigerants are handled by licensed technicians; leaks are minimised and logged.
4. Environmental incidents are reported internally and to regulators where required.
5. Contaminated land and legacy issues are managed with specialist advice.

## Incident Response
Spills and discharges are contained using spill kits, cleaned, and reported. Significant incidents
activate emergency and continuity procedures.

## Roles & Responsibilities
- **Operations** maintains controls and responds to incidents.
- **Risk** manages licences and regulator notifications.

Contact: environment@vicinity.example.com.
"""
},
{
 "id":"POL-065","doc_name":"accessibility_inclusion_policy","category":"Sustainability & ESG",
 "title":"Accessibility & Inclusion Policy","eff":"2024-05-10","rev":"2026-05-10",
 "owner":"Operations & Marketing","ver":"1.1",
 "body":"""
## Purpose
To make centres welcoming and accessible to people of all abilities, ages, and backgrounds, meeting
disability access obligations and going beyond minimum compliance.

## Scope
All common areas, amenities, parking, and services at managed centres.

## Commitments
1. Maintain compliant accessible paths of travel, parking, amenities, lifts, and signage.
2. Provide parents' rooms, accessible toilets, and, where feasible, adult change facilities and quiet/low
   sensory experiences.
3. Ensure wayfinding and digital information are accessible.
4. Train staff to assist people with disability respectfully.
5. Consult with people with disability and advocacy groups on improvements.

## Assistance Animals
Assistance animals are welcome; staff do not require shoppers to prove an animal's status beyond what the
law permits.

## Roles & Responsibilities
- **Operations** maintains accessible infrastructure.
- **Marketing/Centre Management** deliver inclusive services and communications.

Contact: accessibility@vicinity.example.com.
"""
},
{
 "id":"POL-066","doc_name":"marketing_advertising_policy","category":"Marketing & Common Area",
 "title":"Centre Marketing & Advertising Standards Policy","eff":"2024-06-10","rev":"2026-06-10",
 "owner":"Marketing","ver":"1.5",
 "body":"""
## Purpose
To ensure centre marketing and advertising are effective, lawful, on-brand, and respectful of the
community.

## Scope
All centre marketing campaigns, advertising, signage, and digital content, and the use of the marketing
levy/fund.

## Standards
1. Marketing complies with consumer law (no misleading or deceptive conduct) and advertising codes.
2. Campaigns are inclusive and avoid offensive, discriminatory, or unsafe content.
3. Marketing fund expenditure is used for the promotion of the centre and reported to contributing
   tenants where required.
4. Sponsorships and partnerships align with brand values and are documented.
5. Competitions and promotions comply with trade-promotion and permit requirements.

## Tenant Participation
Tenant promotions in common areas follow the Casual Mall Leasing and Signage policies.

## Roles & Responsibilities
- **Marketing** plans and approves campaigns and manages the fund.
- **Centre Management** oversees in-centre execution.

Contact: marketing@vicinity.example.com.
"""
},
{
 "id":"POL-067","doc_name":"social_media_policy","category":"Marketing & Common Area",
 "title":"Social Media & Brand Voice Policy","eff":"2024-07-10","rev":"2026-07-10",
 "owner":"Marketing & Communications","ver":"1.2",
 "body":"""
## Purpose
To manage Vicinity and centre social media professionally, protecting brand and reputation and engaging
communities positively.

## Scope
All official Vicinity and centre social media accounts and employee conduct relating to the company
online.

## Rules
1. Only authorised people post on official accounts, following brand voice and approval workflows.
2. Content is accurate, respectful, and compliant with consumer and privacy law.
3. Community management responds to queries and complaints promptly and escalates issues (safety,
   incidents, media) appropriately.
4. Personal posts must not present personal views as the company's; employees must not disclose
   confidential information.
5. User-generated content and shopper images are used only with appropriate rights and privacy
   consideration.

## Crisis
During incidents, social media is coordinated with the Communications and Crisis Management policies.

## Roles & Responsibilities
- **Marketing/Comms** manage accounts and approvals.
- **All staff** follow personal-use guidelines.

Contact: comms@vicinity.example.com.
"""
},
{
 "id":"POL-068","doc_name":"community_engagement_policy","category":"Sustainability & ESG",
 "title":"Community Engagement & Sponsorship Policy","eff":"2024-08-10","rev":"2026-08-10",
 "owner":"Marketing & Sustainability","ver":"1.0",
 "body":"""
## Purpose
To strengthen the role of centres as community hubs through positive engagement, partnerships, and
sponsorships.

## Scope
All community programs, charitable activity, space donations, and sponsorships at managed centres.

## Principles
1. Community partners and charities are selected fairly and align with brand and community values.
2. Free or discounted space for community use is provided within an approved framework and does not
   compromise safety or trade.
3. Fundraising and collections in centre are approved, time-limited, and managed under CML rules.
4. Political and religious activities are managed even-handedly within clear guidelines.
5. Local employment and supplier opportunities are encouraged.

## Approvals
Sponsorships and donations follow the DoA matrix and are recorded for transparency.

## Roles & Responsibilities
- **Marketing** manages community programs and sponsorships.
- **Centre Management** coordinates in-centre delivery.

Contact: community@vicinity.example.com.
"""
},
{
 "id":"POL-069","doc_name":"digital_screens_wayfinding_policy","category":"Marketing & Common Area",
 "title":"Digital Screens & Wayfinding Policy","eff":"2024-09-10","rev":"2026-09-10",
 "owner":"Marketing & Operations","ver":"1.0",
 "body":"""
## Purpose
To manage digital signage, directories, and wayfinding so shoppers can navigate easily and content is
safe, accurate, and compliant.

## Scope
All digital screens, interactive directories, and wayfinding signage in common areas.

## Standards
1. Content is accurate, current, accessible, and complies with advertising and consumer law.
2. Brightness, motion, and audio levels are set to avoid hazards (e.g., glare, photosensitive triggers)
   and nuisance.
3. Emergency messaging can override commercial content when required.
4. Interactive directories meet accessibility standards and protect any personal data collected.
5. Screens are maintained; faulty screens are repaired or switched off.

## Data & Privacy
Any audience-measurement or analytics on screens complies with the Privacy Policy and avoids capturing
identifiable individuals without basis.

## Roles & Responsibilities
- **Marketing** manages content and scheduling.
- **Operations** maintains hardware and emergency override.

Contact: marketing@vicinity.example.com.
"""
},
{
 "id":"POL-070","doc_name":"green_lease_policy","category":"Sustainability & ESG",
 "title":"Green Lease & Tenant Sustainability Policy","eff":"2024-10-10","rev":"2026-10-10",
 "owner":"Sustainability & Leasing","ver":"1.0",
 "body":"""
## Purpose
To partner with tenants to improve the environmental performance of centres through green lease provisions
and collaboration.

## Scope
New leases and renewals across the portfolio, and tenant fit-outs and operations.

## Provisions
1. Green lease clauses cover energy and water data sharing, efficient fit-out standards, and cooperation
   on sustainability initiatives.
2. Fit-out guidelines promote efficient lighting, HVAC, and materials (see Tenant Fit-Out Policy).
3. Shared environmental targets and tenant engagement programs are established at suitable centres.
4. Tenant utility data, where shared, is protected and used for performance improvement.
5. Recognition programs reward high-performing tenants.

## Collaboration
A building management committee or equivalent forum supports joint initiatives at major assets.

## Roles & Responsibilities
- **Leasing** incorporates green clauses.
- **Sustainability** runs programs and tracks outcomes.

Contact: sustainability@vicinity.example.com.
"""
},
{
 "id":"POL-071","doc_name":"code_of_conduct_policy","category":"People & Conduct",
 "title":"Code of Conduct Policy","eff":"2024-01-05","rev":"2026-01-05",
 "owner":"People & Culture","ver":"3.0",
 "body":"""
## Purpose
To set the standards of behaviour expected of everyone at Vicinity, reflecting our values and our
obligations to colleagues, tenants, owners, shoppers, and the community.

## Scope
All employees, contractors, and directors.

## Expected Behaviours
1. Act with honesty, integrity, and fairness.
2. Treat others with respect; no bullying, harassment, or discrimination.
3. Comply with laws, policies, and lawful directions.
4. Protect company and customer information and assets.
5. Avoid and declare conflicts of interest; do not misuse position for personal gain.
6. Use company systems, funds, and resources responsibly.

## Speaking Up
Employees must report suspected breaches of this Code (see Whistleblower and Grievance policies).
Retaliation against people who report in good faith is prohibited.

## Consequences
Breaches may result in disciplinary action up to termination, and referral to authorities where relevant.

## Roles & Responsibilities
- **All staff** uphold the Code.
- **Managers** model and reinforce expected behaviours.
- **People & Culture** advise and manage breaches.

Contact: peopleandculture@vicinity.example.com.
"""
},
{
 "id":"POL-072","doc_name":"equal_opportunity_antidiscrimination_policy","category":"People & Conduct",
 "title":"Equal Opportunity, Anti-Discrimination & Bullying Policy","eff":"2024-02-05","rev":"2026-02-05",
 "owner":"People & Culture","ver":"2.1",
 "body":"""
## Purpose
To provide a workplace free from discrimination, harassment, sexual harassment, victimisation, and
bullying, and to promote equal opportunity.

## Scope
All employees and contractors, in the workplace and at work-related events, including online conduct.

## Standards
1. Discrimination based on protected attributes (e.g., sex, age, race, disability, religion, sexual
   orientation) is prohibited.
2. Sexual harassment is unlawful and will not be tolerated; the company takes a positive duty to prevent
   it.
3. Bullying (repeated unreasonable behaviour creating a risk to health and safety) is prohibited.
4. Complaints are handled promptly, fairly, and confidentially.
5. Victimisation of complainants or witnesses is prohibited.

## Reporting & Support
Concerns can be raised with a manager, People & Culture, or via the Grievance Policy. Support, including
EAP, is available.

## Roles & Responsibilities
- **All staff** maintain respectful conduct.
- **Managers** act on issues they observe or that are reported.
- **People & Culture** manage complaints and prevention.

Contact: peopleandculture@vicinity.example.com.
"""
},
{
 "id":"POL-073","doc_name":"recruitment_policy","category":"People & Conduct",
 "title":"Recruitment & Selection Policy","eff":"2024-03-05","rev":"2026-03-05",
 "owner":"People & Culture","ver":"1.6",
 "body":"""
## Purpose
To attract and select the best candidates through a fair, consistent, and merit-based process.

## Scope
All recruitment for permanent, fixed-term, and casual roles.

## Principles
1. Selection is based on merit against role requirements, free from discrimination.
2. Roles are approved and budgeted before advertising; position descriptions are current.
3. Pre-employment checks (right to work, references, and where relevant police/working-with-children and
   licence checks) are completed before commencement.
4. Conflicts of interest in hiring (e.g., relatives) must be declared and managed.
5. Candidate data is handled under the Privacy Policy.

## Diversity
Inclusive sourcing and selection practices support workforce diversity. Reasonable adjustments are
provided in the process on request.

## Roles & Responsibilities
- **Hiring Managers** define roles and select on merit.
- **People & Culture** manage the process and compliance checks.

Contact: recruitment@vicinity.example.com.
"""
},
{
 "id":"POL-074","doc_name":"onboarding_probation_policy","category":"People & Conduct",
 "title":"Employee Onboarding & Probation Policy","eff":"2024-04-05","rev":"2026-04-05",
 "owner":"People & Culture","ver":"1.2",
 "body":"""
## Purpose
To set new employees up for success through structured onboarding and to manage probation fairly.

## Scope
All new employees and internal transfers.

## Onboarding
1. New starters complete induction covering values, code of conduct, WHS, and systems access before or on
   day one.
2. Role-specific training and a clear set of early objectives are provided.
3. Mandatory compliance training is completed within defined timeframes.

## Probation
1. Probation periods are set in the employment contract and used to assess suitability.
2. Regular check-ins provide feedback; performance concerns are raised early and supported.
3. Decisions to confirm, extend, or end probation are fair, documented, and follow employment law.

## Roles & Responsibilities
- **Managers** deliver onboarding and manage probation.
- **People & Culture** provide tools and ensure compliance.

Contact: peopleandculture@vicinity.example.com.
"""
},
{
 "id":"POL-075","doc_name":"performance_development_policy","category":"People & Conduct",
 "title":"Performance & Development Policy","eff":"2024-05-05","rev":"2026-05-05",
 "owner":"People & Culture","ver":"1.4",
 "body":"""
## Purpose
To support high performance and growth through clear expectations, regular feedback, and development.

## Scope
All employees.

## Approach
1. Employees have clear goals aligned to team and company objectives.
2. Regular conversations and at least an annual review provide feedback on performance and development.
3. Development plans support capability building and career growth.
4. Underperformance is addressed constructively through a fair performance improvement process.
5. Reward and recognition are linked to performance and values within remuneration frameworks.

## Fair Process
Performance management is evidence-based, documented, and provides a genuine opportunity to improve, with
support.

## Roles & Responsibilities
- **Managers** set goals, give feedback, and support development.
- **Employees** engage in goal-setting and development.
- **People & Culture** provide frameworks and advice.

Contact: peopleandculture@vicinity.example.com.
"""
},
{
 "id":"POL-076","doc_name":"leave_flexible_work_policy","category":"People & Conduct",
 "title":"Leave & Flexible Work Policy","eff":"2024-06-05","rev":"2026-06-05",
 "owner":"People & Culture","ver":"1.3",
 "body":"""
## Purpose
To support employees to balance work and life through fair leave entitlements and flexible work options.

## Scope
All employees, in accordance with their entitlements and applicable employment law/instruments.

## Leave
1. Annual, personal/carer's, compassionate, parental, long service, and other leave are provided per law
   and policy.
2. Leave is applied for and approved in advance where possible and recorded accurately.
3. Evidence (e.g., medical certificates) is required as set by law and policy.

## Flexible Work
1. Flexible arrangements (hours, location, part-time) are considered fairly, balancing role requirements
   and operational needs of a centre-based business.
2. Requests follow the applicable process and are documented.

## Roles & Responsibilities
- **Managers** approve leave and flexibility fairly and consistently.
- **Employees** plan leave and meet evidence requirements.
- **People & Culture** advise on entitlements.

Contact: peopleandculture@vicinity.example.com.
"""
},
{
 "id":"POL-077","doc_name":"drug_alcohol_policy","category":"People & Conduct",
 "title":"Drug & Alcohol Policy","eff":"2024-07-05","rev":"2026-07-05",
 "owner":"People & Culture / WHS","ver":"1.2",
 "body":"""
## Purpose
To maintain a safe workplace by managing the risks associated with alcohol and other drugs (AOD).

## Scope
All employees and contractors while at work or representing Vicinity, including on managed sites.

## Rules
1. Attending work impaired by alcohol or drugs is prohibited; safety-critical work has zero tolerance.
2. Possession, use, or supply of illicit drugs at work is prohibited.
3. Prescription medications that may impair must be disclosed where they affect safety.
4. Alcohol at approved work functions must be consumed responsibly; safe transport is supported.
5. Testing may occur where permitted by law/instrument, especially after incidents or on reasonable
   suspicion.

## Support
Employees are encouraged to seek help; EAP and support pathways are available. A genuine help-seeking
approach is balanced with safety obligations.

## Roles & Responsibilities
- **Managers** act on impairment concerns to protect safety.
- **People & Culture/WHS** manage testing, support, and consequences.

Contact: whs@vicinity.example.com.
"""
},
{
 "id":"POL-078","doc_name":"grievance_disciplinary_policy","category":"People & Conduct",
 "title":"Grievance & Disciplinary Policy","eff":"2024-08-05","rev":"2026-08-05",
 "owner":"People & Culture","ver":"1.5",
 "body":"""
## Purpose
To resolve workplace grievances fairly and to manage misconduct and performance issues through a just and
consistent process.

## Scope
All employees.

## Grievances
1. Employees are encouraged to raise concerns early and directly where safe to do so.
2. Grievances are handled confidentially, impartially, and promptly, with support available.
3. Outcomes and any actions are communicated appropriately.

## Disciplinary Process
1. Allegations of misconduct are investigated fairly, giving the employee a chance to respond (procedural
   fairness).
2. Outcomes range from coaching and warnings to termination, proportionate to the conduct.
3. Serious misconduct may warrant summary dismissal following proper process.
4. Records are kept confidentially.

## Roles & Responsibilities
- **Managers** address issues and follow due process.
- **People & Culture** advise, ensure fairness, and maintain records.

Contact: peopleandculture@vicinity.example.com.
"""
},
{
 "id":"POL-079","doc_name":"training_compliance_policy","category":"People & Conduct",
 "title":"Mandatory Training & Compliance Learning Policy","eff":"2024-09-05","rev":"2026-09-05",
 "owner":"People & Culture","ver":"1.1",
 "body":"""
## Purpose
To ensure all workers complete the training required to work safely, lawfully, and effectively.

## Scope
All employees and, where applicable, contractors.

## Requirements
1. Mandatory modules (e.g., code of conduct, WHS, anti-bribery, privacy, anti-discrimination, modern
   slavery awareness) are completed within set timeframes and refreshed periodically.
2. Role-specific training and licences (e.g., first aid, fire warden, security licence) are kept current.
3. Completion is tracked; overdue training is escalated to managers.
4. Training records are retained and auditable.

## Non-Completion
Access to certain duties or systems may be restricted until required training is completed.

## Roles & Responsibilities
- **People & Culture** maintain the curriculum and tracking.
- **Managers** ensure their teams complete training on time.

Contact: learning@vicinity.example.com.
"""
},
{
 "id":"POL-080","doc_name":"workplace_surveillance_policy","category":"People & Conduct",
 "title":"Workplace Surveillance & Monitoring Policy","eff":"2024-10-05","rev":"2026-10-05",
 "owner":"People & Culture / IT","ver":"1.0",
 "body":"""
## Purpose
To inform workers about workplace surveillance and to ensure monitoring is lawful, proportionate, and
respectful of privacy.

## Scope
All Vicinity workers and the surveillance of computers, email, internet, location, and (for safety/
security) CCTV in workplaces.

## Principles
1. Surveillance is conducted only with appropriate notice as required by workplace surveillance law.
2. Computer and communications monitoring is for security, compliance, and legitimate business purposes —
   not covert performance monitoring outside notified arrangements.
3. CCTV in workplaces is governed by the CCTV Policy and is not used to covertly monitor employees.
4. Location data from vehicles or devices is collected for safety and operational purposes with notice.
5. Personal information from monitoring is handled under the Privacy Policy and access is restricted.

## Roles & Responsibilities
- **IT** administers technical monitoring within policy.
- **People & Culture** manage notice and any employment use.

Contact: privacy@vicinity.example.com.
"""
},
{
 "id":"POL-081","doc_name":"risk_management_policy","category":"Compliance, Legal & Risk",
 "title":"Enterprise Risk Management Policy","eff":"2024-01-25","rev":"2026-01-25",
 "owner":"Risk","ver":"2.0",
 "body":"""
## Purpose
To manage risk consistently across Vicinity so that risks to people, assets, owners, reputation, and
strategy are identified, assessed, and treated within appetite.

## Scope
All business activities, managed centres, and corporate functions.

## Framework
1. Risk management aligns to a recognised standard (e.g., ISO 31000) and a defined risk appetite.
2. Risks are identified, assessed (likelihood x consequence), treated, and monitored in risk registers.
3. Key risks and controls are reviewed regularly; control effectiveness is tested.
4. Material risks and incidents are escalated to executive and Board Risk Committee.
5. Risk is considered in decisions, projects, and investments.

## Three Lines
Operational management owns risk (1st line); Risk & Compliance provide oversight (2nd line); Internal
Audit provides assurance (3rd line).

## Roles & Responsibilities
- **Risk** maintains the framework and reporting.
- **Managers** own and treat risks in their area.

Contact: risk@vicinity.example.com.
"""
},
{
 "id":"POL-082","doc_name":"anti_bribery_corruption_policy","category":"Compliance, Legal & Risk",
 "title":"Anti-Bribery & Corruption Policy","eff":"2024-02-25","rev":"2026-02-25",
 "owner":"Risk & Legal","ver":"1.4",
 "body":"""
## Purpose
To prohibit bribery and corruption in all forms and to comply with applicable anti-bribery laws.

## Scope
All employees, directors, contractors, and third parties acting for Vicinity.

## Prohibitions
1. Offering, giving, requesting, or accepting a bribe or improper advantage is prohibited.
2. Facilitation payments are prohibited.
3. Gifts and hospitality must comply with the Gifts & Hospitality Policy and never improperly influence
   decisions.
4. Political donations require executive approval and transparency.
5. Third parties must be subject to due diligence and contractual anti-bribery commitments.

## Red Flags & Reporting
Unusual payment requests, agents demanding high commissions, or requests for cash must be escalated.
Concerns are reported under the Whistleblower Policy.

## Roles & Responsibilities
- **Risk/Legal** own the program and due diligence.
- **All staff** comply and report concerns.

Contact: ethics@vicinity.example.com.
"""
},
{
 "id":"POL-083","doc_name":"gifts_hospitality_policy","category":"Compliance, Legal & Risk",
 "title":"Gifts, Hospitality & Conflicts Policy","eff":"2024-03-25","rev":"2026-03-25",
 "owner":"Risk","ver":"1.2",
 "body":"""
## Purpose
To manage gifts, benefits, and hospitality so they do not create actual or perceived conflicts of
interest or improper influence.

## Scope
All employees and contractors.

## Rules
1. Gifts and hospitality must be modest, infrequent, and never given or received to influence a decision.
2. Cash or cash-equivalents must never be accepted.
3. Gifts/hospitality above a defined value must be declared in the gifts register and may require
   approval or be declined.
4. Conflicts of interest (including secondary employment and personal relationships) must be declared and
   managed.
5. During tenders, gifts and hospitality from bidders must be declined.

## Register
The gifts and conflicts registers are reviewed periodically for patterns and risks.

## Roles & Responsibilities
- **Employees** declare gifts, hospitality, and conflicts.
- **Risk** maintains registers and advises.

Contact: ethics@vicinity.example.com.
"""
},
{
 "id":"POL-084","doc_name":"whistleblower_policy","category":"Compliance, Legal & Risk",
 "title":"Whistleblower Policy","eff":"2024-04-25","rev":"2026-04-25",
 "owner":"Legal & Risk","ver":"1.3",
 "body":"""
## Purpose
To encourage and protect people who report serious wrongdoing, in line with whistleblower protection laws.

## Scope
Eligible whistleblowers including current and former employees, contractors, suppliers, and their
relatives.

## Reportable Conduct
Misconduct or an improper state of affairs, including illegal conduct, fraud, corruption, serious safety
risks, and breaches of law — but generally not personal work-related grievances.

## Protections
1. Disclosures can be made to eligible recipients or anonymously through the external whistleblower
   service.
2. The identity of a discloser is protected and confidentiality maintained.
3. Victimisation or detriment against a discloser is strictly prohibited and itself reportable.
4. Disclosures are handled and investigated independently and fairly.

## How to Report
Reports can be made to Whistleblower Protection Officers or via the confidential hotline/portal.

## Roles & Responsibilities
- **Legal/Risk** administer the program and investigations.
- **Everyone** must not victimise disclosers.

Contact: whistleblower@vicinity.example.com.
"""
},
{
 "id":"POL-085","doc_name":"competition_consumer_law_policy","category":"Compliance, Legal & Risk",
 "title":"Competition & Consumer Law Compliance Policy","eff":"2024-05-25","rev":"2026-05-25",
 "owner":"Legal","ver":"1.1",
 "body":"""
## Purpose
To ensure Vicinity complies with competition and consumer protection laws in its leasing, marketing, and
dealings.

## Scope
All commercial dealings, including leasing negotiations, marketing, and supplier and tenant interactions.

## Key Rules
1. No misleading or deceptive conduct or false representations to tenants, shoppers, or suppliers.
2. No anti-competitive arrangements (e.g., cartel conduct, illegal exclusivity) with competitors or
   suppliers.
3. Unfair contract terms in standard-form small-business and consumer contracts are avoided.
4. Retail leasing legislation requirements (disclosure, prohibited terms) are met.
5. Advertising and promotions are accurate and substantiated.

## Guidance & Escalation
Legal advice is sought for novel arrangements, exclusivities, and any conduct that could raise
competition concerns.

## Roles & Responsibilities
- **Legal** advises and trains on compliance.
- **Leasing/Marketing** apply the rules in practice.

Contact: legal@vicinity.example.com.
"""
},
{
 "id":"POL-086","doc_name":"contract_management_legal_policy","category":"Compliance, Legal & Risk",
 "title":"Contract Management & Legal Review Policy","eff":"2024-06-25","rev":"2026-06-25",
 "owner":"Legal","ver":"1.2",
 "body":"""
## Purpose
To ensure contracts are properly reviewed, approved, executed, and managed to protect Vicinity and the
owners it represents.

## Scope
All contracts, deeds, leases, and binding commitments.

## Requirements
1. Contracts use approved templates where available; deviations and non-standard terms require Legal
   review.
2. Execution follows the Delegations of Authority and proper signing protocols (including electronic
   signing controls).
3. Key obligations, terms, and expiries are recorded and managed in a contract register.
4. Indemnities, liability caps, insurance, and termination rights are reviewed against risk appetite.
5. Originals/executed copies are stored securely.

## Disputes & Variations
Variations are documented; potential disputes are escalated to Legal early.

## Roles & Responsibilities
- **Legal** reviews and advises on non-standard terms.
- **Contract Owners** manage obligations and the register.

Contact: legal@vicinity.example.com.
"""
},
{
 "id":"POL-087","doc_name":"records_management_policy","category":"Compliance, Legal & Risk",
 "title":"Records & Information Management Policy","eff":"2024-07-25","rev":"2026-07-25",
 "owner":"Legal & IT","ver":"1.1",
 "body":"""
## Purpose
To manage records and information as a business asset — captured, stored, retained, and disposed of
appropriately and lawfully.

## Scope
All business records in any format created or received by Vicinity, including for managed assets.

## Requirements
1. Records are captured in approved systems and classified for sensitivity.
2. Retention follows the records retention schedule and legal requirements (e.g., leases 7+ years, trust
   records, tax records).
3. Disposal of records occurs only per the schedule and is documented; disposal is suspended for records
   under legal hold.
4. Information security and privacy controls protect records.
5. Vital records are identified and protected for business continuity.

## Legal Holds
On notice of actual or anticipated litigation or investigation, relevant records must be preserved and
not destroyed.

## Roles & Responsibilities
- **Legal** sets retention and manages legal holds.
- **IT** provides compliant storage and disposal.

Contact: records@vicinity.example.com.
"""
},
{
 "id":"POL-088","doc_name":"delegated_compliance_obligations_policy","category":"Compliance, Legal & Risk",
 "title":"Regulatory Compliance Obligations Policy","eff":"2024-08-25","rev":"2026-08-25",
 "owner":"Risk & Compliance","ver":"1.0",
 "body":"""
## Purpose
To ensure Vicinity systematically identifies and meets its regulatory and licensing obligations across
jurisdictions.

## Scope
All regulatory obligations applicable to the business and managed centres (building, fire, health,
environmental, real estate agency, work safety, privacy, and consumer law).

## Requirements
1. A compliance obligations register maps key obligations to owners and controls.
2. Licences, registrations, and statutory certifications are tracked with renewal reminders.
3. Compliance is monitored through self-assessment, audits, and incident review.
4. Regulatory changes are monitored and impacts assessed and implemented.
5. Breaches are reported, remediated, and notified to regulators where required.

## Assurance
Compliance performance is reported to the Risk Committee; significant breaches are escalated promptly.

## Roles & Responsibilities
- **Compliance** maintains the register and monitors changes.
- **Obligation owners** ensure their obligations are met.

Contact: compliance@vicinity.example.com.
"""
},
{
 "id":"POL-089","doc_name":"insurance_risk_policy","category":"Compliance, Legal & Risk",
 "title":"Insurance & Risk Transfer Policy","eff":"2024-09-25","rev":"2026-09-25",
 "owner":"Risk","ver":"1.3",
 "body":"""
## Purpose
To maintain appropriate insurance and risk-transfer arrangements to protect people, assets, and owners
against insurable losses.

## Scope
All managed centres and corporate operations.

## Requirements
1. Insurance programs (industrial special risks/property, public and products liability, business
   interruption, and others as relevant) are maintained at appropriate limits.
2. Tenants and contractors must hold required insurances and provide certificates of currency.
3. Risk surveys and recommendations from insurers are actioned within agreed timeframes.
4. Claims are reported promptly with documentation; the Claims Finance Policy governs financial flows.
5. Self-insured retentions and excesses are managed and budgeted.

## Owner Arrangements
Where owners place their own insurance, Vicinity verifies cover and interfaces for claims per the
management agreement.

## Roles & Responsibilities
- **Risk** manages the program, brokers, and claims.
- **Operations** implements risk recommendations.

Contact: insurance@vicinity.example.com.
"""
},
{
 "id":"POL-090","doc_name":"internal_audit_policy","category":"Compliance, Legal & Risk",
 "title":"Internal Audit & Assurance Policy","eff":"2024-10-25","rev":"2026-10-25",
 "owner":"Internal Audit","ver":"1.0",
 "body":"""
## Purpose
To provide independent, objective assurance over the effectiveness of governance, risk management, and
controls.

## Scope
All business activities, processes, systems, and managed-centre operations.

## Principles
1. Internal Audit is independent, reporting functionally to the Audit & Risk Committee.
2. A risk-based audit plan is approved annually and updated as risks change.
3. Audits assess control design and effectiveness and provide rated findings and recommendations.
4. Management agrees actions with owners and due dates; implementation is tracked to completion.
5. Audit access to people, records, and systems is unrestricted.

## Reporting
Findings and the status of remediation are reported to the Audit & Risk Committee.

## Roles & Responsibilities
- **Internal Audit** plans and conducts audits.
- **Management** implements agreed actions on time.

Contact: internalaudit@vicinity.example.com.
"""
},
{
 "id":"POL-091","doc_name":"privacy_policy","category":"Data, Privacy & IT",
 "title":"Privacy Policy","eff":"2024-01-30","rev":"2026-01-30",
 "owner":"Privacy Officer / Legal","ver":"2.2",
 "body":"""
## Purpose
To describe how Vicinity collects, uses, discloses, and protects personal information, in compliance with
applicable privacy laws and the privacy principles.

## Scope
Personal information of shoppers, tenants, suppliers, employees, and visitors, collected through centres,
car parks, apps, websites, loyalty programs, CCTV, and Wi-Fi.

## Principles
1. **Collection:** only collect personal information that is reasonably necessary, by lawful and fair
   means, with notice.
2. **Use & disclosure:** use information for the purposes collected or related purposes, or with consent
   or legal authority.
3. **Security:** protect information with appropriate safeguards and restrict access.
4. **Access & correction:** individuals may request access to and correction of their information.
5. **Retention:** retain only as long as needed, then securely destroy or de-identify.

## Specific Collections
- **CCTV** for safety and security (see CCTV Policy).
- **Car park** licence-plate and payment data for access and billing.
- **Marketing/loyalty** data used with consent; opt-out available.

## Data Breaches
Eligible data breaches are assessed and notified to affected individuals and the regulator as required
(see Cyber Incident Response Policy).

## Contact
Privacy Officer: privacy@vicinity.example.com.
"""
},
{
 "id":"POL-092","doc_name":"information_security_policy","category":"Data, Privacy & IT",
 "title":"Information Security & Data Governance Policy","eff":"2024-02-28","rev":"2026-02-28",
 "owner":"IT / Information Security","ver":"1.7",
 "body":"""
## Purpose
To protect the confidentiality, integrity, and availability of Vicinity's information and systems and to
govern data as an asset.

## Scope
All information, systems, devices, and users (employees, contractors, third parties).

## Controls
1. Information is classified and handled according to sensitivity.
2. Access is role-based and least-privilege; multi-factor authentication is required for remote and
   privileged access.
3. Systems are patched, hardened, logged, and monitored; backups are maintained and tested.
4. Data is encrypted in transit and, where appropriate, at rest.
5. Third-party and cloud services are assessed for security before use.

## Data Governance
Data ownership, quality, and lifecycle are defined; personal data is handled under the Privacy Policy.

## Roles & Responsibilities
- **Information Security** sets standards and monitors threats.
- **All users** protect credentials and report incidents.

Contact: infosec@vicinity.example.com.
"""
},
{
 "id":"POL-093","doc_name":"acceptable_use_it_policy","category":"Data, Privacy & IT",
 "title":"Acceptable Use of Technology Policy","eff":"2024-03-28","rev":"2026-03-28",
 "owner":"IT","ver":"1.5",
 "body":"""
## Purpose
To set the rules for appropriate use of Vicinity's IT systems, devices, networks, and data.

## Scope
All users of Vicinity technology, including email, internet, devices, and applications.

## Rules
1. Systems are primarily for business use; limited reasonable personal use is permitted if it does not
   breach policy or affect work.
2. Users must protect credentials, lock devices, and not share accounts.
3. Prohibited: accessing illegal or offensive material, unauthorised software, circumventing security,
   or misusing data.
4. Company data must not be sent to personal accounts or unapproved cloud/storage services.
5. Lost or stolen devices and suspected compromises must be reported immediately.

## Monitoring
Use of systems may be monitored consistent with the Workplace Surveillance Policy.

## Roles & Responsibilities
- **Users** comply with acceptable use.
- **IT** provisions, secures, and supports systems.

Contact: ithelpdesk@vicinity.example.com.
"""
},
{
 "id":"POL-094","doc_name":"cyber_incident_response_policy","category":"Data, Privacy & IT",
 "title":"Cyber Incident & Data Breach Response Policy","eff":"2024-04-28","rev":"2026-04-28",
 "owner":"Information Security / Risk","ver":"1.3",
 "body":"""
## Purpose
To detect, respond to, and recover from cyber incidents and data breaches quickly, limiting harm and
meeting notification obligations.

## Scope
All cyber incidents and personal data breaches affecting Vicinity systems and information.

## Response
1. Suspected incidents are reported immediately to IT/Information Security and triaged by severity.
2. The incident response team contains, eradicates, and recovers, preserving evidence.
3. Eligible data breaches are assessed for likely serious harm and notified to affected individuals and
   the regulator within required timeframes.
4. Major incidents activate the Crisis Management and Business Continuity plans.
5. Post-incident reviews identify root cause and improvements.

## Communications
External communications are coordinated under the Communications Policy with legal input.

## Roles & Responsibilities
- **Information Security** leads technical response.
- **Risk/Legal** manage notifications and obligations.

Contact: infosec@vicinity.example.com.
"""
},
{
 "id":"POL-095","doc_name":"tenant_fitout_construction_policy","category":"Operations & Maintenance",
 "title":"Tenant Fit-Out & Construction Policy","eff":"2024-05-28","rev":"2026-05-28",
 "owner":"Design & Operations","ver":"1.8",
 "body":"""
## Purpose
To manage tenant fit-out and construction works so they are safe, compliant, high-quality, and do not
adversely affect the centre, other tenants, or base-building systems.

## Scope
All tenant fit-outs, refurbishments, and works within leased premises in managed centres.

## Requirements
1. Fit-out drawings must be approved against the centre's design and technical criteria before works.
2. Tenants and their contractors must provide insurances, licences, SWMS, and permits (see WHS and
   Contractor policies).
3. Works must not impair base-building services, fire systems, or accessibility; any interface works are
   coordinated and certified.
4. Hoarding, dust, noise, and waste are controlled to protect shoppers and neighbours; noisy works may be
   restricted to after hours.
5. On completion, certificates of compliance/occupancy and as-built/essential-safety documentation are
   provided before trade.

## Make-Good
At lease end, tenants make good per the lease, including removal of works and reinstatement, unless
otherwise agreed.

## Roles & Responsibilities
- **Design** approves drawings; **Operations** supervises site works.
- **Tenant** delivers compliant works and documentation.

Contact: fitout@vicinity.example.com.
"""
},
{
 "id":"POL-096","doc_name":"car_park_management_policy","category":"Parking & Traffic",
 "title":"Car Park Management & Traffic Policy","eff":"2024-06-28","rev":"2026-06-28",
 "owner":"Operations","ver":"1.6",
 "body":"""
## Purpose
To operate centre car parks safely, fairly, and efficiently for shoppers, tenants, and the community.

## Scope
All car parks and traffic areas at managed centres, including paid and free parking.

## Operations
1. Tariffs, free periods, and conditions of entry are clearly displayed and lawful.
2. Pedestrian safety is prioritised through marked crossings, speed controls, lighting, and signage.
3. Accessible and parents-with-prams bays are provided and enforced; misuse is managed fairly.
4. Number-plate recognition and payment data are handled under the Privacy Policy.
5. Incidents, breakdowns, and abandoned vehicles are managed under defined procedures.

## Enforcement
Any enforcement (e.g., overstay management) is conducted lawfully and fairly with a clear appeals
process. Boom gates and equipment are maintained for safe operation.

## Roles & Responsibilities
- **Operations** manages the car park operator, equipment, and safety.
- **Security** supports incident response.

Contact: parking@vicinity.example.com.
"""
},
{
 "id":"POL-097","doc_name":"ev_charging_policy","category":"Parking & Traffic",
 "title":"Electric Vehicle Charging Policy","eff":"2024-07-28","rev":"2026-07-28",
 "owner":"Operations & Sustainability","ver":"1.0",
 "body":"""
## Purpose
To provide safe, reliable electric vehicle (EV) charging that supports sustainability goals and shopper
amenity.

## Scope
All EV charging infrastructure installed at managed centres.

## Requirements
1. EV chargers are installed to electrical standards by licensed contractors, with appropriate protection
   and signage.
2. Charging bays are clearly marked; time limits and tariffs are displayed and enforced fairly.
3. Fire and electrical safety risks of EV charging are assessed and managed, including emergency
   isolation and response procedures.
4. Charger availability and faults are monitored; faulty units are isolated and repaired.
5. Energy use is integrated with the Energy Management Policy and may use renewable supply.

## Data & Payment
Payment and user data from charging networks are handled under the Privacy Policy.

## Roles & Responsibilities
- **Operations** manages installation, safety, and maintenance.
- **Sustainability** aligns rollout with targets.

Contact: parking@vicinity.example.com.
"""
},
{
 "id":"POL-098","doc_name":"customer_experience_complaints_policy","category":"Customer Experience",
 "title":"Customer Experience & Complaints Handling Policy","eff":"2024-08-28","rev":"2026-08-28",
 "owner":"Centre Management","ver":"1.4",
 "body":"""
## Purpose
To deliver excellent shopper experiences and to handle feedback and complaints fairly, promptly, and
consistently.

## Scope
All shopper interactions and feedback at managed centres and through centre channels.

## Service Standards
1. Staff and contractors are courteous, helpful, and inclusive.
2. Concierge, amenities, wayfinding, and accessibility support a positive experience.
3. Feedback channels (in-centre, phone, online, social) are accessible and monitored.

## Complaints Handling
1. Complaints are acknowledged promptly and resolved at first contact where possible.
2. Complaints are logged, investigated fairly, and responded to within target timeframes.
3. Safety and injury complaints are escalated under the Incident Management Policy.
4. Trends are analysed to drive improvement.
5. Personal information is handled under the Privacy Policy.

## Roles & Responsibilities
- **Centre Management** owns experience and complaint resolution.
- **All staff** respond helpfully and escalate appropriately.

Contact: customercare@vicinity.example.com.
"""
},
{
 "id":"POL-099","doc_name":"communications_media_policy","category":"Customer Experience",
 "title":"Communications & Media Policy","eff":"2024-09-28","rev":"2026-09-28",
 "owner":"Corporate Affairs","ver":"1.2",
 "body":"""
## Purpose
To ensure communications with media and the public are accurate, consistent, timely, and protect
Vicinity's reputation — particularly during incidents and crises.

## Scope
All external communications, media enquiries, and public statements relating to Vicinity and its centres.

## Rules
1. Only authorised spokespeople speak to media; all media enquiries are referred to Corporate Affairs.
2. Statements are accurate, approved, and consistent with legal and privacy obligations.
3. During incidents/crises, communications are coordinated through the Crisis Management team with a
   single source of truth.
4. Confidential, commercially sensitive, or personal information is not disclosed.
5. Social media communications follow the Social Media Policy.

## Incident Communications
Holding statements are prepared quickly; affected stakeholders (tenants, owners, authorities) are kept
informed appropriately.

## Roles & Responsibilities
- **Corporate Affairs** manages media and approvals.
- **All staff** refer enquiries and do not speak on behalf of Vicinity unless authorised.

Contact: corporateaffairs@vicinity.example.com.
"""
},
{
 "id":"POL-100","doc_name":"ai_emerging_tech_policy","category":"Data, Privacy & IT",
 "title":"Responsible AI & Emerging Technology Use Policy","eff":"2024-10-30","rev":"2026-10-30",
 "owner":"IT / Risk","ver":"1.0",
 "body":"""
## Purpose
To enable safe, ethical, and compliant use of artificial intelligence (AI) and emerging technologies
across Vicinity.

## Scope
All use of AI tools and emerging technologies by employees and contractors for Vicinity business,
including generative AI, analytics, and automation.

## Principles
1. **Approved tools only:** AI tools must be approved and used within their terms; unapproved tools must
   not process company or personal data.
2. **Data protection:** confidential, personal, or commercially sensitive information must not be entered
   into public AI tools; privacy and security policies apply.
3. **Human oversight:** AI outputs are reviewed by a competent person before reliance, especially for
   decisions affecting people (tenants, shoppers, employees).
4. **Fairness & transparency:** AI use avoids unlawful bias and discrimination, and is disclosed where
   required.
5. **Accountability:** the business owner of an AI use case is responsible for its risks and compliance.

## Governance
New or high-risk AI use cases are assessed for privacy, security, legal, and ethical risk before
deployment, and monitored thereafter.

## Roles & Responsibilities
- **IT/Risk** approve tools and assess use cases.
- **All staff** use AI responsibly and protect data.

Contact: ai-governance@vicinity.example.com.
"""
}
]

print(f"Loaded {len(POLICIES)} policy definitions")

# COMMAND ----------

# MAGIC %md ## 4. Validate

# COMMAND ----------

ids = [p["id"] for p in POLICIES]
names = [p["doc_name"] for p in POLICIES]
assert len(POLICIES) == 100, f"expected 100 policies, got {len(POLICIES)}"
assert len(set(ids)) == 100, "duplicate policy ids found"
assert len(set(names)) == 100, "duplicate doc_names found"

word_counts = [len(doc(p).split()) for p in POLICIES]
over = [p["id"] for p in POLICIES if len(doc(p).split()) > 1000]  # ~2 pages
assert not over, f"policies exceeding ~2 pages: {over}"
print(f"OK: 100 unique policies | words {min(word_counts)}-{max(word_counts)} | "
      f"{len(set(p['category'] for p in POLICIES))} categories")

# COMMAND ----------

# MAGIC %md ## 5. Create schema and write the table

# COMMAND ----------

import datetime
from pyspark.sql.types import StructType, StructField, StringType, DateType

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA} "
          f"COMMENT 'Synthetic company policies for retail property management demo'")

schema_def = StructType([
    StructField("policy_id", StringType(), False),
    StructField("doc_name", StringType(), False),
    StructField("category", StringType(), True),
    StructField("title", StringType(), True),
    StructField("effective_date", DateType(), True),
    StructField("review_date", DateType(), True),
    StructField("owner", StringType(), True),
    StructField("version", StringType(), True),
    StructField("content", StringType(), True),
])

def to_date(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()

rows = [(
    p["id"], p["doc_name"], p["category"], p["title"],
    to_date(p["eff"]), to_date(p["rev"]), p["owner"], p["ver"], doc(p),
) for p in POLICIES]

df = spark.createDataFrame(rows, schema_def)

(df.write
   .format("delta")
   .mode(WRITE_MODE)
   .option("overwriteSchema", "true")
   .saveAsTable(FQN))

spark.sql(f"COMMENT ON TABLE {FQN} IS "
          f"'Company policies for a retail property management company; one row per policy, each <=2 pages'")

print(f"Wrote {df.count()} rows to {FQN}")

# COMMAND ----------

# MAGIC %md ## 6. Verify

# COMMAND ----------

display(spark.sql(f"""
    SELECT category, COUNT(*) AS policies
    FROM {FQN}
    GROUP BY category
    ORDER BY policies DESC, category
"""))

# COMMAND ----------

display(spark.sql(f"""
    SELECT policy_id, title, owner, effective_date, LENGTH(content) AS content_chars
    FROM {FQN}
    ORDER BY policy_id
"""))

# COMMAND ----------

# MAGIC %md Preview one policy's Markdown content:

# COMMAND ----------

sample = spark.sql(f"SELECT content FROM {FQN} WHERE policy_id = 'POL-001'").collect()[0][0]
print(sample)

# COMMAND ----------

# MAGIC %md ## 7. Vector Search endpoint & embeddings (optional)
# MAGIC
# MAGIC Creates a Vector Search endpoint and a **Delta Sync index** over the policies. Databricks
# MAGIC generates embeddings automatically with the `databricks-gte-large-en` foundation model
# MAGIC (one embedding per policy on the `content` column). Requires Change Data Feed on the source
# MAGIC table (enabled below) and serverless compute / a Vector Search-enabled workspace.

# COMMAND ----------

# MAGIC %pip install -q databricks-vectorsearch
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("vs_endpoint", "vicinity-policies-vs", "Vector Search endpoint")
dbutils.widgets.text("embedding_model", "databricks-gte-large-en", "Embedding model endpoint")

# re-read widgets after restartPython
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
TABLE = dbutils.widgets.get("table")
FQN = f"{CATALOG}.{SCHEMA}.{TABLE}"
VS_ENDPOINT_NAME = dbutils.widgets.get("vs_endpoint")
EMBEDDING_MODEL = dbutils.widgets.get("embedding_model")
VS_INDEX_NAME = f"{CATALOG}.{SCHEMA}.{TABLE}_index"

# COMMAND ----------

# MAGIC %md ### Create (or reuse) the endpoint

# COMMAND ----------

import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.vectorsearch import EndpointType

w = WorkspaceClient()

try:
    ep = w.vector_search_endpoints.get_endpoint(VS_ENDPOINT_NAME)
    print(f"Endpoint '{VS_ENDPOINT_NAME}' exists (status: {ep.endpoint_status.state.value})")
except Exception:
    print(f"Creating Vector Search endpoint '{VS_ENDPOINT_NAME}'...")
    w.vector_search_endpoints.create_endpoint(
        name=VS_ENDPOINT_NAME, endpoint_type=EndpointType.STANDARD)

# Wait until ONLINE (provisioning can take 5-10 minutes)
for attempt in range(60):
    status = w.vector_search_endpoints.get_endpoint(VS_ENDPOINT_NAME).endpoint_status.state.value
    if status == "ONLINE":
        break
    if attempt % 6 == 0:
        print(f"  waiting for endpoint to be ONLINE (currently: {status})...")
    time.sleep(10)
print(f"Endpoint '{VS_ENDPOINT_NAME}' status: {status}")

# COMMAND ----------

# MAGIC %md ### Enable Change Data Feed and create the Delta Sync index

# COMMAND ----------

spark.sql(f"ALTER TABLE {FQN} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient(disable_notice=True)

# Recreate the index if it already exists
try:
    client.delete_index(endpoint_name=VS_ENDPOINT_NAME, index_name=VS_INDEX_NAME)
    print(f"Deleted existing index: {VS_INDEX_NAME}")
except Exception as e:
    print(f"No existing index to delete ({e})")

index = client.create_delta_sync_index(
    endpoint_name=VS_ENDPOINT_NAME,
    source_table_name=FQN,
    index_name=VS_INDEX_NAME,
    pipeline_type="TRIGGERED",
    primary_key="policy_id",
    embedding_source_column="content",
    embedding_model_endpoint_name=EMBEDDING_MODEL,
)
print(f"Index '{VS_INDEX_NAME}' created; embeddings are syncing.")

# COMMAND ----------

# MAGIC %md ### Wait for the initial sync, then test a similarity search

# COMMAND ----------

idx = client.get_index(endpoint_name=VS_ENDPOINT_NAME, index_name=VS_INDEX_NAME)
for attempt in range(60):
    st = idx.describe().get("status", {})
    if st.get("ready"):
        print(f"Index READY | indexed rows: {st.get('indexed_row_count')}")
        break
    if attempt % 4 == 0:
        print(f"  syncing... state={st.get('detailed_state')} indexed={st.get('indexed_row_count', 0)}")
    time.sleep(15)

# COMMAND ----------

results = idx.similarity_search(
    query_text="What are my obligations if a tenant falls behind on rent?",
    columns=["policy_id", "title", "category"],
    num_results=5,
)
for row in results.get("result", {}).get("data_array", []):
    print(row)

# COMMAND ----------

# MAGIC %md ## 8. Knowledge Assistant (Agent Bricks, optional)
# MAGIC
# MAGIC Builds an **Agent Bricks Knowledge Assistant** chatbot over the policy Vector Search index.
# MAGIC It produces a serving endpoint you can query (and chat with in AI Playground). Requires the
# MAGIC index to use a supported embedding model (`databricks-gte-large-en` does qualify).
# MAGIC
# MAGIC > **Important:** a knowledge source\'s display name becomes the agent\'s retrieval tool name,
# MAGIC > which must match `^[a-zA-Z0-9_-]{1,128}$`. **No spaces or punctuation** — a name like
# MAGIC > "Company Policies" makes every search fail with a 400 and the assistant returns no results.
# MAGIC > Use `company_policies` (underscores), as below.

# COMMAND ----------

# MAGIC %pip install -q --upgrade databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("ka_name", "Vicinity Policy Assistant", "Knowledge Assistant display name")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
TABLE = dbutils.widgets.get("table")
VS_INDEX_NAME = f"{CATALOG}.{SCHEMA}.{TABLE}_index"
KA_DISPLAY_NAME = dbutils.widgets.get("ka_name")
SOURCE_NAME = "company_policies"   # MUST match ^[a-zA-Z0-9_-]{1,128}$ (no spaces!)

INSTRUCTIONS = (
    "You are the Vicinity Centres company policy assistant. Answer questions strictly using the "
    "provided policy documents. Always cite the specific policy you relied on, including its title "
    "and policy ID (e.g., POL-009 Tenant Arrears Management Policy). If the policies do not cover "
    "the question, say so clearly and suggest contacting the relevant team. Be concise and accurate, "
    "and never invent policy details or obligations."
)

# COMMAND ----------

# MAGIC %md ### Create the assistant and attach the index as a knowledge source

# COMMAND ----------

import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.knowledgeassistants import KnowledgeAssistant, KnowledgeSource, IndexSpec

w = WorkspaceClient()

# Reuse an existing assistant with the same display name, else create one
existing = [k for k in w.knowledge_assistants.list_knowledge_assistants()
            if k.display_name == KA_DISPLAY_NAME]
if existing:
    ka = existing[0]
    print(f"Reusing Knowledge Assistant: {ka.name}")
else:
    ka = w.knowledge_assistants.create_knowledge_assistant(
        knowledge_assistant=KnowledgeAssistant(
            display_name=KA_DISPLAY_NAME,
            description=("Answers questions about Vicinity Centres' retail property management "
                         "policies (leasing, operations, WHS, security, finance, compliance, "
                         "sustainability, HR, and more)."),
            instructions=INSTRUCTIONS,
        )
    )
    print(f"Created Knowledge Assistant: {ka.name}")

# Attach the Vector Search index as a knowledge source (idempotent on the compliant name)
sources = list(w.knowledge_assistants.list_knowledge_sources(ka.name))
if not any(s.display_name == SOURCE_NAME for s in sources):
    w.knowledge_assistants.create_knowledge_source(
        parent=ka.name,
        knowledge_source=KnowledgeSource(
            display_name=SOURCE_NAME,
            description="Vicinity Centres company policy documents (100 policies).",
            source_type="index",
            index=IndexSpec(index_name=VS_INDEX_NAME, text_col="content", doc_uri_col="policy_id"),
        ),
    )
    print(f"Attached knowledge source: {SOURCE_NAME} -> {VS_INDEX_NAME}")

w.knowledge_assistants.sync_knowledge_sources(name=ka.name)
print("Sync triggered.")

# COMMAND ----------

# MAGIC %md ### Wait until ACTIVE, then chat with the assistant

# COMMAND ----------

for _ in range(60):
    ka = w.knowledge_assistants.get_knowledge_assistant(ka.name)
    state = ka.state.value if ka.state else None
    if state == "ACTIVE":
        break
    time.sleep(10)
print(f"Knowledge Assistant state: {state} | serving endpoint: {ka.endpoint_name}")

# COMMAND ----------

# Query the assistant endpoint (Agent Bricks uses the ResponsesAgent `input` schema)
resp = w.api_client.do(
    "POST",
    f"/serving-endpoints/{ka.endpoint_name}/invocations",
    body={"input": [{"role": "user",
                     "content": "A tenant is 45 days behind on rent. What is the arrears process "
                                "and can we draw on their bank guarantee? Cite the policy."}]},
)
answer = "".join(
    seg.get("text", "")
    for item in resp.get("output", [])
    for seg in (item.get("content") or [])
    if isinstance(item.get("content"), list)
)
print(answer or resp)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Foot-traffic operational data (for the Genie space)
# MAGIC
# MAGIC Generates synthetic **daily foot-traffic** records per shopping centre and writes
# MAGIC `${catalog}.${ops_schema}.${ops_table}` (defaults `dev` / `operations` / `foot_traffic`).
# MAGIC This is the table the **Vicinity Foot Traffic Genie** space answers questions over
# MAGIC ("how busy is a centre", weekend vs weekday, holiday closures, busiest centres).
# MAGIC
# MAGIC One row per centre per day, with realistic patterns: weekend uplift, a December
# MAGIC pre-Christmas surge, Boxing Day spikes, and zero trade on Christmas Day / Good Friday.

# COMMAND ----------

import datetime

dbutils.widgets.text("ops_schema", "operations", "Foot-traffic schema")
dbutils.widgets.text("ops_table", "foot_traffic", "Foot-traffic table")
dbutils.widgets.text("traffic_days", "180", "Days of history to generate")
dbutils.widgets.text("traffic_end_date", "", "End date YYYY-MM-DD (blank = today)")

OPS_SCHEMA = dbutils.widgets.get("ops_schema")
OPS_TABLE = dbutils.widgets.get("ops_table")
OPS_FQN = f"{CATALOG}.{OPS_SCHEMA}.{OPS_TABLE}"
N_DAYS = int(dbutils.widgets.get("traffic_days") or "180")
_end_raw = dbutils.widgets.get("traffic_end_date").strip()
END_DATE = (datetime.datetime.strptime(_end_raw, "%Y-%m-%d").date()
            if _end_raw else datetime.date.today())
START_DATE = END_DATE - datetime.timedelta(days=N_DAYS - 1)
print(f"Foot-traffic target: {OPS_FQN}  ({N_DAYS} days, {START_DATE} -> {END_DATE})")

# COMMAND ----------

import random

random.seed(42)  # reproducible

# Fictional Vicinity-style portfolio. base_daily = typical weekday visitor count.
# centre_id, name, state, centre_type, gla_sqm, base_daily
CENTRES = [
    ("CTR-01", "Chadstone",          "VIC", "Flagship",     210000, 78000),
    ("CTR-02", "Emporium Melbourne", "VIC", "CBD",           62000, 41000),
    ("CTR-03", "Northland",          "VIC", "Regional",      98000, 39000),
    ("CTR-04", "Box Hill Central",   "VIC", "Sub-regional",  47000, 24000),
    ("CTR-05", "The Glen",           "VIC", "Sub-regional",  64000, 27000),
    ("CTR-06", "DFO South Wharf",    "VIC", "Outlet",        38000, 21000),
    ("CTR-07", "Bankstown Central",  "NSW", "Regional",      83000, 34000),
    ("CTR-08", "Chatswood Chase",    "NSW", "Sub-regional",  46000, 26000),
    ("CTR-09", "Roselands",          "NSW", "Sub-regional",  58000, 23000),
    ("CTR-10", "Galleria",           "WA",  "Regional",      75000, 31000),
    ("CTR-11", "Mandurah Forum",     "WA",  "Sub-regional",  56000, 19000),
    ("CTR-12", "Castle Plaza",       "SA",  "Neighbourhood", 34000, 14000),
]

# --- Australian public holidays: fixed-date + Easter-derived (Anonymous Gregorian) ---
def _easter(year):
    a = year % 19; b = year // 100; c = year % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - d - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)

def au_holidays(years):
    hol = {}
    for y in years:
        hol[datetime.date(y, 1, 1)]   = "New Year's Day"
        hol[datetime.date(y, 1, 26)]  = "Australia Day"
        hol[datetime.date(y, 4, 25)]  = "ANZAC Day"
        hol[datetime.date(y, 12, 25)] = "Christmas Day"
        hol[datetime.date(y, 12, 26)] = "Boxing Day"
        es = _easter(y)
        hol[es - datetime.timedelta(days=2)] = "Good Friday"
        hol[es]                              = "Easter Sunday"
        hol[es + datetime.timedelta(days=1)] = "Easter Monday"
    return hol

HOLIDAYS = au_holidays(range(START_DATE.year, END_DATE.year + 1))
CLOSED = {"Christmas Day", "Good Friday"}  # centres do not trade

DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DOW_FACTOR = {0: 0.92, 1: 0.90, 2: 0.95, 3: 1.00, 4: 1.18, 5: 1.45, 6: 1.22}

def _season(d):
    # December pre-Christmas surge, January sales, mid-winter dip.
    return {12: 1.35, 1: 1.12, 6: 0.93, 7: 0.90}.get(d.month, 1.0)

rows = []
d = START_DATE
while d <= END_DATE:
    wd = d.weekday()
    hol_name = HOLIDAYS.get(d)
    is_hol = hol_name is not None
    closed = hol_name in CLOSED
    for cid, name, state, ctype, gla, base in CENTRES:
        if closed:
            visitors, peak_hour, dwell = 0, None, None
        else:
            f = DOW_FACTOR[wd] * _season(d)
            if hol_name == "Boxing Day":
                f *= 2.4
            elif hol_name == "Easter Sunday":
                f *= 0.6  # restricted trade
            elif is_hol:
                f *= 1.08
            visitors = int(base * f * random.uniform(0.90, 1.10))
            peak_hour = random.choice([12, 13, 14]) if wd >= 5 else random.choice([12, 17, 18])
            dwell = round(
                random.uniform(70, 95) if ctype in ("Flagship", "CBD", "Regional")
                else random.uniform(38, 58), 1)
        rows.append((cid, name, state, ctype, gla, d, DOW[wd],
                     wd >= 5, is_hol, hol_name, (not closed), visitors, peak_hour, dwell))
    d += datetime.timedelta(days=1)

print(f"Generated {len(rows):,} rows ({len(CENTRES)} centres x {N_DAYS} days)")

# COMMAND ----------

from pyspark.sql.types import (StructType, StructField, StringType, DateType,
                               IntegerType, BooleanType, DoubleType)

ft_schema = StructType([
    StructField("centre_id", StringType(), False),
    StructField("centre_name", StringType(), False),
    StructField("state", StringType(), True),
    StructField("centre_type", StringType(), True),
    StructField("gla_sqm", IntegerType(), True),
    StructField("traffic_date", DateType(), False),
    StructField("day_of_week", StringType(), True),
    StructField("is_weekend", BooleanType(), True),
    StructField("is_public_holiday", BooleanType(), True),
    StructField("holiday_name", StringType(), True),
    StructField("is_trading_day", BooleanType(), True),
    StructField("visitor_count", IntegerType(), True),
    StructField("peak_hour", IntegerType(), True),
    StructField("avg_dwell_minutes", DoubleType(), True),
])

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{OPS_SCHEMA} "
          f"COMMENT 'Synthetic operational data (foot traffic) for the property management demo'")

ft_df = spark.createDataFrame(rows, ft_schema)
(ft_df.write
   .format("delta")
   .mode(WRITE_MODE)
   .option("overwriteSchema", "true")
   .saveAsTable(OPS_FQN))

# Table + column comments help Genie generate accurate SQL.
spark.sql(
    f"COMMENT ON TABLE {OPS_FQN} IS "
    f"'Daily foot-traffic (visitor counts) per Vicinity shopping centre; one row per centre "
    f"per day. visitor_count is 0 on non-trading public holidays (Christmas Day, Good Friday).'")
for _col, _desc in [
    ("centre_id", "Stable centre identifier, e.g. CTR-01"),
    ("centre_name", "Shopping centre name"),
    ("state", "Australian state/territory (VIC, NSW, WA, SA)"),
    ("centre_type", "Format: Flagship, CBD, Regional, Sub-regional, Outlet, Neighbourhood"),
    ("gla_sqm", "Gross lettable area in square metres (a proxy for centre size)"),
    ("traffic_date", "Calendar date of the foot-traffic measurement"),
    ("day_of_week", "Day name (Monday..Sunday)"),
    ("is_weekend", "True for Saturday and Sunday"),
    ("is_public_holiday", "True if the date is an Australian public holiday"),
    ("holiday_name", "Name of the public holiday, otherwise null"),
    ("is_trading_day", "False when the centre was closed (no trade)"),
    ("visitor_count", "Total daily visitors (foot traffic); 0 when not trading"),
    ("peak_hour", "Hour of day (0-23) with the most visitors; null when closed"),
    ("avg_dwell_minutes", "Average visitor dwell time in minutes; null when closed"),
]:
    spark.sql(f"COMMENT ON COLUMN {OPS_FQN}.{_col} IS '{_desc}'")

print(f"Wrote {ft_df.count():,} rows to {OPS_FQN}")
display(ft_df.orderBy("traffic_date", ascending=False).limit(20))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create the Genie space (manual, one-time)
# MAGIC
# MAGIC Genie spaces aren't created from this notebook. In the workspace UI:
# MAGIC 1. **Genie → New** and add `${catalog}.${ops_schema}.${ops_table}` as a data table.
# MAGIC 2. Name it (e.g. *Vicinity Foot Traffic Genie*) and attach a SQL warehouse.
# MAGIC 3. Copy the **space id** from the URL into `databricks.yml` (`foot_traffic_genie` resource)
# MAGIC    and `agent_server/agent.py` (the Genie MCP URL).
# MAGIC 4. Grant the app's service principal `CAN_RUN` on the space, plus `USE CATALOG`,
# MAGIC    `USE SCHEMA`, and `SELECT` on this table (see the deploy runbook).
# MAGIC
# MAGIC Sample questions to seed the space:
# MAGIC - "Which centre had the highest foot traffic last weekend?"
# MAGIC - "Compare weekday vs weekend visitors for Chadstone."
# MAGIC - "How busy is Emporium Melbourne on public holidays?"
# MAGIC - "Show daily visitors for VIC centres over the last 30 days."
# MAGIC - "Which days were centres closed, and why?"
