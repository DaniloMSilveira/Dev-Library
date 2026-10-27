import { defineConfig } from 'vitepress'
import { generateCodePages } from './codigo.mts'
import { REPO_URL } from './estudos.mts'
import { buildNavigation, siteLinks } from './navigation.mts'

const code = generateCodePages()
const { nav, sidebar } = buildNavigation(code)

export default defineConfig({
  lang: 'pt-BR',
  title: 'Dev Library',
  description: 'Biblioteca pessoal de estudos com anotações, trilhas e exemplos práticos.',
  base: '/Dev-Library/',
  srcDir: 'estudos',
  // Arquivos de dados dos exemplos (ex.: base de conhecimento do RAG) não são páginas de estudo.
  srcExclude: ['**/exemplos/*/data/**'],
  cleanUrls: true,
  lastUpdated: true,
  ignoreDeadLinks: [
    // READMEs de exemplos apontam para serviços rodando localmente.
    /^https?:\/\/localhost/,
    // Os exemplos 002-payment-status citados na página 5 de SDD ainda não existem no repositório.
    /002-payment-status/,
  ],

  markdown: {
    config: (md) => md.use(siteLinks(code)),
  },

  themeConfig: {
    nav,
    sidebar,
    socialLinks: [{ icon: 'github', link: REPO_URL }],
    editLink: {
      pattern: `${REPO_URL}/edit/main/estudos/:path`,
      text: 'Editar no GitHub',
    },
    search: {
      provider: 'local',
      options: {
        // Páginas com "search: false" no frontmatter (ex.: código gerado) ficam fora da busca.
        _render(src, env, md) {
          const html = md.render(src, env)
          return env.frontmatter?.search === false ? '' : html
        },
        translations: {
          button: { buttonText: 'Buscar', buttonAriaLabel: 'Buscar' },
          modal: {
            displayDetails: 'Mostrar detalhes',
            resetButtonTitle: 'Limpar busca',
            backButtonTitle: 'Fechar busca',
            noResultsText: 'Nenhum resultado para',
            footer: { selectText: 'abrir', navigateText: 'navegar', closeText: 'fechar' },
          },
        },
      },
    },
    outline: { level: [2, 3], label: 'Nesta página' },
    docFooter: { prev: 'Anterior', next: 'Próxima' },
    lastUpdated: { text: 'Atualizado em' },
    notFound: {
      title: 'Página não encontrada',
      quote: 'O endereço pode ter mudado ou a página ainda não foi escrita.',
      linkText: 'Voltar ao início',
    },
    darkModeSwitchLabel: 'Tema',
    lightModeSwitchTitle: 'Mudar para o tema claro',
    darkModeSwitchTitle: 'Mudar para o tema escuro',
    sidebarMenuLabel: 'Menu',
    returnToTopLabel: 'Voltar ao topo',
  },
})
