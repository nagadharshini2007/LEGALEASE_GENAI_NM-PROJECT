import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv

from utils.document_export import (
    format_docx,
    format_pdf,
    format_txt,
)

from utils.text_utils import (
    format_html_preview,
    sanitize_text,
)


load_dotenv()


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

GENERATE_URL = (
    f"{BACKEND_URL}/generate"
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown(
    """
<style>

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #777;
    font-size: 17px;
    margin-bottom: 30px;
}

.legal-preview {
    background: #151515;
    color: #f5f5f5;
    border-radius: 14px;
    padding: 30px;
    min-height: 450px;
    max-height: 650px;
    overflow-y: auto;
    line-height: 1.7;
    border: 1px solid #333;
}

.legal-preview p {
    margin-bottom: 16px;
}

.legal-heading {
    color: #8ab4f8;
    margin-top: 22px;
}

.info-box {
    background: #f5f7fa;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #4f8cff;
}

</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""

if "editing" not in st.session_state:
    st.session_state.editing = False


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Document Generator'
    '</div>',
    unsafe_allow_html=True,
)


st.markdown(
    """
<div class="info-box">
LegalEase helps create editable legal document drafts
from the information you provide. Always review the
generated document carefully and seek qualified legal
advice when appropriate.
</div>
""",
    unsafe_allow_html=True,
)

st.write("")


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("Document Settings")

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Lease Agreement",
            "Freelance Work Contract",
            "Service Agreement",
            "Business Agreement",
            "Offer Letter",
            "Partnership Agreement",
            "General Contract",
            "Other",
        ],
    )

    if document_type == "Other":

        document_type = st.text_input(
            "Enter document type",
            placeholder="Example: Consulting Agreement",
        )

    effective_date = st.date_input(
        "Effective Date",
        value=date.today(),
    )

    st.divider()

    st.markdown(
        """
### Tips

- Enter the parties clearly.
- Separate terms using semicolons.
- Include important payment information.
- Include termination conditions.
- Check the generated document before using it.
"""
    )


# --------------------------------------------------
# Main input area
# --------------------------------------------------

left, right = st.columns(
    [1, 1]
)


with left:

    st.subheader(
        "1. Parties Involved"
    )

    parties = st.text_area(
        "Enter the people or organizations involved",
        placeholder=(
            "Example:\n"
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=180,
    )


with right:

    st.subheader(
        "2. Terms & Conditions"
    )

    terms = st.text_area(
        "Enter terms separated by semicolons",
        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=180,
    )


st.write("")


# --------------------------------------------------
# Generate button
# --------------------------------------------------

generate_clicked = st.button(
    "✨ Generate Legal Document",
    type="primary",
    use_container_width=True,
)


if generate_clicked:

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

    elif not document_type.strip():

        st.error(
            "Please select or enter a document type."
        )

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": (
                effective_date.isoformat()
            ),
        }

        with st.spinner(
            "Generating your legal document..."
        ):

            try:

                response = requests.post(
                    GENERATE_URL,
                    json=payload,
                    timeout=120,
                )

                if response.status_code == 200:

                    data = response.json()

                    st.session_state.generated_text = (
                        data["generated_text"]
                    )

                    st.session_state.editing = False

                    st.success(
                        "Document generated successfully!"
                    )

                else:

                    try:
                        detail = response.json().get(
                            "detail",
                            "Unknown backend error."
                        )
                    except Exception:
                        detail = response.text

                    st.error(
                        f"Backend error: {detail}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to FastAPI backend. "
                    "Make sure uvicorn is running on port 8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. "
                    "Please try again."
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )


# --------------------------------------------------
# Generated document section
# --------------------------------------------------

if st.session_state.generated_text:

    st.divider()

    st.subheader(
        "3. Generated Document"
    )

    button_col1, button_col2 = st.columns(
        [1, 1]
    )

    with button_col1:

        if st.button(
            "✏️ Edit Document",
            use_container_width=True,
        ):

            st.session_state.editing = True

    with button_col2:

        if st.button(
            "👁️ Preview Document",
            use_container_width=True,
        ):

            st.session_state.editing = False


    # --------------------------------------------------
    # Editable mode
    # --------------------------------------------------

    if st.session_state.editing:

        edited_text = st.text_area(
            "Edit your document",
            value=st.session_state.generated_text,
            height=650,
        )

        if st.button(
            "💾 Save Changes",
            type="primary",
        ):

            st.session_state.generated_text = (
                sanitize_text(edited_text)
            )

            st.session_state.editing = False

            st.success(
                "Changes saved successfully."
            )

            st.rerun()


    # --------------------------------------------------
    # Preview mode
    # --------------------------------------------------

    else:

        preview_html = format_html_preview(
            st.session_state.generated_text
        )

        st.markdown(
            f"""
<div class="legal-preview">
{preview_html}
</div>
""",
            unsafe_allow_html=True,
        )


    # --------------------------------------------------
    # Downloads
    # --------------------------------------------------

    st.write("")

    st.subheader(
        "4. Download Document"
    )

    current_text = sanitize_text(
        st.session_state.generated_text
    )

    txt_data = format_txt(
        current_text
    )

    docx_data = format_docx(
        current_text,
        document_type,
    )

    pdf_data = format_pdf(
        current_text,
        document_type,
    )

    download_col1, download_col2, download_col3 = (
        st.columns(3)
    )


    with download_col1:

        st.download_button(
            label="📄 Download TXT",
            data=txt_data,
            file_name="LegalEase_Document.txt",
            mime="text/plain",
            use_container_width=True,
        )


    with download_col2:

        st.download_button(
            label="📝 Download DOCX",
            data=docx_data,
            file_name="LegalEase_Document.docx",
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            use_container_width=True,
        )


    with download_col3:

        st.download_button(
            label="📕 Download PDF",
            data=pdf_data,
            file_name="LegalEase_Document.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "LegalEase | AI-Assisted Legal Document Generator"
)