"""
One-time KB expansion script — Arvind Limited Knowledge Base.

Builds out 24 new role families across 5 new departments
(supply_chain, sales_marketing, design_merchandising, environmental, telecom)
plus additions to existing departments (manufacturing, finance, hr, retail, it),
sourced from Arvind_Limited_JD_Knowledge_Base.pdf (company overview, role
hierarchy, skills taxonomy, qualifications matrix, and 9 verbatim scraped JDs).

Run once: python3 build_kb_expansion.py
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

import yaml

KB_ROOT = Path(__file__).parent / "kb"

VERSION_DEFAULTS = {
    "current_version": "v1.0",
    "approved_jds_count": 0,
    "feedback_submissions_count": 0,
    "avg_quality_rating": None,
    "edit_ratio_trend": [],
    "last_updated": datetime.now().strftime("%Y-%m-%d"),
}

BAND_LABELS = {
    "junior":    ("Junior / Trainee", "0-2", "Junior"),
    "mid":       ("Executive / Assistant Manager", "2-5", "Mid"),
    "senior":    ("Manager / Senior Manager", "5-8", "Senior"),
    "lead":      ("Deputy GM / GM", "8-12", "Lead"),
    "executive": ("VP / SVP / CXO", "12+", "Executive"),
}


# ════════════════════════════════════════════════════════════════════════════
# ROLE DEFINITIONS — sourced from the Arvind KB PDF (sections 5, 6, 7, 12)
# ════════════════════════════════════════════════════════════════════════════

ROLES = [

    # ── SUPPLY CHAIN (new department) ─────────────────────────────────────
    {
        "dept": "supply_chain", "family": "supply_chain_manager",
        "role_family": "Supply Chain Manager", "division": "Arvind Limited — Supply Chain",
        "bands": ["mid", "senior", "lead", "executive"],
        "core": {
            "mid": ["Demand planning and inventory management", "Vendor coordination and PO management",
                    "SAP MM/SD transaction processing", "Logistics tracking and dispatch coordination"],
            "senior": ["End-to-end supply chain strategy", "Vendor management and contract negotiation",
                       "Logistics optimization across plants", "S&OP (Sales & Operations Planning)"],
            "lead": ["Multi-site supply chain leadership", "3PL management and cost reduction programs",
                     "Demand forecasting at group level", "Cross-functional alignment with Sales and Finance"],
            "executive": ["Group supply chain strategy and transformation", "Network design across business units",
                          "Strategic vendor partnerships at CXO level"],
        },
        "arvind": {
            "mid": ["SAP MM/SD for Arvind plant operations"],
            "senior": ["Multi-plant logistics across Gujarat/Karnataka/Rajasthan facilities"],
            "lead": ["Supply chain harmonisation across Arvind Limited and Arvind Fashions"],
            "executive": ["SVP Supply Chain — group-wide ownership"],
        },
        "tone_keywords": "fabric/garment supply chain, 3PL, S&OP, demand forecasting",
        "qual": "MBA Supply Chain / Engineering + MBA",
    },
    {
        "dept": "supply_chain", "family": "sourcing_manager",
        "role_family": "Sourcing Manager (Fabric/Trim)", "division": "Arvind Limited — Sourcing",
        "bands": ["junior", "mid", "senior", "lead"],
        "core": {
            "junior": ["Fabric/trim sample tracking", "Vendor data maintenance", "Basic costing support"],
            "mid": ["Fabric sourcing and vendor development", "Costing negotiation", "Quality benchmarking against buyer requirements"],
            "senior": ["Sourcing strategy for fabric categories (denim/woven/knit)", "Vendor audits and capability mapping",
                       "Cost optimization across sourcing portfolio"],
            "lead": ["Group sourcing strategy", "Strategic vendor partnerships", "New material/vendor development pipelines"],
        },
        "arvind": {
            "junior": ["Exposure to Arvind's denim and woven fabric categories"],
            "mid": ["Sourcing for Arvind Fashions brand portfolio (Arrow, USPA, Flying Machine)"],
            "senior": ["Vendor audits aligned to Arvind quality standards"],
            "lead": ["Cross-BU sourcing strategy across Arvind Limited and AFL"],
        },
        "tone_keywords": "fabric construction, weave types, costing, vendor audits, NIFT",
        "qual": "B.Sc./B.Tech Textile + MBA or NIFT",
    },

    # ── MANUFACTURING (additions) ──────────────────────────────────────────
    {
        "dept": "manufacturing", "family": "trainee_operator",
        "role_family": "Trainee Operator / Machine Operator", "division": "Arvind Limited — Manufacturing",
        "bands": ["junior", "mid"],
        "core": {
            "junior": ["Machine operation (weaving/spinning/finishing)", "Basic quality checks", "Shift discipline and safety protocols"],
            "mid": ["Skilled machine operation across multiple lines", "Preventive maintenance adherence",
                    "Mentoring trainee operators", "Quality defect identification"],
        },
        "arvind": {
            "junior": ["Arvind plant operations at Kalol/Naroda/Santej"],
            "mid": ["Senior operator role on Arvind's denim/woven production lines"],
        },
        "tone_keywords": "machine handling, shift discipline, ITI qualification, plant floor",
        "qual": "7th – ITI pass",
    },
    {
        "dept": "manufacturing", "family": "shift_supervisor_dyeing",
        "role_family": "Shift Supervisor – Dyeing (Cotton Yarn / CCM)", "division": "Arvind Limited — Textile Manufacturing",
        "bands": ["mid", "senior"],
        "core": {
            "mid": ["Develop and formulate dyeing recipes for cotton yarn per shade requirements",
                     "Perform lab dyeing trials and colour matching",
                     "Operate and manage Computer Colour Matching (CCM) system",
                     "Analyze colour deviations and adjust recipes",
                     "Maintain dye formulation and lab trial records"],
            "senior": ["Ensure lab-to-bulk reproducibility across shifts",
                       "Optimize recipes for cost, quality, and process efficiency",
                       "Conduct fastness/quality evaluations per customer standards",
                       "Troubleshoot dyeing and shade variation issues",
                       "Collaborate with production, QA, and merchandising for shade approvals"],
        },
        "arvind": {
            "mid": ["CCM-based recipe generation for Arvind's cotton yarn dyeing operations in Ahmedabad"],
            "senior": ["Shade approval ownership across customer accounts for Arvind's yarn dyeing unit"],
        },
        "tone_keywords": "dyeing recipe formulation, CCM, colour matching, fastness testing, QMS",
        "qual": "B.Sc./Diploma in Textile Chemistry / Dyeing Technology",
    },
    {
        "dept": "manufacturing", "family": "associate_manager_nonwoven",
        "role_family": "Associate Manager – Production (Needle Punch Non-Woven)", "division": "Arvind Advanced Materials",
        "bands": ["mid", "senior"],
        "core": {
            "mid": ["Needle Punch Non-Woven production process management",
                     "Carding, Cross-Lapping, Drafting, Needle Loom operations",
                     "GSM/Thickness/Density/Width/Mechanical Properties control",
                     "RCA & problem-solving on production line issues"],
            "senior": ["Full production line ownership: targets, quality, waste minimization",
                       "Team and manpower management across shifts",
                       "Process optimization for fibre types: Polyester, Polypropylene, Meta-Aramid, Para-Aramid, Viscose, Recycled Fibres",
                       "5S and safety standard enforcement"],
        },
        "arvind": {
            "mid": ["Arvind Advanced Materials' Dholka non-woven facility, Grade E1-E2"],
            "senior": ["Reporting to Chief Manager – Non-Woven Production at Arvind Advanced Materials"],
        },
        "tone_keywords": "needle punch, non-woven, fibre properties, carding, ERP/SAP, 5S",
        "qual": "Diploma / Degree in Textile Technology / Nonwoven Technology",
    },

    # ── FINANCE (additions) ─────────────────────────────────────────────────
    {
        "dept": "finance", "family": "finance_manager",
        "role_family": "Finance Manager / DGM Finance", "division": "Arvind Limited — Finance & Accounts",
        "bands": ["senior", "lead", "executive"],
        "core": {
            "senior": ["Financial strategy and budgeting", "Fund management and treasury operations",
                       "SEBI/legal compliance and MIS reporting", "SAP FICO ownership"],
            "lead": ["Investor relations and board reporting", "IndAS/IFRS compliance across entities",
                     "Costing and profitability analysis at group level", "Cross-functional financial governance"],
            "executive": ["Group financial strategy and capital allocation", "M&A and corporate finance advisory",
                          "CXO-level investor and analyst relationship management"],
        },
        "arvind": {
            "senior": ["SAP FICO for Arvind Limited's multi-entity structure"],
            "lead": ["Investor relations for NSE: ARVIND / BSE: 500101"],
            "executive": ["CFO-level financial leadership across Arvind Group entities"],
        },
        "tone_keywords": "SAP FICO, IndAS/IFRS, FP&A, costing, legal compliance, treasury",
        "qual": "CA / CMA / MBA Finance",
    },
    {
        "dept": "finance", "family": "r2r_manager",
        "role_family": "Manager – Record to Report (R2R)", "division": "Arvind Limited — Finance & Accounting",
        "bands": ["senior", "lead"],
        "core": {
            "senior": ["End-to-end R2R management: GL, Fixed Assets, Intercompany Accounting, Accruals, Provisions",
                       "BS reconciliations and timely month/quarter/year-end close",
                       "Review journal entries, account reconciliations, financial reports",
                       "Prepare financial statements per IFRS/US GAAP/local standards",
                       "Coordinate with internal and external auditors"],
            "lead": ["Drive process improvements, standardization, automation across R2R function",
                     "Track KPIs and SLAs for shared services delivery",
                     "Collaborate with AP, AR, FP&A, Tax, Treasury teams",
                     "Lead, mentor, and develop a team of accountants",
                     "Support system implementations and finance transformation initiatives"],
        },
        "arvind": {
            "senior": ["R2R operations supporting Arvind Limited's multi-entity consolidation"],
            "lead": ["Leading R2R team within Arvind's Finance Shared Services / GCC structure"],
        },
        "tone_keywords": "GL accounting, IFRS/US GAAP, reconciliation, shared services, BlackLine, Hyperion",
        "qual": "CA / CMA / CPA / MBA Finance",
    },

    # ── HUMAN RESOURCES (additions) ────────────────────────────────────────
    {
        "dept": "hr", "family": "chro",
        "role_family": "CHRO / HR Head", "division": "Arvind Limited — Human Resources",
        "bands": ["lead", "executive"],
        "core": {
            "lead": ["HR strategy across business units", "Talent management framework design",
                     "Succession planning for senior leadership", "HR digitization initiatives"],
            "executive": ["Org transformation at group level", "DEI strategy and execution",
                          "Global talent management frameworks", "Board-level HR reporting"],
        },
        "arvind": {
            "lead": ["HR leadership across Arvind Limited's manufacturing and corporate functions"],
            "executive": ["Group CHRO role spanning Arvind Limited, AFL, and subsidiary entities"],
        },
        "tone_keywords": "org transformation, HR digitization, DEI, succession planning",
        "qual": "MBA HR / PGDM HR, 20-25 years experience",
    },
    {
        "dept": "hr", "family": "payroll_welfare_officer",
        "role_family": "Payroll & Welfare Officer", "division": "Arvind Limited — Garment Factory HR",
        "bands": ["junior", "mid"],
        "core": {
            "junior": ["Maintain statutory worker welfare facilities: canteen, first aid, crèche, sanitation",
                       "Organize health check-ups, safety training, hygiene awareness programs",
                       "Process attendance, overtime, and leave for wage calculation",
                       "Handle worker grievances and mediate disputes"],
            "mid": ["End-to-end monthly payroll processing per Minimum Wages Act",
                    "Statutory deductions: ESI, EPF — timely submissions and record maintenance",
                    "Source and recruit skilled/unskilled workers via employment exchanges and local networks",
                    "Conduct interviews and skill assessments (stitching, finishing)",
                    "Support labour inspections and statutory audits",
                    "Maintain compliance with Factories Act 1948, Minimum Wages Act, Payment of Wages Act, ESI Act, EPF Act"],
        },
        "arvind": {
            "junior": ["Worker welfare programs at Arvind's Bengaluru garment factory"],
            "mid": ["Payroll ownership for Arvind's garment manufacturing workforce"],
        },
        "tone_keywords": "payroll software, labour compliance, statutory registers, worker welfare",
        "qual": "MSW / MBA HR / IR",
    },
    {
        "dept": "hr", "family": "industrial_relations",
        "role_family": "Associate Manager – Industrial Relations / Employee Relations", "division": "Arvind Limited — Plant HR",
        "bands": ["mid", "senior"],
        "core": {
            "mid": ["Day-to-day employee grievance handling and resolution",
                     "Maintain harmonious relations across workers, contract labour, supervisors",
                     "Labour law compliance and statutory record maintenance",
                     "Contractor coordination: attendance, wages, PF/ESIC, documentation"],
            "senior": ["Lead disciplinary actions, domestic enquiries, and misconduct case management",
                       "Shop-floor rounds for discipline and engagement monitoring",
                       "Liaise with labour authorities during audits and inspections",
                       "Design and execute employee engagement and welfare programs"],
        },
        "arvind": {
            "mid": ["IR/ER for Arvind's plant workforce at Kadi/Kalol, Gujarat"],
            "senior": ["Plant-level IR leadership reporting into Plant HR Head"],
        },
        "tone_keywords": "IR/ER practices, labour laws, conflict handling, domestic enquiry",
        "qual": "MBA HR / IR / Labour Law",
    },

    # ── SALES & MARKETING (new department) ─────────────────────────────────
    {
        "dept": "sales_marketing", "family": "brand_manager",
        "role_family": "Brand Manager / Senior Brand Manager", "division": "Arvind Fashions Limited",
        "bands": ["mid", "senior", "lead"],
        "core": {
            "mid": ["Brand campaign planning and execution", "Trade marketing coordination",
                    "Retail rollout support and merchandising alignment"],
            "senior": ["Brand P&L ownership", "GTM strategy and licensing management",
                       "Agency management for ATL/BTL campaigns", "Trend forecasting integration into brand strategy"],
            "lead": ["Multi-brand portfolio strategy", "Cross-functional leadership across Design, Retail, and Supply Chain",
                     "Brand licensing negotiation and management"],
        },
        "arvind": {
            "mid": ["Brand support for Arrow, U.S. Polo Assn, or Flying Machine"],
            "senior": ["P&L ownership for a brand within Arvind Fashions' portfolio"],
            "lead": ["Portfolio strategy across Arvind Fashions' Premium Formal / Smart Casual segments"],
        },
        "tone_keywords": "brand positioning, retail analytics, ATL/BTL, licensing, trend forecasting",
        "qual": "MBA Marketing / NIFT / Fashion Management",
    },
    {
        "dept": "sales_marketing", "family": "ceo_brand",
        "role_family": "CEO – Brand", "division": "Arvind Fashions Limited",
        "bands": ["executive"],
        "core": {
            "executive": ["Full P&L ownership for an Arvind Fashions brand", "Retail strategy and omni-channel expansion",
                          "Merchandising and licensing management at brand level", "Board and stakeholder reporting"],
        },
        "arvind": {
            "executive": ["CEO role across brands: Arrow, USPA, Flying Machine, Ed Hardy, or Cole Haan"],
        },
        "tone_keywords": "P&L ownership, retail strategy, omni-channel, merchandising, licensing",
        "qual": "15-25 years senior leadership experience",
    },
    {
        "dept": "sales_marketing", "family": "chief_revenue_officer",
        "role_family": "Chief Revenue Officer (CRO)", "division": "Arvind Fashions Limited",
        "bands": ["executive"],
        "core": {
            "executive": ["Full sales portfolio ownership across all brands and channels (EBO, MBO, LFS, online)",
                          "Sales operations and channel strategy design", "Omni-channel transformation leadership",
                          "Cross-functional leadership spanning Sales, Marketing, and Retail Ops"],
        },
        "arvind": {
            "executive": ["CRO role spanning Arvind Fashions' full brand and channel portfolio"],
        },
        "tone_keywords": "sales operations, channel strategy, omni-channel, cross-functional leadership",
        "qual": "20+ years across sales & operations",
    },
    {
        "dept": "sales_marketing", "family": "sales_manager_home_linen",
        "role_family": "Sales Manager – Home Linen", "division": "Ankur Textiles (Arvind Limited)",
        "bands": ["mid", "senior"],
        "core": {
            "mid": ["Primary field sales representation for assigned Home Linen zone",
                     "Relationship management with dealers, distributors, and retailers",
                     "Lead generation, follow-up, and conversion",
                     "Coordination with internal teams for order processing and delivery"],
            "senior": ["Support Zonal Head on sales strategy and market expansion",
                       "Institutional customer relationship management",
                       "Market intelligence and competitor activity tracking",
                       "Trade activation, sampling, and promotional execution"],
        },
        "arvind": {
            "mid": ["Field sales for Ankur Textiles' Home Linen portfolio across assigned zone"],
            "senior": ["Zonal sales leadership supporting Ankur Textiles' pan-India expansion"],
        },
        "tone_keywords": "field sales, dealer/distributor management, target-driven, high-travel",
        "qual": "Graduate with field sales experience",
    },

    # ── RETAIL (additions) ──────────────────────────────────────────────────
    {
        "dept": "retail", "family": "fashion_consultant",
        "role_family": "Fashion Consultant / Retail Sales Associate", "division": "Arvind Brands",
        "bands": ["junior"],
        "core": {
            "junior": ["Customer service and styling advice", "Product knowledge across brand collections",
                       "Upselling and cross-selling techniques", "Store planning and merchandising basics"],
        },
        "arvind": {
            "junior": ["Customer-facing role at an Arvind Brands EBO (Arrow, USPA, Flying Machine, etc.)"],
        },
        "tone_keywords": "customer service, styling, upselling, store basics",
        "qual": "Graduate, 0-3 years",
    },
    {
        "dept": "retail", "family": "area_sales_manager",
        "role_family": "Area Sales Manager / Regional Manager", "division": "Arvind Brands",
        "bands": ["senior", "lead"],
        "core": {
            "senior": ["Multi-store performance management", "Field team leadership and training",
                       "Store expansion tracking", "Scheme execution and promotional rollout"],
            "lead": ["Regional P&L ownership across store clusters", "Retail analytics and BTL activation strategy",
                     "MIS reporting to brand leadership", "New store opening project management"],
        },
        "arvind": {
            "senior": ["Area management across an Arvind Brands cluster of EBOs/MBOs"],
            "lead": ["Regional leadership for Arvind Brands across a city tier or state"],
        },
        "tone_keywords": "retail analytics, team management, BTL activation, MIS, EBO/MBO/LFS",
        "qual": "Graduate/MBA, 7-12 years",
    },

    # ── DESIGN & MERCHANDISING (new department) ─────────────────────────────
    {
        "dept": "design_merchandising", "family": "fashion_designer",
        "role_family": "Fashion Designer", "division": "Arvind Fashions Limited",
        "bands": ["mid", "senior"],
        "core": {
            "mid": ["Trend research and seasonal concept development", "CAD development for garment design",
                     "Colour forecasting integration", "Tech pack preparation for production handoff"],
            "senior": ["Full collection design ownership", "Cross-brand design language consistency",
                       "Vendor and production team collaboration for sample development",
                       "Design team mentorship"],
        },
        "arvind": {
            "mid": ["Design support for an Arvind Fashions brand collection cycle"],
            "senior": ["Lead designer role for a brand within Arvind Fashions' portfolio"],
        },
        "tone_keywords": "Adobe Illustrator, CorelDRAW, NIFT/NID training, tech packs, CADs",
        "qual": "NIFT / NID / Pearl Academy",
    },
    {
        "dept": "design_merchandising", "family": "merchandiser",
        "role_family": "Merchandiser / Buying Manager", "division": "Arvind Fashions Limited",
        "bands": ["mid", "senior", "lead"],
        "core": {
            "mid": ["Range planning support", "Open-to-buy (OTB) tracking", "Vendor coordination for sampling and delivery"],
            "senior": ["Full range planning and OTB management", "Trend analysis integration into buying decisions",
                       "Vendor negotiation and capacity planning"],
            "lead": ["Category-level buying strategy", "Cross-functional alignment with Design and Retail",
                     "Margin and markdown strategy ownership"],
        },
        "arvind": {
            "mid": ["Merchandising support for an Arvind Fashions brand category"],
            "senior": ["OTB ownership for a brand category within Arvind Fashions"],
            "lead": ["Category buying leadership across Arvind Fashions' brand portfolio"],
        },
        "tone_keywords": "OTB management, range planning, vendor negotiation, trend analysis",
        "qual": "NIFT / FMS / MBA (Retail)",
    },

    # ── IT / DIGITAL TECHNOLOGY (additions) ─────────────────────────────────
    {
        "dept": "it", "family": "it_manager_digital",
        "role_family": "IT Manager / Digital Transformation", "division": "Arvind Limited — IT",
        "bands": ["senior", "lead"],
        "core": {
            "senior": ["ERP rollout and system integration management", "Data governance frameworks",
                       "Digital initiative project management", "Infrastructure planning and vendor management"],
            "lead": ["Digital transformation strategy across business units", "API integration architecture",
                     "Cybersecurity governance oversight", "Cross-functional digital roadmap ownership"],
        },
        "arvind": {
            "senior": ["SAP core module rollout across Arvind plants"],
            "lead": ["Digital transformation leadership ahead of Arvind's GCC expansion"],
        },
        "tone_keywords": "SAP, Microsoft Azure, Power BI, API integration, project management",
        "qual": "B.Tech CS/IT + MBA or relevant tech degree",
    },
    {
        "dept": "it", "family": "data_analyst_powerbi",
        "role_family": "Sr. Specialist – Power BI Reporting (Data Analyst)", "division": "Arvind Limited",
        "bands": ["mid", "senior"],
        "core": {
            "mid": ["Design Power BI reports: daily ops views to multi-page reports with filters, slicers, drill-throughs",
                     "Write DAX measures: YTD, MTD, period-over-period, running totals, conditional formatting",
                     "Apply bookmarks, tooltips, dynamic titles, and page navigation purposefully",
                     "Gather requirements from operations managers, commercial leads, and finance teams"],
            "senior": ["Build executive summary AND operational detail views",
                       "Diagnose and resolve report performance issues (slow visuals, heavy queries, inefficient DAX)",
                       "Manage Power BI deployment pipelines (dev → test → production)",
                       "Maintain documentation per report: what it shows, data source, audience"],
        },
        "arvind": {
            "mid": ["Power BI reporting from Microsoft Fabric data lake — manufacturing/retail domain"],
            "senior": ["OEE, OTIF, sell-through, shrinkage, and margin reporting for Arvind's manufacturing/retail operations"],
        },
        "tone_keywords": "Power BI, DAX, Microsoft Fabric, manufacturing/retail KPIs, PL-300",
        "qual": "B.Tech/BCA + Power BI/DAX expertise, 5-7 years",
    },

    # ── ENVIRONMENTAL / PROCESS ENGINEERING (new department — Arvind Envisol) ─
    {
        "dept": "environmental", "family": "process_engineer",
        "role_family": "Proposal / Process Engineer", "division": "Arvind Envisol Limited",
        "bands": ["mid", "senior"],
        "core": {
            "mid": ["Study enquiries, prepare preliminary drawings, and create cost estimations",
                     "Process engineering for water and wastewater treatment plants",
                     "Prepare BEP and Basic Engineering Drawings: PFD, P&ID, HFD",
                     "Process equipment selection and technical specification"],
            "senior": ["Lead proposal preparation: design, process description, control philosophy, scope of supply",
                       "Tender study, specification analysis, and pre-bid query resolution",
                       "Process scheme selection across MBR, RO, ZLD technologies",
                       "Technical evaluation and cost estimation of process equipment"],
        },
        "arvind": {
            "mid": ["Proposal engineering for Arvind Envisol's water/wastewater treatment projects"],
            "senior": ["Process scheme leadership for Arvind Envisol's ZLD and patented polymeric film evaporation technology"],
        },
        "tone_keywords": "process design, proposal engineering, BEP/PFD/P&ID, ZLD, MBR, RO",
        "qual": "B.Tech Chemical / Environmental Engineering",
    },
    {
        "dept": "environmental", "family": "project_manager_etp",
        "role_family": "Project Manager – ETP/STP", "division": "Arvind Envisol Limited",
        "bands": ["senior", "lead"],
        "core": {
            "senior": ["EPC project execution for ETP/STP installations", "Contract management with vendors and subcontractors",
                       "EHS compliance enforcement on project sites", "Commissioning and handover management"],
            "lead": ["Multi-project portfolio leadership", "Client relationship management for large ZLD projects",
                     "Project profitability and timeline ownership", "Team leadership across project sites"],
        },
        "arvind": {
            "senior": ["ETP/STP project delivery for Arvind Envisol's industrial clients"],
            "lead": ["Project portfolio leadership across Arvind Envisol's ZLD project pipeline"],
        },
        "tone_keywords": "EPC project management, contract management, EHS compliance, commissioning",
        "qual": "B.Tech + PMP preferred, 8-15 years",
    },

    # ── TELECOM / AV (new department — Arvind Syntel) ──────────────────────
    {
        "dept": "telecom", "family": "enterprise_sales_manager",
        "role_family": "Enterprise Sales Manager – AV/Telecom/Networking/Security", "division": "Arvind Syntel",
        "bands": ["senior", "lead"],
        "core": {
            "senior": ["Enterprise business development and revenue growth", "End-to-end project sales lifecycle: lead generation to closure",
                       "Opportunity identification across AV, Telecom, Networking, and Security domains",
                       "Relationship building with corporate clients"],
            "lead": ["Government and large enterprise account ownership", "Techno-commercial solution selling leadership",
                     "OEM and System Integrator partnership management", "Sales team leadership and pipeline ownership"],
        },
        "arvind": {
            "senior": ["Enterprise sales for Arvind Syntel's AV, Telecom, and Security solutions portfolio"],
            "lead": ["Regional sales leadership across Mumbai/Ahmedabad/Hyderabad for Arvind Syntel"],
        },
        "tone_keywords": "solution selling, techno-commercial, system integrator, OEM relationships",
        "qual": "10+ years B2B/Enterprise Sales",
    },
    {
        "dept": "telecom", "family": "presales_network_engineer",
        "role_family": "Pre-sales / Network Engineer", "division": "Arvind Syntel",
        "bands": ["mid", "senior"],
        "core": {
            "mid": ["LAN/WAN design support", "CCTV and access control system configuration", "AV integration technical support"],
            "senior": ["SD-WAN architecture and deployment", "Pre-sales technical proposal development",
                       "Cisco-certified network design (CCNA/CCNP)", "Client-facing technical demonstrations"],
        },
        "arvind": {
            "mid": ["Network and security technical support for Arvind Syntel's enterprise clients"],
            "senior": ["Pre-sales technical leadership for Arvind Syntel's networking and security practice"],
        },
        "tone_keywords": "LAN/WAN, SD-WAN, CCTV, access control, Cisco CCNA/CCNP",
        "qual": "B.Tech/Diploma + Cisco certifications preferred",
    },
]


# ════════════════════════════════════════════════════════════════════════════
# REAL SCRAPED JDs (verbatim, gold-standard) — mapped to role families above
# ════════════════════════════════════════════════════════════════════════════

REAL_JDS = [
    {
        "dept": "it", "family": "data_analyst_powerbi", "band": "senior",
        "role_title": "Sr. Specialist – Power BI Reporting (Data Analyst)",
        "text": """Role Summary
