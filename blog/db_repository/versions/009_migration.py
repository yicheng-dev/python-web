from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
migration_tmp = Table('migration_tmp', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('timestamp', DATETIME),
    Column('disabled', BOOLEAN),
    Column('author_id', INTEGER),
    Column('post_id', INTEGER),
)

comments = Table('comments', post_meta,
    Column('author_id', Integer),
    Column('post_id', Integer),
)

comment = Table('comment', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('body', TEXT),
    Column('body_html', TEXT),
    Column('timestamp', DATETIME),
    Column('disabled', BOOLEAN),
    Column('author_id', INTEGER),
    Column('post_id', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['migration_tmp'].drop()
    post_meta.tables['comments'].create()
    pre_meta.tables['comment'].columns['author_id'].drop()
    pre_meta.tables['comment'].columns['post_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['migration_tmp'].create()
    post_meta.tables['comments'].drop()
    pre_meta.tables['comment'].columns['author_id'].create()
    pre_meta.tables['comment'].columns['post_id'].create()
