import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

interface SidebarItem {
  text: string
  link?: string
  items?: SidebarItem[]
  collapsed?: boolean
}

export function generateSidebar(section: string, maxDepth = 2): SidebarItem[] {
  const sectionPath = path.resolve(__dirname, `../../../${section}`)
  
  if (!fs.existsSync(sectionPath)) {
    return []
  }

  return scanDirectory(sectionPath, section, 0, maxDepth)
}

function scanDirectory(
  dirPath: string, 
  baseRoute: string, 
  currentDepth: number,
  maxDepth: number
): SidebarItem[] {
  const items: SidebarItem[] = []
  const entries = fs.readdirSync(dirPath, { withFileTypes: true })
  
  const sortedEntries = entries.sort((a, b) => {
    if (a.name === 'index.md') return -1
    if (b.name === 'index.md') return 1
    return a.name.localeCompare(b.name)
  })

  for (const entry of sortedEntries) {
    const fullPath = path.join(dirPath, entry.name)
    const relativePath = path.relative(path.resolve(__dirname, '../../..'), fullPath)
    
    if (entry.isDirectory() && currentDepth < maxDepth) {
      const subItems = scanDirectory(
        fullPath, 
        `${baseRoute}/${entry.name}`, 
        currentDepth + 1,
        maxDepth
      )
      
      if (subItems.length > 0) {
        const indexPath = path.join(fullPath, 'index.md')
        let dirTitle = entry.name.replace(/-/g, ' ')
        
        if (fs.existsSync(indexPath)) {
          const content = fs.readFileSync(indexPath, 'utf-8')
          const { data } = matter(content)
          dirTitle = data.title || dirTitle
        }
        
        items.push({
          text: dirTitle,
          items: subItems,
          collapsed: currentDepth > 0
        })
      }
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      const fileName = entry.name.replace('.md', '')
      if (fileName === 'index') continue
      
      const content = fs.readFileSync(fullPath, 'utf-8')
      const { data } = matter(content)
      
      const item: SidebarItem = {
        text: data.title || fileName.replace(/-/g, ' '),
        link: `/${baseRoute}/${fileName}/`
      }
      
      if (data.order) {
        (item as any).order = data.order
      }
      
      items.push(item)
    }
  }

  return items.sort((a: any, b: any) => {
    const orderA = a.order || 999
    const orderB = b.order || 999
    return orderA - orderB
  })
}