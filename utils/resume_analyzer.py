import re
import datetime

# Extended, categorized keywords for richer resume mapping
CATEGORIZED_KEYWORDS = {
    "Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Golang", 
        "Ruby", "PHP", "Swift", "Kotlin", "Rust", "Scala", "SQL", "HTML", "CSS", "Bash"
    ],
    "Frameworks & Libraries": [
        "React", "Angular", "Vue", "Next.js", "Nuxt", "Svelte", "Express", "Django", 
        "Flask", "FastAPI", "Spring Boot", "Rails", "Laravel", "ASP.NET", "Tailwind", "Bootstrap",
        "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Keras"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Terraform", "Ansible", 
        "Jenkins", "Git", "GitHub Actions", "CI/CD", "Prometheus", "Grafana", "Nginx", "Linux", "Serverless"
    ],
    "Databases & Systems": [
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQLite", "Oracle", 
        "DynamoDB", "Cassandra", "Redshift", "Snowflake", "BigQuery", "Kafka", "Spark", "Hadoop"
    ],
    "Methodologies & Tools": [
        "Project Management", "Product Management", "Agile", "Scrum", "Kanban", "Jira", "System Design",
        "Microservices", "REST API", "GraphQL", "gRPC", "Testing", "Pytest", "Jest", "CI-CD", "DevOps"
    ],
    "Soft Skills": [
        "Communication", "Leadership", "Teamwork", "Problem Solving", "Mentorship", 
        "Research", "Automation", "Optimization", "Collaboration", "Management"
    ]
}

# Flatten for backward compatibility
KEYWORDS = sorted(list({kw for sublist in CATEGORIZED_KEYWORDS.values() for kw in sublist}))

REQUIRED_SECTIONS = [
    "summary", "experience", "education", "skills", "projects", "certifications"
]

SECTION_PATTERNS = {
    "summary": ["summary", "profile", "about me", "professional summary", "objective"],
    "experience": ["experience", "work history", "professional experience", "employment", "work experience"],
    "education": ["education", "academic", "degree", "university", "college", "education history"],
    "skills": ["skills", "technical skills", "key skills", "core competencies", "technologies"],
    "projects": ["projects", "project experience", "academic projects", "key projects"],
    "certifications": ["certifications", "certified", "achievements", "licenses", "awards"]
}

ACTION_VERBS = [
    "managed", "developed", "designed", "led", "created", "implemented",
    "built", "improved", "automated", "analyzed", "optimized", "coordinated",
    "streamlined", "delivered", "launched", "scaled", "accelerated", "orchestrated",
    "established", "formulated", "conceptualized", "engineered", "pioneered", "revamped",
    "overhauled", "cultivated", "spearheaded", "directed", "supervised", "mentored",
    "collaborated", "facilitated", "negotiated", "secured", "generated", "maximized",
    "decreased", "increased", "reduced", "saved", "achieved", "executed", "architected"
]

CONTACT_PATTERNS = {
    "email": r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}",
    "phone": r"(?:\+?\d{1,3}[\s-]?)?(?:\(\d{3}\)|\d{3})[\s-]?\d{3}[\s-]?\d{4}",
    "linkedin": r"linkedin\.com/[\w\-]+",
    "github": r"github\.com/[\w\-]+",
    "website": r"https?://[\w\.-]+\.[a-zA-Z]{2,}(/[\w\-./?%&=]*)?"
}

METRIC_PATTERNS = [
    r"\d+%",                         # e.g., 40%, 100%
    r"\$\d+[\d,]*",                  # e.g., $10,000, $5M
    r"\d+\s*(?:years|yrs|months|mos)",# e.g., 5 years, 6 months
    r"\d+\s*(?:x|times)",            # e.g., 3x, 5 times
    r"\d{2,}\s*(?:people|users|clients|customers|servers|databases|projects|leads|bugs)" # e.g. 50 users, 15 bugs
]

