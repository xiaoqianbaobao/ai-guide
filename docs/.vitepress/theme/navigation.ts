/** 路线数据与视图解耦；URL 继续兼容 VitePress 的 cleanUrls 和 /ai-guide/。 */
export interface LessonLink { text: string; link: string }
export interface LessonGroup { text: string; items?: LessonLink[] }
export type LessonSidebar = Record<string, LessonGroup[]>
export interface LessonNeighbors { prev: LessonLink | false; next: LessonLink | false }

export function normalizeLessonPath(value: string): string {
  return '/' + value.replace(/^\/+/, '').replace(/(?:\/index)?\.md$/, '').replace(/\/$/, '')
}

export function lessonNeighbors(sidebar: LessonSidebar, relativePath: string): LessonNeighbors {
  const page = normalizeLessonPath(relativePath)
  const sections = Object.entries(sidebar).sort(([a], [b]) => b.length - a.length)
  const section = sections.find(([prefix]) => `${page}/`.startsWith(prefix))
  if (!section) return { prev: false, next: false }
  const entries = section[1].flatMap(group => group.items ?? []).filter(item => item.link)
  const index = entries.findIndex(item => normalizeLessonPath(item.link) === page)
  if (index < 0) return { prev: false, next: false }
  return { prev: entries[index - 1] ?? false, next: entries[index + 1] ?? false }
}
