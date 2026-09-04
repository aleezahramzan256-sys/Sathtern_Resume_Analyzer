import streamlit as st
from pypdf import PdfReader
import re


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Sathtern Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📄 Sathtern Resume Analyzer")
st.write(
    "Upload your resume and get an intelligent ATS-style resume analysis."
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def contains_term(text, term):
    """
    Safely check whether a term exists in text.
    Handles multi-word terms and symbols such as C++, C#, .NET.
    """
    escaped = re.escape(term.lower())

    if re.search(r"(?<!\w)" + escaped + r"(?!\w)", text.lower()):
        return True

    return False


def detect_terms(text, terms):
    """Return terms detected in text."""
    detected = []

    for term in terms:
        if contains_term(text, term):
            detected.append(term)

    return detected


def count_words(text):
    """Count readable words."""
    return len(re.findall(r"\b[\w+#.-]+\b", text))


def clean_pdf_text(text):
    """
    Clean common PDF extraction problems while preserving
    readable line structure.
    """

    text = text.replace("\r", "\n")

    # Fix excessive spaces while keeping line breaks
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def extract_section(text, headings):
    """
    Attempt to extract text belonging to a resume section.
    """

    heading_pattern = "|".join(
        re.escape(h) for h in headings
    )

    pattern = (
        r"(?:"
        + heading_pattern
        + r")"
        r"(.*?)(?="
        r"\n(?:"
        + "|".join([
            "professional summary",
            "summary",
            "profile",
            "objective",
            "education",
            "academic background",
            "skills",
            "technical skills",
            "experience",
            "work experience",
            "professional experience",
            "internship",
            "projects",
            "academic projects",
            "personal projects",
            "certifications",
            "certificates",
            "achievements",
            "awards",
            r"$"
        ])
        + r")",
        re.IGNORECASE | re.DOTALL
    )

    match = re.search(pattern, text)

    if match:
        return match.group(1).strip()

    return ""


# ============================================================
# PDF UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF)",
    type=["pdf"]
)


# ============================================================
# ANALYSIS
# ============================================================

