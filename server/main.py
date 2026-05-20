from typing import Any
import traceback

import clickhouse_connect
import clickhouse_connect.driver
from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from litestar.static_files import StaticFilesConfig

CH_HOST = "localhost"
CH_PORT = 8123
CH_USER = "cheakf"
CH_PASSWORD = "Swq8855830."


def _ch() -> clickhouse_connect.driver.Client:
    return clickhouse_connect.get_client(
        host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASSWORD
    )


def _load_org_hierarchy(
    client: clickhouse_connect.driver.Client,
) -> dict[str, dict[str, Any]]:
    """Return dict[org_id -> {name, parent_id, level}] for all orgs."""
    rows = client.query(
        """
        SELECT zid, "组织名称", "上级组织ID", "等级"
        FROM dwd.person_organization
        WHERE "组织状态" = '启用'
        """
    )
    orgs: dict[str, dict[str, Any]] = {}
    for row in rows.named_results():
        orgs[str(row["zid"])] = {
            "name": row["组织名称"] or "",
            "parent_id": str(row["上级组织ID"]) if row["上级组织ID"] else "",
            "level": row["等级"] or 0,
        }
    return orgs


def _resolve_org_display(
    org_id: str,
    orgs: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    """Walk up the org tree; return (plate, group)."""
    chain: list[str] = []
    current = org_id
    visited: set[str] = set()
    while current and current not in visited and current in orgs:
        visited.add(current)
        chain.append(orgs[current]["name"])
        current = orgs[current]["parent_id"]

    # chain[0] = the employee's immediate org
    # chain[-1] = top-level org (plate)
    if len(chain) >= 3:
        plate = chain[-1]
        group = chain[1]
    elif len(chain) == 2:
        plate = chain[1]
        group = chain[0]
    else:
        plate = chain[0] if chain else ""
        group = ""

    return plate, group


@get("/api/contacts", sync_to_thread=False)
def get_contacts() -> list[dict[str, str]]:
    try:
        client = _ch()

        orgs = _load_org_hierarchy(client)

        rows = client.query(
            """
            SELECT
                e.zid AS zid,
                e."工号" AS employee_id,
                e."姓名" AS name,
                e."手机号" AS phone,
                COALESCE(p."职位名称", '') AS position,
                e."所属组织ID" AS org_id
            FROM dwd.person_employee e
            LEFT JOIN dwd.person_position p ON e."所属职位ID" = p.zid
            WHERE e."手机号" != ''
            ORDER BY e.zid
            """
        )

        contacts: list[dict[str, str]] = []
        for row in rows.named_results():
            org_id = str(row["org_id"]) if row["org_id"] else ""
            plate, group = _resolve_org_display(org_id, orgs)

            contacts.append(
                {
                    "id": str(row["zid"]),
                    "plate": plate,
                    "group": group,
                    "position": row["position"] or "",
                    "name": row["name"] or "",
                    "employeeId": row["employee_id"] or "",
                    "phone": row["phone"] or "",
                }
            )

        return contacts
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
    uvicorn.run("main:app", host="::", port=12379)