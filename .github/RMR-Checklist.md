# RMR Review Checklist

This is the authoritative checklist the RMR Reviewer agent uses to review a
Risk Management Report (RMR) based on template **GLB-QS-TMP-0186**.

For every item, report one of: **PASS**, **FAIL**, or **N/A** (with a short
reason and the location in the document). Items marked *(evidence)* also require
that the referenced report actually exists in the `reports/` folder.

## Purpose
- [ ] Provides a reference to the intended use statement (preferred) or a copy of it.
- [ ] References the User Needs or Pre-Market Regulatory Plan.

## Scope
- [ ] Lists the product name and version number being assessed.
- [ ] States whether the product is a Cyber Device or not.

## Reference Documents
- [ ] All required supporting documents are referenced: Product Security Plan,
      SBOM, CRA, Threat Model Report, SCR, VA, Penetration Test reports, etc.

## Product Security Test Activities — SCR (Secure Code Review)
- [ ] SCR entry completed with exact version numbers, image versions, or commit hashes.
- [ ] Latest assessment date, tool used, and DHF report location completed. *(evidence)*

## VA (Vulnerability Assessment)
- [ ] VA entry completed with a version identifier for the system assessed
      (e.g., OS configuration).
- [ ] Assessment date, tool used, and DHF report location completed. *(evidence)*

## Penetration Testing (PT)
- [ ] PT entry completed with the tested system/product version identifier.
- [ ] Test date, team, and PT report location in the DHF completed. *(evidence)*

## SBOM
- [ ] SBOM table entry completed with exact software versions or commit hashes.
- [ ] Assessment date, tool used, and DHF report location completed. *(evidence)*

## Threat Risk Disposition (Cyber Devices)
- [ ] All medium, high, and critical residual risks are appropriately summarized.
- [ ] Risk disposition decisions are clearly documented as one or more of:
      - **Eliminate** — eliminate the threat so it no longer exists.
      - **Mitigate** — reduce residual risk using safeguards or compensating controls.
      - **Communicate** — inform stakeholders through labeling, contracts, IFU, or Service Manual.

## List of Unmitigated Vulnerability Findings
- [ ] For Cyber Devices, this section is marked N/A.
- [ ] The table contains only unmitigated vulnerabilities.
- [ ] Vulnerabilities with implemented mitigations are excluded from the table.
- [ ] All required columns completed: ID, Vulnerability, Source, Severity,
      Security Impact, Safety Impact, Privacy Impact, Workaround (customer-centric).
- [ ] Security, Safety, and Privacy Impact fields are populated and not marked N/A.
- [ ] For Critical or High findings, a workaround or compensating control is documented.

## Status of Product Security Plan Implementation
- [ ] An implementation status is provided for the current release.
- [ ] The implementation status aligns with the Product Security Plan roadmap.
- [ ] If a previous Product Security Plan exists, the roadmap progression makes sense.

## Risk Summary Table (Cyber Devices)
- [ ] Residual risk numbers match the CRA summary or Table 3.3.
- [ ] Security, privacy, and safety risk totals are internally consistent throughout the document.

## Vulnerability Summary Table (Non-Cyber Devices)
- [ ] Severity classifications (Low, Medium, High, Critical) align with the
      approved assessment methodology (SCR, VA, PT, SBOM, XPT).

## Customer Actionable Information
- [ ] Recommended customer mitigations, security requirements, or workarounds are documented or referenced.
- [ ] Information intended for inclusion in the IFU is identified where required.

## Cybersecurity Metrics
- [ ] For Cyber Devices, patching and vulnerability remediation metrics are reported.
- [ ] Metrics are complete and supported by available data.

## Conclusion
- [ ] Justifies residual risk acceptability.
- [ ] States that mitigations have been implemented and verified.
- [ ] States that the benefits outweigh the remaining cybersecurity risks.

## Document Revision Change Control
- [ ] Revision history completed with author, location, and rationale for changes.

## Content Approvals
- [ ] All required approvers are included according to GLB-QS-PCD-0046.
