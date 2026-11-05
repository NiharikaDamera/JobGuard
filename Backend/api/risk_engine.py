
import re


def analyze_job_risk(job_description):
    text = job_description.lower()

    risk_score = 0
    risk_factors = []

    # Split the job description into individual sentences
    sentences = re.split(r'(?<=[.!?;])\s+|\n\s*\n+', text)

    # 1. Payment requests - very high risk
    # 1. Payment requests - very high risk
# 1. Payment requests - very high risk
    payment_keywords = [
        "registration fee",
        "processing fee",
        "application fee",
        "joining fee",
        "placement fee",
        "pay money",
        "pay a fee",
        "security deposit",
        "deposit money",
        "training fee",
        "training charges",
        "pay before joining",
        "pay to get the job",
        "pay for interview",
        "pay for placement"
    ]

    negation_patterns = [
        r"^\s*(?:we|our company|the company|employer)\s+"
        r"(?:never|do not|don't|does not|doesn't|will not|won't)\s+"
        r"(?:charge|ask for|require|collect)\b",

        r"^\s*(?:applicants|candidates)\s+"
        r"(?:are not required to|do not have to|don't have to)\s+"
        r"pay\b",

        r"^\s*no\s+(?:registration|application|joining|processing|training)\b"
    ]

    payment_found = False

    for sentence in sentences:

        is_negated = any(
            re.search(pattern, sentence)
            for pattern in negation_patterns
        )

        if is_negated:
            continue

        if any(keyword in sentence for keyword in payment_keywords):
            payment_found = True
            break

    if payment_found:
        risk_score += 30
        risk_factors.append(
            "The job appears to request money from applicants."
        )
    # 2. Sensitive personal information requests - high risk

    sensitive_info_patterns = [
        r"\b(?:send|share|submit|upload|provide)\b"
        r"[\s\S]{0,80}\b(?:your|their|the|a|an)?\s*aadhaar\b",

        r"\b(?:send|share|submit|upload|provide)\b"
        r"[\s\S]{0,80}\b(?:your|their|the|a|an)?\s*pan(?:\s+card)?\b",

        r"\b(?:send|share|submit|upload|provide)\b"
        r"[\s\S]{0,80}\b(?:identity proof|identity documents|id proof|"
        r"passport copy|government id)\b",

        r"\b(?:send|share|submit|upload|provide)\b"
        r"[\s\S]{0,80}\b(?:bank details|bank account details|"
        r"account number|bank account number)\b",

        r"\b(?:send|share|provide|tell us)\b"
        r"[\s\S]{0,40}\b(?:otp|one time password|credit card details|"
        r"debit card details|cvv)\b"
    ]

    sensitive_negation_patterns = [
        r"\bnever\s+(?:ask|request|require)\b"
        r"[\s\S]{0,60}\b(?:to\s+)?"
        r"(?:send|share|submit|upload|provide)\b",

        r"\b(?:do not|don't|will not|won't)\s+"
        r"(?:ask|request|require)\b"
        r"[\s\S]{0,60}\b(?:to\s+)?"
        r"(?:send|share|submit|upload|provide)\b",

        r"\b(?:do not|don't|never)\s+"
        r"(?:send|share|submit|upload|provide)\b"
    ]

    sensitive_info_found = False

    for sentence in sentences:
        request_found = any(
            re.search(pattern, sentence)
            for pattern in sensitive_info_patterns
        )

        warning_found = any(
            re.search(pattern, sentence)
            for pattern in sensitive_negation_patterns
        )

        if request_found and not warning_found:
            sensitive_info_found = True
            break

    if sensitive_info_found:
        risk_score += 30
        risk_factors.append(
            "The posting appears to request sensitive personal "
            "or financial information from applicants."
        )

    # 3. Unrealistic salary claims - high risk
        # 3. Unrealistic salary claims - high risk

    salary_keywords = [
        "huge salary",
        "huge income",
        "unlimited income",
        "unlimited earning",
        "earn lakhs from home",
        "earn thousands daily",
        "earn money easily",
        "high income with no experience"
    ]

    # Detect unusually high monthly salary amounts
    salary_patterns = [
        r"(?:₹|rs\.?\s*)\s*(\d+(?:,\d{3})*)\s*(?:per month|/month|monthly)",
        r"(\d+(?:,\d{3})*)\s*(?:per month|/month|monthly)",
        r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs)\s*(?:per month|/month|monthly)"
    ]

    salary_found = False

    # Check predefined suspicious salary claims
    if any(keyword in text for keyword in salary_keywords):
        salary_found = True

    # Check numeric monthly salary claims
    for pattern in salary_patterns:
        matches = re.findall(pattern, text)

        for match in matches:
            try:
                amount = float(match.replace(",", ""))

                # Convert lakh amounts into rupees
                if "lakh" in pattern or "lac" in pattern:
                    amount *= 100000

                if amount > 50000:
                    salary_found = True
                    break

            except ValueError:
                continue

        if salary_found:
            break

    if salary_found:
        risk_score += 20
        risk_factors.append(
            "The posting may contain an unusually high or unrealistic salary claim."
        )
    # 4. Suspicious communication channels - medium risk
    contact_keywords = [
        "whatsapp only",
        "contact me on whatsapp",
        "message me on telegram",
        "contact on whatsapp",
        "contact on telegram",
        "dm me on telegram",
        "dm me on whatsapp",
        "message me privately",
        "contact via whatsapp",
        "contact via telegram",
        "recruiter on whatsapp",
        "recruiter on telegram",
        "recruiter directly through whatsapp",
        "recruiter directly through telegram"
    ]

    contact_found = False

    for sentence in sentences:
        normalized_sentence = re.sub(r'\s+', ' ', sentence).strip()

        if any(keyword in normalized_sentence for keyword in contact_keywords):
            contact_found = True
            break

    if contact_found:
        risk_score += 15
        risk_factors.append(
            "The recruiter appears to rely on a potentially suspicious communication channel."
        )

    # 5. Guaranteed job claims - high risk
    guarantee_keywords = [
        "guaranteed job",
        "100% job guarantee",
        "job guaranteed",
        "guaranteed placement",
        "100% placement",
        "guaranteed employment",
        "assured job",
        "job assured",
        "no interview required",
        "job without interview",
        "selection guaranteed",
        "immediate selection",
        "direct selection guaranteed"
    ]

    for keyword in guarantee_keywords:
        if keyword in text:
            risk_score += 20
            risk_factors.append(
                "The posting makes a guaranteed job or placement claim."
            )
            break

    # 6. Urgency - lower risk
    urgency_keywords = [
        "apply immediately",
        "limited seats",
        "urgent hiring",
        "apply today",
        "act now",
        "apply now",
        "hurry",
        "last chance",
        "limited vacancies",
        "limited openings",
        "only a few positions left",
        "respond immediately",
        "join immediately",
        "immediate joining",
        "offer expires today"
    ]

    for keyword in urgency_keywords:
        if keyword in text:
            risk_score += 10
            risk_factors.append(
                "The posting uses urgency or pressure to encourage immediate action."
            )
            break

    # 7. Suspicious work-from-home claims
    remote_keywords = [
        "work from home and earn",
        "earn from home with no experience",
        "easy work from home",
        "part time work from home",
        "make money from home",
        "earn money from home",
        "work from home no experience",
        "easy online work",
        "easy online job",
        "earn daily from home",
        "working from home",
    ]

    for keyword in remote_keywords:
        if keyword in text:
            risk_score += 10
            risk_factors.append(
                "The posting promotes potentially unrealistic work-from-home or easy-income claims."
            )
            break

    # 8. Too-good-to-be-true claims
    unrealistic_keywords = [
        "earn money instantly",
        "get rich quick",
        "make money fast",
        "work less earn more",
        "zero investment high returns",
        "no investment high returns"
    ]

    for keyword in unrealistic_keywords:
        if keyword in text:
            risk_score += 10
            risk_factors.append(
                "The posting contains potentially unrealistic or too-good-to-be-true claims."
            )
            break

    # 9. Combination rule
    # No experience required is NOT suspicious by itself.
    # It becomes more concerning when combined with an unrealistic salary.
    if "no experience required" in text and salary_found:
        risk_score += 10
        risk_factors.append(
            "The posting combines no experience requirements with an unusually high income claim."
        )

    # 10. Multiple independent warning signs
    if len(risk_factors) >= 4:
        risk_score += 5
        risk_factors.append(
            "Multiple independent risk indicators were detected in the same job posting."
        )

    # Keep score between 0 and 100
    risk_score = min(risk_score, 100)

    # Determine risk level
    if risk_score >= 80:
        risk_level = "Critical"
    elif risk_score >= 60:
        risk_level = "High"
    elif risk_score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return risk_score, risk_level, risk_factors
