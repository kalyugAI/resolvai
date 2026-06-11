import os
import requests
from requests.auth import HTTPBasicAuth

def extract_description(node):

    result = []

    def walk(obj):

        if isinstance(
            obj,
            dict
        ):

            if (
                obj.get(
                    "type"
                )
                ==
                "text"
            ):

                result.append(

                    obj.get(
                        "text",
                        ""
                    )

                )

            elif (
                obj.get(
                    "type"
                )
                ==
                "hardBreak"
            ):

                result.append(
                    "\n"
                )

            for value in obj.values():

                walk(
                    value
                )

        elif isinstance(
            obj,
            list
        ):

            for x in obj:

                walk(
                    x
                )

    walk(node)

    return (
        " "
        .join(
            result
        )
        .replace(
            " \n ",
            "\n"
        )
    )

def fetch_jira():

    if (

        os.getenv(
            "ENABLE_JIRA",
            "false"
        ).lower()

        !=

        "true"

    ):

        return []

    response = requests.get(

        f'{os.getenv("JIRA_URL")}/rest/api/3/search/jql',

        params={

            "jql":

            f'project={os.getenv("JIRA_PROJECT")}',

            "fields":

            "summary,description,status,comment"

        },

        headers={

            "Accept":

            "application/json"

        },

        auth=

        HTTPBasicAuth(

            os.getenv(
                "JIRA_USER"
            ),

            os.getenv(
                "JIRA_TOKEN"
            )

        )

    )

    response.raise_for_status()

    issues = (

        response
        .json()
        .get(
            "issues",
            []
        )

    )

    records = []

    for issue in issues:

        fields = (

            issue.get(
                "fields",
                {}
            )

        )

        comments = (

            fields
            .get(
                "comment",
                {}
            )
            .get(
                "comments",
                []
            )

        )

        latest_comment = ""

        if comments:

            latest_comment = (

                extract_description(

                    comments[-1]
                    .get(
                        "body"
                    )

                )

            )

        if not latest_comment:

            latest_comment = (

                fields
                .get(
                    "status",
                    {}
                )
                .get(
                    "name",
                    ""
                )

            )

        records.append({

            "id":

            issue.get(
                "key",
                ""
            ),

            "incident":

            (
                fields.get(
                    "summary",
                    ""
                )

                +

                "\n"

                +

                extract_description(

                    fields.get(
                        "description"
                    )

                )

            ),

            "resolution":

            latest_comment

        })

    return records
