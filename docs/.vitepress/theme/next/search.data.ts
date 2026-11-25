import { createContentLoader } from 'vitepress'

export interface SearchDocument { title: string; url: string; text: string }
export declare const data: SearchDocument[]

export default createContentLoader('**/*.md', {
  includeSrc: true,
  transform(pages): SearchDocument[] {
    return pages.filter(page => !page.url.endsWith('/README.html')).map(page => ({
      title: String(page.frontmatter.title || page.src?.match(/^#\s+(.+)$/m)?.[1]?.replace(/\s+#+\s*$/, '').trim() || page.url),
      url: page.url.replace(/^\/ai-guide(?=\/)/, ''),
      text: (page.src || '').replace(/^---[\s\S]*?---\s*/, '').replace(/```[\s\S]*?```/g, ' ').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
    }))
  }
})
