import hashlib
import json
import os
from contextlib import closing
from typing import Annotated

import mysql.connector
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Business Listings")


class Listing(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    business_name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=500)
    phone: str | None = Field(default=None, max_length=60)
    source: str = Field(min_length=1, max_length=100)


def connect():
    return mysql.connector.connect(host="db", database="honeybee", user="dashboard",
                                   password=os.environ["MYSQL_PASSWORD"])


@app.post("/api/listings")
def insert(listings: Annotated[list[Listing], Field(min_length=1, max_length=1000)]):
    rows = []
    for item in listings:
        identity = [s.casefold() for s in (item.source, item.business_name, item.city, item.address)]
        key = hashlib.sha256(json.dumps(identity).encode()).digest()
        rows.append((item.business_name, item.category, item.city, item.address,
                     item.phone, item.source, key))
    with closing(connect()) as db, closing(db.cursor()) as cursor:
        cursor.executemany("""
            INSERT INTO listing_master (business_name, category, city, address, phone, source, identity_hash)
            VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE id=listing_master.id
        """, rows)
        inserted = cursor.rowcount
        db.commit()
    return {"received": len(rows), "inserted": inserted}


@app.get("/api/dashboard")
def dashboard():
    reports = {}
    with closing(connect()) as db, closing(db.cursor(dictionary=True)) as cursor:
        for column in ("city", "category", "source"):
            cursor.execute(f"SELECT {column} AS label, COUNT(*) AS count FROM listing_master "
                           f"GROUP BY {column} ORDER BY count DESC, label")
            reports[column] = cursor.fetchall()
    return reports
