
"""allow duplicate license plates and vehicle colors

Revision ID: 7f841f36cb93
Revises: 812a959b2266
Create Date: 2026-10-28 08:52:15.895687
"""

from alembic import op
import sqlalchemy as sa

revision = '7f841f36cb93'
down_revision = '812a959b2266'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "drivers_license_number_key",
        "drivers",
        type_="unique"
    )
    op.drop_constraint(
        "vehicles_plate_number_key",
        "vehicles",
        type_="unique"
    )
    op.drop_constraint(
        "vehicles_color_key",
        "vehicles",
        type_="unique"
    )


def downgrade():
    op.create_unique_constraint(
        "drivers_license_number_key",
        "drivers",
        ["license_number"]
    )
    op.create_unique_constraint(
        "vehicles_plate_number_key",
        "vehicles",
        ["plate_number"]
    )
    op.create_unique_constraint(
        "vehicles_color_key",
        "vehicles",
        ["color"]
    )
