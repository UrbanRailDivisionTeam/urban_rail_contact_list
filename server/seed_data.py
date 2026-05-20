"""Generate ~3000 test rows into dwd.person_organization / _position / _employee."""
import random
import uuid
from datetime import datetime, timedelta

import clickhouse_connect

CH_HOST = "localhost"
CH_PORT = 8123
CH_USER = "cheakf"
CH_PASSWORD = "Swq8855830."

SEED = 42
random.seed(SEED)

NOW = datetime(2026, 5, 20, 10, 0, 0)

CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS dwd.person_organization
    (
        zid           String,
        "最后修改时间"  String,
        "简称"         String,
        "HCM_HID"      String,
        "组织编码"      String,
        "组织名称"      String,
        "起始时间"      String,
        "终止时间"      String,
        "等级"          Int32,
        "缩写"         String,
        "组织层级"      String,
        "组织层级名称"  String,
        "介绍"         String,
        "备注"         String,
        "上级组织ID"    String,
        "所属组织路径"  String,
        "index"        Int32,
        "组织状态"      String
    )
    ENGINE = MergeTree()
    ORDER BY (zid)
    """,
    """
    CREATE TABLE IF NOT EXISTS dwd.person_position
    (
        zid              String,
        "上次更新时间"     String,
        "HCM_OID"         String,
        "职位编码"         String,
        "职位名称"         String,
        "所属组织ID"       String,
        "所属组织名称"     String,
        "上级职位ID"       String,
        "起始时间"         String,
        "终止时间"         String,
        "职群编号"         String,
        "职群"            String,
        "职类编号"         String,
        "职类"            String,
        "职种编号"         String,
        "所属职种"         String,
        "最低职级编码"     String,
        "最低职级"         String,
        "最高职级编码"     String,
        "最高职级"         String,
        "工作地点"         String,
        "工作内容"         String,
        "职位体系"         String,
        "是否为当前组织主管者" String,
        "数据状态"         String
    )
    ENGINE = MergeTree()
    ORDER BY (zid)
    """,
    """
    CREATE TABLE IF NOT EXISTS dwd.person_employee
    (
        zid              String,
        "最后修改时间"     String,
        "HCM对象ID_ek"    String,
        "工号"            String,
        "姓名"            String,
        "身份证号"        String,
        "生日"            String,
        "政治面貌"        String,
        "邮箱"            String,
        "身份"            String,
        "手机号"          String,
        "参加工作时间"     String,
        "任职状态"        String,
        "所属组织ID"      String,
        "所属职位ID"      String,
        "性别"            String,
        "学历"            String,
        "学位"            String
    )
    ENGINE = MergeTree()
    ORDER BY (zid)
    """,
]

# ---------------------------------------------------------------------------
# data pools
# ---------------------------------------------------------------------------
SURNAMES = [
    "张", "李", "王", "赵", "刘", "陈", "杨", "黄", "周", "吴",
    "徐", "孙", "马", "朱", "胡", "郭", "何", "高", "林", "罗",
    "郑", "梁", "谢", "宋", "唐", "韩", "曹", "许", "邓", "冯",
    "彭", "曾", "肖", "田", "董", "潘", "袁", "蔡", "蒋", "余",
    "于", "杜", "叶", "程", "苏", "魏", "吕", "丁", "任", "沈",
]
GIVEN_MALE = [
    "伟", "强", "磊", "洋", "鹏", "超", "涛", "峰", "明", "辉",
    "刚", "亮", "军", "勇", "杰", "文", "斌", "龙", "飞", "平",
    "建", "国", "华", "志", "新", "海", "波", "宁", "鑫", "博",
]
GIVEN_FEMALE = [
    "芳", "娜", "静", "敏", "婷", "丽", "燕", "娟", "琳", "莹",
    "红", "悦", "怡", "睿", "雪", "梅", "兰", "竹", "菊", "琴",
    "慧", "云", "霞", "丹", "洁", "思", "雨", "雯", "琪", "佳",
]
POSITIONS = [
    "总监", "副总监", "经理", "副经理", "组长", "副组长",
    "高级工程师", "工程师", "助理工程师", "技术员",
    "安全员", "质量员", "文员", "专员", "调度员",
]
PLATES = [
    ("PLATE-001", "通信板块", "TX"),
    ("PLATE-002", "信号板块", "XH"),
    ("PLATE-003", "综合板块", "ZH"),
    ("PLATE-004", "供电板块", "GD"),
    ("PLATE-005", "车辆板块", "CL"),
    ("PLATE-006", "安质板块", "AZ"),
]
GROUPS = [
    ("通信板块", "传输组", "TX-CS"),
    ("通信板块", "无线组", "TX-WX"),
    ("通信板块", "交换组", "TX-JH"),
    ("通信板块", "数据组", "TX-SJ"),
    ("通信板块", "网管组", "TX-WG"),
    ("信号板块", "联锁组", "XH-LS"),
    ("信号板块", "ATP组", "XH-ATP"),
    ("信号板块", "ATO组", "XH-ATO"),
    ("信号板块", "ATS组", "XH-ATS"),
    ("信号板块", "DCS组", "XH-DCS"),
    ("综合板块", "综合组", "ZH-ZH"),
    ("综合板块", "行政组", "ZH-XZ"),
    ("综合板块", "人事组", "ZH-RS"),
    ("综合板块", "财务组", "ZH-CW"),
    ("供电板块", "变电组", "GD-BD"),
    ("供电板块", "接触网组", "GD-JC"),
    ("供电板块", "电力监控组", "GD-DJ"),
    ("供电板块", "电缆组", "GD-DL"),
    ("车辆板块", "检修组", "CL-JX"),
    ("车辆板块", "调试组", "CL-TS"),
    ("车辆板块", "轮轴组", "CL-LZ"),
    ("车辆板块", "电气组", "CL-DQ"),
    ("车辆板块", "机械组", "CL-JQ"),
    ("安质板块", "安全组", "AZ-AQ"),
    ("安质板块", "质量组", "AZ-ZL"),
    ("安质板块", "环保组", "AZ-HB"),
    ("安质板块", "培训组", "AZ-PX"),
]
PHONE_PREFIXES = ["138", "139", "137", "136", "135", "134", "159", "158", "188", "186"]

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _dt_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def _name(gender: int) -> str:
    return random.choice(SURNAMES) + (
        random.choice(GIVEN_MALE) if gender == 1 else random.choice(GIVEN_FEMALE)
    )

def _phone(i: int) -> str:
    return random.choice(PHONE_PREFIXES) + f"{random.randint(10000000, 99999999)}"

def _id_card() -> str:
    area = f"{random.randint(110000, 659000)}"
    birth = f"19{random.randint(60, 99):02d}{random.randint(1, 12):02d}{random.randint(1, 28):02d}"
    tail = f"{random.randint(1000, 9999)}"
    return area + birth + tail

# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------
def generate() -> None:
    client = clickhouse_connect.get_client(
        host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASSWORD
    )

    # --- 0. Create tables ---
    print("Creating database and tables ...")
    client.command("CREATE DATABASE IF NOT EXISTS dwd")
    for sql in CREATE_TABLES_SQL:
        client.command(sql)
    print("  -> tables ready")

    # --- 1. Organizations (plate + group, ~32 rows) ---
    print("Inserting organizations ...")
    all_orgs: list[dict] = []
    # plate-level orgs
    for pid, pname, abbr in PLATES:
        all_orgs.append({
            "zid": pid,
            "最后修改时间": _dt_str(NOW),
            "简称": pname,
            "HCM_HID": f"HID-{abbr}",
            "组织编码": f"ORG-{abbr}",
            "组织名称": pname,
            "起始时间": _dt_str(NOW - timedelta(days=2000)),
            "终止时间": "2099-12-31 00:00:00",
            "等级": 1,
            "缩写": abbr,
            "组织层级": "1",
            "组织层级名称": "板块",
            "介绍": f"{pname}介绍",
            "备注": "",
            "上级组织ID": "",
            "所属组织路径": f"城轨制造中心/{pname}",
            "index": 0,
            "组织状态": "启用",
        })

    # group-level orgs
    for plate_name, group_name, abbr in GROUPS:
        plate_id = next(pid for pid, pn, _ in PLATES if pn == plate_name)
        all_orgs.append({
            "zid": f"ORG-{abbr}",
            "最后修改时间": _dt_str(NOW),
            "简称": group_name,
            "HCM_HID": f"HID-{abbr}",
            "组织编码": f"ORG-{abbr}",
            "组织名称": group_name,
            "起始时间": _dt_str(NOW - timedelta(days=1500)),
            "终止时间": "2099-12-31 00:00:00",
            "等级": 2,
            "缩写": abbr,
            "组织层级": "2",
            "组织层级名称": "组室",
            "介绍": f"{group_name}介绍",
            "备注": "",
            "上级组织ID": plate_id,
            "所属组织路径": f"城轨制造中心/{plate_name}/{group_name}",
            "index": 0,
            "组织状态": "启用",
        })

    org_rows = []
    for o in all_orgs:
        org_rows.append([
            o["zid"], o["最后修改时间"], o["简称"], o["HCM_HID"],
            o["组织编码"], o["组织名称"], o["起始时间"], o["终止时间"],
            o["等级"], o["缩写"], o["组织层级"], o["组织层级名称"],
            o["介绍"], o["备注"], o["上级组织ID"], o["所属组织路径"],
            o["index"], o["组织状态"],
        ])
    client.insert("dwd.person_organization", org_rows,
                  column_names=[
                      "zid", "最后修改时间", "简称", "HCM_HID",
                      "组织编码", "组织名称", "起始时间", "终止时间",
                      "等级", "缩写", "组织层级", "组织层级名称",
                      "介绍", "备注", "上级组织ID", "所属组织路径",
                      "index", "组织状态",
                  ])
    print(f"  -> {len(org_rows)} orgs inserted")

    # --- 2. Positions (~80 rows, 2-3 per group) ---
    print("Inserting positions ...")
    all_positions: list[dict] = []
    pos_idx = 0
    # Only assign positions to group-level orgs (not the plate-level ones)
    group_orgs = [o for o in all_orgs if o["等级"] == 2]
    for org in group_orgs:
        # 2-3 unique positions per group
        n_pos = random.randint(2, 3)
        picked = random.sample(POSITIONS, n_pos)
        for pos_name in picked:
            pos_idx += 1
            pid = f"POS-{pos_idx:04d}"
            all_positions.append({
                "zid": pid,
                "上次更新时间": _dt_str(NOW),
                "HCM_OID": str(uuid.uuid4()),
                "职位编码": f"POS-CODE-{pos_idx:04d}",
                "职位名称": pos_name,
                "所属组织ID": org["zid"],
                "所属组织名称": org["组织名称"],
                "上级职位ID": "",
                "起始时间": _dt_str(NOW - timedelta(days=1000)),
                "终止时间": "2099-12-31 00:00:00",
                "职群编号": "",
                "职群": "",
                "职类编号": "",
                "职类": "",
                "职种编号": "",
                "所属职种": "",
                "最低职级编码": "",
                "最低职级": "",
                "最高职级编码": "",
                "最高职级": "",
                "工作地点": "城轨制造中心",
                "工作内容": f"负责{org['组织名称']}的{pos_name}工作",
                "职位体系": "技术序列",
                "是否为当前组织主管者": "否",
                "数据状态": "启用",
            })

    pos_rows = []
    for p in all_positions:
        pos_rows.append([
            p["zid"], p["上次更新时间"], p["HCM_OID"], p["职位编码"],
            p["职位名称"], p["所属组织ID"], p["所属组织名称"],
            p["上级职位ID"], p["起始时间"], p["终止时间"],
            p["职群编号"], p["职群"], p["职类编号"], p["职类"],
            p["职种编号"], p["所属职种"],
            p["最低职级编码"], p["最低职级"],
            p["最高职级编码"], p["最高职级"],
            p["工作地点"], p["工作内容"], p["职位体系"],
            p["是否为当前组织主管者"], p["数据状态"],
        ])
    client.insert("dwd.person_position", pos_rows,
                  column_names=[
                      "zid", "上次更新时间", "HCM_OID", "职位编码",
                      "职位名称", "所属组织ID", "所属组织名称",
                      "上级职位ID", "起始时间", "终止时间",
                      "职群编号", "职群", "职类编号", "职类",
                      "职种编号", "所属职种",
                      "最低职级编码", "最低职级",
                      "最高职级编码", "最高职级",
                      "工作地点", "工作内容", "职位体系",
                      "是否为当前组织主管者", "数据状态",
                  ])
    print(f"  -> {len(pos_rows)} positions inserted")

    # --- 3. Employees (3000) ---
    print("Inserting employees ...")
    emp_rows = []
    for i in range(3000):
        gender = random.choice([1, 2])  # 1=男, 2=女
        pos = random.choice(all_positions)
        # find which group org this position belongs to
        org_id = pos["所属组织ID"]
        # find the group-level org
        org = next(o for o in all_orgs if o["zid"] == org_id)
        plate_id = org["上级组织ID"]
        emp_id = f"EMP-{i+1:05d}"

        emp_rows.append([
            f"EMP-ZID-{i+1:05d}",
            _dt_str(NOW - timedelta(days=random.randint(1, 1000))),
            str(uuid.uuid4()),
            emp_id,
            _name(gender),
            _id_card(),
            f"199{random.randint(0, 9)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            random.choice(["中共党员", "共青团员", "群众", "民主党派"]),
            f"{emp_id.lower()}@urban-rail.com",
            random.choice(["正式员工", "合同工", "实习生"]),
            _phone(i),
            _dt_str(NOW - timedelta(days=random.randint(365, 5000))),
            random.choice(["在职", "在职", "在职", "试用期"]),
            org_id,
            pos["zid"],
            "男" if gender == 1 else "女",
            random.choice(["本科", "硕士", "博士", "大专"]),
            random.choice(["学士", "硕士", "博士"]),
        ])

    client.insert("dwd.person_employee", emp_rows,
                  column_names=[
                      "zid", "最后修改时间", "HCM对象ID_ek", "工号",
                      "姓名", "身份证号", "生日", "政治面貌",
                      "邮箱", "身份", "手机号", "参加工作时间",
                      "任职状态", "所属组织ID", "所属职位ID",
                      "性别", "学历", "学位",
                  ])
    print(f"  -> {len(emp_rows)} employees inserted")

    print("\nAll done!")


if __name__ == "__main__":
    generate()
