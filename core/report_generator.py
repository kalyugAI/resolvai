def save(
    text
):

    path = (
        "output/report.txt"
    )

    with open(
        path,
        "w"
    ) as f:

        f.write(
            text
        )

    return path
