from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, audit_repository: AuditRepository) -> None:
        self.audit_repository = audit_repository

    async def record(
        self,
        *,
        user_id: str | None,
        event: str,
        actor: str,
        ip_address: str | None,
        user_agent: str | None,
        metadata: dict,
    ) -> None:
        await self.audit_repository.log_event(
            user_id=user_id,
            event=event,
            actor=actor,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )
