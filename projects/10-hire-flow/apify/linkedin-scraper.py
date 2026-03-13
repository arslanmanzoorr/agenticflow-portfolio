"""
HireFlow - LinkedIn Candidate Scraper (Apify Actor)

Simulated Apify actor that scrapes candidate profiles from LinkedIn
based on job title, skills, and location filters. Returns structured
candidate data for downstream processing in the n8n hiring pipeline.

Note: This is a simulation actor for demonstration purposes.
Real LinkedIn scraping requires compliance with LinkedIn's ToS
and appropriate API access or authorized scraping partnerships.
"""

import json
import hashlib
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from apify import Actor


SIMULATED_CANDIDATES = [
    {
        "name": "Sarah Chen",
        "headline": "Senior Software Engineer | Python & Cloud Architecture",
        "current_company": "TechCorp Inc.",
        "current_title": "Senior Software Engineer",
        "location": "San Francisco, CA",
        "experience_years": 7,
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "duration": "2021 - Present",
                "description": "Leading backend architecture for microservices platform. Designed event-driven systems handling 50K+ requests/sec.",
            },
            {
                "title": "Software Engineer",
                "company": "StartupXYZ",
                "duration": "2018 - 2021",
                "description": "Full-stack development with Python/Django and React. Built CI/CD pipelines and automated testing infrastructure.",
            },
            {
                "title": "Junior Developer",
                "company": "WebAgency Co.",
                "duration": "2016 - 2018",
                "description": "Developed client-facing web applications using Python and JavaScript frameworks.",
            },
        ],
        "skills": ["Python", "AWS", "Kubernetes", "PostgreSQL", "Redis", "Docker", "Terraform", "CI/CD", "Microservices", "System Design"],
        "education": [
            {
                "degree": "M.S. Computer Science",
                "school": "Stanford University",
                "year": 2016,
            },
            {
                "degree": "B.S. Computer Science",
                "school": "UC Berkeley",
                "year": 2014,
            },
        ],
        "profile_url": "https://linkedin.com/in/sarah-chen-demo",
        "connections": 1200,
    },
    {
        "name": "Marcus Johnson",
        "headline": "Full Stack Developer | React & Node.js Expert",
        "current_company": "Digital Solutions LLC",
        "current_title": "Full Stack Developer",
        "location": "Austin, TX",
        "experience_years": 5,
        "experience": [
            {
                "title": "Full Stack Developer",
                "company": "Digital Solutions LLC",
                "duration": "2022 - Present",
                "description": "Building SaaS platform with React, Node.js, and MongoDB. Implemented real-time collaboration features.",
            },
            {
                "title": "Frontend Developer",
                "company": "CreativeApps",
                "duration": "2020 - 2022",
                "description": "Developed responsive web applications with React and TypeScript. Improved page load times by 40%.",
            },
        ],
        "skills": ["React", "Node.js", "TypeScript", "MongoDB", "GraphQL", "AWS", "Docker", "Jest", "Webpack", "Tailwind CSS"],
        "education": [
            {
                "degree": "B.S. Software Engineering",
                "school": "University of Texas at Austin",
                "year": 2019,
            },
        ],
        "profile_url": "https://linkedin.com/in/marcus-johnson-demo",
        "connections": 850,
    },
    {
        "name": "Priya Patel",
        "headline": "Data Engineer | Big Data & ML Pipelines",
        "current_company": "DataFlow Analytics",
        "current_title": "Senior Data Engineer",
        "location": "New York, NY",
        "experience_years": 6,
        "experience": [
            {
                "title": "Senior Data Engineer",
                "company": "DataFlow Analytics",
                "duration": "2021 - Present",
                "description": "Architecting data pipelines processing 10TB+ daily. Leading migration from on-prem Hadoop to cloud-native stack.",
            },
            {
                "title": "Data Engineer",
                "company": "FinTech Corp",
                "duration": "2019 - 2021",
                "description": "Built ETL pipelines with Apache Spark and Airflow. Designed data warehouse schema for financial reporting.",
            },
            {
                "title": "Software Developer",
                "company": "ConsultingFirm",
                "duration": "2017 - 2019",
                "description": "Developed data integration solutions for enterprise clients using Python and SQL.",
            },
        ],
        "skills": ["Python", "Apache Spark", "Airflow", "Snowflake", "Kafka", "AWS", "SQL", "dbt", "Terraform", "Machine Learning"],
        "education": [
            {
                "degree": "M.S. Data Science",
                "school": "Columbia University",
                "year": 2017,
            },
            {
                "degree": "B.Tech Information Technology",
                "school": "IIT Bombay",
                "year": 2015,
            },
        ],
        "profile_url": "https://linkedin.com/in/priya-patel-demo",
        "connections": 2100,
    },
    {
        "name": "Alex Rivera",
        "headline": "DevOps Engineer | Infrastructure Automation",
        "current_company": "CloudNine Systems",
        "current_title": "DevOps Engineer",
        "location": "Seattle, WA",
        "experience_years": 4,
        "experience": [
            {
                "title": "DevOps Engineer",
                "company": "CloudNine Systems",
                "duration": "2022 - Present",
                "description": "Managing Kubernetes clusters across multi-cloud environments. Implemented GitOps workflows with ArgoCD.",
            },
            {
                "title": "Systems Administrator",
                "company": "MidSize Tech",
                "duration": "2020 - 2022",
                "description": "Automated infrastructure provisioning with Terraform and Ansible. Reduced deployment time by 70%.",
            },
        ],
        "skills": ["Kubernetes", "Docker", "Terraform", "AWS", "GCP", "ArgoCD", "Prometheus", "Grafana", "Python", "Bash", "Linux"],
        "education": [
            {
                "degree": "B.S. Computer Engineering",
                "school": "University of Washington",
                "year": 2020,
            },
        ],
        "profile_url": "https://linkedin.com/in/alex-rivera-demo",
        "connections": 650,
    },
    {
        "name": "Emily Nakamura",
        "headline": "Product Manager | B2B SaaS & Growth",
        "current_company": "GrowthTech",
        "current_title": "Senior Product Manager",
        "location": "San Francisco, CA",
        "experience_years": 8,
        "experience": [
            {
                "title": "Senior Product Manager",
                "company": "GrowthTech",
                "duration": "2020 - Present",
                "description": "Leading product strategy for enterprise SaaS platform. Drove 150% ARR growth through data-driven feature prioritization.",
            },
            {
                "title": "Product Manager",
                "company": "SaaSStartup",
                "duration": "2018 - 2020",
                "description": "Managed end-to-end product lifecycle for B2B collaboration tools. Launched 3 major features adopted by 80% of users.",
            },
            {
                "title": "Business Analyst",
                "company": "ConsultCo",
                "duration": "2015 - 2018",
                "description": "Conducted market research and competitive analysis for technology clients. Developed product roadmaps and go-to-market strategies.",
            },
        ],
        "skills": ["Product Strategy", "Agile", "Data Analysis", "SQL", "Figma", "Jira", "A/B Testing", "User Research", "Roadmapping", "Stakeholder Management"],
        "education": [
            {
                "degree": "MBA",
                "school": "Wharton School of Business",
                "year": 2015,
            },
            {
                "degree": "B.A. Economics",
                "school": "UCLA",
                "year": 2013,
            },
        ],
        "profile_url": "https://linkedin.com/in/emily-nakamura-demo",
        "connections": 3500,
    },
]


