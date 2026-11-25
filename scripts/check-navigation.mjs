import { readdir, readFile, access } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const output = path.join(project, 'dist')
const base = '/ai-guide/'
async function allHtml(dir) {
  const entries = await readdir(dir, { withFileTypes: true })
  return (await Promise.all(entries.map(e => e.isDirectory() ? allHtml(path.join(dir, e.name)) : e.name.endsWith('.html') ? [path.join(dir, e.name)] : []))).flat()
}
function route(file) {
  const rel = path.relative(output, file).split(path.sep).join('/')
  return `/${rel.replace(/index\.html$/, '').replace(/\.html$/, '').replace(/\/$/, '')}`.replace(/^\/$/, '/')
}
function normalizedLink(href) {
  if (!href.startsWith(base)) throw new Error(`非本站路径: ${href}`)
  return '/' + href.slice(base.length).replace(/\/$/, '')
}
const pages = new Map()
for (const file of await allHtml(output)) {
  const html = await readFile(file, 'utf8')
  const nav = html.match(/<nav class="prev-next"[\s\S]*?<\/nav>/)?.[0] ?? ''
  const sidebar = html.match(/<aside\b[^>]*class="next-sidebar"[\s\S]*?<\/aside>/)?.[0] ?? ''
  const entries = [...sidebar.matchAll(/<a\b([^>]*)>/g)].map(match => {
    const attrs = match[1]
    const href = attrs.match(/\bhref="([^"]+)"/)?.[1]
    return href ? { path: normalizedLink(href), current: /\baria-current="page"/.test(attrs) } : null
  }).filter(Boolean)
  const links = {}
  for (const match of nav.matchAll(/<a\b[^>]*class="[^"]*pager-link (prev|next)[^"]*"[^>]*href="([^"]+)"/g)) links[match[1]] = normalizedLink(match[2])
  pages.set(route(file), { links, entries, file })
}
const errors = []
let edges = 0
for (const [current, { links, entries }] of pages) {
  const matches = entries.map((entry, index) => entry.current ? index : -1).filter(index => index >= 0)
  const matchingPaths = entries.filter(entry => entry.path === current)
  if (matchingPaths.length > 1) errors.push(`${current}: 课程目录中重复收录当前页面`)
  if (matchingPaths.length === 1 && matches.length === 0) errors.push(`${current}: 课程目录缺少当前页标记`)
  if (matches.length > 1) errors.push(`${current}: 课程目录存在多个当前项`)
  if (matches.length === 1) {
    const index = matches[0]
    if (entries[index].path !== current) errors.push(`${current}: 当前目录项指向 ${entries[index].path}`)
    for (const [direction, expected] of [['prev', entries[index - 1]?.path], ['next', entries[index + 1]?.path]]) {
      if (links[direction] !== expected) errors.push(`${current} ${direction}: ${links[direction] ?? '空'}，课程目录中的相邻项为 ${expected ?? '空'}`)
    }
  } else if (Object.keys(links).length) errors.push(`${current}: 有分页链接，但课程目录没有当前项`)
  for (const [direction, target] of Object.entries(links)) {
    edges++
    const other = pages.get(target)
    if (!other) { errors.push(`${current} ${direction}: 找不到 ${target}`); continue }
    const reverse = direction === 'next' ? 'prev' : 'next'
    if (other.links[reverse] !== current) errors.push(`${current} ${direction}: ${target} 的 ${reverse} 指向 ${other.links[reverse] ?? '空'}`)
    const section = s => (s === '/models/python-basics' || s.startsWith('/models/python-basics/')) ? '/models/python-basics' : '/' + s.split('/')[1]
    if (section(current) !== section(target)) errors.push(`${current} ${direction}: 意外跨专题到 ${target}`)
  }
}
for (const [from, target] of [
  ['/03-memory/dreaming-offline-consolidation', '/03-memory/memory-evaluation'],
  ['/models/python-basics/lesson-04', '/models/python-basics/lesson-05'],
  ['/01-llm-foundations/chapter-06d-gqa-mqa-and-bandwidth', undefined],
  ['/guide/example-article', undefined],
]) {
  if (pages.get(from)?.links.next !== target) errors.push(`${from} 的下一篇不是预期的 ${target ?? '无'}`)
}
if (errors.length) { console.error(errors.join('\n')); process.exitCode = 1 }
else console.log(`已检查 ${pages.size} 个 HTML 页面与 ${edges} 个分页链接；目标存在、前后互指、不跨专题且与课程目录顺序一致。`)
