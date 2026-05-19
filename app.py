from __future__ import annotations

import csv
import io
import tempfile
import zipfile
from datetime import date
from pathlib import Path

import streamlit as st

from generate_offer_letters import (
    DEFAULT_COMPANY,
    DEFAULT_OFFICE,
    DEFAULT_TEMPLATE,
    build_offer_letter,
    safe_filename,
)


APP_ROOT = Path(__file__).resolve().parent
DEFAULT_RESPONSIBILITIES = [
    "Design and develop scalable backend applications using Java (8+) and Spring Boot.",
    "Build and deploy serverless applications using AWS services such as Lambda, API Gateway, and CloudWatch.",
    "Develop RESTful APIs to support system integration and data exchange.",
    "Implement and maintain business logic to ensure application performance and data accuracy.",
    "Configure and manage AWS infrastructure components including Lambda, API Gateway, and DynamoDB.",
    "Perform unit testing, debugging, and code validation to ensure application reliability.",
    "Conduct code reviews and follow best practices for coding standards, security, and performance.",
    "Troubleshoot and resolve issues across development and testing environments.",
    "Support CI/CD pipelines for application build and deployment.",
    "Maintain technical documentation including system design and API specifications.",
    "Participate in Agile processes such as sprint planning and backlog refinement.",
]


st.set_page_config(
    page_title="Team AD Automations",
    page_icon="AD",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_secret_list(name: str) -> list[str]:
    value = st.secrets.get(name, [])
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return list(value)


def user_email() -> str:
    return str(st.user.get("email", "")).lower()


def auth_configured() -> bool:
    try:
        return "auth" in st.secrets
    except Exception:
        return False


def is_logged_in() -> bool:
    return bool(st.user.to_dict().get("is_logged_in", False))


def require_login() -> None:
    st.title("Team AD Automations")
    st.caption("Secure document generation and operations utilities for the team.")

    if not auth_configured():
        st.warning("Google login is not configured yet.")
        st.write("Create `.streamlit/secrets.toml` from `.streamlit/secrets.example.toml`, then add your Google OAuth client details.")
        st.stop()

    if not is_logged_in():
        st.button("Log in with Google", on_click=st.login, type="primary")
        st.stop()

    allowed_emails = [email.lower() for email in get_secret_list("allowed_emails")]
    allowed_domains = [domain.lower().lstrip("@") for domain in get_secret_list("allowed_domains")]
    email = user_email()
    domain = email.split("@")[-1] if "@" in email else ""

    if allowed_emails and email not in allowed_emails:
        st.error("Your account is not allowed to access this app.")
        st.button("Log out", on_click=st.logout)
        st.stop()

    if allowed_domains and domain not in allowed_domains:
        st.error("Your email domain is not allowed to access this app.")
        st.button("Log out", on_click=st.logout)
        st.stop()


def offer_row(
    candidate_name: str,
    role: str,
    annual_salary: int,
    offer_date: date,
    company: str,
    office_address: str,
    signer_name: str,
    signer_title: str,
    responsibilities: str,
) -> dict[str, str]:
    return {
        "candidate_name": candidate_name,
        "role": role,
        "annual_salary": str(annual_salary),
        "offer_date": offer_date.isoformat(),
        "company": company,
        "office_address": office_address,
        "signer_name": signer_name,
        "signer_title": signer_title,
        "responsibilities": "|".join(
            line.strip() for line in responsibilities.splitlines() if line.strip()
        ),
    }


def generate_docx_bytes(row: dict[str, str]) -> tuple[str, bytes]:
    filename = f"{safe_filename(row['candidate_name'])}_offer_letter.docx"
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / filename
        build_offer_letter(DEFAULT_TEMPLATE, output_path, row)
        return filename, output_path.read_bytes()


def csv_template_bytes() -> bytes:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "candidate_name",
            "role",
            "annual_salary",
            "offer_date",
            "company",
            "office_address",
            "signer_name",
            "signer_title",
            "responsibilities",
        ],
    )
    writer.writeheader()
    writer.writerow(
        offer_row(
            candidate_name="Alex Candidate",
            role="Java Developer",
            annual_salary=84000,
            offer_date=date.today(),
            company=DEFAULT_COMPANY,
            office_address=DEFAULT_OFFICE,
            signer_name="Mounika Bandari",
            signer_title="President",
            responsibilities="\n".join(DEFAULT_RESPONSIBILITIES),
        )
    )
    return output.getvalue().encode("utf-8")


def single_offer_letter() -> None:
    with st.form("single_offer_letter"):
        left, right = st.columns(2)
        with left:
            candidate_name = st.text_input("Candidate name", value="Alex Candidate")
            role = st.text_input("Role", value="Java Developer")
            annual_salary = st.number_input("Annual salary", min_value=0, value=84000, step=1000)
            offer_date = st.date_input("Offer date", value=date.today())
        with right:
            company = st.text_input("Company", value=DEFAULT_COMPANY)
            office_address = st.text_input("Office address", value=DEFAULT_OFFICE)
            signer_name = st.text_input("Signer name", value="Mounika Bandari")
            signer_title = st.text_input("Signer title", value="President")

        responsibilities = st.text_area(
            "Responsibilities",
            value="\n".join(DEFAULT_RESPONSIBILITIES),
            height=260,
        )
        submitted = st.form_submit_button("Generate offer letter", type="primary")

    if submitted:
        if not candidate_name.strip() or not role.strip():
            st.error("Candidate name and role are required.")
            return
        row = offer_row(
            candidate_name,
            role,
            int(annual_salary),
            offer_date,
            company,
            office_address,
            signer_name,
            signer_title,
            responsibilities,
        )
        filename, content = generate_docx_bytes(row)
        st.success(f"Generated {filename}")
        st.download_button(
            "Download Word document",
            data=content,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )


def bulk_offer_letters() -> None:
    st.download_button(
        "Download CSV template",
        data=csv_template_bytes(),
        file_name="offer_letters_template.csv",
        mime="text/csv",
    )
    upload = st.file_uploader("Upload completed CSV", type=["csv"])
    if upload is None:
        return

    rows = list(csv.DictReader(io.StringIO(upload.getvalue().decode("utf-8-sig"))))
    st.write(f"{len(rows)} row(s) loaded.")
    if not rows:
        return

    if st.button("Generate ZIP", type="primary"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for row in rows:
                if not row.get("candidate_name", "").strip():
                    continue
                filename, content = generate_docx_bytes(row)
                archive.writestr(filename, content)
        st.download_button(
            "Download generated ZIP",
            data=zip_buffer.getvalue(),
            file_name="offer_letters.zip",
            mime="application/zip",
        )


def offer_letter_page() -> None:
    st.header("Offer Letter Generator")
    tab_single, tab_bulk = st.tabs(["Single letter", "Bulk CSV"])
    with tab_single:
        single_offer_letter()
    with tab_bulk:
        bulk_offer_letters()


def placeholder_page(title: str) -> None:
    st.header(title)
    st.info("This utility slot is ready. Add the template and generator logic next.")


def main() -> None:
    require_login()

    with st.sidebar:
        st.write(f"Signed in as {st.user.name}")
        st.caption(user_email())
        st.button("Log out", on_click=st.logout)
        utility = st.radio(
            "Utilities",
            [
                "Offer Letter Generator",
                "NDA Generator",
                "Experience Letter Generator",
                "Employee Data Formatter",
            ],
        )

    if utility == "Offer Letter Generator":
        offer_letter_page()
    else:
        placeholder_page(utility)


if __name__ == "__main__":
    main()
