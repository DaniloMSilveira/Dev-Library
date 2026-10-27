// Gera o menu do site a partir da estrutura de estudos/, para que páginas novas
// apareçam sem precisar editar a configuração.
import fs from 'node:fs'
import path from 'node:path'
import type { DefaultTheme } from 'vitepress'
import type MarkdownIt from 'markdown-it'
import { type CodeSite, exampleContaining } from './codigo.mts'
import { CODE_DIR, SRC_DIR, folderLabel, githubUrl, isExcludedDir, pageTitle } from './estudos.mts'

type Item = DefaultTheme.SidebarItem

function pageLink(relFile: string): string {
  return '/' + relFile.replace(/\.md$/, '')
}

// Caminhos relativos a estudos/, sempre com "/".
function listDir(relDir: string) {
  const entries = fs
    .readdirSync(path.join(SRC_DIR, relDir), { withFileTypes: true })
    .filter((e) => !e.name.startsWith('.') && e.name !== 'node_modules')
    .sort((a, b) => a.name.localeCompare(b.name, 'pt-BR', { numeric: true }))
  return {
    pages: entries.filter((e) => e.isFile() && e.name.endsWith('.md') && e.name !== 'README.md' && e.name !== 'index.md'),
    dirs: entries.filter((e) => e.isDirectory() && !isExcludedDir(path.posix.join(relDir, e.name))),
    hasReadme: entries.some((e) => e.isFile() && e.name === 'README.md'),
  }
}

function buildItems(relDir: string, depth: number, code: CodeSite): Item[] {
  const { pages, dirs } = listDir(relDir)
  const items: Item[] = pages.map((p) => {
    const rel = path.posix.join(relDir, p.name)
    return { text: pageTitle(path.join(SRC_DIR, rel)), link: pageLink(rel) }
  })
  for (const d of dirs) {
    const rel = path.posix.join(relDir, d.name)
    // A pasta docs/ é só organização do repositório; seu conteúdo sobe um nível no menu.
    if (d.name === 'docs') {
      items.push(...buildItems(rel, depth, code))
      continue
    }
    const group = buildGroup(rel, depth, code)
    if (group) items.push(group)
  }
  return items
}

function buildGroup(relDir: string, depth: number, code: CodeSite): Item | null {
  const children = buildItems(relDir, depth + 1, code)
  const readme = listDir(relDir).hasReadme ? path.posix.join(relDir, 'README.md') : null
  const example = code.examples.get(relDir)
  if (example) {
    // Exemplo só com código vira um link direto para a árvore de arquivos.
    if (!children.length && !readme) return { text: folderLabel(path.posix.basename(relDir)), link: example.treeLink }
    children.unshift({ text: 'Arquivos do exemplo', link: example.treeLink })
  }
  if (!children.length && !readme) return null
  return {
    text: readme ? pageTitle(path.join(SRC_DIR, readme)) : folderLabel(path.posix.basename(relDir)),
    link: readme ? pageLink(readme) : undefined,
    items: children.length ? children : undefined,
    collapsed: children.length ? depth > 0 : undefined,
  }
}

function firstLink(items: Item[]): string | undefined {
  for (const item of items) {
    const link = item.link ?? (item.items && firstLink(item.items))
    if (link) return link
  }
}

// Cada pasta de primeiro nível em estudos/ é uma área, com aba no topo e menu lateral próprio.
// As páginas de código geradas de uma área usam o mesmo menu.
export function buildNavigation(code: CodeSite) {
  const nav: DefaultTheme.NavItem[] = []
  const sidebar: DefaultTheme.SidebarMulti = {}
  for (const area of listDir('').dirs.map((d) => d.name).filter((d) => d !== CODE_DIR)) {
    const items = buildItems(area, 0, code)
    if (listDir(area).hasReadme) items.unshift({ text: 'Visão geral', link: pageLink(`${area}/README.md`) })
    const link = firstLink(items)
    if (!link) continue
    nav.push({ text: folderLabel(area), link, activeMatch: `^/(${CODE_DIR}/)?${area}/` })
    sidebar[`/${area}/`] = items
    sidebar[`/${CODE_DIR}/${area}/`] = items
  }
  return { nav, sidebar }
}

// Links relativos para pastas ou arquivos de código passam a apontar para as páginas
// geradas em codigo.mts; o que não tem página no site aponta para o GitHub.
export function siteLinks(code: CodeSite) {
  return (md: MarkdownIt) => {
    md.core.ruler.push('site-links', (state) => {
      const relativePath: string | undefined = state.env.relativePath
      if (!relativePath) return
      for (const block of state.tokens) {
        for (const token of block.children ?? []) {
          if (token.type !== 'link_open') continue
          const href = token.attrGet('href')
          if (!href || /^([a-z][a-z0-9+.-]*:|#|\/)/i.test(href)) continue
          const target = decodeURI(href.split('#')[0])
          if (!target || /\.(md|html)$/i.test(target)) continue
          const srcPath = path.posix.normalize(path.posix.join(path.posix.dirname(relativePath), target)).replace(/\/$/, '')
          const absPath = path.join(SRC_DIR, srcPath)
          // Caminhos fora de estudos/ ou inexistentes ficam como estão para o build acusar o link quebrado.
          if (srcPath.startsWith('..') || !fs.existsSync(absPath)) continue
          const newHref = fs.statSync(absPath).isDirectory()
            ? (exampleContaining(srcPath, code)?.treeLink ?? githubUrl('tree', srcPath))
            : (code.fileLinks.get(srcPath) ?? githubUrl('blob', srcPath))
          token.attrSet('href', newHref)
        }
      }
    })
  }
}
