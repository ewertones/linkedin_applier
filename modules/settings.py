from typing import Literal

from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    model_config = ConfigDict(strict=True, validate_default=True)

    # BASIC SETTINGS
    # Only if you are not logged in
    username: str = ""
    password: str = ""

    search_term: str = (
        "python"  # Eg: "Software Engineer", "Software Developer", "Selenium Developer". If needed, use BOOLEAN search
    )
    sort_by: str = "Most recent"  # "Most recent", "Most relevant" or ("" to not select)
    date_posted: Literal["", "Any time", "Past month", "Past week", "Past 24 hours"] = "Past 24 hours"

    # OTHER SETTINGS
    # PERSONAL SETTINGS
    first_name: str = "Ewerton"
    middle_name: str = "Evangelista"
    last_name: str = "de Souza"
    phone_number: str = "5531998546167"
    current_city: str = "Belo Horizonte, Brazil"
    street: str = "Belo Horizonte"
    state: str = "Minas Gerais"
    zipcode: str = "31320455"
    country: str = "Brazil"
    ethnicity: Literal[
        "Decline",
        "Hispanic/Latino",
        "American Indian or Alaska Native",
        "Asian",
        "Black or African American",
        "Native Hawaiian or Other Pacific Islander",
        "White",
        "Other",
    ] = "Hispanic/Latino"
    gender: Literal["Male", "Female", "Other", "Decline", ""] = "Male"
    disability_status: Literal["Yes", "No", "Decline"] = "No"
    veteran_status: Literal["Yes", "No", "Decline"] = "No"

    # APPLICATION SETTINGS
    years_of_experience: str = "5"
    require_visa: Literal["Yes", "No"] = "No"
    website: str = "https://ewerton.com.br/"
    linkedin: str = "https://www.linkedin.com/in/ewertones/"
    us_citizenship: Literal[
        "U.S. Citizen/Permanent Resident",
        "Non-citizen allowed to work for any employer",
        "Non-citizen allowed to work for current employer",
        "Non-citizen seeking work authorization",
        "Canadian Citizen/Permanent Resident",
        "Other",
    ] = "Non-citizen allowed to work for any employer"
    desired_salary: int = 100000
    notice_period_in_days: int = 7
    headline: str = "A Software Developer working as a Data wildcard: Engineer, Scientist, Analyst, DevOps and so on"
    summary: str = (
        "Hello! I'm a Software Developer working as a Data wildcard: Engineer, Scientist, Analyst, DevOps and so on"
    )
    cover_letter: str = "Hey, let's talk :)"
    recent_employer: str = "Not Applicable"  # "", "Lala Company", "Google", "Snowflake", "Databricks"
    confidence_level: str = "8"  # To answer questions having a confidence level of 1-10
    overwrite_previous_answers: bool = False  # Do you want to overwrite previous answers?

    # SEARCH SETTINGS
    search_location: str = "United States"  # Some valid examples: "", "United States", "European Union"
    salary: Literal[
        "$40,000+",
        "$60,000+",
        "$80,000+",
        "$100,000+",
        "$120,000+",
        "$140,000+",
        "$160,000+",
        "$180,000+",
        "$200,000+",
    ] = "$80,000+"
    experience_level: list[
        Literal[
            "Internship",
            "Entry level",
            "Associate",
            "Mid-Senior level",
            "Director",
            "Executive",
        ]
    ] = []
    job_type: list[
        Literal[
            "Full-time",
            "Part-time",
            "Contract",
            "Temporary",
            "Volunteer",
            "Internship",
            "Other",
        ]
    ] = [
        "Full-time",
        "Part-time",
        "Contract",
    ]
    on_site: list[Literal["On-site", "Remote", "Hybrid"]] = ["Remote"]
    companies: list[str] = (
        []
    )  # Eg: "7-eleven", "Google","X, the moonshot factory","YouTube","Adometry (acquired by Google)", and so on...
    location: list[str] = []
    industry: list[str] = []
    job_function: list[str] = []
    job_titles: list[str] = []
    benefits: list[str] = []
    commitments: list[str] = []
    under_10_applicants: bool = False
    in_your_network: bool = False
    fair_chance_employer: bool = False
    about_company_bad_words: list[str] = [
        "Coinbase",
        "Jobot",
        "Harnham",
    ]  # Skip these companies, and companies with these words in their 'About'
    about_company_good_words: list[str] = (
        []
    )  # Skip checking for `about_company_bad_words` for these companies if they have these good words in their 'About'

    bad_words: list[str] = [
        "US Citizen",
        "USA Citizen",
        "No C2C",
        "No Corp2Corp",
        ".NET",
        "Embedded Programming",
        "PHP",
        "Ruby",
        "CNC",
        "Java",
        "C++",
        "Ruby",
    ]  # Avoid applying to these companies if they have these bad words in their 'Job Description' section...
    security_clearance: bool = False  # Do you have an active Security Clearance?
    # Avoid applying to jobs if their required experience is above your current_experience.
    # (Set value as -1 if you want to apply to all ignoring their required experience...)
    current_experience: int = -1

    # Bot settings
    click_gap: int = 0  # Set the maximum amount of time allowed to wait between each click in secs
    safe_mode: bool = False  # Run Chrome in guest mode
    stealth_mode: bool = True  # Run in undetected mode to bypass anti-bot protections
    # Directory and name of the files where history of applied jobs is saved
    logs_folder_path: str = "logs/"
    file_name: str = "logs/applied_applications_history.csv"
    failed_file_name: str = "logs/failed_applications_history.csv"
