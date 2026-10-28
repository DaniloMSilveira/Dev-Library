// Verificações estruturais do acervo que o build do site não cobre (o build já acusa
// links internos quebrados). Erros fazem o comando falhar; avisos só são exibidos.
// Uso: npm run estudos:verificar
import fs from 'node:fs'
import path from 'node:path'
import {
  ESTUDOS,
  h1Titles,
  isExampleFile,
  linesOutsideFences,
  listAreas,
  listDrafts,
  listStudyFiles,
  readText,
} from './comum.mjs'

const errors = []
const warnings = []
const pages = listStudyFiles().filter((f) => f.endsWith('.md') && f !== 'index.md')

for (const page of pages) {
  const text = readText(path.join(ESTUDOS, page))

  // O título # vira o nome da página no menu; exemplos reproduzem artefatos e podem fugir à regra.
  if (!isExampleFile(page)) {
    const titles = h1Titles(text)
    if (titles.length === 0) errors.push(`${page}: sem título "# " (ele vira o nome da página no menu).`)
    if (titles.length > 1)
      errors.push(`${page}: ${titles.length} títulos "# " (linhas ${titles.map((t) => t.number).join(', ')}); use apenas um.`)
  }

  // O VitePress interpreta {{ }} fora de código como template Vue, o que quebra o build.
  for (const { line, number } of linesOutsideFences(text)) {
    if (/\{\{|\}\}/.test(line.replace(/`[^`]*`/g, '')))
      errors.push(`${page}:${number}: "{{" ou "}}" fora de código; coloque o trecho entre crases.`)
  }
}

// Direitos autorais: o acervo é público e não guarda material de cursos nem citações de terceiros.
const THIRD_PARTY_MARKERS = /projeto desenvolvido na|todos os direitos reservados|all rights reserved/i
const TEXT_FILES = /\.(md|py|ipynb|tf|hcl|ya?ml|json|sh|toml|txt|js|ts|cs|sql|html|css)$|(^|\/)Dockerfile$/
for (const file of listStudyFiles().filter((f) => TEXT_FILES.test(f))) {
  readText(path.join(ESTUDOS, file))
    .split(/\r?\n/)
    .forEach((line, i) => {
      if (THIRD_PARTY_MARKERS.test(line)) errors.push(`${file}:${i + 1}: marca de material de terceiros ("${line.trim().slice(0, 60)}").`)
    })
}
for (const page of pages) {
  for (const { line, number } of linesOutsideFences(readText(path.join(ESTUDOS, page)))) {
    if (/^>\s*["“]/.test(line))
      warnings.push(`${page}:${number}: citação em bloco entre aspas; confirme que é texto próprio (guia de estilo, seção 8).`)
  }
}

// Trilhas numeradas: 1..n sem buracos nem repetições, e título começando pelo número.
const numberedByDir = new Map()
for (const page of pages.filter((p) => !isExampleFile(p))) {
  const match = path.posix.basename(page).match(/^(\d+)-/)
  if (!match) continue
  const dir = path.posix.dirname(page)
  if (!numberedByDir.has(dir)) numberedByDir.set(dir, [])
  numberedByDir.get(dir).push({ page, n: Number(match[1]) })
}
for (const [dir, items] of numberedByDir) {
  const numbers = items.map((i) => i.n).sort((a, b) => a - b)
  const expected = numbers.map((_, i) => i + 1)
  if (numbers.join() !== expected.join())
    errors.push(`${dir}/: numeração da trilha é ${numbers.join(', ')}; esperado ${expected.join(', ')}.`)
  for (const { page, n } of items) {
    const title = h1Titles(readText(path.join(ESTUDOS, page)))[0]?.title
    if (title && !title.startsWith(`${n}. `)) warnings.push(`${page}: título "${title}" não começa com "${n}. ".`)
  }
}

// Cada área precisa de um card na página inicial.
const home = readText(path.join(ESTUDOS, 'index.md'))
for (const area of listAreas()) {
  if (!listStudyFiles(area).some((f) => f.endsWith('.md'))) continue
  if (!home.includes(`link: /${area}/`)) errors.push(`index.md: a área "${area}" não tem card em "features".`)
  if (!fs.existsSync(path.join(ESTUDOS, area, 'README.md')))
    warnings.push(`${area}/: área sem README.md (ele vira a "Visão geral" no menu).`)
}

const pending = listDrafts().filter((d) => d.status !== 'documentado')

for (const w of warnings) console.log(`AVISO  ${w}`)
for (const e of errors) console.log(`ERRO   ${e}`)
if (pending.length) console.log(`INFO   ${pending.length} rascunho(s) pendente(s) em rascunhos/ (npm run estudos:catalogo).`)
console.log(`\n${pages.length} páginas verificadas: ${errors.length} erro(s), ${warnings.length} aviso(s).`)
process.exit(errors.length ? 1 : 0)
