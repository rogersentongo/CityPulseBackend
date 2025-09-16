#!/usr/bin/env python3
"""Create MongoDB indexes and print Atlas Vector Search configuration."""
import asyncio
import json
import sys

from app.config import settings
from app.dao import DatabaseOperations
from app.deps import db_manager


async def create_indexes():
    """Create all MongoDB indexes."""
    print("🗄️  CityPulse Database Index Setup")
    print("=" * 40)

    try:
        # Connect to database
        print("Connecting to MongoDB Atlas...")
        await db_manager.connect()
        db = db_manager.get_database()

        # Create indexes
        print("\n📊 Creating database indexes...")
        db_ops = DatabaseOperations(db)
        results = await db_ops.create_indexes()

        # Report results
        print("\nIndex Creation Results:")
        print("-" * 25)
        for index_name, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {index_name}")

        # Check if all succeeded
        success_count = sum(results.values())
        total_count = len(results)

        if success_count == total_count:
            print(f"\n🎉 All {total_count} indexes created successfully!")
        else:
            print(f"\n⚠️  {success_count}/{total_count} indexes created successfully")

        print("\n" + "=" * 50)
        print("🔍 MongoDB Atlas Vector Search Index Configuration")
        print("=" * 50)

        # Atlas Vector Search index configuration
        vector_search_config = {
            "name": "embedding_index",
            "type": "vectorSearch",
            "definition": {
                "mappings": {
                    "dynamic": False,
                    "fields": {
                        "embedding": {
                            "type": "knnVector",
                            "dimensions": 1536,
                            "similarity": "cosine"
                        },
                        "borough": {
                            "type": "string"
                        },
                        "created_at": {
                            "type": "date"
                        },
                        "tags": {
                            "type": "string"
                        }
                    }
                }
            }
        }

        print("\n📋 Copy this configuration to MongoDB Atlas:")
        print("   1. Go to Atlas → Your Cluster → Search")
        print("   2. Click 'Create Search Index'")
        print("   3. Choose 'JSON Editor'")
        print("   4. Select database: 'citypulse', collection: 'videos'")
        print("   5. Paste the following configuration:")
        print("\n" + "-" * 50)
        print(json.dumps(vector_search_config, indent=2))
        print("-" * 50)

        print("\n💡 Vector Search Index Setup:")
        print("   • Index Name: embedding_index")
        print("   • Vector Dimensions: 1536 (text-embedding-3-small)")
        print("   • Similarity: cosine")
        print("   • Filterable Fields: borough, created_at, tags")

        print("\n🚀 Once the index is created, your vector search will be active!")
        print("   The index typically takes 2-5 minutes to build.")

        return True

    except Exception as e:
        print(f"\n❌ Error during index creation: {e}")
        return False

    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    success = asyncio.run(create_indexes())
    sys.exit(0 if success else 1)