import { createContentLoader } from 'vitepress'

export interface SearchDocument { title: string; url: string; text: string }
export declare const data: SearchDocument[]

function searchableText(source: string): string {
  return source.replace(/^\uFEFF*---[\s\S]*?---\s*/, '')
    // Keep code examples searchable while removing only Markdown fence markers.
    .replace(/^\s{0,3}(?:`{3,}|~{3,})[^\n]*$/gm, ' ')
    .replace(/!?\[([^\]]*)\]\([^)]+\)/g, '$1')
    .replace(/^\s*\|?[\s:|-]{3,}\|?\s*$/gm, ' ')
    .replace(/^\s{0,3}(?:#{1,6}|>|[-*+]|\d+\.)\s+/gm, '')
    .replace(/<\/?[A-Za-z][A-Za-z0-9-]*(?:\s+(?:"[^"]*"|'[^']*'|[^'"<>])*)?\s*\/?>/g, ' ')
    .replace(/[`~|]/g, ' ')
    .replace(/\s+/g, ' ').trim()
}

export default createContentLoader('**/*.md', {
  includeSrc: true,
  transform(pages): SearchDocument[] {
    return pages.filter(page => page.frontmatter.search !== false && !page.url.endsWith('/README.html')).map(page => ({
      title: String(page.frontmatter.title || page.src?.match(/^#\s+(.+)$/m)?.[1]?.replace(/\s+#+\s*$/, '').trim() || page.url),
      url: page.url.replace(/^\/ai-guide(?=\/)/, ''),
      text: searchableText(page.src || '')
    }))
  }
})