You will build Power BI reports and dashboards from a Microsoft Fabric data lake for Arvind Limited's manufacturing and retail operations in Ahmedabad. Manufacturing or retail domain experience is mandatory. You will work directly with operations managers, commercial leads, and finance teams to translate business questions into clear, performant reports.

Key Responsibilities
- Design Power BI reports: daily ops views through multi-page reports with filters, slicers, and drill-throughs
- Write DAX measures: YTD, MTD, period-over-period, running totals, % calculations, conditional formatting
- Apply bookmarks, tooltips, dynamic titles, and page navigation purposefully
- Build executive summary AND operational detail views for the same dataset
- Diagnose and resolve report performance issues — slow visuals, heavy queries, inefficient DAX
- Gather requirements directly from operations managers, commercial leads, and finance teams
- Manage Power BI deployment pipelines across dev, test, and production environments
- Maintain documentation for every report: what it shows, data source, and intended audience

Must-Have Skills
- Power BI (full toolkit) including bookmarks, tooltips, and drill-through navigation
- DAX: YTD/MTD/variance/rolling average calculations
- Microsoft Fabric (Direct Lake / import mode)
- Manufacturing or retail domain knowledge: OEE, OTIF, sell-through, shrinkage, margin
- Strong stakeholder communication skills
- Clean, readable report design sensibility