if uploaded_file:

    st.success("Resume uploaded successfully! ✅")

    analyze_button = st.button(
        "🔍 Analyze Resume",
        type="primary"
    )

    if analyze_button:

        st.info("Resume analysis started...")

        # ====================================================
        # READ PDF
        # ====================================================

        uploaded_file.seek(0)

        try:
            reader = PdfReader(uploaded_file)

            resume_text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    resume_text += page_text + "\n"

        except Exception as error:
            st.error(
                f"Unable to read PDF: {error}"
            )
            st.stop()


        # ====================================================
        # CHECK TEXT
        # ====================================================

        if not resume_text.strip():

            st.error(
                "No readable text could be extracted from this PDF. "
                "The PDF may be scanned/image-based."
            )

            st.info(
                "Try uploading a PDF created from Word, Google Docs, "
                "Canva, or another text-based resume editor."
            )

            st.stop()


        # ====================================================
        # CLEAN TEXT
        # ====================================================

        resume_text = clean_pdf_text(resume_text)

        text_lower = resume_text.lower()

        clean_text = re.sub(
            r"\s+",
            " ",
            text_lower
        ).strip()

        word_count = count_words(resume_text)


        # ====================================================
        # EXTRACTED TEXT
        # ====================================================

        st.subheader("📄 Extracted Resume Text")

        st.text_area(
            "Resume Content",
            resume_text,
            height=350
        )


        # ====================================================
        # SECTION DETECTION
        # ====================================================

        summary_found = bool(
            re.search(
                r"\b("
                r"professional summary|"
                r"summary|"
                r"profile|"
                r"career objective|"
                r"objective"
                r")\b",
                text_lower
            )
        )

        education_found = bool(
            re.search(
                r"\b("
                r"education|"
                r"academic background|"
                r"academic qualification|"
                r"educational background"
                r")\b",
                text_lower
            )
        )

        skills_found = bool(
            re.search(
                r"\b("
                r"skills|"
                r"technical skills|"
                r"core skills|"
                r"technical expertise|"
                r"skills & technologies|"
                r"technologies"
                r")\b",
                text_lower
            )
        )

        experience_found = bool(
            re.search(
                r"\b("
                r"experience|"
                r"work experience|"
                r"professional experience|"
                r"internship|"
                r"employment|"
                r"work history"
                r")\b",
                text_lower
            )
        )

        projects_found = bool(
            re.search(
                r"\b("
                r"projects|"
                r"academic projects|"
                r"personal projects|"
                r"featured projects|"
                r"project experience"
                r")\b",
                text_lower
            )
        )

        certifications_found = bool(
            re.search(
                r"\b("
                r"certifications|"
                r"certificates|"
                r"courses|"
                r"training|"
                r"professional development"
                r")\b",
                text_lower
            )
        )

        achievements_found = bool(
            re.search(
                r"\b("
                r"achievements|"
                r"awards|"
                r"honors|"
                r"accomplishments"
                r")\b",
                text_lower
            )
        )


        # ====================================================
        # CONTACT DETECTION
        # ====================================================

        email_found = bool(
            re.search(
                r"[A-Za-z0-9._%+-]+"
                r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                resume_text
            )
        )

        linkedin_found = bool(
            re.search(
                r"(linkedin\.com|linkedin)",
                text_lower
            )
        )

        github_found = bool(
            re.search(
                r"(github\.com|github)",
                text_lower
            )
        )

        phone_found = bool(
            re.search(
                r"(?:(?:\+92|0092|0)\s*)?"
                r"(?:3\d{2})"
                r"[\s.-]?\d{3}"
                r"[\s.-]?\d{4}",
                resume_text
            )
        )


        # ====================================================
        # STUDENT PROFILE
        # ====================================================

        student_keywords = [
            "student",
            "undergraduate",
            "bachelor",
            "b.s.",
            "bs ",
            "bsc",
            "university",
            "college",
            "semester",
            "academic"
        ]

        student_profile = any(
            keyword in text_lower
            for keyword in student_keywords
        )


        # ====================================================
        # TECHNICAL SKILLS
        # ====================================================

        skill_keywords = [
            "python",
            "java",
            "c++",
            "c#",
            "javascript",
            "typescript",
            "r programming",
            "sql",
            "php",

            "artificial intelligence",
            "machine learning",
            "deep learning",
            "natural language processing",
            "nlp",
            "computer vision",
            "generative ai",
            "large language models",
            "llm",
            "prompt engineering",

            "data science",
            "data analysis",
            "data visualization",
            "statistics",

            "excel",
            "power bi",
            "tableau",

            "pandas",
            "numpy",
            "scikit-learn",
            "matplotlib",
            "seaborn",

            "tensorflow",
            "pytorch",
            "keras",
            "hugging face",

            "html",
            "css",
            "bootstrap",
            "react",
            "node.js",
            "flask",
            "django",
            "streamlit",

            "git",
            "github",
            "docker",
            "jupyter",
            "google colab",
            "vs code",

            "mysql",
            "postgresql",
            "mongodb",
            "sqlite",

            "aws",
            "azure",
            "google cloud",

            "api",
            "rest api",
            "firebase"
        ]

        detected_skills = detect_terms(
            text_lower,
            skill_keywords
        )

        skill_count = len(detected_skills)


        # ====================================================
        # ACTION WORDS
        # ====================================================

        strong_action_words = [
            "developed",
            "created",
            "built",
            "designed",
            "implemented",
            "engineered",
            "automated",
            "analyzed",
            "optimized",
            "improved",
            "deployed",
            "integrated",
            "programmed",
            "tested",
            "trained",
            "evaluated",
            "managed",
            "led",
            "launched",
            "configured",
            "solved",
            "generated",
            "researched",
            "conducted",
            "organized",
            "achieved",
            "delivered",
            "implemented",
            "performed",
            "processed",
            "developing",
            "building",
            "designing",
            "analyzing",
            "creating",
            "deploying"
        ]

        weak_action_words = [
            "worked",
            "helped",
            "assisted",
            "responsible",
            "participated",
            "involved",
            "supported"
        ]

        detected_action_words = detect_terms(
            text_lower,
            strong_action_words
        )

        detected_weak_words = detect_terms(
            text_lower,
            weak_action_words
        )

        action_count = len(
            detected_action_words
        )


        # ====================================================
        # QUANTIFIED ACHIEVEMENTS
        # ====================================================

        quantified_patterns = [
            r"\b\d+(?:\.\d+)?%",
            r"\b\d+\+?\s*(?:users|students|customers|clients|projects|records|datasets|tasks|members|participants)",
            r"\b\d+(?:\.\d+)?\s*(?:years?|months?|weeks?|days?)",
            r"\b\d+(?:\.\d+)?\s*(?:hours?|minutes?)",
            r"\b\d+(?:\.\d+)?\b",
            r"\b\d+/\d+\b"
        ]

        quantified_matches = []

        for pattern in quantified_patterns:

            matches = re.findall(
                pattern,
                clean_text
            )

            quantified_matches.extend(
                matches
            )

        quantified_matches = list(
            dict.fromkeys(
                quantified_matches
            )
        )

        quantified_count = len(
            quantified_matches
        )


        # ====================================================
        # PROJECT TECHNOLOGIES
        # ====================================================

        project_technology_words = [
            "python",
            "machine learning",
            "artificial intelligence",
            "deep learning",
            "tensorflow",
            "pytorch",
            "pandas",
            "numpy",
            "scikit-learn",
            "streamlit",
            "flask",
            "django",
            "github",
            "git",
            "sql",
            "mongodb",
            "mysql",
            "api",
            "rest api",
            "nlp",
            "natural language processing",
            "computer vision",
            "html",
            "css",
            "javascript"
        ]

        project_tech_detected = detect_terms(
            text_lower,
            project_technology_words
        )

        project_tech_count = len(
            project_tech_detected
        )


        # ====================================================
        # ATS KEYWORDS
        # ====================================================

        ats_keywords = [
            "python",
            "machine learning",
            "artificial intelligence",
            "data analysis",
            "data science",
            "sql",
            "pandas",
            "numpy",
            "scikit-learn",
            "tensorflow",
            "pytorch",
            "git",
            "github",
            "api",
            "statistics",
            "deep learning",
            "nlp",
            "computer vision",
            "streamlit",
            "data visualization",
            "natural language processing",
            "generative ai",
            "prompt engineering",
            "flask",
            "django",
            "javascript",
            "html",
            "css",
            "docker"
        ]

        detected_ats_keywords = detect_terms(
            text_lower,
            ats_keywords
        )

        ats_count = len(
            detected_ats_keywords
        )


        # ====================================================
        # PROFESSIONAL SUMMARY SCORE — 10
        # ====================================================

        summary_score = 0

        if summary_found:

            summary_score += 4

            summary_match = re.search(
                r"(professional summary|"
                r"summary|"
                r"profile|"
                r"career objective|"
                r"objective)"
                r"(.*?)(?="
                r"\n(?:education|skills|experience|projects|"
                r"certifications|achievements)|$)",
                resume_text,
                re.IGNORECASE | re.DOTALL
            )

            if summary_match:

                summary_text = (
                    summary_match.group(2)
                )

                summary_word_count = count_words(
                    summary_text
                )

                if 35 <= summary_word_count <= 100:
                    summary_score += 3

                elif 20 <= summary_word_count < 35:
                    summary_score += 2

                elif 100 < summary_word_count <= 140:
                    summary_score += 2

                elif summary_word_count > 140:
                    summary_score += 1

            relevant_summary_words = [
                "artificial intelligence",
                "machine learning",
                "python",
                "data science",
                "data analysis",
                "software",
                "developer",
                "technology",
                "ai",
                "analytics"
            ]

            if any(
                word in text_lower
                for word in relevant_summary_words
            ):
                summary_score += 2

            career_words = [
                "seeking",
                "eager",
                "passionate",
                "contribute",
                "career",
                "goal",
                "opportunity",
                "looking to",
                "aspire"
            ]

            if any(
                word in text_lower
                for word in career_words
            ):
                summary_score += 1

        summary_score = min(
            summary_score,
            10
        )


        # ====================================================
        # EDUCATION SCORE — 10
        # ====================================================

        education_score = 0

        if education_found:

            education_score += 5

            if re.search(
                r"\b("
                r"bachelor|"
                r"master|"
                r"bsc|"
                r"bs|"
                r"msc|"
                r"ms|"
                r"phd|"
                r"degree|"
                r"diploma"
                r")\b",
                text_lower
            ):
                education_score += 2

            if re.search(
                r"\b("
                r"cgpa|"
                r"gpa|"
                r"grade|"
                r"percentage|"
                r"marks"
                r")\b",
                text_lower
            ):
                education_score += 2

            if re.search(
                r"\b(19\d{2}|20\d{2})\b",
                text_lower
            ):
                education_score += 1

        education_score = min(
            education_score,
            10
        )


        # ====================================================
        # SKILLS SCORE — 15
        # ====================================================

        skills_score = 0

        if skills_found:
            skills_score += 5

        if skill_count >= 12:
            skills_score += 10

        elif skill_count >= 10:
            skills_score += 9

        elif skill_count >= 8:
            skills_score += 8

        elif skill_count >= 6:
            skills_score += 6

        elif skill_count >= 4:
            skills_score += 5

        elif skill_count >= 2:
            skills_score += 3

        elif skill_count >= 1:
            skills_score += 2

        skills_score = min(
            skills_score,
            15
        )


        # ====================================================
        # EXPERIENCE SCORE — 15
        # ====================================================

        experience_score = 0

        if experience_found:

            experience_score += 6

            if action_count >= 8:
                experience_score += 5

            elif action_count >= 6:
                experience_score += 4

            elif action_count >= 4:
                experience_score += 3

            elif action_count >= 2:
                experience_score += 2

            elif action_count >= 1:
                experience_score += 1

            if quantified_count >= 4:
                experience_score += 4

            elif quantified_count >= 2:
                experience_score += 3

            elif quantified_count >= 1:
                experience_score += 2

        else:

            # Students can receive limited credit for
            # practical/project experience.

            if student_profile and projects_found:

                experience_score += 2

        experience_score = min(
            experience_score,
            15
        )


        # ====================================================
        # PROJECT SCORE — 15
        # ====================================================

        project_score = 0

        if projects_found:

            project_score += 6

            if project_tech_count >= 6:
                project_score += 4

            elif project_tech_count >= 4:
                project_score += 3

            elif project_tech_count >= 2:
                project_score += 2

            elif project_tech_count >= 1:
                project_score += 1

            if action_count >= 6:
                project_score += 2

            elif action_count >= 3:
                project_score += 2

            elif action_count >= 1:
                project_score += 1

            if quantified_count >= 2:
                project_score += 1

            elif quantified_count >= 1:
                project_score += 1

            if github_found:
                project_score += 2

        project_score = min(
            project_score,
            15
        )


        # ====================================================
        # ATS SCORE — 10
        # ====================================================

        ats_percentage = (
            ats_count / len(ats_keywords)
        ) * 100

        if ats_percentage >= 70:
            ats_score = 10

        elif ats_percentage >= 55:
            ats_score = 9

        elif ats_percentage >= 45:
            ats_score = 8

        elif ats_percentage >= 35:
            ats_score = 7

        elif ats_percentage >= 25:
            ats_score = 6

        elif ats_percentage >= 18:
            ats_score = 5

        elif ats_percentage >= 10:
            ats_score = 3

        elif ats_count >= 1:
            ats_score = 2

        else:
            ats_score = 0


        # ====================================================
        # ACTION WORD SCORE — 5
        # ====================================================

        if action_count >= 10:
            action_score = 5

        elif action_count >= 7:
            action_score = 4

        elif action_count >= 5:
            action_score = 3

        elif action_count >= 3:
            action_score = 2

        elif action_count >= 1:
            action_score = 1

        else:
            action_score = 0


        # ====================================================
        # ACHIEVEMENT SCORE — 5
        # ====================================================

        if quantified_count >= 6:
            achievement_score = 5

        elif quantified_count >= 4:
            achievement_score = 4

        elif quantified_count >= 2:
            achievement_score = 3

        elif quantified_count >= 1:
            achievement_score = 2

        elif achievements_found:
            achievement_score = 1

        else:
            achievement_score = 0


        # ====================================================
        # CONTACT SCORE — 5
        # ====================================================

        contact_score = 0

        if email_found:
            contact_score += 2

        if phone_found:
            contact_score += 1

        if linkedin_found:
            contact_score += 1

        if github_found:
            contact_score += 1

        contact_score = min(
            contact_score,
            5
        )


        # ====================================================
        # RESUME COMPLETENESS SCORE — 10
        # ====================================================

        completeness_score = 0

        if word_count >= 500:
            completeness_score = 10

        elif word_count >= 400:
            completeness_score = 9

        elif word_count >= 325:
            completeness_score = 8

        elif word_count >= 275:
            completeness_score = 7

        elif word_count >= 225:
            completeness_score = 6

        elif word_count >= 175:
            completeness_score = 5

        elif word_count >= 125:
            completeness_score = 4

        else:
            completeness_score = 3


        # Student adjustment

        if student_profile:

            student_sections = sum([
                education_found,
                skills_found,
                projects_found,
                certifications_found,
                linkedin_found
            ])

            if student_sections >= 4:
                completeness_score += 2

            elif student_sections >= 3:
                completeness_score += 1

        completeness_score = min(
            completeness_score,
            10
        )


        # ====================================================
        # FINAL SCORE
        # ====================================================

        raw_score = (
            summary_score
            + education_score
            + skills_score
            + experience_score
            + project_score
            + ats_score
            + action_score
            + achievement_score
            + contact_score
            + completeness_score
        )

        score = min(
            round(raw_score),
            100
        )


        # ====================================================
        # OVERALL SCORE
        # ====================================================

        st.subheader("📊 Resume Score")

        st.metric(
            "Overall Score",
            f"{score}/100"
        )

        st.progress(
            score / 100
        )

        if score >= 90:

            st.success(
                "🟢 Excellent Resume — Highly Competitive"
            )

        elif score >= 80:

            st.success(
                "🟢 Very Good Resume — Minor Improvements Recommended"
            )

        elif score >= 70:

            st.info(
                "🔵 Good Resume — Some Improvements Recommended"
            )

        elif score >= 60:

            st.warning(
                "🟡 Average Resume — Needs Improvement"
            )

        elif score >= 40:

            st.warning(
                "🟠 Weak Resume — Several Improvements Needed"
            )

        else:

            st.error(
                "🔴 Resume Needs Major Improvement"
            )


        # ====================================================
        # DETAILED SCORE BREAKDOWN
        # ====================================================

        st.subheader(
            "📊 Detailed Score Breakdown"
        )

        breakdown = {
            "Professional Summary": (
                summary_score,
                10
            ),
            "Education": (
                education_score,
                10
            ),
            "Technical Skills": (
                skills_score,
                15
            ),
            "Experience": (
                experience_score,
                15
            ),
            "Projects": (
                project_score,
                15
            ),
            "ATS Keywords": (
                ats_score,
                10
            ),
            "Action Words": (
                action_score,
                5
            ),
            "Achievements": (
                achievement_score,
                5
            ),
            "Contact Information": (
                contact_score,
                5
            ),
            "Resume Completeness": (
                completeness_score,
                10
            )
        }

        for category, values in breakdown.items():

            category_score, maximum = values

            st.write(
                f"**{category}: "
                f"{category_score}/{maximum}**"
            )

            st.progress(
                category_score / maximum
            )


        # ====================================================
        # SECTION ANALYSIS
        # ====================================================

        st.subheader(
            "📋 Resume Section Analysis"
        )

        sections = {
            "Professional Summary": summary_found,
            "Education": education_found,
            "Skills": skills_found,
            "Experience": experience_found,
            "Projects": projects_found,
            "Certifications": certifications_found,
            "Achievements": achievements_found,
            "Email": email_found,
            "Phone": phone_found,
            "LinkedIn": linkedin_found,
            "GitHub": github_found
        }

        for section, found in sections.items():

            if found:

                st.write(
                    f"✅ {section}"
                )

            else:

                st.write(
                    f"❌ {section}"
                )


        # ====================================================
        # SKILLS ANALYSIS
        # ====================================================

        st.subheader(
            "🛠️ Skills Analysis"
        )

        if skill_count > 0:

            st.success(
                f"{skill_count} technical skills detected."
            )

            st.write(
                "**Detected Skills:** "
                + ", ".join(
                    detected_skills
                )
            )

        else:

            st.warning(
                "No common technical skills were detected."
            )


        # ====================================================
        # ATS KEYWORD ANALYSIS
        # ====================================================

        st.subheader(
            "🤖 ATS Keyword Analysis"
        )

        st.write(
            f"**{ats_count}/{len(ats_keywords)} "
            f"ATS keywords detected "
            f"({ats_percentage:.0f}%).**"
        )

        if detected_ats_keywords:

            st.write(
                "**Detected ATS Keywords:** "
                + ", ".join(
                    detected_ats_keywords
                )
            )

        missing_ats_keywords = [
            keyword
            for keyword in ats_keywords
            if keyword not in detected_ats_keywords
        ]

        if missing_ats_keywords:

            st.write(
                "**Potentially useful keywords:** "
                + ", ".join(
                    missing_ats_keywords[:10]
                )
            )

        if ats_count < 6:

            st.warning(
                "Improve ATS keyword coverage by naturally "
                "including job-relevant skills and technologies."
            )

        elif ats_count >= 15:

            st.success(
                "Strong ATS keyword coverage detected."
            )


        # ====================================================
        # ACTION WORD ANALYSIS
        # ====================================================

        st.subheader(
            "⚡ Action Word Analysis"
        )

        if detected_action_words:

            st.success(
                f"{action_count} strong action words detected."
            )

            st.write(
                "**Strong Action Words:** "
                + ", ".join(
                    detected_action_words
                )
            )

        else:

            st.warning(
                "No strong action verbs detected."
            )

        if detected_weak_words:

            st.warning(
                "**Weak/General Words:** "
                + ", ".join(
                    detected_weak_words
                )
            )


        # ====================================================
        # EXPERIENCE ANALYSIS
        # ====================================================

        st.subheader(
            "💼 Experience Analysis"
        )

        if experience_found:

            st.success(
                "Experience section detected."
            )

            if action_count >= 3:

                st.success(
                    "Good use of action-oriented language."
                )

            else:

                st.warning(
                    "Experience descriptions should use "
                    "strong action verbs."
                )

            if quantified_count:

                st.success(
                    f"{quantified_count} measurable details detected."
                )

            else:

                st.warning(
                    "No measurable results detected in the resume."
                )

        else:

            if student_profile:

                st.info(
                    "No formal work-experience section detected. "
                    "For a student resume, internships, academic work, "
                    "volunteer work, and projects can demonstrate experience."
                )

            else:

                st.warning(
                    "No experience section detected."
                )


        # ====================================================
        # PROJECT ANALYSIS
        # ====================================================

        st.subheader(
            "📁 Project Analysis"
        )

        if projects_found:

            st.success(
                "Projects section detected."
            )

            if project_tech_count >= 4:

                st.success(
                    "Strong technical information detected in projects."
                )

            elif project_tech_count >= 2:

                st.info(
                    "Some project technologies were detected."
                )

            else:

                st.warning(
                    "Add technologies and tools used in your projects."
                )

            if github_found:

                st.success(
                    "GitHub profile detected."
                )

        else:

            st.warning(
                "No projects section detected."
            )


        # ====================================================
        # ACHIEVEMENT ANALYSIS
        # ====================================================

        st.subheader(
            "🏆 Achievement Analysis"
        )

        if quantified_count:

            st.success(
                f"{quantified_count} measurable details detected."
            )

            st.write(
                "**Detected Measurements:** "
                + ", ".join(
                    quantified_matches[:10]
                )
            )

        elif achievements_found:

            st.info(
                "Achievements section detected, but "
                "few measurable results were found."
            )

        else:

            st.warning(
                "No measurable achievements detected."
            )

            st.write(
                "Example: Developed a machine learning model "
                "achieving 92% accuracy."
            )


        # ====================================================
        # STUDENT RESUME ANALYSIS
        # ====================================================

        if student_profile:

            st.subheader(
                "🎓 Student Resume Analysis"
            )

            st.success(
                "Student/undergraduate profile detected."
            )

            st.write(
                "Student resumes are evaluated with more emphasis "
                "on education, technical skills, projects, and "
                "learning achievements."
            )

            student_checks = {
                "Education": education_found,
                "Technical Skills": skills_found,
                "Projects": projects_found,
                "Certifications": certifications_found,
                "LinkedIn": linkedin_found,
                "GitHub": github_found
            }

            for item, found in student_checks.items():

                if found:

                    st.write(
                        f"✅ {item}"
                    )

                else:

                    st.write(
                        f"⚠️ {item} could be added/improved"
                    )


        # ====================================================
        # RESUME STATISTICS
        # ====================================================

        st.subheader(
            "📈 Resume Statistics"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Word Count",
                word_count
            )

        with col2:

            st.metric(
                "Skills",
                skill_count
            )

        with col3:

            st.metric(
                "Action Words",
                action_count
            )

        with col4:

            st.metric(
                "ATS Keywords",
                ats_count
            )


        # ====================================================
        # SMART SUGGESTIONS
        # ====================================================

        st.subheader(
            "💡 Smart Improvement Suggestions"
        )

        suggestions = []

        if not summary_found:

            suggestions.append(
                "Add a professional summary explaining "
                "your background, strongest technical skills, "
                "and target career direction."
            )

        elif summary_score < 7:

            suggestions.append(
                "Strengthen your summary by clearly mentioning "
                "your specialization, technical skills, and career goal."
            )


        if not education_found:

            suggestions.append(
                "Add an Education section with your degree, "
                "university, CGPA/GPA, and dates."
            )

        elif education_score < 7:

            suggestions.append(
                "Improve Education details by including your "
                "degree, institution, CGPA/GPA, and dates."
            )


        if skill_count < 5:

            suggestions.append(
                "Add relevant technical skills that you genuinely "
                "know and that match your target roles."
            )

        elif skill_count < 8:

            suggestions.append(
                "Consider adding relevant tools such as Pandas, "
                "NumPy, SQL, Git, Scikit-learn, or other technologies "
                "you genuinely know."
            )


        if not experience_found:

            if student_profile:

                suggestions.append(
                    "If you have internships, volunteer work, "
                    "freelance work, university activities, or practical "
                    "experience, consider adding them."
                )

            else:

                suggestions.append(
                    "Add relevant professional, internship, freelance, "
                    "volunteer, or practical experience."
                )


        if action_count < 3:

            suggestions.append(
                "Replace weak phrases with strong action verbs "
                "such as developed, built, implemented, analyzed, "
                "designed, automated, optimized, and deployed."
            )


        if quantified_count < 2:

            suggestions.append(
                "Add measurable results using percentages, "
                "accuracy, users, datasets, project counts, "
                "time saved, or other concrete numbers."
            )


        if not projects_found:

            suggestions.append(
                "Add 2–4 relevant technical projects with "
                "technologies used and your specific contribution."
            )

        elif project_tech_count < 3:

            suggestions.append(
                "Mention the technologies, frameworks, libraries, "
                "and tools used in your projects."
            )


        if ats_count < 6:

            suggestions.append(
                "Improve ATS keyword coverage by naturally "
                "including relevant keywords from the job description."
            )


        if not certifications_found:

            suggestions.append(
                "Consider adding relevant certifications, courses, "
                "or training programs you have actually completed."
            )


        if not linkedin_found:

            suggestions.append(
                "Add your LinkedIn profile to your contact section."
            )


        if projects_found and not github_found:

            suggestions.append(
                "Consider adding your GitHub profile or links "
                "to important technical projects."
            )


        if word_count < 125:

            suggestions.append(
                "Your resume is very short. Add meaningful details "
                "about projects, skills, education, experience, "
                "and achievements."
            )

        elif word_count < 175:

            suggestions.append(
                "Consider adding useful details, especially "
                "project descriptions and achievements."
            )

        elif word_count > 800:

            suggestions.append(
                "Consider removing repetitive or less-relevant "
                "information and keeping the resume focused."
            )


        if suggestions:

            for suggestion in suggestions:

                st.warning(
                    "⚠️ " + suggestion
                )

        else:

            st.success(
                "🎉 No major improvements detected!"
            )


        # ====================================================
        # FINAL VERDICT
        # ====================================================

        st.subheader(
            "🎯 Final Resume Verdict"
        )

        if score >= 90:

            st.success(
                "Excellent! Your resume has strong structure, "
                "technical skills, ATS coverage, projects, "
                "and measurable achievements."
            )

        elif score >= 80:

            st.success(
                "Very good resume. A few targeted improvements "
                "could make it highly competitive."
            )

        elif score >= 70:

            st.info(
                "Good resume. Improve ATS keywords, action verbs, "
                "achievements, and project details to increase "
                "your competitiveness."
            )

        elif score >= 60:

            st.warning(
                "Your resume has a reasonable foundation, "
                "but several areas should be improved before "
                "applying to competitive positions."
            )

        else:

            st.error(
                "Your resume needs significant improvement "
                "in structure, content, skills, experience, "
                "and measurable achievements."
            )


else:

    st.info(
        "👆 Upload a PDF resume above to begin your analysis."
    )