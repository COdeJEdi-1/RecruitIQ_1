"""
KB Builder — Arvind Limited (Stage 1: uploaded-docs KB only)

Builds /kb_master/{DEPARTMENT}/{role_family}/ from 41 uploaded JD/context
documents in /Users/chahatd/Downloads/JDs/. Isolated from the live app's
/kb/ folder (different naming convention: ALL CAPS departments, en-dash
YoE bands) — Stage 1 deliverable only, no backend/UI wiring.

Run: python3 build_kb_master.py
"""

import json
from datetime import datetime
from pathlib import Path

import yaml

KB_ROOT = Path(__file__).parent / "kb_master"
TODAY = "2026-06-25"

DEPT_TO_DIVISION = {
    "MANUFACTURING / PRODUCTION": "MANUFACTURING & PLANT OPERATIONS",
    "INDUSTRIAL ENGINEERING": "MANUFACTURING & PLANT OPERATIONS",
    "QUALITY ASSURANCE / QUALITY CONTROL": "MANUFACTURING & PLANT OPERATIONS",
    "MAINTENANCE & ENGINEERING": "MANUFACTURING & PLANT OPERATIONS",
    "RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT": "MANUFACTURING & PLANT OPERATIONS",
    "SUPPLY CHAIN & LOGISTICS": "MANUFACTURING & PLANT OPERATIONS",
    "HUMAN RESOURCES": "CORPORATE / SHARED FUNCTIONS",
    "FINANCE & ACCOUNTS": "CORPORATE / SHARED FUNCTIONS",
    "INFORMATION TECHNOLOGY": "CORPORATE / SHARED FUNCTIONS",
    "LEGAL & COMPLIANCE": "CORPORATE / SHARED FUNCTIONS",
    "STRATEGY & CORPORATE DEVELOPMENT": "CORPORATE / SHARED FUNCTIONS",
    "SUSTAINABILITY / ESG": "CORPORATE / SHARED FUNCTIONS",
    "MARKETING & COMMUNICATIONS": "CORPORATE / SHARED FUNCTIONS",
    "SUPPLY CHAIN / PROCUREMENT": "CORPORATE / SHARED FUNCTIONS",
    "RETAIL OPERATIONS": "RETAIL & BRANDS (ARVIND BRANDS)",
    "MERCHANDISING & BUYING": "RETAIL & BRANDS (ARVIND BRANDS)",
    "DESIGN": "RETAIL & BRANDS (ARVIND BRANDS)",
}

BAND_LABELS = {
    "junior":    ("Junior / Executive", "0–2", "Junior"),
    "mid":       ("Senior Executive / Assistant Manager", "2–5", "Mid"),
    "senior":    ("Manager / Senior Manager", "5–8", "Senior"),
    "lead":      ("Deputy General Manager / General Manager", "8–12", "Lead"),
    "executive": ("Vice President / Chief Officer", "12+", "Executive"),
}
BAND_ORDER = ["junior", "mid", "senior", "lead", "executive"]


def slugify(text: str) -> str:
    out = []
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in (" ", "-", "/", "_", "&"):
            out.append("_")
    s = "".join(out)
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


# ════════════════════════════════════════════════════════════════════════════
# ROLE FAMILY DATA — extracted verbatim from uploaded documents
# ════════════════════════════════════════════════════════════════════════════
# Each entry: dept, role_family, bands{ band_key: {...} }, jds[ {band, source_doc, text} ]

ROLES = []

# ── 1. LEGAL & COMPLIANCE — Head Legal ──────────────────────────────────────
ROLES.append({
    "dept": "LEGAL & COMPLIANCE",
    "role_family": "Head Legal",
    "source_docs": ["2-JD-Head-Legal (2) (1).pdf"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Analyse and identify legal risks and implications of business transactions",
                "Keep senior management informed of developments in laws and regulations that potentially affect the business",
                "Drafting of MOUs, Term Sheets, Agreements, Commercial Contracts, Agreement to Sell, Conveyance Deeds, Notices, Security Documents and other transaction/structuring documents pertaining to Real Estate business",
                "Understand, review and comment on Title due diligence",
                "Understand various court processes and advise management on legal strategy",
                "Liaise with authorities like Revenue, Stamp, RERA, etc.",
                "Ensure compliance of various applicable laws",
                "Experience working with senior legal professionals on various drafting and litigation matters",
            ],
            "arvind_specific": ["Arvind Smartspaces — Real Estate business legal function"],
            "leadership_skills": ["Independently heads the large Legal department"],
            "qualifications": [
                "Law Graduate from a Premier Law Institute / National Law School",
                "10+ years of experience",
                "Strong legal acumen and drafting skills",
                "Strong communication skills",
                "Knowledge of Real Estate transactions, drafting, relevant laws and RERA",
                "Ability to read and understand Gujarati or Kannada an added advantage",
                "Knowledge of Gujarat and/or Karnataka Revenue Laws",
            ],
            "kpis": [],
            "reporting_to": "Chief Operating Officer",
        },
    },
    "jds": [],
})

# ── 2. SUPPLY CHAIN & LOGISTICS — Head – Supply Chain (Knits) ──────────────
ROLES.append({
    "dept": "SUPPLY CHAIN & LOGISTICS",
    "role_family": "Head – Supply Chain (Knits)",
    "source_docs": ["About Arvind and JD - Head SCM, Indigo knits.pdf"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Oversee supply chain (quality, production, product development, technical services) operations of Indigo Knitted fabric (circular, jacquard, warp knits) and Seamless/full Garment (Shimaseiki) operations: Production, Quality, Procurement, Product Development",
                "As a member of the core team, manage complete operations for indigo knit fabrics and seamless to deliver on bottom line performance measures",
                "Ensure targets are met year-on-year; work with stakeholders for smooth operations",
                "Manage production activities through better planning to ascertain viability of production plans",
                "Ensure timely conduct of daily meetings, discuss/follow up issues until resolved",
                "Investigate/review all operations, identify failures, ensure implementation of permanent corrective actions",
                "Contribute to process improvement through continuous improvement initiatives",
                "Analyze training needs for special operations/attachment requirements",
                "Ensure accurate and timely reporting of output to management",
                "Set up and accreditation of knits lab; set up the technical service department",
                "Manage and ensure implementation of quality/control systems/processes to meet product/process quality requirements",
                "Manage the quality assurance department: set targets, plan work, obtain feedback, address issues, allocate resources",
                "Monitor audits; implement, maintain, review and improve quality assurance and control systems/processes",
                "Liaise with customers and suppliers; evaluate feasibility of new embellishment plants and non-conformity issues",
                "Develop, implement, and manage the Procurement Strategy",
                "Lead development and implementation of procurement policies and system strategies: tendering, contracts management, spend analytics, supplier performance management",
                "Drive continuous improvement, best value and quality improvements within team and departments",
                "Develop new products or improve existing products with thrust on reducing cost",
                "Develop fabrics in line with the strategic vision of the Company",
                "Develop innovation pipeline with new performance materials for unique customer experiences on performance, delivery, and cost",
                "New edge technology upgradation or introduction",
                "Drive development & fabric delivery timings with clear understanding of development cycle and production strategy",
                "Build on existing expertise in fabrics processing with focus on best-in-class; apply environmental knowledge to fabric knitting & processing selection",
            ],
            "arvind_specific": ["Indigo Knitted fabric and Seamless/full Garment (Shimaseiki) operations"],
            "leadership_skills": ["Core team member managing complete operations for indigo knit fabrics and seamless garmenting"],
            "qualifications": ["Around 20 years of experience in Knit Fabric & Garmenting Operations"],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 3 & 4. RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT ─────────────────────
ROLES.append({
    "dept": "RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT",
    "role_family": "Head – Product Development (Dress Shirts)",
    "source_docs": ["About Arvind and JD- Dress Shirts Category.docx"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Develop new products for Dress Shirt category fabrics in line with market requirements and business opportunity",
                "Worked extensively in Dress Shirt Category, yarn dyed, specialty in Fabric Finishing",
                "Sustaining, Transformative & Disruptive Product Innovation",
                "Build business through seasonal product newness & material innovation",
                "In-depth product knowledge, insights on cutting-edge innovation, overall understanding of Dress Shirt Category business",
                "Handle complete fabric product development from fiber to fabric design",
                "Develop product range in yarn for men's and women's wear",
                "Liaise with design, product & process development teams",
                "Understand customer trends and create new products to establish business in the market",
                "Set up and oversee continuous new product development for business growth",
                "Assist in raw material sourcing strategy",
            ],
            "arvind_specific": [
                "Foray into Dress Shirt category for Arvind's Textile business",
                "Target companies: Luthai Textile Co. Ltd., Lufeng Company Ltd., Jiangsu Lianfa Textile Co. Ltd, Penn Fabrics, Younger, Esquel — PVH heritage Dress Shirt Design/R&D experience",
            ],
            "leadership_skills": ["Reports to Executive Director"],
            "qualifications": [
                "Bachelors / Masters in Textile Engineering",
                "Minimum 15 years of experience",
                "Very strong on the technical side of textile manufacturing; understands all manufacturing processes in detail",
                "Strong technical expertise in product development on woven fabrics",
                "Commercialization ability and strong result orientation",
            ],
            "kpis": [],
            "reporting_to": "Mr. Punit Lalbhai, Executive Director",
        },
    },
    "jds": [],
})

ROLES.append({
    "dept": "RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT",
    "role_family": "Head – Product Development & Innovation (Activewear)",
    "source_docs": ["Activewear - JD.doc", "Activewear -Product Development and Innovation Head.docx"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Lead the activewear (casual wear at work or at sports) business with thorough experience/exposure in Fabric manufacturing, Apparel Marketing, Strategic Sourcing, Pricing, Innovation/development, and quality of Fabrics for leading sports/leisure apparel brands",
                "Develop new products for foray into athleisure and performance fabrics space in line with market requirements and business opportunity",
                "Sustaining, Transformative & Disruptive Product Innovation",
                "Build the Sportswear business through seasonal newness & material innovation",
                "In-depth product knowledge, insights on cutting-edge innovation, overall understanding of athleisure business",
                "Plan requirement for modern equipment and machinery needed to set up facility to manufacture the products",
                "Design and set up end-to-end processes for efficient functioning of the unit",
                "Set up and oversee continuous new product development for business growth",
                "Assist in recruitment of senior individuals to head various functions of the business",
                "Assist in raw material sourcing strategy",
                "Lead the team of fabric product development from fiber to fabric design, and fabric to apparel",
                "Collaborate on projects for material development with suppliers",
                "Understand customer trends and create new products to establish business in the market",
                "Present seasonal collections based on customer needs and forecasts, co-create with customers",
            ],
            "arvind_specific": [
                "Companies to target: Nike, Adidas, Reebok, Underarmour, Columbia, Timberland, The North Face, L.L.Bean, Puma, VF Corporation, Paul & Shark, Speedo, Umbro, Kelme, Quiksilver, Vans, New Balance, Oakley, Nan Yang Textile",
                "Location: Ahmedabad, Gujarat, India",
            ],
            "leadership_skills": ["Reports to Mr. Punit Lalbhai, Executive Director"],
            "qualifications": [
                "Bachelors / Masters in Textile Engineering",
                "Minimum 15 years of experience",
                "Strong on the technical side of textile manufacturing; understands manufacturing processes in detail",
                "Strong technical expertise in product development on sports wear / active wear",
                "Commercialization ability and strong result orientation",
                "Decision making, Strategic Planning, Innovative Thinking, Adaptability, Team Management, Target Oriented, Authentic Leadership, Operation Management",
            ],
            "kpis": [],
            "reporting_to": "Mr. Punit Lalbhai, Executive Director",
        },
    },
    "jds": [],
})

