// Caminhos e nomes compartilhados pela configuração do site.
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

export const REPO_URL = 'https://github.com/DaniloMSilveira/Dev-Library'
export const ROOT_DIR = fileURLToPath(new URL('..', import.meta.url))
export const SRC_DIR = path.join(ROOT_DIR, 'estudos')
// Pasta gerada a cada build com as páginas de código (ver codigo.mts); não é uma área de estudo.
export const CODE_DIR = 'codigo'

// Nomes de pasta que não ficam bons apenas capitalizando as palavras.
const FOLDER_LABELS: Record<string, string> = {
  'spec-driven-development': 'Spec-Driven Development',
  speckit: 'Spec Kit',
  examples: 'Exemplos',
}
const ACRONYMS = new Set(['aws', 'ec2', 'ecs', 'eks', 'ia', 'api', 'ml', 'llm', 'rag'])

export function folderLabel(name: string): string {
  return (
    FOLDER_LABELS[name] ??
    name
      .split('-')
      .map((w) => (ACRONYMS.has(w.toLowerCase()) ? w.toUpperCase() : w.charAt(0).toUpperCase() + w.slice(1)))
      .join(' ')
  )
}

// Primeiro título "# " fora de blocos de código; se não houver, usa o nome do arquivo.
export function pageTitle(file: string): string {
  let inFence = false
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence
    else if (!inFence && line.startsWith('# ')) return line.slice(2).trim()
  }
  return folderLabel(path.basename(file, '.md'))
}

// Pastas de dados dos exemplos (ex.: base de conhecimento do RAG) ficam fora do site.
// Mantém em sincronia com srcExclude em config.mts.
export function isExcludedDir(relDir: string): boolean {
  return /(^|\/)exemplos\/[^/]+\/data(\/|$)/.test(relDir)
}

// Caminhos relativos a estudos/, sempre com "/".
export function githubUrl(kind: 'blob' | 'tree', srcPath: string): string {
  const encoded = encodeURI(srcPath).replace(/\(/g, '%28').replace(/\)/g, '%29')
  return `${REPO_URL}/${kind}/main/estudos/${encoded}`
}

export function escapeMarkdown(text: string): string {
  return text.replace(/[\\`*_{}[\]<>()#!|~]/g, '\\$&')
}
