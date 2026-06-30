"""
Canonical role taxonomy with must-have skills and exclusion fingerprints.
Used by the JD generator to auto-suggest skills and prevent hallucination bleed.

Structure per entry:
  "canonical_key": {
    "label": display name,
    "department": matches app DEPARTMENTS key,
    "family": matches role family key,
    "sub_category": grouping within dept,
    "role_cluster": tighter grouping,
    "must_have": [...],   # non-negotiable skills for this role
    "nice_to_have": [...],
    "exclude": [...],     # skills that must NOT appear — prevents role bleed
    "keywords": [...],    # role-title keywords that trigger this entry
  }
"""

ROLE_TAXONOMY: dict = {

    # ── TECHNOLOGY ───────────────────────────────────────────────────────────

    "power_bi_analyst": {
        "label": "Power BI Analyst",
        "department": "tech",
        "family": "bi",
        "sub_category": "Data & Analytics",
        "role_cluster": "BI & Reporting",
        "must_have": ["DAX", "Power Query (M)", "Data modelling / star schema",
                      "Power BI Service & Gateway", "SQL (query-only)", "Stakeholder reporting"],
        "nice_to_have": ["Azure Synapse", "Excel Power Pivot", "Paginated Reports (SSRS)",
                         "Python for data prep", "Dataflows"],
        "exclude": ["Python ML libraries", "Model training", "MLOps", "Hyperparameter tuning",
                    "TensorFlow", "PyTorch", "Scikit-learn"],
        "keywords": ["power bi", "bi analyst", "bi developer", "tableau analyst", "reporting analyst"],
    },

    "data_scientist": {
        "label": "Data Scientist",
        "department": "tech",
        "family": "data_science",
        "sub_category": "Data & Analytics",
        "role_cluster": "Data Science & ML",
        "must_have": ["Python / R", "Statistical modelling", "ML algorithms",
                      "Model deployment", "Experiment design / A-B testing", "Pandas / NumPy"],
        "nice_to_have": ["MLflow", "Spark / PySpark", "Feature engineering",
                         "NLP", "Time-series forecasting", "Cloud ML platforms (Azure ML / AWS SageMaker)"],
        "exclude": ["DAX", "Power BI Service admin", "Dashboard design as primary output",
                    "Power Query (M)"],
        "keywords": ["data scientist", "ml engineer", "machine learning", "ai engineer"],
    },

    "data_engineer": {
        "label": "Data Engineer",
        "department": "tech",
        "family": "data_engineering",
        "sub_category": "Data & Analytics",
        "role_cluster": "Data Engineering",
        "must_have": ["SQL / T-SQL", "ETL / ELT pipeline design", "Python or Scala",
                      "Data warehousing concepts", "Azure Data Factory / Glue / Airflow",
                      "Data quality & governance"],
        "nice_to_have": ["Spark", "Databricks", "dbt", "Kafka", "Delta Lake",
                         "Medallion architecture"],
        "exclude": ["DAX", "Power BI dashboard design", "ML model training"],
        "keywords": ["data engineer", "etl developer", "pipeline engineer", "etl"],
    },

    "backend_engineer": {
        "label": "Backend Engineer",
        "department": "tech",
        "family": "backend",
        "sub_category": "Software Engineering",
        "role_cluster": "Backend",
        "must_have": ["Server-side language (Java / .NET / Node.js / Python)",
                      "REST / GraphQL API design", "Database design (SQL + NoSQL)",
                      "Microservices architecture", "System design"],
        "nice_to_have": ["Docker / Kubernetes", "Message queues (Kafka / RabbitMQ)",
                         "Redis caching", "API security (OAuth 2.0 / JWT)"],
        "exclude": ["Frontend frameworks as primary skill", "React / Vue / Angular",
                    "BI dashboarding", "ML model training"],
        "keywords": ["backend", "backend developer", "java engineer", ".net developer",
                     "node engineer", "api developer", "server-side"],
    },

    "frontend_engineer": {
        "label": "Frontend / Full-stack Engineer",
        "department": "tech",
        "family": "frontend",
        "sub_category": "Software Engineering",
        "role_cluster": "Frontend / Full-stack",
        "must_have": ["React / Vue / Angular", "HTML5 / CSS3 / JavaScript (ES6+)",
                      "TypeScript", "REST API consumption", "Component-based architecture",
                      "Responsive design"],
        "nice_to_have": ["Next.js / Nuxt.js", "State management (Redux / Pinia)",
                         "Unit testing (Jest / Vitest)", "CI/CD basics", "Web accessibility (WCAG)"],
        "exclude": ["Backend microservices as primary", "ML model training",
                    "Infrastructure provisioning", "Data engineering pipelines"],
        "keywords": ["frontend", "front-end", "full-stack", "fullstack", "react developer",
                     "vue developer", "angular developer"],
    },

    "devops_engineer": {
        "label": "DevOps / SRE Engineer",
        "department": "tech",
        "family": "devops",
        "sub_category": "Infrastructure & Ops",
        "role_cluster": "DevOps / SRE",
        "must_have": ["CI/CD pipelines (GitHub Actions / Azure DevOps / Jenkins)",
                      "IaC (Terraform / Ansible)", "Docker & Kubernetes",
                      "Cloud platforms (Azure / AWS / GCP)", "Observability (Prometheus / Grafana / ELK)"],
        "nice_to_have": ["GitOps / ArgoCD", "Vault / secrets management",
                         "Linux administration", "Scripting (Bash / Python)", "FinOps"],
        "exclude": ["ML model building", "BI dashboarding", "Full-stack web development as primary"],
        "keywords": ["devops", "sre", "site reliability", "cloud engineer", "platform engineer",
                     "infrastructure engineer"],
    },

    "qa_automation_engineer": {
        "label": "QA Automation Engineer",
        "department": "tech",
        "family": "qa_automation",
        "sub_category": "Quality Engineering",
        "role_cluster": "QA",
        "must_have": ["Selenium / Playwright / Cypress", "Test scripting (Python / Java)",
                      "CI test integration", "Defect management (Jira / Azure DevOps)",
                      "Test planning & execution"],
        "nice_to_have": ["API testing (Postman / RestAssured)", "Performance testing (k6 / JMeter)",
                         "BDD (Cucumber)", "Mobile testing (Appium)"],
        "exclude": ["Infrastructure provisioning", "ML model training",
                    "Dashboard design", "Backend API development as primary"],
        "keywords": ["qa", "quality assurance", "test engineer", "automation tester",
                     "sdet", "qa engineer"],
    },

    "erp_consultant": {
        "label": "SAP / ERP Consultant",
        "department": "tech",
        "family": "enterprise_apps",
        "sub_category": "Enterprise Applications",
        "role_cluster": "ERP",
        "must_have": ["SAP modules (FICO / MM / SD / PP)", "Business process mapping",
                      "Configuration & customisation", "UAT support",
                      "Functional specification writing"],
        "nice_to_have": ["ABAP basics", "SAP S/4HANA", "Power Platform",
                         "Integration (SAP PI/PO / BTP)", "Data migration"],
        "exclude": ["ML model training", "BI dashboarding as primary", "React / Vue frontend"],
        "keywords": ["sap", "erp", "sap fico", "sap mm", "sap sd", "sap consultant",
                     "erp consultant", "power platform"],
    },

    "it_support": {
        "label": "IT Support / Service Desk",
        "department": "tech",
        "family": "it_ops",
        "sub_category": "IT Operations",
        "role_cluster": "Support",
        "must_have": ["ITSM tools (ServiceNow / Jira Service)", "Hardware & OS troubleshooting",
                      "Active Directory / Azure AD", "Networking basics (TCP/IP / DNS / DHCP)",
                      "SLA management"],
        "nice_to_have": ["ITIL Foundation certified", "O365 administration",
                         "Remote desktop tools", "Asset management"],
        "exclude": ["ML model training", "CI/CD pipelines", "Full-stack development",
                    "SAP functional configuration"],
        "keywords": ["it support", "service desk", "helpdesk", "technical support analyst",
                     "l1 support", "l2 support"],
    },

    # ── HUMAN RESOURCES ──────────────────────────────────────────────────────

    "talent_acquisition": {
        "label": "Talent Acquisition Specialist",
        "department": "hr",
        "family": "talent_acquisition",
        "sub_category": "Talent Acquisition",
        "role_cluster": "Recruiting",
        "must_have": ["Full-cycle recruiting", "ATS management (Naukri / LinkedIn Recruiter)",
                      "JD writing & job posting", "Candidate screening & assessment",
                      "Stakeholder management"],
        "nice_to_have": ["Employer branding", "Campus recruitment", "HR analytics basics",
                         "Diversity hiring practices"],
        "exclude": ["Payroll processing", "L&D curriculum design", "HRIS configuration"],
        "keywords": ["recruiter", "talent acquisition", "hiring", "recruitment specialist"],
    },

    "hrbp": {
        "label": "HR Business Partner",
        "department": "hr",
        "family": "hrbp",
        "sub_category": "HR Business Partnering",
        "role_cluster": "HRBP",
        "must_have": ["Business partnering for a functional unit",
                      "Employee relations & grievance handling",
                      "Performance management", "Workforce planning",
                      "HR policy implementation"],
        "nice_to_have": ["Change management", "Succession planning",
                         "HRIS (SAP HCM / Workday)", "HR analytics"],
        "exclude": ["Full-cycle technical recruiting", "Payroll run", "L&D facilitation as primary"],
        "keywords": ["hrbp", "hr business partner", "people partner", "hr generalist"],
    },

    "learning_development": {
        "label": "Learning & Development Specialist",
        "department": "hr",
        "family": "learning_development",
        "sub_category": "Learning & Development",
        "role_cluster": "L&D",
        "must_have": ["Training needs analysis (TNA)", "Curriculum / content design",
                      "Facilitation & delivery", "LMS administration",
                      "Learning impact measurement"],
        "nice_to_have": ["E-learning authoring (Articulate / iSpring)", "Coaching certification",
                         "Leadership development programmes", "Vendor management"],
        "exclude": ["Payroll processing", "Full-cycle recruiting", "Employee relations as primary"],
        "keywords": ["l&d", "learning", "training", "organisational development", "od specialist"],
    },

    "compensation_benefits": {
        "label": "Compensation & Benefits Specialist",
        "department": "hr",
        "family": "comp_ben",
        "sub_category": "Compensation & Benefits",
        "role_cluster": "C&B",
        "must_have": ["Job evaluation & grading", "Salary benchmarking (Mercer / Korn Ferry)",
                      "Incentive & variable pay design", "Benefits administration",
                      "Excel / comp modelling"],
        "nice_to_have": ["HRIS configuration for payroll", "Global mobility basics",
                         "Market pricing tools", "HR analytics"],
        "exclude": ["Full-cycle recruiting", "L&D curriculum design", "HRBP advisory"],
        "keywords": ["compensation", "c&b", "total rewards", "benefits", "remuneration"],
    },

    # ── FINANCE ──────────────────────────────────────────────────────────────

    "financial_analyst": {
        "label": "Financial Analyst",
        "department": "finance",
        "family": "fpa",
        "sub_category": "FP&A",
        "role_cluster": "Financial Planning & Analysis",
        "must_have": ["Financial modelling (Excel / Power BI)", "Budgeting & forecasting",
                      "Variance analysis", "Management reporting",
                      "P&L / Balance sheet understanding"],
        "nice_to_have": ["SAP FICO basics", "Python / VBA for automation",
                         "Hyperion / Anaplan", "Business intelligence tools"],
        "exclude": ["Statutory audit", "Tax compliance filing", "Cost accountancy as primary"],
        "keywords": ["financial analyst", "fp&a", "finance analyst", "business analyst finance"],
    },

    "cost_accountant": {
        "label": "Cost Accountant",
        "department": "finance",
        "family": "cost_accounting",
        "sub_category": "Cost & Management Accounting",
        "role_cluster": "Costing",
        "must_have": ["Product costing (standard / actual)", "BOM & routing analysis",
                      "Overhead absorption", "Variance analysis (material / labour / overhead)",
                      "SAP CO / PP integration"],
        "nice_to_have": ["Activity-based costing", "Cost audit", "MIS reporting",
                         "Advanced Excel"],
        "exclude": ["External audit", "FP&A modelling as primary", "Payroll processing"],
        "keywords": ["cost accountant", "costing", "management accountant", "cost analyst"],
    },

    "statutory_accountant": {
        "label": "Statutory / Accounts Payable / Receivable",
        "department": "finance",
        "family": "accounting",
        "sub_category": "Accounting & Compliance",
        "role_cluster": "Statutory & Compliance",
        "must_have": ["Ind AS / IFRS / Indian GAAP", "Month-end & year-end close",
                      "AP / AR reconciliations", "TDS / GST compliance",
                      "Audit support"],
        "nice_to_have": ["SAP FI", "Bank reconciliation automation", "Internal controls",
                         "Tally ERP"],
        "exclude": ["FP&A modelling", "Product costing", "Payroll run as primary"],
        "keywords": ["accountant", "accounts payable", "accounts receivable", "statutory",
                     "general ledger", "gst", "ind as"],
    },

    # ── SUPPLY CHAIN ─────────────────────────────────────────────────────────

    "supply_chain_analyst": {
        "label": "Supply Chain / Planning Analyst",
        "department": "supply_chain",
        "family": "demand_planning",
        "sub_category": "Planning & Analytics",
        "role_cluster": "Demand & Supply Planning",
        "must_have": ["Demand forecasting", "Inventory management",
                      "S&OP process", "ERP (SAP MM / APO / IBP)",
                      "Excel / Power BI for supply analytics"],
        "nice_to_have": ["Python for demand sensing", "Logistics optimisation",
                         "Supplier performance scorecards", "SCOR framework"],
        "exclude": ["Production scheduling as primary", "Quality auditing",
                    "Financial reporting"],
        "keywords": ["supply chain", "demand planning", "supply planning", "s&op", "inventory analyst"],
    },

    "procurement_specialist": {
        "label": "Procurement Specialist",
        "department": "supply_chain",
        "family": "sourcing_manager",
        "sub_category": "Procurement & Sourcing",
        "role_cluster": "Sourcing",
        "must_have": ["Strategic sourcing", "RFQ / RFP management",
                      "Supplier evaluation & negotiation", "Contract management",
                      "SAP MM / Ariba"],
        "nice_to_have": ["Category management", "Spend analytics", "Supplier development",
                         "ESG in procurement"],
        "exclude": ["Demand forecasting as primary", "Logistics & distribution",
                    "Quality inspection"],
        "keywords": ["procurement", "sourcing", "buyer", "purchasing", "vendor management"],
    },

    # ── MANUFACTURING / OPERATIONS ────────────────────────────────────────────

    "production_manager": {
        "label": "Production / Plant Manager",
        "department": "manufacturing",
        "family": "production_manager",
        "sub_category": "Production Management",
        "role_cluster": "Manufacturing Operations",
        "must_have": ["Production planning & scheduling", "Lean / Six Sigma tools",
                      "OEE monitoring", "Workforce & shift management",
                      "Safety (EHS) compliance"],
        "nice_to_have": ["SAP PP", "TPM implementation", "Kaizen facilitation",
                         "Cost reduction projects", "5S"],
        "exclude": ["Financial reporting", "Software development", "HR policy design"],
        "keywords": ["production manager", "plant manager", "manufacturing manager",
                     "operations manager", "shift manager"],
    },

    "quality_manager": {
        "label": "Quality Manager / QA Manager",
        "department": "manufacturing",
        "family": "qa_manager",
        "sub_category": "Quality Assurance & Control",
        "role_cluster": "Quality",
        "must_have": ["Quality management systems (ISO 9001 / SA8000)",
                      "Inline & final inspection (AQL sampling)",
                      "Root cause analysis (8D / Ishikawa)",
                      "Customer audit management",
                      "Quality KPI reporting"],
        "nice_to_have": ["Lean Six Sigma Green Belt", "SPC / statistical quality tools",
                         "Fabric testing knowledge", "Supplier quality development"],
        "exclude": ["Software QA / test automation", "Financial auditing",
                    "Production scheduling as primary"],
        "keywords": ["quality manager", "qa manager", "quality assurance", "quality control",
                     "qc manager", "aql"],
    },

    # ── SALES & MARKETING ─────────────────────────────────────────────────────

    "brand_manager": {
        "label": "Brand / Marketing Manager",
        "department": "marketing",
        "family": "brand_manager",
        "sub_category": "Brand & Marketing",
        "role_cluster": "Brand Management",
        "must_have": ["Brand strategy & positioning", "Go-to-market planning",
                      "Consumer research & insights", "Campaign management",
                      "P&L ownership for brand"],
        "nice_to_have": ["Digital / performance marketing", "Agency management",
                         "Retail / trade marketing", "Social media strategy"],
        "exclude": ["Software development", "Financial modelling as primary",
                    "HR policy design"],
        "keywords": ["brand manager", "marketing manager", "product manager marketing",
                     "brand marketing"],
    },

    "sales_manager": {
        "label": "Sales Manager / Key Account Manager",
        "department": "sales",
        "family": "sales_manager_home_linen",
        "sub_category": "Sales",
        "role_cluster": "B2B Sales",
        "must_have": ["Key account management", "Revenue & quota achievement",
                      "Customer relationship management (CRM)",
                      "Commercial negotiation", "Sales forecasting"],
        "nice_to_have": ["Channel / distributor management", "Trade promotions",
                         "Salesforce / SAP CRM", "B2B solution selling"],
        "exclude": ["Brand advertising", "Software development", "Financial audit"],
        "keywords": ["sales manager", "key account", "national sales", "regional sales",
                     "account manager", "business development"],
    },
}


