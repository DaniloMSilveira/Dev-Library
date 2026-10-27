// O VitePress só transforma Markdown em página. Para o código dos exemplos poder
// ser lido no site, este módulo gera em estudos/codigo/ uma página por arquivo de
// código e uma página com a árvore de arquivos de cada exemplo. A pasta é recriada
// sempre que o site sobe ou é gerado, e fica fora do repositório (.gitignore).
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import {
  CODE_DIR,
  ROOT_DIR,
  SRC_DIR,
  escapeMarkdown,
  folderLabel,
  githubUrl,
  isExcludedDir,
  pageTitle,
} from './estudos.mts'

const EXAMPLE_DIRS = new Set(['exemplos', 'examples'])

// Extensões exibidas no site, com a linguagem usada no realce de sintaxe.
// O resto (notebooks, CSVs) abre no GitHub, que já sabe exibir esses formatos.
const LANGUAGES: Record<string, string> = {
  py: 'python',
  tf: 'hcl',
  hcl: 'hcl',
  yml: 'yaml',
  yaml: 'yaml',
  sh: 'bash',
  json: 'json',
  toml: 'toml',
  ini: 'ini',
  cfg: 'ini',
  example: 'ini',
  txt: 'txt',
  dockerignore: 'txt',
  gitignore: 'txt',
  dockerfile: 'dockerfile',
  css: 'css',
  html: 'html',
  js: 'js',
  ts: 'ts',
  cs: 'csharp',
  sql: 'sql',
}
const MAX_SIZE = 100_000

export interface Example {
  dir: string
  label: string
  treeLink: string
}

export interface CodeSite {
  examples: Map<string, Example>
  // Caminho do arquivo em estudos/ -> link da página gerada.
  fileLinks: Map<string, string>
}

function language(file: string): string | undefined {
  const name = path.posix.basename(file).toLowerCase()
  if (name === 'dockerfile') return LANGUAGES.dockerfile
  return name.includes('.') ? LANGUAGES[name.slice(name.lastIndexOf('.') + 1)] : undefined
}

function isViewable(file: string): boolean {
  return (
    !file.endsWith('.md') &&
    !isExcludedDir(path.posix.dirname(file)) &&
    language(file) !== undefined &&
    fs.statSync(path.join(SRC_DIR, file)).size <= MAX_SIZE
  )
}

// Usa o git para respeitar o .gitignore: .env, .venv e afins nunca entram no site.
function studyFiles(): string[] {
  const output = execFileSync(
    'git',
    ['ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', 'estudos'],
    { cwd: ROOT_DIR, encoding: 'utf8' },
  )
  return output
    .split('\0')
    .filter(Boolean)
    .map((f) => f.slice('estudos/'.length))
    .filter((f) => fs.existsSync(path.join(SRC_DIR, f)))
}

// Um exemplo é cada subpasta de exemplos/ (ou examples/) com arquivos que não são Markdown.
// Se exemplos/ tiver arquivos soltos, a própria pasta exemplos/ é o exemplo.
function findExampleDirs(files: string[]): string[] {
  const dirs = new Set<string>()
  for (const file of files) {
    if (file.endsWith('.md')) continue
    const parts = file.split('/')
    const i = parts.findIndex((p) => EXAMPLE_DIRS.has(p))
    if (i < 0) continue
    const isLooseFile = parts.length === i + 2
    dirs.add(parts.slice(0, isLooseFile ? i + 1 : i + 2).join('/'))
  }
  return [...dirs].filter((d) => ![...dirs].some((other) => d.startsWith(other + '/')))
}

function urlSegment(segment: string): string {
  return segment.normalize('NFKD').replace(/[^\w-]+/g, '-')
}

function exampleLabel(dir: string, files: string[]): string {
  const name = path.posix.basename(dir)
  if (files.includes(`${dir}/README.md`)) return pageTitle(path.join(SRC_DIR, dir, 'README.md'))
  if (EXAMPLE_DIRS.has(name)) return `Exemplos de ${folderLabel(path.posix.basename(path.posix.dirname(dir)))}`
  return folderLabel(name)
}

function writePage(link: string, content: string) {
  const file = path.join(SRC_DIR, link.endsWith('/') ? `${link}index.md` : `${link}.md`)
  fs.mkdirSync(path.dirname(file), { recursive: true })
  fs.writeFileSync(file, content)
}

function frontmatter(title: string, extra: string[] = []): string {
  return ['---', `title: ${JSON.stringify(title)}`, 'editLink: false', 'lastUpdated: false', ...extra, '---', ''].join(
    '\n',
  )
}