# ── 5. STRATEGY & CORPORATE DEVELOPMENT — COO (Institutional, Ahmedabad University) ──
ROLES.append({
    "dept": "STRATEGY & CORPORATE DEVELOPMENT",
    "role_family": "Chief Operating Officer (Institutional)",
    "source_docs": ["Ahmedabad University - JD.pdf"],
    "note": "Not a core Arvind business unit — Ahmedabad University is affiliated with Ahmedabad Education Society (AES), founded with involvement of Kasturbhai Lalbhai. Mapped to closest-fit department (STRATEGY & CORPORATE DEVELOPMENT) per instructions.",
    "bands": {
        "executive": {
            "progressive_skills": [
                "Oversee organization's ongoing operations and procedures to maintain control of operations",
                "Oversee HR, Campus Operations, IT, Finance",
                "Coordinate on large construction projects (internal customer requirements)",
                "Build and coordinate non-faculty organization",
                "Drive organizational & digital transformation & service excellence",
                "Oversee Residential Life",
                "Coordinate campus projects",
                "Medium & Long-term Planning and annual budgeting",
                "Local community relations: maintain peace on campus",
                "Campus health services",
                "Campus technical facilities",
                "Oversee Bookstore, café & merchandize operations",
                "Classrooms, Audio-visual, Instructional Technology",
                "Assist in closure of schools, new school development",
            ],
            "arvind_specific": [],
            "leadership_skills": ["COO-level institutional operations leadership"],
            "qualifications": [
                "Preferable Background: some tech background, MBA, COO experience, diverse background (some experience in health care/hospitality may help)",
                "Research skills", "Confidence", "Determination", "Self-motivation",
                "Ability to work effectively under pressure", "IT skill",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 6. STRATEGY & CORPORATE DEVELOPMENT — Business Head Security & Surveillance (Telecom) ──
ROLES.append({
    "dept": "STRATEGY & CORPORATE DEVELOPMENT",
    "role_family": "Business Head – Security & Surveillance (Telecom)",
    "source_docs": ["Business Head Security and Survillence - Telecom.pdf"],
    "note": "Source doc does not give an exact designation title beyond 'senior management team' Business Development hire — mapped under this role_family per the filename's intent.",
    "bands": {
        "executive": {
            "progressive_skills": [
                "Strategize the Company's entry and profitable growth in the Security and Surveillance Industry (CCTV Cameras, DVRs & NVRs) in India",
                "Decide on selection of products to be introduced and key differentiators",
                "Decide on selection of sourcing partners for the chosen products",
                "Decide whether to use current brand name (line extension mode) or choose a new brand name",
                "Decide on single or multi-tier distribution architecture",
                "Define positioning strategy and meet success requirements to enroll new Distribution Partners",
                "Design the sales, service and marketing organization",
                "Decide on local manufacturing or trading",
                "Build a business plan and resource requirements for the first 3 years",
                "In-depth knowledge of success requirements for establishing and growing a new entrant business: product sourcing, positioning, building a robust distribution ecosystem from the ground up in the face of firmly entrenched large competitors",
            ],
            "arvind_specific": [
                "Arvind's Telecom business (Syntel) — market leader in Mini-EPABXs for SOHO/SMB, partnered with NEC, Alcatel Lucent Enterprise, Cisco, Polycom",
                "Arvind's Shared Mobile Radio Service and GPS-based vehicle tracking/Fleet Management Systems — India's largest Public Mobile Radio Trunking Services operator with 90%+ market share",
                "Entering the Security and Surveillance Industry (CCTV Cameras, DVRs & NVRs) as a new business line",
            ],
            "leadership_skills": ["Senior management team addition with Business Development ownership of new business entry"],
            "qualifications": ["More than 15 years in the Security & Surveillance Industry in a Business Development role"],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 7. MAINTENANCE & ENGINEERING — Administration & Facility Management ────
ROLES.append({
    "dept": "MAINTENANCE & ENGINEERING",
    "role_family": "Administration & Facility Management",
    "source_docs": [
        "Central Administration and facility mgmt.doc", "Central Administration and facility mgmt.pdf",
        "Chief Manager Administration and facility mgmt.doc", "Chief Manager Administration and facility mgmt.pdf",
    ],
    "note": "Corporate administration/facilities function — mapped to closest-fit department (MAINTENANCE & ENGINEERING) since it covers building/utility maintenance, not a perfect match to any listed department.",
    "bands": {
        "lead": {
            "progressive_skills": [
                "Handling operation & maintenance of office premises",
                "Managing overall maintenance of facilities & equipment: UPS, IBMS, Access control, CCTV, kitchen equipment, Wind Solar hybrid systems, solar water heating systems, solar BIPV system, Rain water harvesting, water & sewage treatment plants, RO system, organic waste composting, fire fighting & alarm system, fire suppression system",
                "Ensuring proper work space planning and allocation",
                "Managing Help Desk, Fire & Safety, Security, Transport, Travel, VISA, Passport, Telephone Set, EPBX system, Cafeteria Management, Event Management, Mail Desk, Housekeeping operations",
                "Establishing systems & processes for improving effectiveness of the function through cost, quality & delivery compliance",
                "Interacting with departments for executing maintenance of equipment / timely delivery of new equipment",
                "Inspecting field sites/facilities to evaluate condition and ensure general up-keep of premises/equipment/furniture/furnishings/vehicles",
                "Management of all COVID-related protocols and systems (internal and external)",
                "Ensuring administration-related SOPs are implemented",
                "Responsibility for central kitchen management",
            ],
            "arvind_specific": ["Facilities managed: Operations of Arvind Ltd based in and around Ahmedabad"],
            "leadership_skills": ["Chief Manager-level facility management ownership for a single-site scope"],
            "qualifications": ["Graduate in any discipline", "PG Degree – any discipline", "15-20 years of experience"],
            "kpis": [],
            "reporting_to": "",
        },
        "executive": {
            "progressive_skills": [
                "Spearheading transport system: OTA / No-shows tracking, logging, checking, routing",
            ],
            "arvind_specific": [
                "Facilities managed: Textile and garment Operations of Arvind Ltd based in Ahmedabad and Bangalore, Gujarat, Corporate Office, Envisol",
            ],
            "leadership_skills": ["Central Head-level facility management ownership across multiple sites/business units"],
            "qualifications": ["Graduate in any discipline", "PG Degree – any discipline", "15-20 years of experience"],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 8-11. STRATEGY & CORPORATE DEVELOPMENT — CEO postings ───────────────────
ROLES.append({
    "dept": "STRATEGY & CORPORATE DEVELOPMENT",
    "role_family": "CEO – Business Unit (Human Protection)",
    "source_docs": ["CEO - Human Protection.pdf"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Strategic Leadership: define and execute long-term vision and growth strategy for the division; identify new markets, technologies, and partnerships to strengthen global presence",
                "Operational Excellence: oversee manufacturing, R&D, and quality assurance for protective fabrics and garments; ensure compliance with international safety standards (ISO, NFPA, EN norms)",
                "Innovation & Product Development: drive development of next-generation protective solutions (FR fabrics, combat gear, specialty protection); collaborate with global fiber and chemical partners for advanced material integration",
                "Financial Management: manage P&L, optimize costs, ensure sustainable profitability; align investments with strategic priorities and ROI targets",
                "Team Leadership: build and mentor a high-performing leadership team across operations, R&D, and sales; foster a culture of safety, innovation, and accountability",
                "Stakeholder Engagement: represent the division in global forums, client meetings, and strategic alliances; maintain relationships with government bodies, defense agencies, and industrial clients",
            ],
            "arvind_specific": [
                "Arvind Human Protection Division, established 2008 — pioneer in high-performance flame-retardant fabrics and protective garments for oil & gas, energy, construction, automotive, utilities, healthcare, and defense forces",
                "IGNX™ — advanced solution for protection against electric arc, flash fire, molten metal splash, foul weather, and biological hazards",
            ],
            "leadership_skills": ["CEO-level strategic leadership and operational oversight for the Human Protection Division"],
            "qualifications": [
                "MBA or equivalent with strong technical background (Textiles/Materials Science preferred)",
                "18+ years of experience in technical textiles or protective solutions, with at least 8 years in senior leadership",
                "Proven track record in scaling businesses globally and managing complex operations",
                "Strong understanding of compliance standards and advanced material technologies",
                "Strategic Vision & Execution, Innovation Leadership, Global Business Acumen, Operational & Financial Excellence, Stakeholder Management",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

ROLES.append({
    "dept": "STRATEGY & CORPORATE DEVELOPMENT",
    "role_family": "CEO – Business Unit (Knits)",
    "source_docs": ["CEO Knits.pdf"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Strategic Leadership: define and execute the company's long-term strategy in alignment with business goals and market trends",
                "P&L Management: full ownership of the company's P&L; drive revenue growth, cost efficiency, and profitability across all business verticals",
                "Operational Oversight: supervise all functional departments including manufacturing, sales, sourcing, HR and finance to ensure smooth day-to-day operations",
                "Production Excellence: oversee production planning and quality control, ensuring high standards and on-time delivery in line with customer expectations",
                "Market & Customer Focus: build strong relationships with key customers (domestic and export), identify new market opportunities, drive product innovation",
                "Team Leadership: build and lead a high-performance leadership team; foster a performance-driven, accountable, and collaborative work culture",
                "Compliance & Governance: ensure compliance with legal, environmental, and industry standards; maintain strong governance practices",
            ],
            "arvind_specific": ["Knits-based apparel business, Bangalore — Garments-Knits industry"],
            "leadership_skills": ["CEO-level leadership driving performance across production, merchandising, marketing, supply chain and finance"],
            "qualifications": [
                "Bachelor's degree in Apparel or BE in any stream Engg. and/or MBA",
                "Minimum 25 years of experience, with at least 5 years in a senior leadership role in the knits garments business",
                "Proven experience in managing P&L in a manufacturing-driven environment",
                "Strong understanding of textile manufacturing processes, supply chain management, and global market dynamics",
                "Excellent leadership, communication, and decision-making skills",
                "Demonstrated ability to scale businesses, optimize operations, and manage diverse teams",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

ROLES.append({
    "dept": "STRATEGY & CORPORATE DEVELOPMENT",
    "role_family": "CEO – Turnaround Specialist (Distressed Assets)",
    "source_docs": ["CEO- Envisol.docx", "CEO- Turnaround Specialist.docx"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Identify distressed assets in textile domain and independently evaluate present circumstances",
                "Prepare the current state assessment of distressed assets",
                "Prepare the business plan outlining and suggesting possible courses of action",
                "Implement the business plan and build the team both inside the company and from outside resources",
                "Monitor the business plan — analyze variances to determine causes and validity of underlying assumptions",
                "Focus on cash flow — stabilize cash flow, analyze sales and profit centers and asset utilization",
                "Rebuild credibility and confidence with lenders, trade suppliers, employees, customers, shareholders, local community",
                "Serve as liaison/intermediary with outside constituencies to calm troubled waters and present a recovery plan",
            ],
            "arvind_specific": ["Acquiring and turning around distressed textile-domain assets for Arvind Ltd."],
            "leadership_skills": ["Works in tandem with promoters/senior management team of Arvind Ltd."],
            "qualifications": [
                "Management graduate with minimum 20 years of experience in a manufacturing company",
                "Currently working as a Business Head with a minimum of 2 turnaround experiences from earlier companies",
                "Good understanding of financial ratios — the 'Z Score' for evaluating a distressed manufacturing company",
                "Goal-oriented professional capable of taking hard decisions",
                "Experienced negotiator with creditors",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

ROLES.append({
    "dept": "STRATEGY & CORPORATE DEVELOPMENT",
    "role_family": "CEO – Business Unit (Water/EPC)",
    "source_docs": ["CEO- Water.docx"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Supervise and control all strategic and business aspects of the company",
                "Develop high quality business strategies and plans ensuring alignment with short-term and long-term objectives",
                "Lead and motivate subordinates to advance employee engagement, develop a high performing managerial team",
                "Oversee all operations and business activities to ensure desired results consistent with overall strategy and mission",
                "Make high-quality investing decisions to advance the business and increase profits",
                "Enforce adherence to legal guidelines and in-house policies to maintain legality and business ethics",
                "Review financial and non-financial reports to devise solutions or improvements",
                "Build trust relations with key partners and stakeholders, act as point of contact for important shareholders",
                "Analyse problematic situations and provide solutions for company survival and growth",
                "Maintain deep knowledge of the markets and industry of the company",
            ],
            "arvind_specific": ["Water treatment / EPC and infrastructure business"],
            "leadership_skills": ["CEO-level company leadership"],
            "qualifications": [
                "ME / M.Tech / B.Tech Engineering or relevant field with MBA an added advantage",
                "Proven experience as CEO or similar managerial role",
                "Experience in EPC and/or infrastructure sector",
                "Experience in waste water treatment projects",
                "Familiarity with diverse business functions: Business Development, Projects, Commercial, Procurement",
                "Shaping the Strategy, Decision Making, Achievement Orientation, Leading Teams, Authentic Leadership, Adaptability, Driving Innovation",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 12. FINANCE & ACCOUNTS — CFO (Institutional, Education Society) ────────
ROLES.append({
    "dept": "FINANCE & ACCOUNTS",
    "role_family": "Chief Financial Officer (Institutional)",
    "source_docs": ["CFO JD.docx"],
    "note": "Not a core Arvind business unit — client is a non-profit Education Society (Ahmedabad-based, est. 1935). Mapped to closest-fit department per instructions.",
    "bands": {
        "executive": {
            "progressive_skills": [
                "Oversee the financial management of the education society",
                "Develop and manage the annual budget and long-term financial plans",
                "Provide strategic financial guidance to the senior leadership team and Board of Governors",
                "Analyze financial data and provide recommendations to improve financial performance",
                "Ensure accuracy and integrity of financial records and compliance with financial reporting requirements",
                "Oversee investment and debt management programs",
                "Manage financial risk, including financial modeling and forecasting",
                "Develop and implement financial policies and procedures to ensure compliance with applicable laws and regulations",
                "Oversee procurement and contracts management activities",
                "Manage financial relationships with external stakeholders: lenders, investors, donors",
                "Lead and manage the finance team, including hiring, training, and performance management",
            ],
            "arvind_specific": [],
            "leadership_skills": ["CFO-level leadership of the finance team", "Reports to Chairman, Board of Governors"],
            "qualifications": [
                "CA with 25 to 30 years of experience",
                "Experience of working in premier universities/educational institutes desirable",
                "Strong leadership, communication, and interpersonal skills",
                "Excellent analytical and problem-solving skills",
            ],
            "kpis": [
                "Financial Performance: revenue growth, profitability, cash flow management, cost management",
                "Risk Management: risk exposure and risk mitigation strategies",
                "Strategic Planning: financial planning and analysis, capital allocation, ROI",
                "Compliance: audit outcomes, regulatory compliance, financial reporting accuracy",
                "Team Management: productivity, employee engagement, talent retention",
            ],
            "reporting_to": "Chairman, Board of Governors",
        },
    },
    "jds": [],
})

# ── 13. FINANCE & ACCOUNTS — CFO (Arvind Smartspaces) ───────────────────────
ROLES.append({
    "dept": "FINANCE & ACCOUNTS",
    "role_family": "Chief Financial Officer (Arvind Smartspaces)",
    "source_docs": ["CFO - Arvind Smartspaces.doc.pdf"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Ensure appropriate financial systems and processes are in place: Company Reporting, Cash Management, Debt Facilities, Risk Management and Audits, Tax Compliance, Insurance, Contract Management, Terms of Trade & Accounting Projects & Analysis",
                "Corporate Finance: optimizing the balance sheet structure",
                "Financial Strategy: budgeting, forecasting, contributing to overall strategy and investment prioritization, investor relationship management",
                "Risk Management: organizational risk framework (strategic and financial)",
                "Assist the CEO in developing, for Board approval, a strategic financial direction and positioning to ensure the Company's success",
                "Develop and recommend an annual operating plan and financial budget supporting the Company's long-term strategy",
                "Work directly with the CEO to help raise funding, loans and venture capital for the company",
                "Create, coordinate and evaluate the financial controls and supporting information systems of the Company",
                "Approve and coordinate changes and improvements to disclosure controls and internal control over financial and MIS reporting",
                "Develop appropriate KPIs to monitor and drive the financial performance of the Company and operating business units",
                "Oversee and monitor the Company's financial position, banking and financing activities, capital structure, banking/financial covenants and hedging arrangements",
                "Ensure adequacy of the Company's insurance coverage",
                "Oversee and monitor effective tax strategies and compliance for both direct and indirect taxation",
                "Ensure optimal team size of the Department with proper work allocation",
                "Coordinate preparation of the Company's financial statements and management discussion and analysis (annual and interim)",
                "Coordinate the annual audit with Internal and external auditors",
                "Assist the Audit Committee in performing its duties under applicable laws",
                "Attend Board and Committee meetings and present financial information necessary for discharging duties",
                "Establish and maintain communications with the investor community; oversee dissemination of press releases, annual reports, analyst/media communications, investor relations",
                "Provide people management and subject matter leadership to the corporate finance team",
                "Strategic business partnering and business analytics for management decision making",
                "Drive automation and digitalization for financial processes",
                "Evaluate strategic decisions for business growth",
            ],
            "arvind_specific": ["Arvind Smartspaces Ltd — real estate business; reports to CEO & MD, Smartspaces"],
            "leadership_skills": ["CFO-level leadership of the corporate finance team"],
            "qualifications": ["Financial Strategy", "Risk Management", "Problem Solver", "Analytical", "Conflict Management"],
            "kpis": [],
            "reporting_to": "CEO & MD, Smartspaces",
        },
    },
    "jds": [],
})

# ── 16/17/18. FINANCE & ACCOUNTS — Tax & FP&A Senior Analysts ───────────────
ROLES.append({
    "dept": "FINANCE & ACCOUNTS",
    "role_family": "Direct Tax",
    "source_docs": ["Direct Tax_ Sr Analyst_Job_Descriptions.docx"],
    "bands": {
        "mid": {
            "progressive_skills": [
                "Prepare computation of total income and support filing of Income Tax Returns (ITR) within statutory timelines",
                "Compute current tax and deferred tax provisions, support tax-related disclosures for financial statements",
                "Support tax audit compliance, including preparation of Form 3CD details, schedules, and supporting documentation",
                "Compute and arrange for advance tax payments based on projected income",
                "Support income tax assessments and litigation by preparing submissions, data, and documentation, coordinating with consultants and tax authorities",
                "Perform TDS/TCS reconciliation (books vs. returns vs. Form 26AS) and ensure timely correction of mismatches",
                "Prepare and validate Form 15CA / 15CB documentation for foreign remittances, assess TDS applicability on forex payments including treaty/withholding considerations",
                "Ensure statutory compliance reporting and adherence to direct tax due dates",
                "Compute Professional Tax and support periodic Professional Tax return filing across applicable states",
                "Manage tax queries from business, finance, and auditors",
                "Prepare MIS and tax dashboards covering compliance status, provisions, demands, and refunds",
                "Adhere to SOPs, audit requirements, internal controls, and defined SLAs; identify opportunities for process improvement and automation",
                "Work independently with minimal supervision in a fast-paced Shared Services environment; provide guidance to junior team members",
            ],
            "arvind_specific": ["Shared Services environment within a leading Indian conglomerate (GCC)"],
            "leadership_skills": ["Provides guidance to junior team members"],
            "qualifications": [
                "Graduate in Commerce/Accounting (B.Com) or equivalent; CA / Inter-CA / CMA preferred",
                "3–5 years of relevant experience in Direct Tax / corporate taxation / tax compliance",
                "Strong understanding of the Income Tax Act, TDS/TCS provisions, tax provisioning (current and deferred), and tax audit requirements",
                "Working knowledge of Form 15CA/15CB and withholding tax on foreign remittances",
                "Mandatory hands-on experience working on SAP (FI); familiarity with tax filing utilities and TDS software preferred",
                "Understanding of Indian statutory compliance and reporting requirements",
                "Good verbal and written communication skills",
                "Strong analytical, problem-solving, and organizational abilities with good working knowledge of MS Excel",
                "Experience working in Shared Services / GCC / large corporate environment preferred",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

ROLES.append({
    "dept": "FINANCE & ACCOUNTS",
    "role_family": "Indirect Tax (GST)",
    "source_docs": ["Indirect Tax_ Sr Analyst_Job_Descriptions.docx"],
    "bands": {
        "mid": {
            "progressive_skills": [
                "Manage GST registrations and amendments across applicable states and entities",
                "Prepare and file periodic GST returns: GSTR-1, GSTR-3B, GSTR-6 (ISD), GSTR-7 (TDS), GSTR-8 (TCS), and the annual GSTR-9, within statutory timelines",
                "Prepare and file ITC-04 for goods sent to and received from job workers, ensuring accurate tracking and reconciliation",
                "Perform GST reconciliations: GSTR-2B vs. books for input tax credit, GSTR-1 vs. GSTR-3B, books vs. returns; resolve mismatches",
                "Manage and optimize Input Tax Credit (ITC) — eligibility checks, reversals, timely availment per GST provisions",
                "Prepare and file GST refund applications and follow up with authorities for timely processing",
                "Support handling of GST tax queries, notices, and litigations by preparing data, replies, and documentation",
                "Ensure statutory compliance reporting and adherence to GST due dates",
                "Manage GST-related queries from business, finance, and auditors",
                "Prepare MIS and dashboards covering GST compliance status, ITC, refunds, and open notices/litigation",
                "Adhere to SOPs, audit requirements, internal controls, and defined SLAs",
                "Work independently with minimal supervision in a fast-paced Shared Services environment; provide guidance to junior team members",
            ],
            "arvind_specific": ["Shared Services environment within a leading Indian conglomerate (GCC)"],
            "leadership_skills": ["Provides guidance to junior team members"],
            "qualifications": [
                "Graduate in Commerce/Accounting (B.Com) or equivalent; CA / Inter-CA / CMA preferred",
                "3–5 years of relevant experience in Indirect Tax / GST compliance",
                "Strong understanding of GST law, return filing (GSTR-1, 3B, 6, 7, 8, 9), ITC provisions, and refund processes",
                "Working knowledge of GST reconciliations (GSTR-2B, GSTR-1 vs. 3B) and handling of notices/litigation",
                "Mandatory hands-on experience working on SAP (FI); familiarity with GST filing/reconciliation tools (GSP/ASP solutions) preferred",
                "Understanding of Indian statutory compliance and reporting requirements",
                "Good verbal and written communication skills",
                "Strong analytical, problem-solving, and organizational abilities with good working knowledge of MS Excel",
                "Experience working in Shared Services / GCC / large corporate environment preferred",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

ROLES.append({
    "dept": "FINANCE & ACCOUNTS",
    "role_family": "FP&A",
    "source_docs": ["FP&A_ Sr Analyst_Job_Descriptions.docx"],
    "bands": {
        "mid": {
            "progressive_skills": [
                "Prepare timely and accurate Flash Reports and month-end MIS reports for leadership",
                "Conduct working capital review across receivables, payables, and inventory, highlighting trends, blockages, and improvement opportunities",
                "Partner on inventory management analytics — ageing, provisioning inputs, slow/non-moving stock analysis, inventory KPI tracking",
                "Build and maintain dashboards and reporting templates to improve speed, accuracy, and decision usefulness of FP&A outputs",
                "Ensure compliance with internal controls, reporting standards, and defined SLAs across all planning and reporting deliverables",
                "Monitor reporting accuracy, turnaround time, and other operational KPIs",
                "Identify opportunities for standardization, automation, and process improvement",
                "Work independently with minimal supervision in a fast-paced Shared Services environment; provide guidance to junior team members",
            ],
            "arvind_specific": ["Shared Services environment within a leading Indian conglomerate (GCC)"],
            "leadership_skills": ["Provides guidance to junior team members"],
            "qualifications": [
                "Graduate in Commerce/Accounting (B.Com) or equivalent; CA / CMA / MBA (Finance) preferred",
                "3–5 years of relevant experience in FP&A / business finance / management reporting",
                "Strong understanding of forecasting, variance analysis, MIS reporting, and working capital concepts",
                "Mandatory hands-on experience working on SAP (CO / FI); exposure to BPC or planning tools an advantage",
                "Strong financial modelling and analytical skills with the ability to translate data into insight",
                "Advanced working knowledge of MS Excel; exposure to reporting/analytics tools (e.g., Power BI) strongly preferred",
                "Good verbal and written communication skills, with the ability to present analysis to senior stakeholders",
                "Experience working in Shared Services / GCC / large corporate environment preferred",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 14. INFORMATION TECHNOLOGY — Chief Information Officer (merged CIO + CIDO) ──
ROLES.append({
    "dept": "INFORMATION TECHNOLOGY",
    "role_family": "Chief Information Officer",
    "source_docs": ["CIO.doc", "Chief Info and Digital Officer.docx"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Lead IT as a business function focusing on Process innovations, Business Model setup, Business Engagements, IT Management — governance setup, with specialization in Business Intelligence and functional skills",
                "Create an environment for Business Excellence through IT enablers",
                "Responsible for leading and providing strategic direction for developing business applications",
                "Prepare IT Budgets and ensure compliance to IT budget, optimized resource utilization, setup IT organization",
                "Responsible for driving projects and tracking budgets and KRAs",
                "Synergize & align IT applications to businesses & Group",
                "Help business reduce overall operation cost by process revamping, process automations",
                "Lead a team managing IT Infrastructure, Business Applications, ERP activities across businesses",
                "Vendor management for IT facilities & procurement of IT Infrastructure",
                "Setup of IT organization structure, recruitment of right talent",
                "Develop IT Roadmap, IT Policy and Standards for the Group",
                "Establish network across locations",
                "Disaster Recovery System, assuring near zero downtime",
                "Institutionalize key processes in Operations, Security, Support, Documentation",
                "Project management and support to SAP implementations and up-gradations",
                "Evaluate emerging technologies for deployment across the Group",
                "Develop Information Security Policy for the Group, establish Governance structure and measurement processes",
                "Improve the baseline of security across the Group at minimal cost and time",
                "Management of outsourcing for IT Facility management services across the group",
                "IT Procurement with effective evaluation and negotiation, stringent SLAs",
                "Develop IT competencies of team through job analysis & skill evaluation, deliver training (classroom & e-learning)",
                "Implementation and maintenance of Knowledge management systems and document management systems",
                "Develop and execute a comprehensive digital strategy aligned with the organization's vision and business objectives",
                "Drive digital innovation and serve as a change agent, fostering a culture of continuous improvement and digital-first mindset",
                "Collaborate with stakeholders to integrate digital initiatives with business processes and strategies",
                "Oversee management of digital projects, ensuring they deliver value and meet ROI expectations",
                "Stay abreast of emerging technologies and digital trends, recommend new technologies",
                "Identify and prepare roadmap for deploying Robotic processes in functions like manufacturing, procurement, warehouse",
            ],
            "arvind_specific": ["IT leadership across the Group's diversified businesses, SAP implementation across Group entities"],
            "leadership_skills": ["Team size: 40", "Leads IT department, sets objectives and strategies for technology use"],
            "qualifications": [
                "Graduate in any discipline / B.Tech in Computers, IT, BCA; PG Degree IT Management; certificate course related to the job",
                "Minimum 20 years of experience in IT department and in Manufacturing Industry, at least 3 years handling IT function for a diversified Group",
                "Proven experience as CIDO, CIO, CTO, or similar leadership role in digital transformation and IT management in diversified industries",
                "Strong understanding of digital technologies: cloud computing, data analytics, cybersecurity, enterprise software",
                "SAP Implementation Exposure",
                "Bachelor's or Master's degree in Information Technology, Computer Science, Business Administration, or related field",
                "Inter-personal Skills, Conflict Management, Execution Skills, Negotiation Skills, Strategic Thinker, Leadership Skills",
            ],
            "kpis": [],
            "reporting_to": "Chief Finance Officer (CFO) / Business CEOs",
        },
    },
    "jds": [],
})

# ── 19. STRATEGY & CORPORATE DEVELOPMENT — Executive Assistant – GCC Leadership ──
ROLES.append({
    "dept": "STRATEGY & CORPORATE DEVELOPMENT",
    "role_family": "Executive Assistant – GCC Leadership",
    "source_docs": ["GCC EA JD.pdf"],
    "note": "Executive Assistant role mapped to closest-fit department (STRATEGY & CORPORATE DEVELOPMENT — office of GCC leadership) since no dedicated admin/EA department exists in the given list.",
    "bands": {
        "lead": {
            "progressive_skills": [
                "Serve as the central coordination point for GCC leadership activities, ensuring effective management of leadership priorities and schedules",
                "Proactively manage leadership calendars, ensuring optimal prioritization of strategic meetings and commitments",
                "Anticipate scheduling conflicts and resolve them effectively while maintaining alignment with business priorities",
                "Manage complex calendars involving internal leadership, internal stakeholders, and external partners",
                "Coordinate leadership reviews, strategic meetings, project updates, and governance forums",
                "Prepare meeting agendas, coordinate briefing materials, and ensure follow-up on action items",
                "Manage domestic and international travel planning including flights, visas, accommodation, itineraries, and ground logistics",
                "Ensure seamless travel experience for leadership through proactive planning and coordination",
                "Manage travel expenses and ensure compliance with corporate policies",
                "Facilitate communication between GCC leadership and internal stakeholders including HR, Finance, Operations, and other teams",
                "Support preparation of leadership presentations, briefing notes, and communication materials",
                "Maintain confidentiality and professionalism in handling sensitive information",
                "Coordinate logistics for leadership visits, global stakeholder engagements, and internal leadership forums",
                "Support planning and execution of town halls, leadership offsites, and strategic workshops",
                "Manage leadership office documentation, expense reports, and key administrative processes",
                "Maintain structured records of meetings, key decisions, and follow-ups",
                "Continuously improve processes to enhance leadership office efficiency",
            ],
            "arvind_specific": ["Office of GCC Leadership — Arvind's Global Capability Centre in Ahmedabad"],
            "leadership_skills": ["Trusted partner to GCC leadership ensuring operational efficiency"],
            "qualifications": [
                "7–12 years of experience supporting senior executives, business heads, or GCC leadership teams",
                "Experience working in multinational organizations, consulting firms, or global services environments preferred",
                "Proven ability to manage complex schedules and multiple senior stakeholders",
                "Bachelor's degree in Business Administration, Management, or related field",
                "Executive Presence, Proactive Problem Solving, Exceptional Organizational Skills, Stakeholder Management, Discretion & Confidentiality",
            ],
            "kpis": [],
            "reporting_to": "Head – GCC / GCC Leadership Office",
        },
    },
    "jds": [],
})

# ── 20/21. HUMAN RESOURCES — Head of HR (GCC) and HR Shared Services Tower Lead ──
ROLES.append({
    "dept": "HUMAN RESOURCES",
    "role_family": "Head of HR – GCC",
    "source_docs": ["HR.docx"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Lead the people strategy for a new, fast-scaling Global Capability Centre spanning Finance, Technology, Procurement, and HR operations",
                "Shape the organisation structure, build leadership and capability, strengthen culture, ensure seamless high-quality employee experience across the GCC",
                "Partner closely with HR COEs for rewards, policies, and specialised frameworks",
                "Own the full employee lifecycle within the centre",
                "Build a scalable HR operating model",
                "Lead talent acquisition and workforce planning",
                "Drive performance, development, and engagement",
                "Enable leadership effectiveness",
                "Ensure disciplined HR governance, compliance, and operational excellence",
                "Bring people insights, talent intelligence, and organisational judgment into GCC leadership discussions",
            ],
            "arvind_specific": ["Arvind GCC — new, fast-scaling Global Capability Centre"],
            "leadership_skills": ["Head of HR-level ownership of GCC people strategy"],
            "qualifications": [
                "15–18 years of HR experience with 5+ years leading HR in a GCC",
                "Experience scaling centres from early phases to 1000+ employees",
                "Strong expertise in HR business partnering, talent management, org design, and operations",
                "Ability to work closely with global COEs and navigate complex stakeholder environments",
                "Data-driven, execution-focused approach with strong leadership presence",
            ],
            "kpis": [
                "Smooth scaling of the GCC with strength in talent, culture, and capability",
                "High levels of employee and manager experience",
                "Mature and reliable HR processes with strong governance",
                "Strong global alignment and stakeholder confidence",
            ],
            "reporting_to": "",
        },
    },
    "jds": [],
})

ROLES.append({
    "dept": "HUMAN RESOURCES",
    "role_family": "HR Shared Services Tower Lead",
    "source_docs": ["HR.docx"],
    "bands": {
        "lead": {
            "progressive_skills": [
                "Lead the Employee Lifecycle Shared Services tower, delivering consistent, SLA-driven HR services from hire-to-retire across group companies",
                "Own end-to-end employee lifecycle services: onboarding, lifecycle changes, benefits, exits",
                "Run HR service delivery through ticketing, knowledge base, and workflow platforms",
                "Ensure SLA adherence, first-time resolution, and employee experience metrics",
                "Drive process standardisation and automation across HR transactions",
                "Partner with COEs and Business HR on seamless handoffs and clarity of ownership",
                "Build dashboards on service quality, volumes, root causes, and productivity",
            ],
            "arvind_specific": ["Arvind GCC — Employee Lifecycle Shared Services tower across group companies"],
            "leadership_skills": ["Tower Lead-level ownership of Employee Lifecycle Shared Services"],
            "qualifications": ["12 to 15 years of experience"],
            "kpis": ["SLA adherence", "First-time resolution", "Employee experience metrics", "Service quality, volumes, root causes, productivity"],
            "reporting_to": "Head – HR Operations / GCC Head",
        },
    },
    "jds": [],
})

# ── 22. INFORMATION TECHNOLOGY — IT Support Manager ─────────────────────────
ROLES.append({
    "dept": "INFORMATION TECHNOLOGY",
    "role_family": "IT Support Manager",
    "source_docs": ["IT_Support_Manager_JD.docx"],
    "bands": {
        "lead": {
            "progressive_skills": [
                "Own end-to-end IT operations for the GCC, ensuring uptime, security, and service quality across desktops, servers, network, and core applications including Active Directory, Microsoft 365",
                "Administer and govern Active Directory and Microsoft 365 user lifecycle, access provisioning, license allocation, and email/data security",
                "Maintain fundamental oversight of network infrastructure — switches, routers, Wi-Fi, internet/ISP links and connectivity across GCC locations; act as escalation point for connectivity and infrastructure issues",
                "Design and enforce backup and disaster recovery practices, including backup scheduling, restore testing, and recovery time/point objectives",
                "Manage IT vendors and service providers, negotiating SLAs, tracking performance, resolving escalations",
                "Maintain a single source of truth for IT asset and inventory management — procurement, allocation, tracking, retirement of hardware and software",
                "Run IT support operations on ITIL-aligned principles — incident, problem, change, and request management using ITSM and monitoring tools",
                "Act as the primary stakeholder interface for IT support across business teams",
                "Build, mentor, and manage the GCC's IT support team, setting clear ownership, escalation paths, and performance standards",
            ],
            "arvind_specific": ["Arvind GCC — IT operations backbone supporting multiple business units across the Arvind Group"],
            "leadership_skills": ["Builds, mentors, and manages the GCC's IT support team"],
            "qualifications": [
                "8-10 years of progressive experience in IT support / IT operations, including at least 2–3 years in a managerial or team-lead capacity",
                "Prior experience supporting a GCC, shared services centre, or captive/MNC environment strongly preferred",
                "Hands-on experience with Active Directory, Microsoft 365 / Office 365 administration",
                "Solid fundamental understanding of networking — switches, routers, LAN/WAN, Wi-Fi, internet connectivity",
                "Working knowledge of backup and disaster recovery tools and practices",
                "Demonstrated experience in vendor management, stakeholder management, and IT asset/inventory management",
                "Comfort working across multiple ITSM, monitoring, and productivity tools simultaneously; fundamental understanding of ITIL practices",
                "Bachelor's degree in IT, Computer Science, or related field, or equivalent practical experience",
                "ITIL Foundation (v4) certification (preferred)",
                "Microsoft certifications (preferred)",
                "Exposure to AI-powered IT support tools (preferred)",
                "Experience operating across multiple legal entities or business units within a conglomerate structure (preferred)",
            ],
            "kpis": [],
            "reporting_to": "Chief Information Officer (CIO)",
        },
    },
    "jds": [],
})

# ── 23. INFORMATION TECHNOLOGY — Technical Support Associate ───────────────
ROLES.append({
    "dept": "INFORMATION TECHNOLOGY",
    "role_family": "Technical Support Associate",
    "source_docs": ["Technical_Support_Associate_JD.docx"],
    "bands": {
        "mid": {
            "progressive_skills": [
                "Pick up tickets, calls, and walk-ups from GCC users and resolve hardware, software, and account issues — laptops, printers, peripherals, OS, standard business applications",
                "Provide deskside support for issues that need a physical visit, and remote support for everything else, using standard remote-assistance tools",
                "Set up new laptops and desktops for joiners — imaging, software installs, standard configuration; handle returns/recovery when people exit or move",
                "Handle routine Active Directory and Microsoft 365 tasks — password resets, account unlocks, mailbox access, basic license/license-group changes",
                "Troubleshoot everyday connectivity issues — Wi-Fi drops, VPN access, network printer setup; escalate to network team when fix is beyond desk-level access",
                "Log every ticket properly: clear notes, accurate categorization, timely updates",
                "Recognize when something is beyond Tier 1–2 scope and escalate to the IT Support Manager or the right specialist team",
                "Keep IT asset records current — tagging new equipment, updating allocations, flagging missing/due-for-return items",
            ],
            "arvind_specific": ["Arvind GCC — IT Operations, Tier 1 and Tier 2 support"],
            "leadership_skills": [],
            "qualifications": [
                "3-5 years in a helpdesk, desktop support, or technical support role, with real Tier 1-2 ticket ownership",
                "Bachelor's degree in IT, Computer Science, or related field, or equivalent hands-on experience",
                "Hands-on troubleshooting on Windows 11 hardware, OS, and common business software",
                "Basic Active Directory and Microsoft 365 administration — account, password, and access tasks",
                "Comfortable doing both deskside visits and remote sessions in the same day",
                "Basic networking know-how — Wi-Fi, VPN, network printers",
                "Clear, patient communication with users who don't think in technical terms",
                "Disciplined ticket hygiene",
                "Experience supporting a GCC, shared services centre, or similar multi-business-unit setup (good to have)",
                "Basic exposure to O365 administration (good to have)",
                "CompTIA A+ or equivalent foundational certification (good to have)",
                "Familiarity with imaging/deployment tools such as Intune or Autopilot (good to have)",
            ],
            "kpis": [],
            "reporting_to": "IT Support Manager",
        },
    },
    "jds": [],
})

# ── 24. INFORMATION TECHNOLOGY — Automation & AI Associate ─────────────────
ROLES.append({
    "dept": "INFORMATION TECHNOLOGY",
    "role_family": "Automation & AI Associate",
    "source_docs": ["Job Description - Associate Automation & AI.docx"],
    "bands": {
        "junior": {
            "core_skills": [
                "Design, build, and deploy automation workflows across business functions (Finance, HR, Procurement, Ops, Business teams)",
                "Develop Python-based scripts/tools for process automation, data handling, and integrations",
                "Build and experiment with AI-led use cases (LLMs, copilots, agents, internal tools)",
                "Use Microsoft Power Platform (Power Apps, Power Automate)",
                "Use RPA tools (Automation Anywhere / UiPath / equivalent)",
                "Rapidly prototype and ship internal products/tools",
                "Integrate APIs, SaaS tools, and internal systems to create end-to-end automation",
                "Identify manual processes and convert them into scalable automation solutions",
                "Work directly with business stakeholders to translate problems into working solutions",
            ],
            "arvind_specific": ["Core of the Automation & AI capability within the Arvind GCC"],
            "leadership_skills": [],
            "qualifications": [
                "1 – 3 years of experience",
                "Background irrelevant (Tech, Ops, Consulting, Startup, etc.)",
                "Strong hands-on capability in Python scripting",
                "Experience with automation tools: Power Automate / Power Apps; RPA tools (Automation Anywhere, UiPath, etc.)",
                "Working knowledge of APIs & integrations",
                "Working knowledge of data handling (Excel, SQL, basic data pipelines)",
                "Exposure to AI tools / LLMs / automation frameworks (OpenAI, Azure AI, or similar ecosystems)",
                "Ability to build prototypes quickly and iterate",
                "Builder mindset (has created something real)",
                "High ownership (doesn't wait for instructions)",
                "Bias for action (ships fast, learns faster)",
                "Comfortable working in zero-structure environments",
            ],
            "kpis": [
                "Ships working automations, not concepts",
                "Reduces manual effort and turnaround time measurably",
                "Builds reusable tools/products, not one-off hacks",
                "Operates with speed and ownership, not dependency",
            ],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 25. FINANCE & ACCOUNTS — Legal Entity Controller ────────────────────────
ROLES.append({
    "dept": "FINANCE & ACCOUNTS",
    "role_family": "Legal Entity Controller",
    "source_docs": ["Legal Entity Controller.docx"],
    "bands": {
        "lead": {
            "progressive_skills": [
                "Lead end-to-end financial governance of the GCC legal entity, including statutory accounting, taxation, transfer pricing, and cross-charge allocations to group companies",
                "Lead end-to-end accounting and financial management for the GCC legal entity",
                "Ensure accurate monthly, quarterly, and annual financial reporting in compliance with applicable accounting standards and group policies",
                "Oversee general ledger management, reconciliations, financial close, and audit readiness",
                "Establish strong internal controls and financial governance frameworks for the GCC",
                "Ensure full compliance with direct and indirect tax regulations: GST, TDS, corporate tax filings",
                "Manage tax assessments, audits, and liaison with tax authorities",
                "Coordinate with external advisors on regulatory and compliance matters",
                "Manage transfer pricing framework for services provided by the GCC to various group entities",
                "Design and administer cost allocation and cross-charge mechanisms across business units",
                "Ensure compliance with transfer pricing regulations and documentation requirements",
                "Lead statutory audits, internal audits, and tax audits for the GCC entity",
                "Implement and monitor financial controls and risk mitigation processes",
                "Drive finance operations on SAP ERP, ensuring data integrity and efficient financial processes",
                "Establish scalable finance processes suitable for a growing GCC environment",
                "Partner with Group Finance, Tax, and Business Finance teams across the organization",
                "Act as the primary finance point of contact for the GCC entity",
            ],
            "arvind_specific": ["Arvind Limited — Global Capability Centre (GCC) legal entity financial governance"],
            "leadership_skills": ["Primary finance point of contact for the GCC entity"],
            "qualifications": [
                "Chartered Accountant (CA) – Mandatory",
                "10–12 years of experience in controllership, taxation, and financial governance",
                "Strong experience in GST, TDS, corporate taxation, and transfer pricing",
                "Experience managing intercompany cross-charges and allocation models",
                "Hands-on experience with SAP ERP",
                "Experience in shared services / GCC / multi-entity environments preferred",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 26. INFORMATION TECHNOLOGY — Master Data Management (MDM) Manager ──────
ROLES.append({
    "dept": "INFORMATION TECHNOLOGY",
    "role_family": "Master Data Management (MDM) Manager",
    "source_docs": ["MDM - JD.docx", "MDM - Manager.docx"],
    "bands": {
        "lead": {
            "progressive_skills": [
                "Lead the design, setup, and scaling of the Master Data Management (MDM) function within the GCC",
                "Define and implement the MDM vision, roadmap, and operating model for GCC",
                "Establish centralized MDM services for Vendor and Customer master data",
                "Drive transition of MDM activities from business units / locations into GCC",
                "Develop SOPs, policies, and standard templates for data governance",
                "Set up and lead data governance framework: data ownership & stewardship model, data standards, policies, and controls",
                "Define KPIs/KRAs for data quality, accuracy, completeness, and timeliness",
                "Implement data quality tools, audits, and monitoring dashboards",
                "Oversee end-to-end vendor/customer master data lifecycle: creation, modification, blocking, archival",
                "Ensure proper validations (KYC, tax details, banking, credit limits)",
                "Drive standardization and deduplication initiatives",
                "Collaborate with Procurement, Finance, Sales, and IT teams",
            ],
            "arvind_specific": ["Arvind GCC — Master Data Management function for Vendor and Customer master data"],
            "leadership_skills": ["Manager-level MDM leadership; builds and leads MDM team within GCC"],
            "qualifications": [
                "10–12 years of experience (Manager band)",
                "Strong experience in Master Data Management (Vendor/Customer)",
                "Shared Services / GCC setup or transformation roles",
                "Process migration / transitions experience",
                "Experience in manufacturing / textile / retail domains preferred",
                "Strong knowledge of ERP systems (SAP S/4HANA preferred)",
                "Exposure to MDM tools (SAP MDG, Informatica, Collibra, etc.)",
            ],
            "kpis": ["Data accuracy and completeness %", "Reduction in duplicate records", "Turnaround time for master data requests", "Audit compliance and error rates"],
            "reporting_to": "",
        },
        "executive": {
            "progressive_skills": [
                "Identify and implement opportunities for process automation (RPA, workflows) and digital tools (MDM platforms, data catalogs)",
                "Drive continuous improvement and process re-engineering",
                "Leverage analytics for proactive data quality management",
                "Partner with senior stakeholders across Finance, Procurement, Sales, Supply Chain, IT",
                "Act as SPOC for MDM governance and escalations",
                "Define roles like Data Stewards, Analysts, and Specialists",
                "Drive training, capability building, and knowledge management",
            ],
            "arvind_specific": ["Senior Manager-level MDM governance across the Arvind GCC"],
            "leadership_skills": ["Builds and leads a high-performing MDM team within GCC; SPOC for MDM governance and escalations"],
            "qualifications": [
                "12–15 years of experience (Sr. Manager band)",
                "Workflow and automation tools (RPA – UiPath, Automation Anywhere, etc.)",
                "Strong stakeholder management and influencing skills",
                "Ability to work in ambiguity and build from scratch",
            ],
            "kpis": ["% automation in MDM processes", "Stakeholder satisfaction scores"],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 27. FINANCE & ACCOUNTS — Procure to Pay (P2P) ───────────────────────────
ROLES.append({
    "dept": "FINANCE & ACCOUNTS",
    "role_family": "Procure to Pay (P2P)",
    "source_docs": ["Manager - P2P.docx"],
    "bands": {
        "lead": {
            "progressive_skills": [
                "Manage end-to-end Procure-to-Pay (P2P) operations including invoice processing, vendor payments, vendor reconciliations, vendor master management, and T&E processing",
                "Ensure timely and accurate processing of invoices in compliance with company policies, accounting standards, and defined SLAs",
                "Perform invoice verification, PO/GRN matching, discrepancy resolution, and payment processing activities",
                "Maintain and update vendor master data with proper documentation, approvals, and internal controls",
                "Handle vendor and stakeholder queries effectively, ensure timely issue resolution",
                "Support month-end and year-end closing activities related to Accounts Payable and P2P processes",
                "Ensure compliance with Indian statutory requirements including GST, TDS, and related accounting regulations",
                "Adhere to SOPs, audit requirements, compliance standards, and internal financial controls",
                "Coordinate with procurement, finance, treasury, auditors, and business teams for smooth process execution",
                "Monitor process accuracy, turnaround time, aging, and other operational KPIs",
            ],
            "arvind_specific": ["Shared Services environment within a leading Indian conglomerate (GCC)"],
            "leadership_skills": ["Team Manager role type; must have experience managing a team"],
            "qualifications": [
                "Graduate in Commerce/Accounting (B.Com) or equivalent qualification",
                "10+ years of relevant experience in Procure-to-Pay (P2P) / Accounts Payable operations",
                "Must have experience in managing a team",
                "Strong understanding of end-to-end P2P lifecycle and accounting concepts",
                "Mandatory hands-on experience working on SAP",
                "Understanding of Indian accounting practices and statutory compliance including GST and TDS",
                "Good working knowledge of MS Excel",
                "Experience working in Shared Services / GCC / large corporate environment preferred",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 28. FINANCE & ACCOUNTS — Record to Report (R2R) ─────────────────────────
ROLES.append({
    "dept": "FINANCE & ACCOUNTS",
    "role_family": "Record to Report (R2R)",
    "source_docs": ["Manager - R2R.docx"],
    "bands": {
        "lead": {
            "progressive_skills": [
                "Manage end-to-end Record to Report (R2R) operations including journal processing, accruals and provisions, balance sheet reconciliations, fixed assets, intercompany accounting, and period-end close",
                "Ensure timely and accurate posting of journals and completion of close activities in compliance with company policies, accounting standards, and defined SLAs",
                "Own and review balance sheet account reconciliations, ensure timely clearing of reconciling items, escalate aged or unusual items",
                "Drive month-end, quarter-end, and year-end close per the close calendar, monitor task completion and dependencies, ensure cut-off adherence",
                "Prepare and review financial schedules, flux/variance analysis, and management reporting inputs, providing commentary on key movements",
                "Manage fixed asset accounting, intercompany reconciliations, and resolution of mismatches with counterpart entities",
                "Ensure compliance with applicable accounting standards (IFRS/Ind AS), Indian statutory requirements, and internal financial controls (including SOX, where applicable)",
                "Adhere to SOPs, audit requirements, compliance standards, and internal controls; support statutory and internal audits with timely, audit-ready documentation",
                "Coordinate with FP&A, treasury, tax, auditors, and business teams for smooth process execution",
                "Monitor process accuracy, turnaround time, reconciliation aging, and other operational KPIs",
                "Identify opportunities for standardization, automation, and process improvement",
                "Work independently with minimal supervision in a fast-paced Shared Services environment; provide guidance to junior team members",
            ],
            "arvind_specific": ["Shared Services environment within a leading Indian conglomerate (GCC)"],
            "leadership_skills": ["Provides guidance to junior team members"],
            "qualifications": [
                "Graduate in Commerce/Accounting (B.Com) or equivalent; semi-qualified CA/CMA or MBA (Finance) preferred",
                "10-15 years of relevant experience in Record to Report (R2R) / general accounting / month-end close operations",
                "Strong understanding of the end-to-end R2R lifecycle and core accounting concepts",
                "Mandatory hands-on experience working on SAP (FI module)",
                "Understanding of Indian accounting practices and statutory compliance, including GST and TDS, and exposure to IFRS/Ind AS",
                "Good working knowledge of MS Excel; exposure to reporting/analytics tools (e.g., Power BI) an added advantage",
                "Experience working in Shared Services / GCC / large corporate environment preferred",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 29/30. HUMAN RESOURCES — Manager HR / Business Head HR & IR ────────────
ROLES.append({
    "dept": "HUMAN RESOURCES",
    "role_family": "Manager HR / Sr Manager HR",
    "source_docs": ["Business HR.doc"],
    "bands": {
        "senior": {
            "progressive_skills": [
                "Maintain and enhance the organization's human resources function by planning, implementing, and evaluating employee relations and HR policies, programs, and practices",
                "Look into HR Operations function delivering proactive and business-focused HR advice and services, including recruitment and selection, employee relations, reward and systems",
                "Manpower planning and forecasting for the business",
                "Hiring people as per requirement; reduce lead time for hiring and cost of hiring",
                "Identify Training service providers as per TNI identified; ensure identified TNI are addressed through appropriate and timely programs",
                "Support the formulation of KRAs",
                "Support Business Managers in Selection, Recruitment, Appraisal, Internal Transfer of employees",
                "Design and develop Employee Engagement activities",
                "Ensure attrition rate is measured at single-digit level",
                "Manage grievances of Manager and above of the business",
            ],
            "arvind_specific": ["HR Operations for a manufacturing set up at Arvind, based in Ahmedabad"],
            "leadership_skills": ["Manager / Sr Manager HR, Grade M2"],
            "qualifications": [
                "Graduate in any discipline",
                "PG Degree in HR",
                "Minimum 6 years of experience in Human Resource from a manufacturing set up",
                "Interview Skills / Convincing Skills, Performance Management Programme, Inter-personal Skills, Conflict Management / Problem solving, Communication (Written/Oral), Motivation, Leadership",
            ],
            "kpis": ["Attrition rate measured on single-digit level", "Reduced lead time and cost of hiring"],
            "reporting_to": "Administrative: Business Head; Functionally: Business Head HR",
        },
    },
    "jds": [],
})

ROLES.append({
    "dept": "HUMAN RESOURCES",
    "role_family": "Business Head – HR & Industrial Relations",
    "source_docs": ["Business Head HR and IR Textiles.doc", "Business Head HR and IR_17.12.15.doc"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Formulate short-term and long-term IR strategies at a business/group level",
                "Create a fair and high-performance culture enabling operators to contribute their best across all factory locations",
                "Manage all statutory, legal, and payroll aspects; create a win-win environment with union leaders and representatives",
                "Plan human resource requirements in consultation with heads of functional and operational areas",
                "Revamp processes to run operations with optimal/reduced manpower",
                "Redeploy workmen and ensure adequate training across operations",
                "Define and standardize productivity norms by role/task/job code",
                "Maintain balance between permanent and contractual workers (e.g., outsourcing non-core activities)",
                "Ongoing evaluation and feasibility study of automation (especially material movement)",
                "Conceptualize & develop training & development initiatives for improved productivity, capability building, quality enhancement",
                "Identify capable workmen and develop them into Supervisors",
                "Train workforce to multi-skill to mitigate impact of absenteeism",
                "Conduct surveys on work climate analysis; recommend changes for good working environment",
                "Manage Health, Safety, and Hygiene of the plant",
                "Salary Administration / Performance Appraisal",
                "Develop Employee Engagement activities for workmen",
                "Handle Employee Grievances",
                "Ensure implementation of Code of Conduct, Code of Business Ethics, Standing Order, Discipline policy, Sexual Harassment Committee per legal directive",
                "Revamp work environment and facilities at workplace (transport, canteens, etc.)",
                "Overhaul occupational safety practices and systems",
                "Address collective bargaining, arbitration & negotiation preparation; settle bipartite and tripartite settlements with unions",
                "Deal with multi-union culture; represent before Conciliation Officer to settle demands",
                "Handle industrial disputes and unrest: Gate meetings, Gherao, demonstration, sabotage, Strike, lock-out, Police and court interventions, retrenchment",
                "Compensation design, career and skill development; CTC component design (including performance incentives, overtime bonus)",
                "Worker engagement, communication and morale building (town halls, magazines, festival celebrations)",
                "Support through external tie-ups for benefits of workers (soft loans, insurance schemes)",
                "Build trustworthy relationship with society for business continuity (CSR)",
                "Conduct CSR surveys, identify areas of operations, prepare activities calendar, align with NSDC and NGOs",
                "Establish and maintain liaison and rapport with Govt. authorities, Local Police, local influencing bodies",
                "Implement OD interventions and Competency Framework per company strategy",
                "Formulate strategy for Capability building and Succession planning",
                "Ensure coordination for performance management system implementation within the company's PMS framework",
            ],
            "arvind_specific": [
                "Group-level Employee Relations across all Arvind factory locations",
                "Fluency in Gujarati required (Read and Speak) for one variant of this role",
            ],
            "leadership_skills": [
                "BMH grade; reports to CEO of Businesses (BU-level variant, 4-5 reportees, team size 15+) or Group CFO & Executive Director (Group-level variant, 10+ reportees, team size 20)",
            ],
            "qualifications": [
                "Graduate in any discipline",
                "PG Degree – Human Resource / Industrial Relations / Labour Welfare",
                "15+ years of experience in HR & IR / Industrial Relations of a manufacturing set up",
                "Innovative Thinking, Business Acumen, Operational Excellence, Strategy formulation & Implementation, Negotiation skills, Inter-personal Skills, Conflict Management, Team management skills",
                "Union Negotiations, Training of Workmen, Workforce Planning, Labour Laws, Managing and Leading a large team",
            ],
            "kpis": [],
            "reporting_to": "CEO of Businesses (BU-level) / Group CFO & Executive Director (Group-level)",
        },
    },
    "jds": [],
})

# ── 15. MERCHANDISING & BUYING — Merchandising (merged 2 docs, 2 bands) ────
ROLES.append({
    "dept": "MERCHANDISING & BUYING",
    "role_family": "Merchandising",
    "source_docs": ["Chief Merchandising Officer.doc", "Chief Merchandising Officer_Internet.doc"],
    "bands": {
        "senior": {
            "progressive_skills": [
                "Manage all aspects of the supply chain including procurement, pricing, merchandising, assortment planning, inventory management, new product range execution, logistics and distribution in a timely and cost-effective manner to meet sales and contribution targets",
                "Work with reporting officer in seasonal merchandise planning for each product category",
                "Plan product ranges and prepare sales and stock plans to meet sales targets, meeting budgeted contribution targets",
                "Plan re-order levels and replenishments to minimize stock outs and optimize sales",
                "Establish prices for profit maximization to manage performance of seasonal ranges",
                "Plan budgets and present sales forecasts and figures for new ranges",
                "Carry out product line and product profitability analysis regularly to ensure conformance to budgeted contributions",
                "Monitor product margins at all times to ensure no dilution of product profitability",
                "Review price points for weak-selling product categories; implement solutions for slow lines and ends of range",
                "Implement markdowns for non-selling goods based on sales performance / stock levels",
                "Responsible for procurement activities related to store merchandise based on seasonal procurement schedules",
                "Develop Terms And Conditions (TAC) for procurement activity in line with merchandise planning",
                "Ensure order booking process per TACs; monitor TACs of supplies and delivery schedules",
                "Ensure re-order levels met and maintenance of inventory per defined standards",
                "Ensure replenishment of merchandise at warehouse and stores; manage store-wise and category-wise inventory turnover",
                "Analyse stock movements daily for efficient inventory management; minimize inventory holding cost and monitor inventory ageing",
                "Work towards shorter merchandise replenishment cycle",
                "Resolve issues of slides in procurement delivery dates; update retail operations team and EBO head for delays",
                "Track high-demand categories to minimize stock outs and lost sales",
                "Carry out competitor shopping for comparison of products, range, quality, pricing",
                "Work towards reduction in procurement costs and lead times without compromising quality; measure and monitor time to market",
                "Implement promotions and markdowns for slow-moving lines, ends of range, excess stock",
                "Procure store consumables and packaging material at optimum costs and in a timely manner",
                "Responsible for monthly report generation of Source to Plan Deviation Reports, root cause analysis to reduce future deviations",
                "Ensure implementation of standard operating procedures for merchandise handling and movement",
                "Ensure efficient management of merchandise to various stores in time to meet sales targets",
                "Manage transportation of merchandise to stores and logistics from store to warehouse",
                "Control storage and in-transit losses; undertake preventive steps",
                "Budget warehousing and distribution costs and monitor actual expenses against budget",
                "Ensure legal compliances and documentation pertaining to logistics and distribution",
                "Analyse category-wise product profitability to ensure GMROI and GMROF targets are met",
                "Carry out contribution reconciliation to bridge gaps between actual and predicted contributions",
                "Analyse and report on: GMROI, stock turnover rate, markdown goods %, shrinkage to net sales, average selling price, ageing, reorder levels, liquidation plans",
                "Work with reporting officer to execute product development and commercialization strategies across stores",
                "Keep abreast of market developments related to pricing, fashion trends, customer requirements, competitor's product mix",
            ],
            "arvind_specific": [
                "Ankur Textiles division — Voiles Business, Merchandising Manager (M3 / Chief Manager grade)",
                "Role requires frequent traveling to meet vendors and store locations throughout India",
            ],
            "leadership_skills": ["No direct reportees at this level (Merchandising Mgr. band)"],
            "qualifications": [
                "Business/Marketing related degree from a recognized institute or university, with at least 50% marks or equivalent CGPA",
                "5+ years experience, of which at least three years in handling merchandising and supply chain functions for an apparel retail organization",
                "Strong knowledge of retail merchandising and supply chain activities, budgeting, forecasting",
                "Proficient in MS Office 2000 or later (particularly Excel and Word); Internet and email",
                "Strong knowledge of and exposure to Retail MIS/ERP",
                "Excellent planning and organizing skills, strong analytical and creative thinking skills, meticulous attention to detail, time management, strong interpersonal and negotiation skills, problem solving and decision making skills, professional presentation skills",
            ],
            "kpis": ["GMROI", "stock turnover rate", "markdown goods %", "shrinkage to net sales", "average selling price", "ageing", "reorder levels", "liquidation plans"],
            "reporting_to": "Chief Mgr. (Merchandising & Supply Chain) — Functional and Administrative",
        },
        "executive": {
            "progressive_skills": [
                "Responsible for all Arvind Brands, brands of 3rd party & foreign JV/collaborations",
                "Own the complete merchandising operations",
                "Own the P&L accountability of Merchandising activity",
                "Plan seasonal merchandising for each product category for profit maximization across all brands",
                "Market intelligence on competitor's data for comparison of products, range, quality, pricing",
                "New product development and commercialization strategies planned & executed across stores",
            ],
            "arvind_specific": ["Arvind Internet Limited — Chief Merchandising Officer role, team size growing from 5-10 to 30-50 people over 2-3 years"],
            "leadership_skills": ["Build and Manage Teams", "Reports to COO or ED", "P&L accountability of Merchandising activity"],
            "qualifications": [
                "Graduate, specialization in NID or NIFT",
                "Minimum 10+ years of experience",
                "Fully conversant with all qualitative and technical aspects of apparel and other fashion/lifestyle merchandise",
                "Should have handled more than one brand; experience in handling shoes & accessories preferred",
                "Excellent understanding of Products and customer dynamics",
                "Planning and organizing skills, strong analytical and creative thinking skills, meticulous attention to detail, strong interpersonal and negotiation skills, problem solving and decision making skills, presentation skills",
            ],
            "kpis": ["ROI", "stock turnover rate", "markdown goods %", "shrinkage to net sales", "average selling price", "ageing", "reorder levels", "liquidation plans"],
            "reporting_to": "COO or ED",
        },
    },
    "jds": [],
})

# ── 31. MARKETING & COMMUNICATIONS — Institutional Sales Head (Home Linen) ──
ROLES.append({
    "dept": "MARKETING & COMMUNICATIONS",
    "role_family": "Institutional Sales Head (Home Linen)",
    "source_docs": ["JD - Institutional Sales Head.docx"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Lead Arvind's bed linen business for institutional and bulk B2B channels",
                "Build and grow revenue from hotels, hospitals, railways, hospitality chains, facility management companies, corporate gifting houses, government institutions, and similar large-volume buyers",
                "Own the institutional business strategy for bed linen and related linen categories",
                "Drive new business acquisition, retention, renewal, and account expansion",
                "Build strong relationships with procurement heads, purchase managers, admins, consultants, and tendering teams",
                "Develop and manage national/regional accounts across hotels, hospitals, railways, hostels, resorts, corporates, and gifting channels",
            ],
            "arvind_specific": [
                "Arvind's bed linen / home linen business",
                "Target companies: Welspun, Trident, Kurlon, D'Decor, Raymond Home, Story@Home, Indo Count, and similar textile/home furnishing companies",
            ],
            "leadership_skills": ["Institutional Business Head — owns institutional channel strategy"],
            "qualifications": [
                "12-26 years of total experience",
                "Strong institutional/B2B sales leadership in home furnishing",
                "Tendering, negotiation, and key account management skills",
                "Experience selling to hotels, hospitals, railways, government bodies, corporates, or contract furnishing buyers",
                "Strong network in hospitality, healthcare, government procurement, or corporate purchasing",
                "History of selling bulk textile products to institutional buyers",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 32/33. Accel positions.docx — Business Head (Water/OEM) & Process Expert ──
ROLES.append({
    "dept": "STRATEGY & CORPORATE DEVELOPMENT",
    "role_family": "Business Head – Water & Wastewater Solutions",
    "source_docs": ["Accel positions.docx"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Responsible for Technical, commercial and operational strategy, maintaining profitability, winning market share in strategic and emerging regions, delivering revenue and EBITDA growth as per budget",
                "Develop strategy for business operations, including M&A, Technological JV with Business Development & revenue generation",
                "Overall responsible for operational activities and execution of ZLD/ETP/RO Project",
                "Responsible for proposals, detailed process & design engineering of WTP/ETP/RO/ZLD, Client Interaction & Networking",
                "Complete process knowledge for ETP/RO/ZLD",
                "Knowledge of emerging technologies: MBR, MBBR, UF, RO, CPU, Ion Exchange",
                "Make effective marketing strategies, promote dealer network, develop new customers, provide better services to existing clients",
                "Implement marketing strategies based on market feedback, assign jobs to junior staff, promote dealer network, analyze performance, provide technical/marketing training",
                "Analyze customer need and market demand, create new prospects, carry out surveys",
                "Prepare Sales Budget, implement MIS, implement marketing promotional strategies",
                "Organize trade shows and participate in exhibitions to promote product & brand awareness",
                "Handle new product development process",
                "Recruitment & selection of sales & support staff at various levels",
                "Control and manage warehouse and inventories for all products",
            ],
            "arvind_specific": ["Arvind Envisol — Water & Wastewater Solutions business (ZLD/ETP/RO)"],
            "leadership_skills": ["Business Head-level ownership"],
            "qualifications": [">20 Years of experience", "B.E. Chemical/Mechanical", "CTC range 25-30 LAC"],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

ROLES.append({
    "dept": "RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT",
    "role_family": "Process Expert – RO/ETP",
    "source_docs": ["Accel positions.docx"],
    "bands": {
        "senior": {
            "progressive_skills": [
                "Process design, Detail Engineering of industrial/waste water and/or water, DM Plant, UF, RO, Desalination plant, thermal power plant",
                "FEED Process selection, process design calculation, Estimation, proposals, Mass balance, hydraulic calculations, Flow diagram (PFD), Piping & instrumentation (P&ID) diagram, Layout Plan, HAZOP, Basic Engineering Package",
                "Sizing chemical handling facilities for water/wastewater; Sizing Pumping system",
                "Developing and operating field/pilot testing for design",
                "Process selection for the handling, treatment, and disposal of solid, liquid, hazardous and toxic wastes; Recycle & Reuse of Industrial wastewater",
                "Detail engineering during project execution",
                "Knowledge of energy recovery devices for energy conservation",
                "Updated with latest software used for RO-UF Projection",
                "Expert in designing ETP Plants preferably in food and beverages, Chemical, Pulp and paper, and oil and gas sector",
                "Knowledge of technology for oil removal, suspended solids removal, BOD and COD reduction technology",
                "Conduct feasibility study & technical validation of Service (O&M, Retrofits, Revamp, Modification, Water Audit) & System proposals",
                "Review customer's Service PO, submission of BoM to SCM, plan for mobilization of manpower",
                "Provide inputs for successful troubleshooting by Service Engineers and O&M Site Managers",
                "Ensure customer satisfaction targets, response time, turnaround time, warranty & contract service delivery",
                "After-sales warranty / contract management of all sites under warranty/contract",
                "Conduct periodic and regular training for Branch/HO Service Engineers and O&M crew at all sites",
                "Technical evaluation of vendor offers for Service Orders",
            ],
            "arvind_specific": ["Arvind Envisol — Process Expert for RO and ETP technologies"],
            "leadership_skills": [],
            "qualifications": [">6-7 Years of experience", "B.E. Chemical/Mechanical", "CTC range 10-15 LAC"],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 34. RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT — ATIRA Director ───────
ROLES.append({
    "dept": "RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT",
    "role_family": "Director – Textile Research Institute (ATIRA)",
    "source_docs": ["ATIRA - Dy Director or Director-31 10 17.docx"],
    "note": "ATIRA (Textile Industry Research Association) is an affiliated research institute founded by Dr. Vikram Sarabhai and Shri Kasturbhai Lalbhai — not a direct Arvind Limited business unit, but closely tied to the Lalbhai family/textile ecosystem. Mapped to closest-fit department per instructions.",
    "bands": {
        "executive": {
            "progressive_skills": [
                "Head the research institute, focusing on creative applications for the textile industry",
                "Centre of Excellence work for Composites, GeoTextiles and Nano Technology",
                "Collaborate with reputed international textile R&D institutes in Germany and the UK",
                "Lead a team of young, dynamic & qualified professionals for multifaceted institute growth",
            ],
            "arvind_specific": ["ATIRA — Textile Industry Research Association, founded by Dr Vikram Sarabhai and Shri Kasturbhai Lalbhai"],
            "leadership_skills": ["Director / Deputy Director-level leadership of the research institute"],
            "qualifications": [
                "Great leadership skills",
                "Enough Industry/Technology handling experience (Age bracket: 45-50 years)",
                "Good textile background with extensive experience in product development, Industrial interface; can effectively run the Institute",
                "Doctorate degree an added credential",
                "Publications in scientific/international journals",
                "Patented/patentable research work",
                "International exposure to industry/R&D/scientific work preferred",
                "Flair and passion for R&D",
                "Passion for Techno Start-ups / monetizing technology, ideas, innovation",
                "Good communication skills, good administrative abilities, effective networking skills",
                "Exposure to working with Government agencies",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 35. STRATEGY & CORPORATE DEVELOPMENT — Business Head – Egypt ───────────
ROLES.append({
    "dept": "STRATEGY & CORPORATE DEVELOPMENT",
    "role_family": "Business Head – International Operations (Egypt)",
    "source_docs": ["Business Head-Egypt.docx"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Oversee the financial performance of the Egypt operations, ensuring profitability and cost efficiency",
                "Develop and maintain strong relationships with vendors to ensure quality and timely delivery of services and products per Company Standards",
                "Manage outsourcing processes to optimize operational efficiency and cost-effectiveness, ensuring alignment with company standards and customer expectations",
                "Strive for new business opportunities to drive growth and expand market presence in and around Egypt",
                "Develop and implement strategic plans to achieve business objectives and enhance competitive positioning",
                "Lead, mentor & develop a high-performing team to achieve business goals and foster a positive work environment",
            ],
            "arvind_specific": ["Arvind Ltd. — Egypt international operations"],
            "leadership_skills": ["Business Head-level leadership of Egypt operations"],
            "qualifications": [
                "20+ years of experience in a similar industry",
                "Proven track record in P&L management and vendor relations",
                "Extensive experience in outsourcing, OEM management & managing local collaborations",
                "Strong business development skills with a strategic mindset",
                "Excellent leadership and team management abilities",
                "Exceptional communication and interpersonal skills",
                "Ability to work effectively in a dynamic and fast-paced environment",
                "Preferred industry experience: Manufacturing, Apparel",
            ],
            "kpis": [],
            "reporting_to": "",
        },
    },
    "jds": [],
})

# ── 36. FINANCE & ACCOUNTS — VP – Head of Finance (GCC) ─────────────────────
ROLES.append({
    "dept": "FINANCE & ACCOUNTS",
    "role_family": "VP – Head of Finance (GCC)",
    "source_docs": ["JD_Head of Finance.pdf"],
    "bands": {
        "executive": {
            "progressive_skills": [
                "Establish, stabilise, and scale Finance Operations at the Global Capability Centre (GCC)",
                "Lead end-to-end delivery of Procure-to-Pay (PTP), Order-to-Cash (OTC), Controllership (CTR), and Consolidation processes for multiple entities, managing a team of 200+ FTEs",
                "Lead end-to-end setup and scaling of Finance operations at the GCC, including organisation design, governance, operating model, and capability build",
                "Build a strong leadership team across PTP, OTC, CTR, and Consolidation",
                "Establish a high-performance culture focused on accountability, continuous improvement, and talent development",
                "Ensure adherence to SLAs, KPIs, internal controls, SOX, and compliance requirements",
                "Drive standardisation, harmonisation, and documentation of global finance processes",
                "Act as the single point of accountability for finance service delivery to multiple stakeholders",
                "Lead large-scale finance transitions into the GCC",
                "Define and execute structured transition methodologies including process migration, shadowing, reverse shadowing, and stabilisation",
                "Manage transition risks, change management, and stakeholder communication",
                "Drive finance transformation initiatives: process re-engineering and simplification, automation (RPA, workflow tools), ERP optimisation (SAP & S/4HANA), advanced analytics and reporting",
                "Partner with IT and Transformation teams to build a future-ready finance function",
                "Deliver measurable productivity, cost, and quality improvements year-on-year",
                "Establish robust governance mechanisms including SteerCos, Ops Reviews, and performance dashboards",
                "Partner closely with Group CFOs, Business Finance leaders, Internal Audit, and external auditors",
                "Provide strategic insights and recommendations to finance leadership",
                "Lead hiring, capability development, and succession planning for finance teams",
                "Build strong functional expertise across accounting, reporting, compliance, and analytics",
                "Drive learning agendas including leadership development, digital skills, and functional depth",
            ],
            "arvind_specific": ["Arvind Limited's Global Capability Centre (GCC) — Finance Operations setup and scaling"],
            "leadership_skills": ["VP-level leadership managing a team of 200+ FTEs"],
            "qualifications": [
                "Chartered Accountant (CA) – Preferred",
                "15+ years of progressive finance experience (SAP and S4 HANA Mandatory)",
                "Minimum 5 years in GCC / Shared Services setup or leadership roles",
                "Proven experience setting up or scaling GCCs",
                "Proven experience leading multi-process finance operations",
                "Proven experience managing large transitions and transformations",
                "Prior experience in manufacturing environments preferred",
                "Deep expertise across PTP, OTC, RTR/CTR, and Consolidation",
                "Proven experience with SAP and S4 HANA (Non-Negotiable)",
                "Strong exposure to finance transformation and automation",
                "Proven people leader with experience managing large finance teams",
                "Strong executive presence and stakeholder management skills",
                "Transformation mindset with ability to lead change in complex environments",
                "Structured, data-driven, and execution-focused",
            ],
            "kpis": [],
            "reporting_to": "Head of Global Capability Centre (GCC)",
        },
    },
    "jds": [],
})

print(f"ALL ROLES LOADED: {len(ROLES)} role families")

# ════════════════════════════════════════════════════════════════════════════
# JD SOURCE TEXT MAPPING — (dept, role_family, band) -> extracted .txt filename(s)
# ════════════════════════════════════════════════════════════════════════════

EXTRACT_DIR = Path("/tmp/jd_extract")

JD_SOURCE_MAP = [
    ("LEGAL & COMPLIANCE", "Head Legal", "executive", ["2-JD-Head-Legal (2) (1)"]),
    ("SUPPLY CHAIN & LOGISTICS", "Head – Supply Chain (Knits)", "executive", ["About Arvind and JD - Head SCM, Indigo knits"]),
    ("RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT", "Head – Product Development (Dress Shirts)", "executive", ["About Arvind and JD- Dress Shirts Category"]),
    ("RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT", "Head – Product Development & Innovation (Activewear)", "executive", ["Activewear - JD", "Activewear -Product Development and Innovation Head"]),
    ("STRATEGY & CORPORATE DEVELOPMENT", "Chief Operating Officer (Institutional)", "executive", ["Ahmedabad University - JD"]),
    ("STRATEGY & CORPORATE DEVELOPMENT", "Business Head – Security & Surveillance (Telecom)", "executive", ["Business Head Security and Survillence - Telecom"]),
    ("MAINTENANCE & ENGINEERING", "Administration & Facility Management", "lead", ["Chief Manager Administration and facility mgmt"]),
    ("MAINTENANCE & ENGINEERING", "Administration & Facility Management", "executive", ["Central Administration and facility mgmt"]),
    ("STRATEGY & CORPORATE DEVELOPMENT", "CEO – Business Unit (Human Protection)", "executive", ["CEO - Human Protection"]),
    ("STRATEGY & CORPORATE DEVELOPMENT", "CEO – Business Unit (Knits)", "executive", ["CEO Knits"]),
    ("STRATEGY & CORPORATE DEVELOPMENT", "CEO – Turnaround Specialist (Distressed Assets)", "executive", ["CEO- Envisol", "CEO- Turnaround Specialist"]),
    ("STRATEGY & CORPORATE DEVELOPMENT", "CEO – Business Unit (Water/EPC)", "executive", ["CEO- Water"]),
    ("FINANCE & ACCOUNTS", "Chief Financial Officer (Institutional)", "executive", ["CFO JD"]),
    ("FINANCE & ACCOUNTS", "Chief Financial Officer (Arvind Smartspaces)", "executive", ["CFO - Arvind Smartspaces.doc"]),
    ("INFORMATION TECHNOLOGY", "Chief Information Officer", "executive", ["CIO", "Chief Info and Digital Officer"]),
    ("MERCHANDISING & BUYING", "Merchandising", "senior", ["Chief Merchandising Officer"]),
    ("MERCHANDISING & BUYING", "Merchandising", "executive", ["Chief Merchandising Officer_Internet"]),
    ("FINANCE & ACCOUNTS", "Direct Tax", "mid", ["Direct Tax_ Sr Analyst_Job_Descriptions"]),
    ("FINANCE & ACCOUNTS", "Indirect Tax (GST)", "mid", ["Indirect Tax_ Sr Analyst_Job_Descriptions"]),
    ("FINANCE & ACCOUNTS", "FP&A", "mid", ["FP&A_ Sr Analyst_Job_Descriptions"]),
    ("STRATEGY & CORPORATE DEVELOPMENT", "Executive Assistant – GCC Leadership", "lead", ["GCC EA JD"]),
    ("HUMAN RESOURCES", "Head of HR – GCC", "executive", ["HR"]),
    ("HUMAN RESOURCES", "HR Shared Services Tower Lead", "lead", ["HR"]),
    ("INFORMATION TECHNOLOGY", "IT Support Manager", "lead", ["IT_Support_Manager_JD"]),
    ("INFORMATION TECHNOLOGY", "Technical Support Associate", "mid", ["Technical_Support_Associate_JD"]),
    ("INFORMATION TECHNOLOGY", "Automation & AI Associate", "junior", ["Job Description - Associate Automation & AI"]),
    ("FINANCE & ACCOUNTS", "Legal Entity Controller", "lead", ["Legal Entity Controller"]),
    ("INFORMATION TECHNOLOGY", "Master Data Management (MDM) Manager", "lead", ["MDM - Manager"]),
    ("INFORMATION TECHNOLOGY", "Master Data Management (MDM) Manager", "executive", ["MDM - JD"]),
    ("FINANCE & ACCOUNTS", "Procure to Pay (P2P)", "lead", ["Manager - P2P"]),
    ("FINANCE & ACCOUNTS", "Record to Report (R2R)", "lead", ["Manager - R2R"]),
    ("HUMAN RESOURCES", "Manager HR / Sr Manager HR", "senior", ["Business HR"]),
    ("HUMAN RESOURCES", "Business Head – HR & Industrial Relations", "executive", ["Business Head HR and IR Textiles", "Business Head HR and IR_17.12.15"]),
    ("MARKETING & COMMUNICATIONS", "Institutional Sales Head (Home Linen)", "executive", ["JD - Institutional Sales Head"]),
    ("STRATEGY & CORPORATE DEVELOPMENT", "Business Head – Water & Wastewater Solutions", "executive", ["Accel positions"]),
    ("RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT", "Process Expert – RO/ETP", "senior", ["Accel positions"]),
    ("RESEARCH & DEVELOPMENT / PRODUCT DEVELOPMENT", "Director – Textile Research Institute (ATIRA)", "executive", ["ATIRA - Dy Director or Director-31 10 17"]),
    ("STRATEGY & CORPORATE DEVELOPMENT", "Business Head – International Operations (Egypt)", "executive", ["Business Head-Egypt"]),
    ("FINANCE & ACCOUNTS", "VP – Head of Finance (GCC)", "executive", ["JD_Head of Finance"]),
]


def clean_extracted_text(raw: str) -> str:
    lines = raw.split("\n")
    cleaned = []
    skip_markers = ("Page  PAGE", "Page PAGE", "NUMPAGES", "Job Description\n")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if any(m in stripped for m in skip_markers):
            continue
        if stripped == "Job Description":
            continue
        cleaned.append(stripped)
    return "\n".join(cleaned)


def attach_jd_sources():
    by_key = {(r["dept"], r["role_family"]): r for r in ROLES}
    for dept, role_family, band, doc_stems in JD_SOURCE_MAP:
        role = by_key.get((dept, role_family))
        if role is None:
            print(f"  ! WARNING: no role found for {dept} / {role_family}")
            continue
        texts = []
        for stem in doc_stems:
            fpath = EXTRACT_DIR / f"{stem}.txt"
            if not fpath.exists():
                print(f"  ! WARNING: missing extracted file {fpath}")
                continue
            texts.append(clean_extracted_text(fpath.read_text(encoding="utf-8")))
        if not texts:
            continue
        combined = "\n\n".join(texts)
        ext_names = [f"{s}.docx" if not s.endswith(".doc") else f"{s}.doc" for s in doc_stems]
        role["jds"].append({"band": band, "source_docs": doc_stems, "text": combined})


attach_jd_sources()
total_jds = sum(len(r["jds"]) for r in ROLES)
print(f"Attached {total_jds} sample JD text blocks across all role families")


# ════════════════════════════════════════════════════════════════════════════
# FILE WRITERS
# ════════════════════════════════════════════════════════════════════════════

FIELD_KEYS = ["core_skills", "progressive_skills", "arvind_specific", "leadership_skills",
              "qualifications", "kpis"]


def build_taxonomy_yaml(role: dict) -> dict:
    division = DEPT_TO_DIVISION[role["dept"]]
    bands_out = {}
    for band_key in BAND_ORDER:
        band_data = role["bands"].get(band_key)
        label, years, tag = BAND_LABELS[band_key]
        if band_data is None:
            bands_out[band_key] = {
                "label": label,
                "years": years,
                "seniority_tag": tag,
                "data_available": False,
                "note": "No document found for this band — infer from adjacent band if needed",
            }
            continue
        entry = {
            "label": label,
            "years": years,
            "seniority_tag": tag,
        }
        prev_band = BAND_ORDER[BAND_ORDER.index(band_key) - 1] if BAND_ORDER.index(band_key) > 0 else None
        if prev_band and role["bands"].get(prev_band):
            entry["inherits_from"] = prev_band
        for key in FIELD_KEYS:
            entry[key] = band_data.get(key, [])
        entry["reporting_to"] = band_data.get("reporting_to", "")
        bands_out[band_key] = entry

    out = {
        "role_family": role["role_family"],
        "department": role["dept"],
        "division": division,
        "company": "Arvind Limited",
        "source_docs": role["source_docs"],
        "experience_bands": bands_out,
    }
    if role.get("note"):
        out["note"] = role["note"]
    return out


def build_jd_text(role: dict, jd: dict) -> str:
    """Reconstruct/clean a JD into the file format with metadata header."""
    band_key = jd["band"]
    label, years, tag = BAND_LABELS[band_key]
    division = DEPT_TO_DIVISION[role["dept"]]
    metadata = {
        "role_family": role["role_family"],
        "department": role["dept"],
        "division": division,
        "yoe_band": years,
        "seniority_label": label,
        "source_doc": ", ".join(f"{s}.docx" if not any(s.endswith(e) for e in (".doc", ".pdf")) else s
                                  for s in jd["source_docs"]),
        "extracted_date": TODAY,
        "approved_by": "seed",
        "generation_version": "v1.0",
        "feedback_score": None,
    }
    meta_json = json.dumps(metadata, indent=2, ensure_ascii=False)
    return f"---METADATA---\n{meta_json}\n---END METADATA---\n\n{jd['text']}"


def jd_filename(role: dict, band_key: str) -> str:
    role_slug = slugify(role["role_family"])
    band_suffix = band_key  # junior/mid/senior/lead/executive — unique within role dir already
    yoe_slug = BAND_LABELS[band_key][1].replace("–", "_").replace("+", "plus")
    return f"{role_slug}_{yoe_slug}.txt"


def build_tone_guide(dept: str, dept_roles: list) -> str:
    division = DEPT_TO_DIVISION[dept]
    all_arvind_lines = []
    for r in dept_roles:
        for band in r["bands"].values():
            all_arvind_lines.extend(band.get("arvind_specific", []))
    arvind_context = "\n".join(f"- {line}" for line in dict.fromkeys(all_arvind_lines)) or "- (no Arvind-specific terms observed in the uploaded docs for this department)"

    role_names = ", ".join(sorted(set(r["role_family"] for r in dept_roles)))

    return f"""Department: {dept}
Division: {division}
Company: Arvind Limited

TONE OBSERVED IN UPLOADED DOCUMENTS:
Documents for this department span from operational/transactional process descriptions
(Shared Services / GCC roles: tax, R2R, P2P, IT support) written in compact, compliance-driven
language with heavy use of acronyms (SLA, KPI, SOP, GST, TDS) — to senior leadership and CEO/CXO
postings (Business Head, CEO, Director roles) written in a more strategic, vision-led register
("define and execute long-term strategy," "drive global expansion," "own the P&L").
Role families covered in this department: {role_names}.
Across both registers, responsibilities are listed as flat action-verb bullets rather than narrative
prose, and seniority is signalled through scope language ("end-to-end," "own," "lead," "drive,"
"set the vision for") rather than adjectives.

LANGUAGE RULES:
- Voice: Second-person ("You will", "You have", "You are")
- Avoid: rockstar, ninja, guru, wizard, superstar, passionate, driven
- Always name Arvind Limited in the Role Summary
- Reference relevant plants / brands / BUs where contextually appropriate

SECTION FORMAT (all JDs must follow this):
1. Role Summary (3–4 lines)
2. Key Responsibilities (5–7 bullets)
3. Must-Have Skills (5–6 bullets)
4. Nice-to-Have Skills (3–4 bullets)
5. What We Offer (optional)

RESPONSIBILITY LANGUAGE BY YoE BAND:
- 0–2 years:   "You will support / assist / execute"
- 2–5 years:   "You will own / manage / lead"
- 5–8 years:   "You will drive / develop / oversee"
- 8–12 years:  "You will define / build / transform"
- 12+ years:   "You will set the vision for / own the P&L of / lead the strategy for"

ARVIND-SPECIFIC CONTEXT NOTES FOR THIS DEPARTMENT:
{arvind_context}
"""


def folder_safe(name: str) -> str:
    """Sanitize a department/role_family name for use as a filesystem path segment.
    Preserves the literal name in YAML/JSON content — this only affects directory names."""
    return name.replace("/", "-").strip()


def write_role(role: dict) -> None:
    dept_dir_name = folder_safe(role["dept"])
    family_dir_name = folder_safe(role["role_family"])
    base = KB_ROOT / dept_dir_name / family_dir_name
    (base / "sample_jds").mkdir(parents=True, exist_ok=True)
    (base / "feedback").mkdir(parents=True, exist_ok=True)

    taxonomy = build_taxonomy_yaml(role)
    (base / "skills_taxonomy.yaml").write_text(
        yaml.dump(taxonomy, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8"
    )

    version_data = {
        "current_version": "v1.0",
        "last_updated": TODAY,
        "approved_jds_count": 0,
        "feedback_submissions_count": 0,
        "avg_quality_rating": None,
        "edit_ratio_trend": "stable",
        "source_docs_count": len(role["source_docs"]),
    }
    (base / "version.yaml").write_text(
        yaml.dump(version_data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    for jd in role["jds"]:
        filename = jd_filename(role, jd["band"])
        content = build_jd_text(role, jd)
        (base / "sample_jds" / filename).write_text(content, encoding="utf-8")

    (base / "feedback" / "feedback_log.jsonl").write_text("", encoding="utf-8")
    (base / "feedback" / "edit_diffs.jsonl").write_text("", encoding="utf-8")


def write_tone_guides() -> None:
    depts = sorted(set(r["dept"] for r in ROLES))
    for dept in depts:
        dept_roles = [r for r in ROLES if r["dept"] == dept]
        guide = build_tone_guide(dept, dept_roles)
        dept_dir = KB_ROOT / folder_safe(dept)
        dept_dir.mkdir(parents=True, exist_ok=True)
        (dept_dir / "tone_guide.txt").write_text(guide, encoding="utf-8")


def main():
    for role in ROLES:
        write_role(role)
    write_tone_guides()

    total_jd_files = sum(len(r["jds"]) for r in ROLES)
    depts_covered = sorted(set(r["dept"] for r in ROLES))

    print()
    print("=" * 70)
    print("KB BUILD COMPLETE")
    print("=" * 70)
    print(f"Role families built: {len(ROLES)}")
    print(f"Sample JD files written: {total_jd_files}")
    print(f"Departments covered ({len(depts_covered)}):")
    for d in depts_covered:
        count = len([r for r in ROLES if r["dept"] == d])
        print(f"  - {d} ({count} role family/families)")
    print(f"Tone guides written: {len(depts_covered)}")
    print(f"Output root: {KB_ROOT}")


if __name__ == "__main__":
    main()