REWRITE_TEMPLATES = [
    {
        "pattern": r"\b(testing|test|tested)\b",
        "before_default": "Responsible for testing the system",
        "after": "Architected and executed automated testing suites using Pytest/Selenium, improving test coverage by 35% and reducing deployment cycles."
    },
    {
        "pattern": r"\b(sql|database|db|query|queries)\b",
        "before_default": "Wrote SQL queries and managed database",
        "after": "Designed and optimized complex SQL queries and PostgreSQL database schemas, reducing query response times by 40%."
    },
    {
        "pattern": r"\b(python|code|coded|coding|program)\b",
        "before_default": "Wrote Python code for the application",
        "after": "Engineered high-performance, modular Python microservices and REST APIs, reducing latency by 20% and improving code throughput."
    },
    {
        "pattern": r"\b(managed|manager|leadership|led|team)\b",
        "before_default": "Managed a team of developers",
        "after": "Spearheaded and mentored a cross-functional team of 6 engineers to deliver core cloud features, increasing sprint velocity by 25%."
    },
    {
        "pattern": r"\b(website|frontend|html|css|javascript|react|ui|ux)\b",
        "before_default": "Helped build the website front-end",
        "after": "Developed responsive, accessible React/TypeScript user interfaces, improving web page performance scores by 30%."
    },
    {
        "pattern": r"\b(cloud|aws|azure|devops|docker|kubernetes|deploy)\b",
        "before_default": "Handled deployment and cloud infrastructure",
        "after": "Orchestrated containerized deployment pipelines on AWS using Docker, Kubernetes, and Terraform, achieving 99.9% uptime."
    }
]


def analyze_resume(text, target_job="", job_description=""):
    """Analyze resume text and return structured feedback."""
    text = text or ""
    normalized = text.lower()
    target_job = target_job or ""
    job_description = job_description or ""

    # 1. Keyword search (categorized & flat)
    categorized_found = {}
    flat_found = []
    for category, kws in CATEGORIZED_KEYWORDS.items():
        found_in_category = []
        for kw in kws:
            kw_low = kw.lower()
            if len(kw) <= 3:
                # Word boundary match for short keywords (like Go, AWS, SQL)
                pattern = r"\b" + re.escape(kw_low) + r"\b"
                if re.search(pattern, normalized):
                    found_in_category.append(kw)
                    flat_found.append(kw)
            else:
                if kw_low in normalized:
                    found_in_category.append(kw)
                    flat_found.append(kw)
        if found_in_category:
            categorized_found[category] = found_in_category

    keywords_found = sorted(list(set(flat_found)))

    # 2. Section detection
    sections_found = _detect_sections(normalized)
    missing_sections = [section for section in REQUIRED_SECTIONS if section not in sections_found]

    # 3. Action verbs
    action_verb_count = _count_action_verbs(normalized)

    # 4. Bullet check & structure
    bullet_analysis = _analyze_bullets(text)
    bullet_count = bullet_analysis["count"]

    # 5. Experience duration
    experience_years = _estimate_experience_years(normalized)

    # 6. Contact info extraction
    contact_info = _extract_contact_info(text)

    # 7. Metrics extraction
    metrics_count = _count_metrics(text)

    # 8. Alignment with Job Description & Job Title
    alignment = _calculate_alignment(text, target_job, job_description)
    target_matches = len(alignment["matched"])

    # 9. ATS checks
    ats_compatibility = _check_ats_compatibility(text, len(normalized.split()), contact_info, missing_sections)

    # 10. Generate bullet point rewrites
    bullet_rewrites = _generate_rewrites(bullet_analysis["weak_bullets"])

    # Compute overall score and breakdown weights
    score, breakdown = _compute_score(
        len(keywords_found),
        len(missing_sections),
        action_verb_count,
        bullet_count,
        bullet_analysis["starting_with_verb"],
        experience_years,
        metrics_count,
        contact_info,
        alignment["score"],
        ats_compatibility["score"],
        len(normalized)
    )

    strengths = _build_strengths(
        keywords_found, 
        sections_found, 
        action_verb_count, 
        contact_info, 
        metrics_count, 
        alignment["score"], 
        ats_compatibility["score"]
    )

    feedback = _build_feedback(
        missing_sections, 
        keywords_found, 
        action_verb_count, 
        bullet_analysis, 
        metrics_count, 
        contact_info, 
        alignment, 
        target_job, 
        ats_compatibility
    )

    return {
        "score": round(score, 2),
        "score_breakdown": breakdown,
        "keywords_found": keywords_found,
        "categorized_keywords": categorized_found,
        "sections_found": sorted(sections_found),
        "missing_sections": missing_sections,
        "strengths": strengths,
        "feedback": feedback,
        "contact_info": contact_info,
        "metrics_count": metrics_count,
        "bullet_count": bullet_count,
        "bullet_stats": {
            "total": bullet_count,
            "starting_with_verb": bullet_analysis["starting_with_verb"],
            "containing_metrics": bullet_analysis["containing_metrics"],
            "average_length": bullet_analysis["average_length"]
        },
        "experience_years": experience_years,
        "job_target": target_job,
        "job_description": job_description,
        "target_matches": target_matches,
        "alignment_details": alignment,
        "ats_compatibility": ats_compatibility,
        "bullet_rewrites": bullet_rewrites,
        "word_count": len(normalized.split()),
        "preview_text": text[:1200].strip()
    }