Nice-to-Have Skills
- PL-300 certification
- Power BI mobile layout design
- Experience managing deployment pipelines
- Basic data pipeline understanding

What We Offer
Exposure to Arvind's manufacturing and retail data at scale, direct collaboration with business leadership, and the opportunity to shape reporting standards as part of Arvind's growing analytics function.""",
    },
    {
        "dept": "finance", "family": "r2r_manager", "band": "lead",
        "role_title": "Manager – Record to Report (R2R)",
        "text": """Role Summary
You will manage end-to-end Record to Report operations for Arvind Limited in Ahmedabad, reporting to the Senior Manager / Finance Controller. You will own General Ledger, Fixed Assets, Intercompany Accounting, Accruals, and Provisions across the entity, ensuring accurate and timely financial close.

Key Responsibilities
- Manage end-to-end R2R: GL, Fixed Assets, Intercompany Accounting, Accruals, Provisions, BS Reconciliations
- Drive timely month-end, quarter-end, and year-end close
- Review journal entries, account reconciliations, and financial reports
- Prepare financial statements per IFRS / US GAAP / local accounting standards
- Coordinate directly with internal and external auditors
- Drive process improvements, standardization, and automation across the R2R function
- Track KPIs and SLAs for finance shared services delivery
- Collaborate closely with AP, AR, FP&A, Tax, and Treasury teams
- Lead, mentor, and develop team members
- Support system implementations and finance transformation initiatives