def get_role_match(role_title: str, department: str = "", family: str = "") -> dict | None:
    """
    Best-effort match of a free-text role title to a canonical role entry.
    Returns the matched entry dict, or None if nothing matches well.
    Prefers entries whose department/family match the form selection.
    """
    title_lower = role_title.lower()
    best = None
    best_score = 0

    for key, entry in ROLE_TAXONOMY.items():
        score = 0
        for kw in entry.get("keywords", []):
            if kw in title_lower:
                score += 2 if len(kw) > 8 else 1  # longer keyword = better signal
        if department and entry.get("department") == department:
            score += 1
        if family and entry.get("family") == family:
            score += 2
        if score > best_score:
            best_score = score
            best = entry

    return best if best_score > 0 else None


def suggest_skills(role_title: str, department: str = "", family: str = "") -> dict:
    """Return must_have, nice_to_have, and exclude lists for a given role."""
    match = get_role_match(role_title, department, family)
    if match:
        return {
            "must_have":    match.get("must_have", []),
            "nice_to_have": match.get("nice_to_have", []),
            "exclude":      match.get("exclude", []),
            "canonical_label": match.get("label", ""),
            "sub_category":    match.get("sub_category", ""),
            "role_cluster":    match.get("role_cluster", ""),
        }
    return {"must_have": [], "nice_to_have": [], "exclude": [],
            "canonical_label": "", "sub_category": "", "role_cluster": ""}
