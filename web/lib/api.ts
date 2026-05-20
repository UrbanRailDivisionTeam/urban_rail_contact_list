import type { Contact } from "@/lib/mock-data"

export async function fetchContacts(): Promise<Contact[]> {
  const res = await fetch("/api/contacts")

  if (!res.ok) {
    throw new Error(`获取通讯录失败 (${res.status})`)
  }

  const data: Contact[] = await res.json()
  return data
}