Must-Have Skills
- CA / CMA / CPA / MBA Finance
- 10-12 years in Finance & Accounting
- GL accounting, financial reporting, and reconciliation expertise
- IFRS / US GAAP / internal controls knowledge
- Shared Services / BPO / GCC / MNC background preferred
- ERP experience: SAP / Oracle / Microsoft Dynamics

Nice-to-Have Skills
- BlackLine / Hyperion exposure
- Process transitions and continuous improvement experience

What We Offer
Leadership of a critical finance function within Arvind's shared services structure, exposure to multi-entity consolidation, and a clear path toward broader finance transformation ownership.""",
    },
    {
        "dept": "hr", "family": "payroll_welfare_officer", "band": "mid",
        "role_title": "Payroll & Welfare Officer",
        "text": """Role Summary
You will own worker welfare, recruitment, and payroll operations for Arvind Limited's garment factory in Bengaluru. This is a walk-in role reporting into the plant HR function, covering statutory compliance across the Factories Act, Minimum Wages Act, ESI Act, and EPF Act.

Key Responsibilities
- Maintain statutory facilities: canteen, first aid, crèche, drinking water, sanitation, restrooms
- Organize health check-ups, safety training, hygiene awareness, and wellness programs
- Handle worker grievances and mediate disputes; conduct welfare assessments
- Assess workforce needs with production and HR teams
- Source and recruit skilled/unskilled workers via employment exchanges, institutes, and local networks
- Conduct interviews and skill assessments (stitching, finishing); manage onboarding and induction
- Process attendance, overtime, and leave for accurate wage calculation
- Run monthly payroll as per the Minimum Wages Act
- Manage statutory deductions — ESI, EPF — with timely submissions
- Maintain statutory records and support labour inspections and audits

Must-Have Skills
- Payroll software proficiency
- Labour law compliance: Factories Act 1948, Minimum Wages Act, Payment of Wages Act, ESI Act, EPF Act
- Interpersonal and counselling skills for grievance handling
- Hindi plus local dialect fluency preferred

What We Offer
Direct ownership of worker welfare and payroll for a large garment manufacturing workforce, with exposure to the full HR generalist lifecycle on the shop floor.""",
    },
    {
        "dept": "manufacturing", "family": "associate_manager_nonwoven", "band": "mid",
        "role_title": "Associate Manager – Production (Needle Punch Non-Woven)",
        "text": """Role Summary
You will ensure efficient Needle Punch Non-Woven production at Arvind Advanced Materials' Dholka, Gujarat facility, reporting to the Chief Manager – Non-Woven Production. You will own production targets, quality, waste minimization, and machine performance for this Grade E1-E2 role.

Key Responsibilities
- Ensure efficient Needle Punch Non-Woven production: achieve targets, maintain quality, minimize waste
- Optimize machine performance and ensure safety and process standards
- Manage Carding, Cross-Lapping, Drafting, and Needle Loom operations
- Control GSM, Thickness, Density, Width, and Mechanical Properties to specification
- Apply Root Cause Analysis and structured problem-solving to production issues
- Coordinate across the production flow: Fibre Opening & Blending → Carding → Cross Lapper → Needle Punch Line → Finishing → QA → Maintenance → Planning & Dispatch
- Manage team and manpower across shifts
- Maintain ERP/SAP records and enforce 5S and safety standards

Must-Have Skills
- Needle Punch Non-Woven process expertise
- Fibre properties knowledge: Polyester, Polypropylene, Meta-Aramid, Para-Aramid, Viscose, Recycled Fibres
- Carding, Cross-Lapping, Drafting, Needle Loom operations
- RCA and structured problem-solving
- Team and manpower management
- ERP/SAP and MS Office proficiency
- 5S and safety standard enforcement

What We Offer
Diploma or Degree in Textile Technology / Nonwoven Technology required, with 2-5 years of experience. Direct ownership of a production line within Arvind's growing Advanced Materials business.""",
    },
    {
        "dept": "hr", "family": "industrial_relations", "band": "mid",
        "role_title": "Associate Manager – Industrial Relations / Employee Relations",
        "text": """Role Summary
You will manage day-to-day industrial and employee relations for Arvind Limited's plant in Kadi / Kalol, Gujarat, ensuring harmonious relations between workers, contract labour, and supervisors while maintaining full labour law compliance.

Key Responsibilities
- Handle day-to-day employee grievances and drive resolution
- Maintain harmonious relations across workers, contract labour, and supervisors
- Ensure labour law compliance and maintain statutory records
- Coordinate with contractors on attendance, wages, PF/ESIC, and documentation
- Manage disciplinary actions, domestic enquiries, and misconduct cases
- Conduct shop-floor rounds for discipline and engagement monitoring
- Assist in audits, inspections, and labour authority liaison
- Drive employee engagement and welfare activities

Must-Have Skills
- IR/ER practices and case management
- Labour law knowledge
- Strong communication and conflict-handling skills
- Documentation and compliance management

What We Offer
Salary range of ₹35,417–50,000/month for this full-time, on-site plant HR role, with direct exposure to Arvind's industrial relations function at one of its key Gujarat manufacturing sites.""",
    },
    {
        "dept": "sales_marketing", "family": "sales_manager_home_linen", "band": "mid",
        "role_title": "Sales Manager – Home Linen",
        "text": """Role Summary
You will serve as the primary field sales representative for an assigned Home Linen zone under Ankur Textiles (a division of Arvind Limited), supporting the Zonal Head on sales, market expansion, and customer servicing across a pan-India territory.

Key Responsibilities
- Act as the primary field sales rep for your assigned Home Linen zone
- Support the Zonal Head on sales execution, market expansion, and customer servicing
- Build and maintain relationships with dealers, distributors, retailers, and institutional customers
- Drive lead generation, follow-up, and conversion
- Coordinate with internal teams for order processing, delivery, and issue resolution
- Gather and share market intelligence, competitor activity, and customer feedback
- Assist with promotions, launches, sampling, and trade activations

Must-Have Skills
- Field sales experience
- Customer relationship management
- Strong communication and negotiation skills
- Home Linen product and market knowledge
- Comfort with a target-driven, high-travel environment
- Reporting and follow-up discipline

What We Offer
Pan-India opportunities across North/East/West/South zones, with direct exposure to Ankur Textiles' Home Linen growth strategy under the Arvind Limited umbrella.""",
    },
    {
        "dept": "manufacturing", "family": "shift_supervisor_dyeing", "band": "mid",
        "role_title": "Shift Supervisor – Dyeing (Cotton Yarn / CCM)",
        "text": """Role Summary
You will develop and manage dyeing recipes for cotton yarn at Arvind Limited's Ahmedabad textile manufacturing facility, owning the Computer Colour Matching (CCM) system and ensuring lab-to-bulk shade reproducibility for customer orders.

Key Responsibilities
- Develop and formulate dyeing recipes for cotton yarn per customer shade requirements
- Perform lab dyeing trials and colour matching against approved standards
- Operate and manage the Computer Colour Matching (CCM) System: recipe generation and shade correction
- Analyze colour deviations and adjust recipes for the desired shade
- Ensure lab-to-bulk reproducibility across production runs
- Maintain records of dye formulations, lab trials, approvals, and colour data
- Collaborate with production, QA, and merchandising teams for timely shade approvals
- Optimize recipes for cost, quality, and process efficiency
- Conduct fastness and quality evaluations per customer and industry standards
- Troubleshoot dyeing and shade variation issues
- Ensure safety, environmental, and QMS compliance

Must-Have Skills
- Dyeing recipe formulation
- CCM System operation
- Colour matching and deviation analysis
- Lab-to-bulk consistency management
- Fastness testing standards knowledge
- QMS compliance

What We Offer
Hands-on ownership of the colour matching function for Arvind's cotton yarn dyeing operations, with direct collaboration across production, QA, and merchandising teams.""",
    },
    {
        "dept": "environmental", "family": "process_engineer", "band": "senior",
        "role_title": "Associate/Deputy Manager – Proposal & Costing",
        "text": """Role Summary
You will lead proposal engineering and cost estimation for water and wastewater treatment projects at Arvind Envisol Limited, based in Pune or Ahmedabad. Arvind Envisol delivers world-class water management — water treatment, industrial wastewater, sewage treatment, and Zero Liquid Discharge (ZLD) solutions — including patented polymeric film evaporation technology.

Key Responsibilities
- Study enquiries and prepare preliminary drawings, estimations, and offers
- Lead proposal preparation, project bidding, tendering, and cost estimation for water and wastewater treatment projects
- Own process engineering for water and wastewater treatment plants
- Select process schemes for plants based on technical and commercial requirements
- Prepare BEP and Basic Engineering Drawings: PFD, P&IDs, HFD
- Select process equipment and prepare technical specifications
- Conduct technical evaluation and cost estimation of process equipment
- Study tenders, analyze specifications, resolve pre-bid queries, and select schemes
- Develop technical proposals: design, process description, control philosophy, scope of supply

Must-Have Skills
- Process Design and Proposal Engineering
- Cost Estimation
- BEP / PFD / P&ID / HFD preparation
- Water & Wastewater Treatment domain knowledge: ETP, STP, ZLD, MBR, RO
- Strong technical writing skills

What We Offer
Direct exposure to Arvind Envisol's patented ZLD technology and a ₹266 Cr revenue water management business, with end-to-end ownership of the proposal lifecycle.""",
    },
    {
        "dept": "telecom", "family": "enterprise_sales_manager", "band": "lead",
        "role_title": "Enterprise Sales Manager – AV/Telecom/Networking/Security",
        "text": """Role Summary
You will drive enterprise business growth across Audio-Visual (AV), Telecom, Data Networking, and Security Solutions for Arvind Syntel, Arvind Limited's telecom division, across Mumbai, Ahmedabad, and Hyderabad. This is a techno-commercial role suited to candidates with a System Integrator or OEM background.

Key Responsibilities
- Drive enterprise business development and revenue growth
- Own the end-to-end project sales lifecycle: lead generation through closure
- Identify opportunities across AV, Telecom, Networking, and Security domains
- Build strong relationships with both corporate and government clients

Must-Have Skills
- Enterprise/B2B solution selling expertise
- Domain knowledge across AV systems, Telecom, Data Networking, and Security
- Strong techno-commercial acumen
- System Integrator or OEM background
- Government and corporate client management experience
- Full project sales cycle ownership

What We Offer
A remote-flexible enterprise sales role with 10+ years of B2B sales experience required, covering Arvind Syntel's full AV, Telecom, Networking, and Security solutions portfolio across corporate and government accounts.""",
    },
]


