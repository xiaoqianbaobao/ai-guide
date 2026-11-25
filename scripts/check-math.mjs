import { readFile } from 'node:fs/promises'
import path from 'node:path'

const page = path.resolve('dist/models/linear-algebra-for-agents.html')
const html = await readFile(page, 'utf8')
const formulas = (html.match(/<mjx-container\b/g) || []).length
if (formulas === 0 || html.includes('data-mml-node="merror"')) {
  throw new Error(`数学示例页面公式渲染异常：发现 ${formulas} 个公式或 MathJax 错误`)
}
console.log(`数学示例页面已生成 ${formulas} 个 MathJax 公式，未发现公式解析错误。`)
