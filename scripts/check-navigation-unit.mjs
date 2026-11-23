import { readFile } from 'node:fs/promises'
import assert from 'node:assert/strict'
import ts from 'typescript'
const source = await readFile(new URL('../docs/.vitepress/theme/navigation.ts', import.meta.url), 'utf8')
const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } }).outputText
const { lessonNeighbors } = await import(`data:text/javascript;base64,${Buffer.from(js).toString('base64')}`)
const sidebar = {
  '/models/': [{ text: 'models', items: [{ text: '主页', link: '/models/' }] }],
  '/models/python-basics/': [{ text: 'python', items: [
    { text: '概述', link: '/models/python-basics/' },
    { text: '第一课', link: '/models/python-basics/lesson-01/' },
    { text: '第二课', link: '/models/python-basics/lesson-02/' }
  ] }]
}
assert.equal(lessonNeighbors(sidebar, 'models/python-basics/index.md').next.text, '第一课')
assert.equal(lessonNeighbors(sidebar, 'models/python-basics/lesson-01.md').prev.text, '概述')
assert.equal(lessonNeighbors(sidebar, 'models/python-basics/lesson-01.md').next.text, '第二课')
assert.equal(lessonNeighbors(sidebar, 'models/python-basics/lesson-02.md').next, false)
assert.deepEqual(lessonNeighbors(sidebar, 'models/python-basics/unlisted.md'), { prev: false, next: false })
assert.deepEqual(lessonNeighbors(sidebar, 'other/index.md'), { prev: false, next: false })
console.log('课程导航边界检查通过（专题入口、首尾、嵌套目录及未收录页面）。')
