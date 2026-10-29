// Hook PreToolUse (matcher "Edit|Write"): roda antes de cada edição ou criação de arquivo.
// Impede alterar segredos, o diretório .git e migrações já commitadas.
// Uma migração nova (gerada por alembic revision e ainda não commitada) continua editável.
// O hook só vê as ferramentas Edit e Write: um comando de terminal ainda pode alterar o arquivo.
import { spawnSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import path from 'node:path'

const evento = JSON.parse(readFileSync(0, 'utf8'))
const arquivo = evento.tool_input?.file_path
if (!arquivo) process.exit(0)

const raiz = process.env.CLAUDE_PROJECT_DIR ?? evento.cwd ?? process.cwd()
const relativo = path.relative(raiz, path.resolve(raiz, arquivo)).split(path.sep).join('/')

function bloquear(motivo) {
  console.error(`Edição bloqueada pelo harness: ${relativo} (${motivo}).`)
  process.exit(2)
}

const nome = path.posix.basename(relativo)
if (nome === '.env' || (nome.startsWith('.env.') && nome !== '.env.example')) {
  bloquear('arquivo de segredos; use .env.example com valores fictícios')
}
if (relativo === '.git' || relativo.startsWith('.git/')) {
  bloquear('diretório interno do git')
}
// git cat-file -e sai com 0 se o arquivo existe no último commit.
const commitada = (arquivo) =>
  spawnSync('git', ['cat-file', '-e', `HEAD:${arquivo}`], { cwd: raiz }).status === 0
if (relativo.startsWith('migrations/') && commitada(relativo)) {
  bloquear('migração já commitada não é editada; crie uma nova com alembic revision')
}
process.exit(0)
