from datetime import datetime, timezone
import enum
from sqlalchemy import Boolean, DateTime

from app.db.database import Base

# These are SQLAlchemy database-related tools.
from sqlalchemy import (
    BigInteger,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Enum as SQLEnum,
    func, #his lets SQLAlchemy call SQL/database functions. func.now()
)

# These are ORM-specific tools.
from sqlalchemy.orm import (
    Mapped,      #This combines Python typing with SQLAlchemy ORM information. This attribute is managed by SQLAlchemy ORM.
    mapped_column, #Create an actual database column for this Python attribute.
    relationship,
)


# =========================================================
# ENUMS
# =========================================================


class UserRole(enum.Enum):
    ADMIN = "admin"
    ENGINEER = "engineer"
    EMPLOYEE = "employee"
    MANAGER = "manager"

class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketCategory(enum.Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    ACCESS = "access"
    OTHER = "other"

class ReactionType(enum.Enum):
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"


# =========================================================
# USER
# =========================================================

# one python object represents one row from the table
class User(Base): # Create a Python ORM model called user. bcz it inherits from base. it's python class
    __tablename__ = "users" # and it's actual database column
    # here id is Python attribute name.  and Mapped[int] is Python/ORM type.
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    ) #mapped_column(...)   This attribute corresponds to a real database column

    role: Mapped[UserRole] = mapped_column(
    SQLEnum(
        UserRole,
        name="user_role",
        values_callable=lambda enum_class: [member.value for member in enum_class]
    ),
    nullable=False
)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
#This is called a forward reference.
    created_tickets: Mapped[list["Ticket"]] = relationship( #ORM-managed attribute containing a list of Ticket objects.
        back_populates="creator", #User.created_tickets and Ticket.creator are the opposite directions of the same relationship.
        foreign_keys="Ticket.created_by_id"
        #This tells SQLAlchemy which actual FK column defines this relationship.
    )

    assigned_tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="assignee",
        foreign_keys="Ticket.assignee_id"
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="author"
    )

    reactions: Mapped[list["CommentReaction"]] = relationship(
        back_populates="user"
    )

    history_changes: Mapped[list["TicketHistory"]] = relationship(
        back_populates="changed_by"
    )


# =========================================================
# TICKET
# =========================================================


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    category: Mapped[TicketCategory] = mapped_column(
    SQLEnum(
        TicketCategory,
        name="ticket_category",
        values_callable=lambda enum_class: [
            member.value for member in enum_class
        ]
    ),
    nullable=False
)

    status: Mapped[TicketStatus] = mapped_column(
    SQLEnum(
        TicketStatus,
        name="ticket_status",
        values_callable=lambda enum_class: [member.value for member in enum_class]
    ),
    nullable=False
)

    priority: Mapped[TicketPriority] = mapped_column(
    SQLEnum(
        TicketPriority,
        name="ticket_priority",
        values_callable=lambda enum_class: [member.value for member in enum_class]
    ),
    nullable=False
)

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    creator: Mapped["User"] = relationship(
        back_populates="created_tickets",
        foreign_keys=[created_by_id]
    )

    assignee: Mapped["User | None"] = relationship(
        back_populates="assigned_tickets",
        foreign_keys=[assignee_id]
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="ticket"
    )

    history: Mapped[list["TicketHistory"]] = relationship(
        back_populates="ticket"
    )
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false"
)

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
)

    deleted_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
) 


# =========================================================
# COMMENT
# =========================================================


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tickets.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    ticket: Mapped["Ticket"] = relationship(
        back_populates="comments"
    )

    author: Mapped["User"] = relationship(
        back_populates="comments"
    )

    reactions: Mapped[list["CommentReaction"]] = relationship(
        back_populates="comment"
    )


# =========================================================
# COMMENT REACTION
# =========================================================


class CommentReaction(Base):
    __tablename__ = "comment_reactions"

    __table_args__ = (
        UniqueConstraint(
            "comment_id",
            "user_id",
            name="uq_comment_user_reaction"
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    comment_id: Mapped[int] = mapped_column(
        ForeignKey(
            "comments.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    reaction_type: Mapped[ReactionType] = mapped_column(
    SQLEnum(
        ReactionType,
        name="reaction_type",
        values_callable=lambda enum_class: [
            member.value for member in enum_class
        ]
    ),
    nullable=False
)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    comment: Mapped["Comment"] = relationship(
        back_populates="reactions"
    )

    user: Mapped["User"] = relationship(
        back_populates="reactions"
    )


# =========================================================
# TICKET HISTORY
# =========================================================


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tickets.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    changed_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    action: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    field_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    old_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    new_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    ticket: Mapped["Ticket"] = relationship(
        back_populates="history"
    )

    changed_by: Mapped["User"] = relationship(
        back_populates="history_changes"
    )