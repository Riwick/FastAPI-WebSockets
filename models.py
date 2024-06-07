from database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    class Config:
        orm_mode = True