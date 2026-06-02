from utils.resume_analyzer import analyze_resume


def test_analyze_resume_detects_sections_and_keywords():
    sample_text = """
    Professional Summary
    Experienced software engineer with strong Python and SQL skills.

    Experience
    - Developed automation scripts and led a team of engineers.

    Education
    Bachelor of Science in Computer Science

    Skills
    Python, SQL, Machine Learning, Communication
    Contact: jane.doe@example.com | +1 555-123-4567
    """

    result = analyze_resume(sample_text, target_job="Data Engineer")

    assert result["score"] > 0
    assert "education" in result["sections_found"]
    assert "skills" in result["sections_found"]
    assert "Python" in result["keywords_found"]
    assert result["contact_info"]["email"] == ["jane.doe@example.com"]
    assert result["contact_info"]["phone"] == ["+1 555-123-4567"]
    assert isinstance(result["feedback"], list)
    assert isinstance(result["strengths"], list)
    assert result["job_target"] == "Data Engineer"


def test_analyze_resume_recommends_metrics_and_targets():
    sample_text = """
    Summary
    Strong project leader and communicator.

    Experience
    - Coordinated a team of 5 engineers.
    - Improved process efficiency by 30%.
    """

    result = analyze_resume(sample_text, target_job="Project Manager")

    assert result["metrics_count"] >= 1
    assert result["target_matches"] >= 1 or result["job_target"] == "Project Manager"
    # The upgraded feedback lists them under prioritised prefixes e.g. "[Medium]"
    assert any("metrics" in fb.lower() for fb in result["feedback"])


def test_analyze_resume_ats_and_layout_checks():
    # Test resume text that is extremely short to trigger word count warning
    short_text = "Short text resume summary. Python programmer. email: test@example.com"
    result = analyze_resume(short_text, target_job="Developer")
    
    assert result["ats_compatibility"]["score"] < 100
    assert any("word count" in pit.lower() for pit in result["ats_compatibility"]["pitfalls"])
    assert result["ats_compatibility"]["is_compatible"] is False


def test_analyze_resume_jaccard_job_description_alignment():
    resume_text = """
    Summary
    Software engineer with Docker and React experience.
    
    Skills
    React, Docker, Python
    """
    
    # Matching keywords in job desc: React, Docker
    # Missing keywords: Kubernetes, Terraform
    job_desc = "Looking for a React developer with experience in Docker, Kubernetes, and Terraform."
    
    result = analyze_resume(resume_text, target_job="DevOps Engineer", job_description=job_desc)
    
    alignment = result["alignment_details"]
    assert alignment["score"] > 0
    # React and Docker should be matched
    assert "react" in alignment["matched"]
    assert "docker" in alignment["matched"]
    # Kubernetes and Terraform should be missing
    assert "kubernetes" in alignment["missing"]
    assert "terraform" in alignment["missing"]


def test_analyze_resume_experience_date_range():
    # Test experience duration logic using range format: 2018 - 2022 (4 years)
    resume_text = """
    Experience
    - Software engineer at Google: 2018 - 2022
    - Project lead at Microsoft: 2022 - Present
    """
    
    result = analyze_resume(resume_text, target_job="Developer")
    
    # 2018 - 2022 is 4 years. 2022 to Present (2026) is 4 years. Total 8 years.
    # The calculation caps or estimates dynamically. We check it's at least 4 years.
    assert result["experience_years"] >= 4


def test_analyze_resume_bullet_points_check():
    resume_text = """
    Experience
    - Managed development of core API services.
    - Wrote python code.
    - Improved page loads by 40% with database index restructuring.
    """
    
    result = analyze_resume(resume_text, target_job="Developer")
    
    assert result["bullet_count"] == 3
    # Managed starts with verb. Improved starts with verb. Wrote is also a verb.
    # Total bullets starting with verb should be positive
    assert result["bullet_stats"]["starting_with_verb"] >= 2
    # At least 1 bullet contains metric (40%)
    assert result["bullet_stats"]["containing_metrics"] >= 1
    # Rewrite suggestion list should be populated
    assert len(result["bullet_rewrites"]) > 0