def build_taxonomy(role: dict) -> dict:
    """Build the experience_bands YAML structure for a role definition."""
    bands_out = {}
    for band in role["bands"]:
        label, years, tag = BAND_LABELS[band]
        bands_out[band] = {
            "label": label,
            "years": years,
            "seniority_tag": tag,
            "core_skills": role["core"].get(band, []),
            "progressive_skills": [],
            "arvind_specific": role["arvind"].get(band, []),
            "leadership_skills": [],
        }
    return {
        "role_family": role["role_family"],
        "department": role["dept"].replace("_", " ").title(),
        "division": role["division"],
        "company": "Arvind Limited",
        "experience_bands": bands_out,
    }


def build_tone_guide(role: dict) -> str:
    title = role["role_family"]
    division = role["division"]
    keywords = role["tone_keywords"]
    qual = role["qual"]
    return f"""TONE GUIDE — {title} · {division}

Voice: Precise, Arvind-specific, and grounded in real operational detail. Avoid generic
corporate language — name the plant, the brand, the system, or the regulation wherever
the skills taxonomy supports it.

DO:
- Reference {division} explicitly in the Role Summary
- Use second-person language throughout: "You will own...", "You will lead...", "You will manage..."
- Name concrete tools, certifications, or domain terms: {keywords}
- Calibrate scope and language precisely to the YoE band requested
- Reflect the qualifications expected for this role: {qual}

DO NOT:
- Use vague phrases like "responsible for quality" or "good communication skills" without specifics
- Overstate scope at junior bands or understate ownership at senior/lead bands
- Use buzzwords (rockstar, ninja, passionate, driven) — Arvind JDs are operational, not aspirational

Structure expectations:
- Role Summary: Arvind business unit / division context, scope of ownership, location if relevant
- Key Responsibilities: specific, action-verb-led tasks calibrated to the YoE band
- Must-Have Skills: non-negotiable requirements drawn from the skills taxonomy
- Nice-to-Have Skills: differentiating but non-mandatory qualifications
- What We Offer: Arvind scale, learning opportunities (Samarth / Arvind University where relevant), and DEI/EEO statement
"""


