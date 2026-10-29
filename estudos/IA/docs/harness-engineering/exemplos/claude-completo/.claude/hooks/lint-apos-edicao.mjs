// Hook PostToolUse (matcher "Edit|Write"): roda logo depois de cada edição.
// O arquivo já foi alterado, então o hook não desfaz nada: ele devolve os problemas
// ao Claude (exit 2 + stderr) para que sejam corrigidos no passo seguinte.
import { spawnSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import path from 'node:path'

const evento = JSON.parse(readFileSync(0, 'utf8'))
const arquivo = evento.tool_input?.file_path
if (!arquivo || !arquivo.endsWith('.py')) process.exit(0)

const raiz = process.env.CLAUDE_PROJECT_DIR ?? evento.cwd ?? process.cwd()
const absoluto = path.resolve(raiz, arquivo)
const relativo = path.relative(raiz, absoluto).split(path.sep).join('/')
const problemas = []

// Regra do projeto (incidente de 2026-10-24): dinheiro não usa float nos serviços.
// Checagem simples por texto: ignora só linhas que são inteiras comentário.
if (relativo.startsWith('app/servicos/')) {
  readFileSync(absoluto, 'utf8')
    .split('\n')
    .forEach((linha, i) => {
      if (/\bfloat\b/.test(linha) && !linha.trim().startsWith('#')) {
        problemas.push(`${relativo}:${i + 1}: use Decimal em vez de float para valores monetários.`)
      }
    })
}

// Lint do arquivo editado. Se o ruff não estiver instalado, esta etapa é pulada sem bloquear.
const ruff = spawnSync('ruff', ['check', absoluto], { encoding: 'utf8' })
if (!ruff.error && ruff.status !== 0) {
  problemas.push(ruff.stdout.trim())
}

if (problemas.length > 0) {
  console.error(problemas.join('\n'))
  process.exit(2)
}
process.exit(0)
