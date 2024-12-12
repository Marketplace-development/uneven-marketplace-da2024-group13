"""class Config:
    SECRET_KEY = 'Group13.RallyUp'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.nbllnkdgvokizryvwqjs:Group13.RallyUp@aws-0-eu-central-1.pooler.supabase.com:6543/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False"""

import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres.nbllnkdgvokizryvwqjs:Group13.RallyUp@aws-0-eu-central-1.pooler.supabase.com:6543/postgres",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "Group13.RallyUp")
        

