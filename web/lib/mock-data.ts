export interface Contact {
    id: string
    department: string
    group: string
    position: string
    name: string
    employeeId: string
    phone: string
}

const surnames = [
    "张",
    "李",
    "王",
    "赵",
    "刘",
    "陈",
    "杨",
    "黄",
    "周",
    "吴",
    "徐",
    "孙",
    "马",
    "朱",
    "胡",
    "郭",
    "何",
    "高",
    "林",
    "罗",
    "郑",
    "梁",
    "谢",
    "宋",
    "唐",
    "韩",
    "曹",
    "许",
    "邓",
    "冯",
    "彭",
    "曾",
    "肖",
    "田",
    "董",
    "潘",
    "袁",
    "蔡",
    "蒋",
    "余",
    "于",
    "杜",
    "叶",
    "程",
    "苏",
    "魏",
    "吕",
    "丁",
    "任",
    "沈",
]

const givenNames = [
    "伟",
    "芳",
    "娜",
    "静",
    "敏",
    "婷",
    "强",
    "磊",
    "洋",
    "鹏",
    "超",
    "涛",
    "峰",
    "明",
    "辉",
    "刚",
    "冰",
    "丽",
    "燕",
    "娟",
    "琳",
    "莹",
    "红",
    "亮",
    "军",
    "勇",
    "杰",
    "文",
    "斌",
    "龙",
    "飞",
    "平",
    "建",
    "国",
    "华",
    "志",
    "新",
    "海",
    "波",
    "宁",
    "鑫",
    "博",
    "浩",
    "宇",
    "晨",
    "曦",
    "悦",
    "怡",
    "睿",
    "翔",
]

const positions = [
    "总监",
    "副总监",
    "经理",
    "副经理",
    "组长",
    "副组长",
    "高级工程师",
    "工程师",
    "助理工程师",
    "技术员",
    "安全员",
    "质量员",
    "文员",
    "专员",
    "调度员",
]

const departmentGroups: Record<string, string[]> = {
    通信部门: ["传输组", "无线组", "交换组", "数据组", "网管组", "动力组"],
    信号部门: ["联锁组", "ATP组", "ATO组", "ATS组", "DCS组", "维护组"],
    综合部门: ["综合组", "行政组", "人事组", "财务组"],
    供电部门: ["变电组", "接触网组", "电力监控组", "电缆组"],
    车辆部门: ["检修组", "调试组", "轮轴组", "电气组", "机械组"],
    安质部门: ["安全组", "质量组", "环保组", "培训组"],
}

const departments = Object.keys(departmentGroups)

function randomItem<T>(arr: T[]): T {
    return arr[Math.floor(Math.random() * arr.length)]
}

function generatePhone(index: number): string {
    const prefixes = ["138", "139", "137", "136", "135", "134", "159", "158", "188", "186"]
    const prefix = prefixes[index % prefixes.length]
    const suffix = String(index + 10000).slice(-5)
    return prefix + "0" + suffix
}

function generateEmployeeId(deptIndex: number, index: number): string {
    const prefix = String.fromCharCode(65 + deptIndex) // A, B, C...
    const num = String(10000 + index).slice(-5)
    return prefix + num
}

function generateAllContacts(count: number): Contact[] {
    const result: Contact[] = []

    for (let i = 0; i < count; i++) {
        const department = departments[i % departments.length]
        const groups = departmentGroups[department]
        const group = groups[Math.floor((i / departments.length) % groups.length)]
        const surname = surnames[i % surnames.length]
        const given = givenNames[Math.floor(i / surnames.length) % givenNames.length]
        const name = surname + given
        const position = positions[i % positions.length]
        const deptIndex = departments.indexOf(department)
        const employeeId = generateEmployeeId(deptIndex, i)
        const phone = generatePhone(i)

        result.push({
            id: String(i + 1),
            department,
            group,
            position,
            name,
            employeeId,
            phone,
        })
    }

    return result
}

export const contacts: Contact[] = generateAllContacts(3000)
