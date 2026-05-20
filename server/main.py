import time
import traceback

import clickhouse_connect
import clickhouse_connect.driver
from litestar import Litestar, get, Request
from litestar.config.cors import CORSConfig
from litestar.static_files import StaticFilesConfig

# CH_HOST = "localhost"
CH_HOST = "10.24.5.59"
CH_PORT = 8123
CH_USER = "cheakf"
CH_PASSWORD = "Swq8855830."


def _ch() -> clickhouse_connect.driver.Client:
    return clickhouse_connect.get_client(
        host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASSWORD
    )


CACHE_TTL = 5  # seconds

_cache: dict = {"data": None, "ts": 0.0}


def _fetch_contacts() -> list[dict[str, str]]:
    client = _ch()

    rows = client.query("""
        SELECT
            e.zid AS zid,
            e."工号" AS employee_id,
            e."姓名" AS name,
            e."手机号" AS phone,
            COALESCE(p."职位名称", '') AS position,
            org."组织名称" AS group_name,
            COALESCE(parent_org."组织名称", '') AS department
        FROM dwd.person_employee e
        LEFT JOIN dwd.person_position p
            ON e."所属职位ID" = p.zid
        LEFT JOIN dwd.person_organization org
            ON e."所属组织ID" = org.zid
            AND org."组织状态" = '启用'
        LEFT JOIN dwd.person_organization parent_org
            ON org."上级组织ID" = parent_org.zid
            AND parent_org."组织状态" = '启用'
        WHERE org.zid IS NOT NULL
            AND E."任职状态" = '正式'
        ORDER BY e.zid
    """)

    contacts: list[dict[str, str]] = []
    for row in rows.named_results():
        contacts.append({
            "id": str(row["zid"]),
            "department": row["department"] or "",
            "group": row["group_name"] or "",
            "position": row["position"] or "",
            "name": row["name"] or "",
            "employeeId": row["employee_id"] or "",
            "phone": row["phone"] or "",
        })

    return contacts


@get("/api/contacts", sync_to_thread=False)
def get_contacts(request: Request) -> list[dict[str, str]]:
    try:
        force = request.query_params.get("refresh") == "1"

        if not force and _cache["data"] is not None and time.time() - _cache["ts"] < CACHE_TTL:
            return _cache["data"]

        data = _fetch_contacts()
        _cache["data"] = data
        _cache["ts"] = time.time()
        return data
    except Exception:
        traceback.print_exc()
        return []


cors_config = CORSConfig(
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    allow_credentials=False,
)

app = Litestar(
    route_handlers=[get_contacts],
    cors_config=cors_config,
    static_files_config=[
        StaticFilesConfig(
            path="/static",
            directories=["static"],
            name="static",
            html_mode=True,
        )
    ],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="", port=12379)
