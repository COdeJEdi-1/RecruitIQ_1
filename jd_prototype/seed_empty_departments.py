"""
One-time seed script — writes one representative sample JD for each
department that currently has zero sample_jds, so the History page
can show a card for every department.

Run once: python3 seed_empty_departments.py
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

KB_ROOT = Path(__file__).parent / "kb"

SEEDS = [
    {
        "dept": "retail", "family": "store_manager", "band": "senior",
        "role_title": "Store Manager — Arrow EBO",
        "text": """Role Summary
You will own the full P&L of an Arrow Exclusive Brand Outlet (EBO) in a Tier-1 city, leading a team of 10-12 store staff and driving monthly revenue targets for one of Arvind Brands' flagship menswear formats.

Key Responsibilities
- Own store-level P&L: revenue, ATV, UPT, and shrinkage targets
- Lead and develop a team of 10-12 sales associates and department managers
- Manage seasonal visual merchandising aligned to Arrow brand guidelines
- Coordinate with the Arvind Brands supply chain team on replenishment and stock allocation
- Drive footfall-to-conversion improvement through staff training and floor management
- Ensure SOP adherence across loss prevention, cash handling, and customer service

Must-Have Skills
- 3-7 years managing an EBO/MBO for a premium or mass apparel brand
- Proven ATV/UPT improvement track record
- Team management and training experience
- Comfort with retail KPI tools and POS systems

Nice-to-Have Skills
- Experience with loyalty programs
- Store opening/launch experience
- Multi-brand retail exposure

