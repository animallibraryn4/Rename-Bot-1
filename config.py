import os



# Required Variables Config
API_ID = int(os.environ.get("API_ID", "22299340"))
API_HASH = os.environ.get("API_HASH", "09b09f3e2ff1306da4a19888f614d937")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN = int(os.environ.get("ADMIN", "5380609667"))


# Premium 4GB Renaming Client Config
STRING_SESSION = os.environ.get("STRING_SESSION", "")


# Log & Force Channel Config
FORCE_SUBS = os.environ.get("FORCE_SUBS", "")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001896877147"))


# Mongo DB Database Config
DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://mikota4432:jkJDQuZH6o8pxxZe@cluster0.2vngilq.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "TechifyBots")


# Other Variables Config
START_PIC = os.environ.get("START_PIC", "https://graph.org/file/ada3f739fed7efdbe7b08.jpg")
