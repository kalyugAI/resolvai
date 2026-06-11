import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from ui.uploader import get_logs

from core.incident_engine import analyze

from core.report_generator import save


st.set_page_config(
    page_title=
    "ResolvAI"
)

st.title(
    "ResolvAI"
)

logs = (
    get_logs()
)

if st.button(
    "Analyze"
):

    if logs:

        with st.spinner():

            result = (
                analyze(
                    logs
                )
            )

        st.success(
            "Done"
        )

        st.write(
            result
        )

        file = (
            save(
                result
            )
        )

        with open(
            file
        ) as f:

            st.download_button(
                "Download Report",
                f,
                file_name=
                "incident_report.txt"
            )