What We Offer
Direct P&L ownership within Arvind Brands' portfolio of premium menswear formats, with a clear path to Area Sales Manager.""",
    },
    {
        "dept": "quality", "family": "qa_manager", "band": "senior",
        "role_title": "QA Manager — Denim Division",
        "text": """Role Summary
You will manage inline and final inspection for Arvind's denim plant in Santej, overseeing a team of 8 QC inspectors, owning AQL Level II sampling plans, and conducting weekly quality reviews with the Plant Head.

Key Responsibilities
- Manage inline and final inspection using the 4-point system for denim fabrics
- Own AQL Level II sampling plans and defect reporting
- Conduct buyer audits (H&M Way, M&S P&Q) as primary QA contact
- Maintain OEKO-TEX 100 and GOTS certification records
- Lead a team of 8 QC inspectors across two production shifts
- Present quality KPIs and PPM trends to the Plant Head

Must-Have Skills
- Hands-on experience with the 4-point inspection system for woven/denim fabrics
- Knowledge of ASTM D5034, ISO 13937, AATCC 61 test standards
- Experience handling H&M or M&S buyer audits as primary contact
- AQL Level II sampling plan ownership
- Team management experience (5-10 inspectors)

Nice-to-Have Skills
- Six Sigma Green Belt
- Third-party lab accreditation experience (SGS, Bureau Veritas, Intertek)
- Chemical testing exposure (RSL/MRSL)

What We Offer
Direct ownership of quality outcomes for one of India's largest denim manufacturing operations, with global buyer exposure.""",
    },
    {
        "dept": "sustainability", "family": "sustainability_reporting", "band": "mid",
        "role_title": "Sustainability Reporting Manager",
        "text": """Role Summary
You will own Arvind's Scope 1 and Scope 2 emissions data consolidation across manufacturing plants, prepare the GHG Protocol inventory, and support BRSR Core disclosure for the listed entity.

Key Responsibilities
- Consolidate Scope 1/2 emissions data across plant-level EHS teams
- Prepare GHG Protocol inventory and BRSR Core disclosure inputs
- Coordinate with plant EHS, supply chain, and finance teams on data collection
- Track Arvind's water stewardship program metrics
- Maintain OEKO-TEX, GOTS, ZDHC MRSL, and BCI certification documentation
- Support buyer sustainability audits (H&M Higg Index, PVH Corp standards)

Must-Have Skills
- GRI, BRSR, and GHG Protocol framework knowledge
- Data consolidation across multiple plant sites
- ZDHC MRSL / RSL compliance understanding
- Stakeholder coordination across EHS, supply chain, and finance functions

Nice-to-Have Skills
- SBTi target-setting exposure
- Familiarity with sustainability data platforms (Watershed, Sweep)
- TCFD reporting experience

What We Offer
Direct ownership of Arvind's operational sustainability disclosure, with exposure to global buyer ESG standards and BRSR compliance for a listed entity.""",
    },
    {
        "dept": "supply_chain", "family": "supply_chain_manager", "band": "senior",
        "role_title": "Supply Chain Manager",
        "text": """Role Summary
You will own end-to-end supply chain strategy for a category within Arvind Limited's textile and apparel business, managing vendor relationships, logistics optimization, and demand planning across multiple plants.

Key Responsibilities
- Own end-to-end supply chain strategy for assigned product categories
- Manage vendor relationships and contract negotiations
- Drive logistics optimization across Gujarat, Karnataka, and Rajasthan plants
- Lead S&OP (Sales & Operations Planning) cycles with Sales and Manufacturing
- Manage SAP MM/SD transactions and master data governance
- Drive cost reduction through 3PL management and route optimization

Must-Have Skills
- SAP MM/SD hands-on experience
- Demand forecasting and S&OP process ownership
- Vendor management and negotiation experience
- Multi-site logistics coordination

Nice-to-Have Skills
- 3PL contract management experience
- Experience in fashion/apparel or FMCG supply chains
- Power BI or analytics tool proficiency

What We Offer
End-to-end ownership of supply chain operations across Arvind's manufacturing footprint, with direct cross-functional exposure to Sales, Finance, and Manufacturing leadership.""",
    },
    {
        "dept": "design_merchandising", "family": "merchandiser", "band": "mid",
        "role_title": "Merchandiser — Arvind Fashions",
        "text": """Role Summary
You will own range planning and Open-to-Buy (OTB) management for a brand category within Arvind Fashions' portfolio, working closely with Design and Retail teams to translate trend insights into a profitable buy plan.

Key Responsibilities
- Build and manage the range plan and OTB tracker for your assigned category
- Translate seasonal trend research into buy quantities and SKU plans
- Coordinate with vendors on sampling, costing, and delivery timelines
- Partner with Design on collection finalization and pricing architecture
- Track sell-through and margin performance, adjusting OTB in-season
- Support markdown and end-of-season clearance planning

Must-Have Skills
- OTB management and range planning experience
- Strong Excel/data modelling skills
- Vendor coordination and negotiation experience
- Trend analysis and sell-through tracking

Nice-to-Have Skills
- ERP/merchandising system experience (SAP, Oracle Retail)
- Exposure to premium or mass apparel brand categories
- NIFT/FMS background

What We Offer
Direct exposure to brand-level buying decisions within Arvind Fashions' portfolio (Arrow, USPA, Flying Machine), with a path toward category buying leadership.""",
    },
]


def main():
    written = 0
    for seed in SEEDS:
        sample_dir = KB_ROOT / seed["dept"] / seed["family"] / "sample_jds"
        sample_dir.mkdir(parents=True, exist_ok=True)

        existing = sorted(sample_dir.glob(f"{seed['band']}_*.txt"))
        if existing:
            continue  # already seeded
        filename = sample_dir / f"{seed['band']}_001.txt"

        metadata = {
            "jd_id": str(uuid.uuid4())[:8],
            "role_family": seed["role_title"],
            "yoe_band": seed["band"],
            "source": "kb_seed",
            "date_added": datetime.now().strftime("%Y-%m-%d"),
            "approved_by": "kb_seed",
        }
        content = json.dumps(metadata) + "\n\n---\n\n" + seed["text"]
        filename.write_text(content, encoding="utf-8")
        written += 1
        print(f"Seeded {seed['dept']}/{seed['family']} ({seed['band']})")

    print(f"\nDone — {written} new sample JD(s) written.")


if __name__ == "__main__":
    main()