def generate_candidate_id(name: str, profile_url: str) -> str:
    """Generate a deterministic unique ID for a candidate."""
    raw = f"{name}:{profile_url}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def matches_job_title(candidate: dict, job_titles: list[str]) -> bool:
    """Check if candidate's experience matches any target job title."""
    if not job_titles:
        return True

    searchable = (
        candidate["headline"].lower()
        + " "
        + candidate["current_title"].lower()
        + " "
        + " ".join(
            exp["title"].lower() for exp in candidate.get("experience", [])
        )
    )

    return any(title.lower() in searchable for title in job_titles)


def matches_location(candidate: dict, locations: list[str]) -> bool:
    """Check if candidate's location matches any target location."""
    if not locations:
        return True

    candidate_loc = candidate["location"].lower()
    return any(loc.lower() in candidate_loc for loc in locations)


def matches_skills(candidate: dict, required_skills: list[str], min_match: int = 1) -> bool:
    """Check if candidate has at least min_match of the required skills."""
    if not required_skills:
        return True

    candidate_skills = {s.lower() for s in candidate.get("skills", [])}
    required_lower = {s.lower() for s in required_skills}
    overlap = candidate_skills & required_lower
    return len(overlap) >= min_match


def matches_experience(candidate: dict, min_years: int, max_years: int) -> bool:
    """Check if candidate's experience falls within the desired range."""
    years = candidate.get("experience_years", 0)
    if min_years and years < min_years:
        return False
    if max_years and years > max_years:
        return False
    return True


