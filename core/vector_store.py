import chromadb


def get_collection():

    client = (
        chromadb
        .PersistentClient(
            path=
            "./vector_db"
        )
    )

    try:

        return (
            client
            .get_collection(
                "incidents"
            )
        )

    except:

        return (
            client
            .create_collection(
                "incidents"
            )
        )