def write_role(role: dict) -> None:
    dept, family = role["dept"], role["family"]
    base = KB_ROOT / dept / family
    (base / "sample_jds").mkdir(parents=True, exist_ok=True)
    (base / "feedback").mkdir(parents=True, exist_ok=True)

    # skills_taxonomy.yaml
    taxonomy = build_taxonomy(role)
    (base / "skills_taxonomy.yaml").write_text(
        yaml.dump(taxonomy, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    # tone_guide.txt
    (base / "tone_guide.txt").write_text(build_tone_guide(role), encoding="utf-8")

    # version.yaml
    (base / "version.yaml").write_text(
        yaml.dump(VERSION_DEFAULTS, allow_unicode=True), encoding="utf-8"
    )


def write_real_jd(entry: dict) -> None:
    """Write a verbatim scraped JD into the matching role family's sample_jds/."""
    dept, family, band = entry["dept"], entry["family"], entry["band"]
    sample_dir = KB_ROOT / dept / family / "sample_jds"
    sample_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(sample_dir.glob(f"{band}_*.txt"))
    next_idx = len(existing) + 1
    filename = sample_dir / f"{band}_{next_idx:03d}.txt"

    metadata = {
        "jd_id": str(uuid.uuid4())[:8],
        "role_family": entry["role_title"],
        "yoe_band": band,
        "source": "real_scraped_jd",
        "date_added": datetime.now().strftime("%Y-%m-%d"),
        "approved_by": "kb_import",
    }
    content = json.dumps(metadata) + "\n\n---\n\n" + entry["text"]
    filename.write_text(content, encoding="utf-8")


def main():
    created = 0
    for role in ROLES:
        write_role(role)
        created += 1
    print(f"Created/updated {created} role family KB folders.")

    jds_written = 0
    for entry in REAL_JDS:
        write_real_jd(entry)
        jds_written += 1
    print(f"Wrote {jds_written} verbatim real JDs into matching sample_jds/.")


if __name__ == "__main__":
    main()