def _detect_sections(text):
    found = set()
    for section, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            # Match using word boundaries or simple matching for section headers
            pattern_regex = r"\b" + re.escape(pattern) + r"\b"
            if re.search(pattern_regex, text):
                found.add(section)
                break
    return found


def _count_action_verbs(text):
    return sum(len(re.findall(r"\b" + re.escape(verb) + r"\b", text)) for verb in ACTION_VERBS)


def _analyze_bullets(text):
    lines = text.split("\n")
    bullet_lines = []
    
    # Bullet point prefix parser
    bullet_pattern = r"^\s*[-*•·▪◦]\s+(.+)$"
    number_pattern = r"^\s*\d+\.\s+(.+)$"
    
    for line in lines:
        m = re.match(bullet_pattern, line) or re.match(number_pattern, line)
        if m:
            bullet_text = m.group(1).strip()
            if len(bullet_text.split()) > 2:  # Avoid matching short artifacts
                bullet_lines.append(bullet_text)
                
    total_bullets = len(bullet_lines)
    if total_bullets == 0:
        return {
            "count": 0,
            "starting_with_verb": 0,
            "containing_metrics": 0,
            "average_length": 0,
            "weak_bullets": []
        }
        
    starting_with_verb = 0
    containing_metrics = 0
    total_words = 0
    weak_bullets = []
    
    verbs_lower = {v.lower() for v in ACTION_VERBS}
    
    for b in bullet_lines:
        words = b.split()
        total_words += len(words)
        
        # Check starting action verb
        first_word = re.sub(r"[^\w]", "", words[0]).lower() if words else ""
        starts_with_verb = first_word in verbs_lower
        if starts_with_verb:
            starting_with_verb += 1
            
        # Check metrics inside the bullet line
        has_metric = False
        for pattern in METRIC_PATTERNS:
            if re.search(pattern, b, re.IGNORECASE):
                has_metric = True
                containing_metrics += 1
                break
                
        # Classify as weak if it lacks action verbs, metrics, or has poor word counts
        is_weak = not starts_with_verb or not has_metric or len(words) < 8 or len(words) > 25
        if is_weak:
            weak_bullets.append(b)
            
    avg_length = round(total_words / total_bullets, 1)
    
    return {
        "count": total_bullets,
        "starting_with_verb": starting_with_verb,
        "containing_metrics": containing_metrics,
        "average_length": avg_length,
        "weak_bullets": weak_bullets
    }


