import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from connectors.local_connector import load_local
from connectors.jira_connector import fetch_jira

load_dotenv()


def normalize(text):

    if not text:
        return ""

    return re.sub(
        r"[^a-z0-9]",
        " ",
        str(text).lower()
    )


def find_matches(logs):

    query = normalize(
        logs
    )

    incidents = []

    try:

        incidents.extend(
            load_local()
        )

    except:

        pass

    try:

        incidents.extend(
            fetch_jira()
        )

    except:

        pass

    query_words = {

        x

        for x in query.split()

        if len(x) >= 4

    }

    ignored = {

        "error",
        "warn",
        "info",
        "failed",
        "failure",
        "service",
        "request",
        "connection",
        "retry",
        "issue",
        "problem"

    }

    query_words = (
        query_words
        -
        ignored
    )

    ranked = []

    for item in incidents:

        text = normalize(

            (
                item.get(
                    "incident",
                    ""
                )

                +

                " "

                +

                item.get(
                    "resolution",
                    ""
                )

            )

        )

        text_words = set(
            text.split()
        )

        overlap = (
            query_words
            &
            text_words
        )

        score = len(
            overlap
        )

        if score >= 2:

            ranked.append(

                (
                    score,
                    item
                )

            )

    ranked.sort(
        key=lambda x:
        x[0],
        reverse=True
    )

    return [

        x[1]

        for x
        in ranked[:5]

    ]


def build_context(
    incidents
):

    output = []

    for x in incidents:

        output.append(

f"""
ID:
{x["id"]}

Incident:
{x["incident"]}

Resolution:
{x["resolution"]}
"""

        )

    return "\n".join(
        output
    )


def analyze(
    logs
):

    matched = (
        find_matches(
            logs
        )
    )

    historical = (
        len(
            matched
        )
        >
        0
    )

    client = OpenAI(

        base_url=
        os.getenv(
            "LITELLM_API_BASE"
        ),

        api_key=
        os.getenv(
            "LITELLM_API_KEY"
        )

    )

    if historical:

        prompt = f"""
User Logs:

{logs}

Matched Historical Incidents:

{build_context(matched)}

Instructions:

Use historical incidents as PRIMARY evidence.

If incident resolution exists:
prefer it over generic recommendations.

Return:

Summary

Matched Incident IDs

Confidence

Suggested Fix

References
"""

    else:

        prompt = f"""
User Logs:

{logs}

No historical incident matched.

Act as Senior SRE.

Return:

Summary

Root Cause

Confidence

AI Recommendation

References

Mention:
No historical match found
"""

    result = (

        client
        .chat
        .completions
        .create(

            model=
            os.getenv(
                "MODEL_NAME"
            ),

            messages=[

                {

                    "role":
                    "user",

                    "content":
                    prompt

                }

            ]

        )

    )

    return (

        result
        .choices[0]
        .message
        .content

    )
