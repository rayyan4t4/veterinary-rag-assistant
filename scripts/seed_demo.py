"""Creates non-clinical UI seed data only. It never indexes veterinary claims."""
import asyncio
from apps.api.app.db import SessionLocal, engine
from apps.api.app.models import Animal, Base, Species
async def main():
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        db.add(Animal(owner_id="00000000-0000-0000-0000-000000000001",name="Demo Animal",species=Species.dog,breed="Mixed breed",notes="Synthetic profile for interface testing only.")); await db.commit()
if __name__=="__main__": asyncio.run(main())