def _estimate_experience_years(text):
    # Regex to capture year ranges like 2018-2022 or 2019 to Present
    pattern = r"\b(19\d{2}|20\d{2})\b\s*(?:-|–|to)\s*\b(19\d{2}|20\d{2}|present|current)\b"
    ranges = re.findall(pattern, text.lower())
    
    current_year = datetime.datetime.now().year
    total_years = 0
    
    if ranges:
        for start, end in ranges:
            start_yr = int(start)
            end_yr = current_year if end in ["present", "current"] else int(end)
            diff = end_yr - start_yr
            total_years += diff if diff > 0 else 1
        return min(total_years, 40)
        
    # Fallback to absolute difference between years found in resume text
    years = [int(match) for match in re.findall(r"\b(19\d{2}|20\d{2})\b", text)]
    if len(years) < 2:
        return len(years)
    diff = max(years) - min(years)
    return min(max(diff, 0), 40)


def _extract_contact_info(text):
    info = {}
    for name, pattern in CONTACT_PATTERNS.items():
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            info[name] = list(dict.fromkeys(matches))
    return info


def _count_metrics(text):
    total = 0
    for pattern in METRIC_PATTERNS:
        total += len(re.findall(pattern, text, flags=re.IGNORECASE))
    return total


def _tokenize(text):
    return [token for token in re.findall(r"\b[a-zA-Z0-9+\-#@]+\b", text.lower()) if token]


def _count_target_alignment(target_terms, text):
    if not target_terms:
        return 0
    return sum(1 for term in target_terms if term in text)


def _calculate_alignment(resume_text, target_job, job_description):
    normalized_resume = resume_text.lower()
    
    # 1. Job Title parsing
    job_title_terms = _tokenize(target_job)
    title_matches = _count_target_alignment(job_title_terms, normalized_resume)
    
    # Check if there is a job description. If not, use job title matching
    if not job_description:
        if not target_job:
            return {"score": 100.0, "matched": [], "missing": []}  # General resume (no target)
            
        target_factor = min(title_matches / max(len(job_title_terms), 1), 1.0)
        return {
            "score": round(target_factor * 100, 1),
            "matched": [term for term in job_title_terms if term in normalized_resume],
            "missing": [term for term in job_title_terms if term not in normalized_resume]
        }
        
    # 2. Deeper Job Description Keyword Overlap
    jd_tokens = set(_tokenize(job_description))
    stop_words = {
        "the", "and", "with", "this", "that", "from", "have", "will", "your", "must", 
        "requirements", "candidate", "role", "work", "team", "experience", "ability",
        "skills", "job", "description", "responsibilities", "required", "preferred",
        "about", "their", "them", "they", "been", "were", "should", "could", "would",
        "other", "using", "highly", "plus", "years", "knowledge", "strong", "excellent",
        "written", "verbal", "communication", "environment", "working", "join", "help"
    }
    
    jd_skills = {token for token in jd_tokens if len(token) > 2 and token not in stop_words}
    
    # Map back to known technical terms to ensure focus on skills
    all_known_keywords = set()
    for cat, kws in CATEGORIZED_KEYWORDS.items():
        for kw in kws:
            all_known_keywords.add(kw.lower())
            
    jd_known_skills = jd_skills.intersection(all_known_keywords)
    if len(jd_known_skills) < 3:
        jd_known_skills = jd_skills  # Fallback if few technical skills matched
        
    if not jd_known_skills:
        return {"score": 0.0, "matched": [], "missing": []}
        
    matched_skills = []
    missing_skills = []
    
    for skill in jd_known_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, normalized_resume):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
            
    score = (len(matched_skills) / len(jd_known_skills)) * 100
    matched_skills.sort()
    missing_skills.sort()
    
    return {
        "score": round(score, 1),
        "matched": matched_skills,
        "missing": missing_skills
    }


