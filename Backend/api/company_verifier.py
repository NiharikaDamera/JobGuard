
import re
from urllib.parse import urlparse


def verify_company(company_name, job_description):
    """
    Check for basic company-verification signals.
    This does not prove whether a company is genuine or fraudulent.
    """

    company_name = company_name.strip()
    description = job_description.lower()

    verification_checks = []

    # Check whether a company name was provided
    if company_name:
        verification_checks.append({
            "check": "Company name provided",
            "status": "PASS",
            "message": "A company name was provided for investigation."
        })
    else:
        verification_checks.append({
            "check": "Company name provided",
            "status": "WARNING",
            "message": "No company name was provided."
        })

    # Look for common requests for money
    payment_terms = [
        "registration fee",
        "security deposit",
        "pay to apply",
        "upfront payment",
        "training fee"
    ]

    payment_found = any(
        term in description for term in payment_terms
    )

    if payment_found:
        verification_checks.append({
            "check": "Recruitment payment",
            "status": "WARNING",
            "message": (
                "The description mentions a possible recruitment "
                "payment. Verify this directly with the employer."
            )
        })
    else:
        verification_checks.append({
            "check": "Recruitment payment",
            "status": "PASS",
            "message": (
                "No configured recruitment-payment phrase was detected. "
                "This does not guarantee the job is safe."
            )
        })

    # Look for official website links in the description
    urls = re.findall(
        r"https?://[^\s]+|www\.[^\s]+",
        job_description,
        flags=re.IGNORECASE
    )

    website_urls = []

    for url in urls:
        cleaned_url = url.rstrip(".,);]")
        if cleaned_url.lower().startswith("www."):
            cleaned_url = "https://" + cleaned_url

        parsed = urlparse(cleaned_url)

        if parsed.hostname:
            website_urls.append({
                "url": cleaned_url,
                "domain": parsed.hostname
            })

    if website_urls:
        verification_checks.append({
            "check": "Website link found",
            "status": "INFO",
            "message": (
                "A website link was found. Check independently that "
                "the domain belongs to the employer."
            ),
            "websites": website_urls
        })
    else:
        verification_checks.append({
            "check": "Website link found",
            "status": "WARNING",
            "message": (
                "No website link was found in the description. "
                "This alone does not mean the company is fraudulent."
            )
        })

    return {
        "company_name": company_name,
        "verification_status": "NEEDS_REVIEW",
        "message": (
            "These are preliminary checks, not a verified company "
            "identity. Confirm the employer through independent sources."
        ),
        "checks": verification_checks
    }