function codePage(file: string, example: Example): string {
  const name = path.posix.basename(file)
  const content = fs.readFileSync(path.join(SRC_DIR, file), 'utf8').replace(/\r\n/g, '\n').trimEnd()
  const fence = '`'.repeat(Math.max(3, ...[...content.matchAll(/`+/g)].map((m) => m[0].length + 1)))
  return [
    // search: false mantém a busca focada nas anotações (ver config.mts).
    frontmatter(name, ['outline: false', 'prev: false', 'next: false', 'search: false']),
    `# ${escapeMarkdown(name)}`,
    '',
    `\`${file.slice(example.dir.length + 1)}\` · [Arquivos: ${escapeMarkdown(example.label)}](${example.treeLink}) · [Ver no GitHub](${githubUrl('blob', file)})`,
    '',
    content ? `${fence}${language(file)}:line-numbers\n${content}\n${fence}` : '_Arquivo vazio._',
    '',
  ].join('\n')
}

interface TreeNode {
  dirs: Map<string, TreeNode>
  files: string[]
}

function treePage(example: Example, files: string[], fileLinks: Map<string, string>): string {
  const root: TreeNode = { dirs: new Map(), files: [] }
  for (const file of files) {
    let node = root
    for (const part of file.slice(example.dir.length + 1).split('/').slice(0, -1)) {
      if (!node.dirs.has(part)) node.dirs.set(part, { dirs: new Map(), files: [] })
      node = node.dirs.get(part)!
    }
    node.files.push(file)
  }

  const byName = (a: string, b: string) => a.localeCompare(b, 'pt-BR', { numeric: true })
  const lines: string[] = []
  const render = (node: TreeNode, depth: number) => {
    const indent = '  '.repeat(depth)
    for (const name of [...node.dirs.keys()].sort(byName)) {
      lines.push(`${indent}- 📁 **${escapeMarkdown(name)}/**`)
      render(node.dirs.get(name)!, depth + 1)
    }
    for (const file of node.files.sort((a, b) => byName(path.posix.basename(a), path.posix.basename(b)))) {
      const label = escapeMarkdown(path.posix.basename(file))
      const isSitePage = file.endsWith('.md') && !isExcludedDir(path.posix.dirname(file))
      const link = fileLinks.get(file) ?? (isSitePage ? '/' + file.replace(/\.md$/, '') : undefined)
      lines.push(link ? `${indent}- [${label}](${link})` : `${indent}- [${label} ↗](${githubUrl('blob', file)})`)
    }
  }
  render(root, 0)

  const readme = files.includes(`${example.dir}/README.md`) ? ` · [Ler o README](/${example.dir}/README)` : ''
  return [
    frontmatter(`Arquivos: ${example.label}`),
    `# Arquivos: ${escapeMarkdown(example.label)}`,
    '',
    `Estrutura de \`${example.dir}\`. Os arquivos de código abrem aqui no site; os marcados com ↗ (notebooks, dados e arquivos grandes) abrem no GitHub.`,
    '',
    `[Ver pasta no GitHub](${githubUrl('tree', example.dir)})${readme}`,
    '',
    ...lines,
    '',
  ].join('\n')
}

export function generateCodePages(): CodeSite {
  fs.rmSync(path.join(SRC_DIR, CODE_DIR), { recursive: true, force: true })
  const files = studyFiles()
  const examples = new Map<string, Example>()
  const fileLinks = new Map<string, string>()

  for (const dir of findExampleDirs(files)) {
    const treeLink = `/${CODE_DIR}/${dir.split('/').map(urlSegment).join('/')}/`
    const example: Example = { dir, label: exampleLabel(dir, files), treeLink }
    examples.set(dir, example)

    const exampleFiles = files.filter((f) => f.startsWith(dir + '/'))
    const usedLinks = new Set<string>()
    for (const file of exampleFiles.filter(isViewable)) {
      const base = `/${CODE_DIR}/${file.split('/').map(urlSegment).join('/')}`
      let link = base.endsWith('/index') ? `${base}-arquivo` : base
      for (let n = 2; usedLinks.has(link); n++) link = `${base}-${n}`
      usedLinks.add(link)
      fileLinks.set(file, link)
      writePage(link, codePage(file, example))
    }
    writePage(treeLink, treePage(example, exampleFiles, fileLinks))
  }
  return { examples, fileLinks }
}

export function exampleContaining(srcPath: string, code: CodeSite): Example | undefined {
  for (const [dir, example] of code.examples) {
    if (srcPath === dir || srcPath.startsWith(dir + '/')) return example
  }
}
