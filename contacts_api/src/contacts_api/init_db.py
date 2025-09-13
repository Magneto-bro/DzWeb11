from contacts_api.database import Base, engine
from contacts_api import models

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