def calculate_skill_match_score(candidate: dict, required_skills: list[str]) -> float:
    """Calculate how well a candidate's skills match requirements (0.0-1.0)."""
    if not required_skills:
        return 1.0

    candidate_skills = {s.lower() for s in candidate.get("skills", [])}
    required_lower = {s.lower() for s in required_skills}
    if not required_lower:
        return 1.0

    overlap = candidate_skills & required_lower
    return len(overlap) / len(required_lower)


def enrich_candidate(candidate: dict, required_skills: list[str]) -> dict:
    """Add metadata fields to a candidate record."""
    candidate_id = generate_candidate_id(
        candidate["name"], candidate["profile_url"]
    )

    skill_score = calculate_skill_match_score(candidate, required_skills)
    matched_skills = []
    missing_skills = []

    if required_skills:
        candidate_skills_lower = {s.lower() for s in candidate.get("skills", [])}
        for skill in required_skills:
            if skill.lower() in candidate_skills_lower:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

    return {
        "candidate_id": candidate_id,
        **candidate,
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "source": "linkedin",
        "skill_match_score": round(skill_score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "status": "sourced",
    }


async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}

        # Extract search parameters from input
        job_titles = actor_input.get("jobTitles", [])
        locations = actor_input.get("locations", [])
        required_skills = actor_input.get("requiredSkills", [])
        min_experience = actor_input.get("minExperience", 0)
        max_experience = actor_input.get("maxExperience", 99)
        min_skill_match = actor_input.get("minSkillMatch", 1)
        max_results = actor_input.get("maxResults", 50)

        Actor.log.info(f"Starting LinkedIn candidate scraper")
        Actor.log.info(f"  Job titles: {job_titles}")
        Actor.log.info(f"  Locations: {locations}")
        Actor.log.info(f"  Required skills: {required_skills}")
        Actor.log.info(f"  Experience range: {min_experience}-{max_experience} years")

        # In production, this would use Playwright/Puppeteer to navigate
        # LinkedIn search results. For demonstration, we filter simulated data.
        candidates = SIMULATED_CANDIDATES

        results = []
        for candidate in candidates:
            if not matches_job_title(candidate, job_titles):
                Actor.log.debug(f"Skipping {candidate['name']} - job title mismatch")
                continue
            if not matches_location(candidate, locations):
                Actor.log.debug(f"Skipping {candidate['name']} - location mismatch")
                continue
            if not matches_skills(candidate, required_skills, min_skill_match):
                Actor.log.debug(f"Skipping {candidate['name']} - skills mismatch")
                continue
            if not matches_experience(candidate, min_experience, max_experience):
                Actor.log.debug(f"Skipping {candidate['name']} - experience mismatch")
                continue

            enriched = enrich_candidate(candidate, required_skills)
            results.append(enriched)

            if len(results) >= max_results:
                break

        # Sort by skill match score descending
        results.sort(key=lambda c: c["skill_match_score"], reverse=True)

        Actor.log.info(f"Found {len(results)} matching candidates")

        # Push results to Apify dataset
        await Actor.push_data(results)

        # Store summary in key-value store
        await Actor.set_value("summary", {
            "total_candidates_found": len(results),
            "search_criteria": {
                "job_titles": job_titles,
                "locations": locations,
                "required_skills": required_skills,
                "experience_range": f"{min_experience}-{max_experience}",
            },
            "top_candidates": [
                {
                    "name": c["name"],
                    "score": c["skill_match_score"],
                    "headline": c["headline"],
                }
                for c in results[:5]
            ],
            "completed_at": datetime.utcnow().isoformat() + "Z",
        })

        Actor.log.info("Scraper run complete")
