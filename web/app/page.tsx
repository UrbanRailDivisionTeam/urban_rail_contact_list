"use client"

import { useState, useEffect } from "react"
import { useTheme } from "next-themes"
import {
    useReactTable,
    getCoreRowModel,
    getPaginationRowModel,
    getFilteredRowModel,
    getSortedRowModel,
    createColumnHelper,
    type FilterFn,
    type Column,
} from "@tanstack/react-table"
import { Search, ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown, Loader2, Sun, Moon } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { type Contact } from "@/lib/mock-data"
import { fetchContacts } from "@/lib/api"

const columnHelper = createColumnHelper<Contact>()

const columnDefs = [
    columnHelper.accessor("department", {
        header: "部门",
        cell: (info) => info.getValue(),
        filterFn: "includesString",
    }),
    columnHelper.accessor("group", {
        header: "组室",
        cell: (info) => info.getValue(),
        filterFn: "includesString",
    }),
    columnHelper.accessor("position", {
        header: "职务",
        cell: (info) => info.getValue(),
        filterFn: "includesString",
    }),
    columnHelper.accessor("name", {
        header: "姓名",
        cell: (info) => <span className="font-medium">{info.getValue()}</span>,
        filterFn: "includesString",
    }),
    columnHelper.accessor("employeeId", {
        header: "工号",
        cell: (info) => <span className="font-mono text-xs">{info.getValue()}</span>,
        filterFn: "includesString",
    }),
    columnHelper.accessor("phone", {
        header: "电话",
        cell: (info) => <span className="font-mono text-xs">{info.getValue()}</span>,
        filterFn: "includesString",
    }),
]

const globalFilterFn: FilterFn<Contact> = (row, _columnId, filterValue) => {
    const kw = String(filterValue).toLowerCase()
    const name = row.original.name.toLowerCase()
    const employeeId = row.original.employeeId.toLowerCase()
    return name.includes(kw) || employeeId.includes(kw)
}

const PAGE_SIZE = 30

function SortIcon({ column }: { column: Column<Contact, unknown> }) {
    const sorted = column.getIsSorted()
    if (!sorted) return <ArrowUpDown className="ml-1 size-3 text-muted-foreground/40" />
    if (sorted === "asc") return <ArrowUp className="ml-1 size-3" />
    return <ArrowDown className="ml-1 size-3" />
}

function PaginationBar({ table, totalFiltered }: { table: ReturnType<typeof useReactTable<Contact>>; totalFiltered: number }) {
    const pageIndex = table.getState().pagination.pageIndex
    const pageCount = table.getPageCount()
    const from = totalFiltered === 0 ? 0 : pageIndex * PAGE_SIZE + 1
    const to = Math.min((pageIndex + 1) * PAGE_SIZE, totalFiltered)

    return (
        <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div>
                显示 {from}–{to} / {totalFiltered} 条
            </div>
            <div className="flex items-center gap-2">
                <Button variant="outline" size="icon-sm" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>
                    <ChevronLeft className="size-3" />
                </Button>

                {generatePageNumbers(pageIndex, pageCount).map((p, i) =>
                    p === null ? (
                        <span key={`ellipsis-${i}`} className="px-1 text-xs">
                            ...
                        </span>
                    ) : (
                        <Button key={p} variant={p === pageIndex ? "default" : "outline"} size="icon-sm" onClick={() => table.setPageIndex(p)}>
                            {p + 1}
                        </Button>
                    )
                )}

                <Button variant="outline" size="icon-sm" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
                    <ChevronRight className="size-3" />
                </Button>
            </div>
        </div>
    )
}

