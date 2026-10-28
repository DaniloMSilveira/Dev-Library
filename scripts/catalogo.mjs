// Mostra o acervo atual (áreas, trilhas, páginas e exemplos) e os rascunhos pendentes,
// para o agente decidir onde um tema novo se encaixa sem depender de um mapa escrito à mão.
// Uso: npm run estudos:catalogo
import path from 'node:path'
import { ESTUDOS, h1Titles, isExampleFile, listAreas, listDrafts, listStudyFiles, readText } from './comum.mjs'

const out = ['# Catálogo de estudos', '']

for (const area of listAreas()) {
  const files = listStudyFiles(area)
  out.push(`## ${area}`)
  const byDir = new Map()
  const exampleCounts = new Map()
  for (const file of files) {
    const dir = path.posix.dirname(file)
    // Exemplos aparecem resumidos: a pasta do exemplo e quantos arquivos ela tem.
    const example = file.match(/^(.*?\/(?:exemplos|examples)\/[^/]+)\//)
    if (isExampleFile(file) && example) {
      exampleCounts.set(example[1], (exampleCounts.get(example[1]) ?? 0) + 1)
      continue
    }
    if (!file.endsWith('.md')) {
      if (isExampleFile(file)) exampleCounts.set(dir, (exampleCounts.get(dir) ?? 0) + 1)
      continue
    }
    if (!byDir.has(dir)) byDir.set(dir, [])
    byDir.get(dir).push(file)
  }
  for (const [dir, pages] of byDir) {
    out.push(`- \`${dir}/\``)
    for (const page of pages) {
      const title = h1Titles(readText(path.join(ESTUDOS, page)))[0]?.title ?? '(sem título #)'
      out.push(`  - ${path.posix.basename(page)} — ${title}`)
    }
  }
  for (const [dir, count] of exampleCounts) out.push(`- exemplo \`${dir}/\` (${count} arquivos)`)
  out.push('')
}

const drafts = listDrafts()
const pending = drafts.filter((d) => d.status !== 'documentado')
out.push(`## Rascunhos pendentes (${pending.length} de ${drafts.length})`)
for (const d of pending) out.push(`- ${d.file} — ${d.tema} [${d.status}]${d.area ? ` (área sugerida: ${d.area})` : ''}`)
if (!pending.length) out.push('- nenhum')

console.log(out.join('\n'))
