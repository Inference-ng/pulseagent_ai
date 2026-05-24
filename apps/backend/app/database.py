"""Database Configuration — Prisma Client"""

from prisma import Prisma

# Global Prisma client instance
prisma = Prisma()


async def connect_db():
    """Connect to the database on startup"""
    await prisma.connect()
    print("✓ Database connected")


async def disconnect_db():
    """Disconnect from the database on shutdown"""
    await prisma.disconnect()
    print("✓ Disconnected from database")
