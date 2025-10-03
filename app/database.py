"""
Database operations for Crypto News API
"""
import os
import psycopg2
import psycopg2.extras
from typing import List, Optional
from fastapi import HTTPException


def get_db_connection():
    """Get database connection using environment variables"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB", "crypto_news"),
        user=os.getenv("POSTGRES_USER", "crypto_user"),
        password=os.getenv("POSTGRES_PASSWORD", "crypto_password"),
    )


def save_to_database(results: List[dict]) -> bool:
    """Save news items to PostgreSQL database using direct connection"""
    try:
        print("🔄 Saving data to database via direct connection...")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        items_saved = 0
        for item in results:
            try:
                # Use parameterized query to prevent SQL injection
                sql = """
                INSERT INTO news_items (
                    external_id, slug, title, description, 
                    published_at, created_at, kind
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (external_id) DO NOTHING;
                """
                
                values = (
                    item.get('id'),
                    item.get('slug', ''),
                    item.get('title', ''),
                    item.get('description', ''),
                    item.get('published_at', ''),
                    item.get('created_at', ''),
                    item.get('kind', '')
                )
                
                cur.execute(sql, values)
                if cur.rowcount > 0:
                    items_saved += 1
                    
            except Exception as e:
                print(f"❌ Error inserting item {item.get('id')}: {e}")
                continue
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Successfully saved {items_saved}/{len(results)} news items to database")
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def get_news_from_database(start: Optional[str] = None, end: Optional[str] = None) -> List[dict]:
    """
    Fetch news items from PostgreSQL using psycopg2.
    Optionally filter by published_at between start and end (ISO8601 strings).
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Build the query with placeholders to prevent SQL injection
        sql = """
            SELECT
                external_id AS id,
                slug,
                title,
                description,
                published_at,
                created_at,
                kind
            FROM news_items
        """
        params = []
        conditions = []
        if start:
            conditions.append("published_at >= %s")
            params.append(start)
        if end:
            conditions.append("published_at <= %s")
            params.append(end)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY published_at DESC LIMIT 100;"

        cur.execute(sql, params)
        rows = cur.fetchall()

        # Convert rows to a list of dicts
        news_items = []
        for row in rows:
            news_items.append({
                "id": row["id"],
                "slug": row["slug"],
                "title": row["title"],
                "description": row["description"],
                "published_at": row["published_at"].isoformat() if row["published_at"] else "",
                "created_at": row["created_at"].isoformat() if row["created_at"] else "",
                "kind": row["kind"]
            })

        cur.close()
        conn.close()

        return news_items

    except Exception as e:
        print(f"❌ Error in get_news_from_database: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching news from database: {e}")