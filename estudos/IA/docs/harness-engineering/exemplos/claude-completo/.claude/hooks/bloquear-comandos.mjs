// Hook PreToolUse (matcher "Bash"): roda antes de cada comando de terminal.
// Bloqueia comandos destrutivos e pede confirmação para comandos arriscados.
// Contrato do Claude Code: recebe o evento em JSON pela entrada padrão;
// exit 2 bloqueia e devolve o stderr ao Claude; exit 0 sem saída segue o fluxo normal.
// Os padrões comparam o texto do comando e têm brechas (um script pode fazer o mesmo):
// são uma camada a mais, não substituem permissões e sandbox.
import { readFileSync } from 'node:fs'

// rm recursivo (-r, -rf, -r -f, --recursive) cujo alvo é a raiz ou a pasta do usuário, com ou sem /, /*.
const RM_RAIZ_OU_HOME =
  /\brm\b(?=[^;&|]*\s(-[a-z]*r|--recursive))[^;&|]*\s(\/|~|\$HOME|\$\{HOME\})\/?\*?(?=\s|$|[;&|])/i

const BLOQUEADOS = [
  { padrao: RM_RAIZ_OU_HOME, motivo: 'apagar a raiz ou a pasta do usuário' },
  { padrao: /\bgit\s+push\b.*(--force\b|\s-f\b)/i, motivo: 'push forçado reescreve o histórico remoto' },
  { padrao: /\b(curl|wget)\b[^|]*\|\s*(ba|z)?sh\b/i, motivo: 'executar script baixado da internet' },
  { padrao: /\bdrop\s+(table|database)\b/i, motivo: 'apagar tabela ou banco' },
]

const PEDIR_CONFIRMACAO = [
  { padrao: /\bgit\s+reset\s+--hard\b/i, motivo: 'descarta alterações locais' },
  { padrao: /\balembic\s+downgrade\b/i, motivo: 'desfaz migrações do banco' },
]

const evento = JSON.parse(readFileSync(0, 'utf8'))
const comando = evento.tool_input?.command ?? ''

const bloqueado = BLOQUEADOS.find(({ padrao }) => padrao.test(comando))
if (bloqueado) {
  console.error(`Comando bloqueado pelo harness (${bloqueado.motivo}). Proponha outra forma de chegar ao objetivo.`)
  process.exit(2)
}

const arriscado = PEDIR_CONFIRMACAO.find(({ padrao }) => padrao.test(comando))
if (arriscado) {
  // Em vez de bloquear, devolve a decisão "ask": o Claude Code pergunta ao usuário.
  console.log(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        permissionDecision: 'ask',
        permissionDecisionReason: `Confirme: ${arriscado.motivo}.`,
      },
    }),
  )
}
process.exit(0)