def _check_ats_compatibility(text, word_count, contact_info, missing_sections):
    pitfalls = []
    ats_score = 100
    
    if word_count < 200:
        pitfalls.append("Resume word count is under 200 words. Expand details of your professional history.")
        ats_score -= 15
    elif word_count > 1500:
        pitfalls.append("Resume exceeds 1500 words. Keep it concise to ensure high parser readability.")
        ats_score -= 15
        
    if not contact_info.get("email") or not contact_info.get("phone"):
        pitfalls.append("Essential contact channels (email or phone) are missing or not detected.")
        ats_score -= 20
        
    if "experience" in missing_sections or "skills" in missing_sections:
        pitfalls.append("Missing core sections (Experience or Skills).")
        ats_score -= 20
        
    # Check for excessive visual delimiters confusing parsing parsers
    delimiters_count = len(re.findall(r"[|•♦★■➔➧✓✕]", text))
    if delimiters_count > 25:
        pitfalls.append("Excessive use of graphic bullet points or pipe separators '|' detected.")
        ats_score -= 10
        
    # Multi-column checker (consecutive horizontal whitespace spans)
    column_indicators = len(re.findall(r" {4,}", text))
    if column_indicators > 15:
        pitfalls.append("Potential multi-column layout detected. Use a single-column layout for safety.")
        ats_score -= 10
        
    return {
        "score": max(30, min(ats_score, 100)),
        "pitfalls": pitfalls,
        "is_compatible": ats_score >= 70
    }


def _generate_rewrites(weak_bullets):
    suggestions = []
    used_templates = set()
    
    for bullet in weak_bullets[:3]:
        matched = False
        for i, temp in enumerate(REWRITE_TEMPLATES):
            if i not in used_templates and re.search(temp["pattern"], bullet, re.IGNORECASE):
                suggestions.append({
                    "before": bullet,
                    "after": temp["after"]
                })
                used_templates.add(i)
                matched = True
                break
        
        if not matched:
            suggestions.append({
                "before": bullet,
                "after": "Redesign: Begin with a strong impact verb (e.g. 'Optimized', 'Spearheaded') and add a quantifiable metric indicating scale or percentage growth."
            })
            
    # Add defaults if list is short
    if len(suggestions) < 3:
        for i, temp in enumerate(REWRITE_TEMPLATES):
            if len(suggestions) >= 3:
                break
            if i not in used_templates:
                suggestions.append({
                    "before": temp["before_default"],
                    "after": temp["after"]
                })
                used_templates.add(i)
                
    return suggestions


def _compute_score(keyword_count, missing_sections, action_verb_count, bullet_count, verb_bullets_count, experience_years, metrics_count, contact_info, alignment_score, ats_score, length):
    if length < 50:
        return 0.0, {}

    # Standardize weights
    # Keywords: 20%
    keyword_factor = min(keyword_count / 15.0, 1.0)
    # Sections: 20%
    section_factor = 1.0 - (missing_sections / len(REQUIRED_SECTIONS))
    # Action Verbs: 15%
    verb_factor = min(action_verb_count / 12.0, 1.0)
    # Formatting & Bullets: 15%
    bullet_ratio = (verb_bullets_count / max(bullet_count, 1)) if bullet_count > 0 else 0.0
    bullet_len_factor = min(bullet_count / 8.0, 1.0)
    formatting_factor = (bullet_ratio * 0.6) + (bullet_len_factor * 0.4)
    # Metrics: 15%
    metrics_factor = min(metrics_count / 6.0, 1.0)
    # Contact Info: 5%
    contact_factor = 1.0 if contact_info.get("email") and contact_info.get("phone") else 0.5 if contact_info else 0.0
    # Target Job/Job Description Alignment: 10%
    alignment_factor = alignment_score / 100.0

    breakdown = {
        "keywords": round(keyword_factor * 20, 1),
        "sections": round(section_factor * 20, 1),
        "action_verbs": round(verb_factor * 15, 1),
        "formatting": round(formatting_factor * 15, 1),
        "metrics": round(metrics_factor * 15, 1),
        "contact": round(contact_factor * 5, 1),
        "target_alignment": round(alignment_factor * 10, 1),
    }
    
    score = sum(breakdown.values())
    
    # Adjust score slightly using ATS score
    final_score = (score * 0.9) + (ats_score * 0.1)
    
    return max(0.0, min(final_score, 100.0)), breakdown


