// Hook SessionStart: roda quando uma sessão começa.
// O que este hook imprime na saída padrão entra no contexto do Claude, então ele
// resume a feature ativa e a última entrada do progresso. O CLAUDE.md continua
// pedindo a leitura completa dos arquivos; aqui é só o ponto de partida.
import { existsSync, readFileSync } from 'node:fs'
import path from 'node:path'

const raiz = process.env.CLAUDE_PROJECT_DIR ?? process.cwd()
const linhas = []

const arquivoFeatures = path.join(raiz, 'feature_list.json')
if (existsSync(arquivoFeatures)) {
  const { features = [] } = JSON.parse(readFileSync(arquivoFeatures, 'utf8'))
  const ativa =
    features.find((f) => f.status === 'em_andamento') ??
    features.filter((f) => f.status === 'pendente').sort((a, b) => a.prioridade - b.prioridade)[0]
  linhas.push(ativa ? `Feature da vez: ${ativa.id} (${ativa.status}) - ${ativa.descricao}` : 'Nenhuma feature pendente.')
}

const arquivoProgresso = path.join(raiz, 'progresso.md')
if (existsSync(arquivoProgresso)) {
  const ultimaEntrada = readFileSync(arquivoProgresso, 'utf8').split(/\n(?=## )/)[1]
  if (ultimaEntrada) linhas.push(`Última entrada de progresso.md:\n${ultimaEntrada.trim()}`)
}

if (linhas.length > 0) console.log(linhas.join('\n\n'))
process.exit(0)