export default function Page() {
    const { resolvedTheme, setTheme } = useTheme()
    const [data, setData] = useState<Contact[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        let cancelled = false
        async function load() {
            try {
                setLoading(true)
                setError(null)
                const contacts = await fetchContacts()
                if (!cancelled) {
                    setData(contacts)
                }
            } catch (err) {
                if (!cancelled) {
                    setError(err instanceof Error ? err.message : "加载失败")
                }
            } finally {
                if (!cancelled) {
                    setLoading(false)
                }
            }
        }
        load()
        return () => {
            cancelled = true
        }
    }, [])

    const table = useReactTable({
        data,
        columns: columnDefs,
        globalFilterFn,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        initialState: {
            pagination: {
                pageSize: PAGE_SIZE,
            },
        },
    })

    const totalFiltered = table.getFilteredRowModel().rows.length
    const totalAll = data.length
    const globalFilter = (table.getState().globalFilter as string) ?? ""
    const hasAnyFilter = globalFilter.length > 0 || table.getState().columnFilters.length > 0

    return (
        <div className="flex min-h-svh flex-col p-6">
            <div className="mb-6 flex items-center justify-between">
                <h1 className="text-xl font-semibold">城轨制造中心电话号码查询</h1>
                <Button variant="ghost" size="icon-sm" onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}>
                    {resolvedTheme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
                </Button>
            </div>

            {error ? (
                <div className="mb-4 rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                    加载失败：{error}
                    <button
                        className="ml-3 underline hover:no-underline"
                        onClick={() => {
                            setError(null)
                            setLoading(true)
                            fetchContacts()
                                .then(setData)
                                .catch((err) => setError(err instanceof Error ? err.message : "加载失败"))
                                .finally(() => setLoading(false))
                        }}
                    >
                        重试
                    </button>
                </div>
            ) : null}

            {loading ? (
                <div className="mb-4 flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="size-4 animate-spin" />
                    正在加载通讯录数据...
                </div>
            ) : null}

            <div className="relative mb-4 w-full max-w-sm">
                <Search className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input placeholder="输入姓名或工号快速查询..." value={globalFilter} onChange={(e) => table.setGlobalFilter(e.target.value)} className="pl-9" />
            </div>

            <div className="mb-2 text-xs text-muted-foreground">
                {hasAnyFilter ? `搜索到 ${totalFiltered} 条 / 共 ${totalAll} 条记录` : `共 ${totalAll} 条记录`}
            </div>

            <div className="mb-3">
                <PaginationBar table={table} totalFiltered={totalFiltered} />
            </div>

            <div className="flex-1 overflow-auto rounded-md border">
                <Table>
                    <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => (
                                    <TableHead key={header.id} className="px-4">
                                        <div
                                            className="flex cursor-pointer items-center font-semibold select-none hover:text-foreground"
                                            onClick={() => header.column.toggleSorting()}
                                        >
                                            {header.column.columnDef.header as string}
                                            <SortIcon column={header.column} />
                                        </div>
                                    </TableHead>
                                ))}
                            </TableRow>
                        ))}
                        <TableRow>
                            {columnDefs.map((col) => {
                                const columnId = col.accessorKey as string
                                const column = table.getColumn(columnId)
                                const filterValue = (column?.getFilterValue() as string) ?? ""
                                return (
                                    <TableHead key={`filter-${columnId}`} className="px-4 py-1">
                                        <Input
                                            placeholder={`筛选${col.header}`}
                                            value={filterValue}
                                            onChange={(e) => column?.setFilterValue(e.target.value)}
                                            className="h-7 text-xs"
                                        />
                                    </TableHead>
                                )
                            })}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={columnDefs.length} className="py-12 text-center text-muted-foreground">
                                    <Loader2 className="mx-auto mb-2 size-5 animate-spin" />
                                    正在加载中...
                                </TableCell>
                            </TableRow>
                        ) : table.getRowModel().rows.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={columnDefs.length} className="py-12 text-center text-muted-foreground">
                                    {error ? "数据加载失败，请重试" : "暂无数据"}
                                </TableCell>
                            </TableRow>
                        ) : (
                            table.getRowModel().rows.map((row) => (
                                <TableRow key={row.id}>
                                    {row.getVisibleCells().map((cell) => {
                                        const rendered = cell.column.columnDef.cell
                                        if (typeof rendered === "function") {
                                            return (
                                                <TableCell key={cell.id} className="px-4">
                                                    {rendered(cell.getContext())}
                                                </TableCell>
                                            )
                                        }
                                        return (
                                            <TableCell key={cell.id} className="px-4">
                                                {String(cell.getValue() ?? "")}
                                            </TableCell>
                                        )
                                    })}
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            <div className="mt-4">
                <PaginationBar table={table} totalFiltered={totalFiltered} />
            </div>
        </div>
    )
}

function generatePageNumbers(current: number, total: number): (number | null)[] {
    if (total <= 14) {
        return Array.from({ length: total }, (_, i) => i)
    }

    const pages: (number | null)[] = []

    if (current <= 5) {
        const end = Math.min(11, total - 3)
        for (let i = 0; i <= end; i++) {
            pages.push(i)
        }
        pages.push(null)
        pages.push(total - 2)
        pages.push(total - 1)
    } else if (current >= total - 6) {
        pages.push(0)
        pages.push(1)
        pages.push(null)
        const start = Math.max(2, total - 12)
        for (let i = start; i < total; i++) {
            pages.push(i)
        }
    } else {
        pages.push(0)
        pages.push(1)

        const windowStart = current - 5
        const windowEnd = current + 5

        if (windowStart > 2) {
            pages.push(null)
        }

        for (let i = windowStart; i <= windowEnd; i++) {
            pages.push(i)
        }

        if (windowEnd < total - 3) {
            pages.push(null)
        }

        pages.push(total - 2)
        pages.push(total - 1)
    }

    return pages
}