def _build_strengths(keywords_found, sections_found, action_verb_count, contact_info, metrics_count, alignment_score, ats_score):
    strengths = []
    if len(keywords_found) >= 8:
        strengths.append("Robust selection of industry-relevant technical keywords and skills.")
    if "skills" in sections_found and "experience" in sections_found:
        strengths.append("Key resume modules (Skills & Experience) are clearly identifiable.")
    if action_verb_count >= 8:
        strengths.append("Strong usage of action verbs conveying direct leadership and ownership.")
    if metrics_count >= 3:
        strengths.append("Measurable business outcomes and quantifiable data points included.")
    if contact_info.get("email") and contact_info.get("phone"):
        strengths.append("Primary contact information (email, phone) is present.")
    if alignment_score >= 60:
        strengths.append("Resume terminology matches the target job definition closely.")
    if ats_score >= 80:
        strengths.append("Highly compliant layout for Applicant Tracking System (ATS) parsers.")
        
    if not strengths:
        strengths.append("Initial setup detected. Refine sections to increase strength rating.")
    return strengths


def _build_feedback(missing_sections, keywords_found, action_verb_count, bullet_analysis, metrics_count, contact_info, alignment, target_job, ats_compatibility):
    feedback = []
    
    # High Priority Critiques
    if missing_sections:
        readable = ", ".join([s.title() for s in missing_sections])
        feedback.append(f"[High] Missing essential sections: {readable}. Create distinct headers for these sections.")
    if not contact_info.get("email"):
        feedback.append("[High] Include your email address so recruiters can reach you easily.")
    if not contact_info.get("phone"):
        feedback.append("[High] Provide a phone number to facilitate direct interview call scheduling.")
    if len(keywords_found) < 5:
        feedback.append("[High] Add more specific skills and technical tools related to your industry.")
        
    # Medium Priority Critiques
    if action_verb_count < 6:
        feedback.append("[Medium] Incorporate more dynamic action verbs (e.g. 'Optimized', 'Spearheaded') to start bullet points.")
    if bullet_analysis["count"] > 0 and (bullet_analysis["starting_with_verb"] / bullet_analysis["count"]) < 0.6:
        feedback.append("[Medium] Ensure at least 60% of your experience description bullet points begin with action verbs.")
    if metrics_count < 3:
        feedback.append("[Medium] Add quantifiable metrics (e.g., %, $, numbers scaled) to describe outcomes rather than duties.")
    if target_job and alignment["score"] < 40:
        feedback.append(f"[Medium] Increase alignment with job target '{target_job}' by copying relevant skill requirements.")
    for pitfall in ats_compatibility["pitfalls"][:2]:
        feedback.append(f"[Medium] ATS Pitfall: {pitfall}")
        
    # Low Priority/Optimization Critiques
    if bullet_analysis["count"] < 5:
        feedback.append("[Low] Expand details of projects and work experience using a bullet point list (target 6-12 points).")
    if bullet_analysis["count"] > 0 and bullet_analysis["average_length"] > 25:
        feedback.append("[Low] Some bullet points are wordy (avg > 25 words). Keep bullets under 2 lines of text for scan-readability.")
    elif bullet_analysis["count"] > 0 and bullet_analysis["average_length"] < 8:
        feedback.append("[Low] Your bullet points are brief (avg < 8 words). Elaborate on the actions and results of your contributions.")
    if not contact_info.get("linkedin"):
        feedback.append("[Low] Include a hyperlink to your LinkedIn professional profile.")
        
    if not feedback:
        feedback.append("[Low] Stellar resume structure! Conduct a final copy-editing review to check for grammar.")
        
    return feedback
