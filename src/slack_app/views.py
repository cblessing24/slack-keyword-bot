from .service_layer.unit_of_work import SQLAlchemyUnitOfWork


def keywords(channel_name: str, subscriber: str, uow: SQLAlchemyUnitOfWork) -> list[str]:
    with uow:
        results = uow.session.execute(
            """
            SELECT keyword FROM subscription_view WHERE channel_name = :channel_name AND subscriber = :subscriber
            """,
            {"channel_name": channel_name, "subscriber": subscriber},
        )
        return [row.keyword for row in results]
