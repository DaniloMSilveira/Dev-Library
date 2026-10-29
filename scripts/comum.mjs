// Funções compartilhadas pelos scripts de scripts/.
import fs from 'node:fs'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

export const ROOT = fileURLToPath(new URL('..', import.meta.url))
export const ESTUDOS = path.join(ROOT, 'estudos')
export const RASCUNHOS = path.join(ROOT, 'rascunhos')

// estudos/codigo é gerado pelo site (.vitepress/codigo.mts).
const GENERATED_TOP_DIRS = new Set(['codigo'])

export function isDataDir(relDir) {
  return /(^|\/)exemplos\/[^/]+\/data(\/|$)/.test(relDir)
}

export function isExampleFile(relPath) {
  return /(^|\/)(exemplos|examples)\//.test(relPath)
}

export function toPosix(p) {
  return p.split(path.sep).join('/')
}

// Lista arquivos de estudos/ (caminhos relativos com "/"), sem pastas ocultas, geradas ou de dados.
export function listStudyFiles(relDir = '') {
  const result = []
  for (const entry of fs.readdirSync(path.join(ESTUDOS, relDir), { withFileTypes: true })) {
    if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === '__pycache__') continue
    const rel = relDir ? `${relDir}/${entry.name}` : entry.name
    if (entry.isDirectory()) {
      if (!relDir && GENERATED_TOP_DIRS.has(entry.name)) continue
      if (isDataDir(rel)) continue
      result.push(...listStudyFiles(rel))
    } else {
      result.push(rel)
    }
  }
  return result.sort((a, b) => a.localeCompare(b, 'pt-BR', { numeric: true }))
}

export function listAreas() {
  return fs
    .readdirSync(ESTUDOS, { withFileTypes: true })
    .filter((e) => e.isDirectory() && !e.name.startsWith('.') && !GENERATED_TOP_DIRS.has(e.name))
    .map((e) => e.name)
    .sort((a, b) => a.localeCompare(b, 'pt-BR'))
}

// Linhas fora de blocos de código cercados (``` ou ~~~), com o número da linha.
export function linesOutsideFences(text) {
  const lines = []
  let fence = null
  text.split(/\r?\n/).forEach((line, i) => {
    const match = line.match(/^\s*(`{3,}|~{3,})/)
    if (match) {
      if (!fence) fence = match[1]
      else if (match[1][0] === fence[0] && match[1].length >= fence.length) fence = null
      return
    }
    if (!fence) lines.push({ line, number: i + 1 })
  })
  return lines
}

export function h1Titles(text) {
  return linesOutsideFences(text)
    .filter(({ line }) => /^# /.test(line))
    .map(({ line, number }) => ({ title: line.slice(2).trim(), number }))
}

export function readText(file) {
  return fs.readFileSync(file, 'utf8')
}

// Frontmatter simples (chave: valor) usado nos rascunhos.
export function frontmatter(text) {
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---/)
  if (!match) return {}
  const data = {}
  for (const line of match[1].split(/\r?\n/)) {
    const kv = line.match(/^([\w-]+):\s*(.*?)\s*(#.*)?$/)
    if (kv) data[kv[1]] = kv[2]
  }
  return data
}

export function listDrafts() {
  if (!fs.existsSync(RASCUNHOS)) return []
  return fs
    .readdirSync(RASCUNHOS)
    .filter((f) => f.endsWith('.md') && !f.startsWith('_') && f !== 'README.md')
    .sort()
    .map((f) => {
      const text = readText(path.join(RASCUNHOS, f))
      const data = frontmatter(text)
      return { file: `rascunhos/${f}`, tema: data.tema || h1Titles(text)[0]?.title || f, status: data.status || 'novo', area: data.area || '' }
    })
}

function git(args) {
  try {
    return execFileSync('git', args, { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, stdio: ['ignore', 'pipe', 'ignore'] })
  } catch {
    return null
  }
}

// Arquivos versionados e novos não ignorados (caminhos relativos à raiz, com "/").
// Fora de um repositório git, recai para os arquivos de estudos/.
export function versionableFiles() {
  const out = git(['ls-files', '-z', '--cached', '--others', '--exclude-standard'])
  if (out === null) return listStudyFiles().map((f) => `estudos/${f}`)
  return [...new Set(out.split('\0').filter(Boolean))].filter((f) => fs.existsSync(path.join(ROOT, f))).sort()
}

export function commitMessages() {
  const out = git(['log', '--all', '--format=%h%x00%B%x01'])
  if (out === null) return []
  return out
    .split('\x01')
    .map((entry) => entry.replace(/^\s+/, ''))
    .filter(Boolean)
    .map((entry) => {
      const [hash, body = ''] = entry.split('\0')
      return { hash, body }
    })
}
