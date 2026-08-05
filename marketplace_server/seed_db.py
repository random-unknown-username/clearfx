import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models import Creator, Design, DesignVersion, Base

DB_PATH = "sqlite+aiosqlite:///data/marketplace.db"
engine = create_async_engine(DB_PATH)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        from sqlalchemy.future import select
        res = await session.execute(select(Creator).limit(1))
        if res.scalars().first():
            print("Already seeded.")
            return

        # Create creators
        c1 = Creator(handle="@mira", display_name="Mira", is_verified=True, api_key_hash="123")
        c2 = Creator(handle="@echo", display_name="Echo", is_verified=False, api_key_hash="123")
        c3 = Creator(handle="@nexus", display_name="Nexus", is_verified=True, api_key_hash="123")
        c4 = Creator(handle="@void", display_name="Void Walker", is_verified=False, api_key_hash="123")
        c5 = Creator(handle="@synth", display_name="Synth", is_verified=True, api_key_hash="123")
        
        session.add_all([c1, c2, c3, c4, c5])
        await session.flush()
        
        # Create designs (some referencing the builtins for previewing)
        # We will set their slugs to match the builtin slugs so the preview works magically
        designs = [
            ("aurora-fold", "Aurora Fold", "Mesmerizing geometric folding patterns.", c1, ["geometry", "math", "chill"]),
            ("plasma-drift", "Plasma Drift", "Fluid dynamics and plasma simulation.", c1, ["fluid", "plasma", "colorful"]),
            ("neon-rain", "Neon Rain", "Matrix-style digital rain with neon colors.", c2, ["matrix", "rain", "retro"]),
            ("cyber-grid", "Cyber Grid", "3D perspective grid moving forward.", c2, ["3d", "grid", "synthwave"]),
            ("particle-swarm", "Particle Swarm", "Boids simulation with colorful trails.", c3, ["particles", "boids", "swarm"]),
            ("quantum-foam", "Quantum Foam", "Cellular automata generating quantum-like noise.", c3, ["cellular", "noise"]),
            ("binary-tree", "Binary Tree", "Fractal tree growth animation.", c4, ["fractal", "nature"]),
            ("hyperspace", "Hyperspace", "Starfield warp effect.", c4, ["space", "stars", "fast"]),
            ("dna-helix", "DNA Helix", "Rotating double helix.", c5, ["biology", "3d", "spin"]),
            ("wave-function", "Wave Function", "Interfering sine waves.", c5, ["math", "waves"]),
            ("fire-works", "Fireworks", "Exploding particle fireworks.", c1, ["particles", "celebration"]),
            ("black-hole", "Black Hole", "Accretion disk simulation.", c2, ["space", "physics"]),
            ("game-of-life", "Game of Life", "Conway's Game of Life.", c3, ["cellular", "classic"]),
            ("maze-gen", "Maze Generation", "Recursive backtracking maze.", c4, ["algorithm", "maze"]),
            ("sorting-vis", "Sorting Visualizer", "Visualizes quicksort.", c5, ["algorithm", "sort"]),
            ("mandelbrot", "Mandelbrot Zoom", "Deep zoom into the Mandelbrot set.", c1, ["fractal", "math"]),
            ("tesseract", "Tesseract", "Rotating 4D hypercube.", c2, ["4d", "geometry"]),
            ("liquid-metal", "Liquid Metal", "Metaballs animation.", c3, ["fluid", "metaballs"]),
            ("ascii-donut", "ASCII Donut", "The classic spinning 3D donut.", c4, ["3d", "classic"]),
            ("matrix-code", "Matrix Code", "Green dropping characters.", c5, ["matrix", "retro"])
        ]
        
        for slug, name, desc, creator, tags in designs:
            d = Design(
                creator_id=creator.id,
                slug=slug,
                name=name,
                description=desc,
                current_version="1.0.0",
                package_hash="mock",
                package_size=1024,
                tags=tags,
                download_count=100 + len(name)*10,
                favorite_count=50 + len(name)
            )
            session.add(d)
            
        await session.commit()
        print("Database seeded with 20 community animations.")

if __name__ == "__main__":
    asyncio.run(seed())
