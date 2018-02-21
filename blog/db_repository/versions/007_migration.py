from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
message = Table('message', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('body', VARCHAR(length=200)),
    Column('timestamp', DATETIME),
    Column('sender_id', INTEGER),
    Column('receiver_id', INTEGER),
)

message = Table('message', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', String(length=200)),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['message'].columns['receiver_id'].drop()
    pre_meta.tables['message'].columns['sender_id'].drop()
    pre_meta.tables['message'].columns['timestamp'].drop()
    post_meta.tables['message'].columns['user_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['message'].columns['receiver_id'].create()
    pre_meta.tables['message'].columns['sender_id'].create()
    pre_meta.tables['message'].columns['timestamp'].create()
    post_meta.tables['message'].columns['user_id'].drop()
