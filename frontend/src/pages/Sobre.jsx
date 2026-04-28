import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Sobre() {
  const loggedIn = useAuth()

  return (
    <div className="page page--sobre">
      <header className="sobre-hero">
        <h1 id="page-title">Sobre o EquiVoz</h1>
        <p className="lead sobre-lead">
          O EquiVoz é uma plataforma para <strong>registro de ocorrências</strong> relacionadas à
          discriminação, violações de direitos e desigualdades que afetam, em especial, minorias
          sociais. A ideia é transformar relatos em <strong>informação visível</strong> para
          apoiar debates, políticas públicas e ações de defesa de direitos.
        </p>
      </header>

      <section className="sobre-section" aria-labelledby="sobre-objetivo">
        <h2 id="sobre-objetivo">O que buscamos</h2>
        <ul className="sobre-lista">
          <li>
            <strong>Visibilizar padrões</strong> — agregar denúncias por tipo, região e contexto, sem
            expor dados pessoais desnecessários na visão pública.
          </li>
          <li>
            <strong>Facilitar o registro</strong> — formulário acessível, com opção de local no mapa
            e apoio de endereço (geocodificação), em português do Brasil.
          </li>
          <li>
            <strong>Respeitar quem relata</strong> — o conteúdo das ocorrências é tratado de forma
            seriada; quem cria a denúncia pode editar ou excluir o que registrou.
          </li>
        </ul>
      </section>

      <section className="sobre-section" aria-labelledby="sobre-dados">
        <h2 id="sobre-dados">Dados e transparência</h2>
        <p>
          O <strong>painel com estatísticas agregadas</strong> (totais, tendências por mês, tipos de
          violação e estabelecimentos com mais relatos) é <strong>público</strong> — qualquer pessoa
          pode consultá-lo na página inicial, sem precisar de conta. Já a <strong>lista completa e o
          mapa</strong> das ocorrências ficam restritos a usuários autenticados, equilibrando
          transparência com o cuidado devido aos relatos.
        </p>
      </section>

      <section className="sobre-section" aria-labelledby="sobre-acessivel">
        <h2 id="sobre-acessivel">Acessibilidade e inclusão</h2>
        <p>
          O sistema foi pensado para ser usado com <strong>teclado</strong> e com{' '}
          <strong>leitores de tela</strong>: atalho para pular para o conteúdo, rótulos em
          formulários, regiões e mensagens de estado anunciadas de forma adequada. No menu
          fixo no <strong>lado direito</strong> da tela, o botão <strong>Cores</strong> alterna para
          uma paleta com tons de azul, laranja e violeta mais fáceis de distinguir para muitas
          pessoas com daltonismo; a escolha fica guardada neste aparelho.
        </p>
        <p>
          A evolução contínua depende de testes com pessoas reais; se algo não funcionar bem
          para você, o feedback é bem-vindo.
        </p>
      </section>

      <section className="sobre-section" aria-labelledby="sobre-participar">
        <h2 id="sobre-participar">Como participar</h2>
        <p>
          Pode acompanhar as <Link to="/">estatísticas públicas</Link> a qualquer momento. Para
          registrar uma ocorrência ou consultar o mapa e a lista completa, é preciso estar
          autenticado.
        </p>
        <p>
          {loggedIn ? (
            <>
              Use <strong>Nova denúncia</strong> ou <strong>Todas as denúncias</strong> no menu
              acima.
            </>
          ) : (
            <>
              <Link to="/cadastro">Crie uma conta</Link> ou <Link to="/login">entre</Link> para
              começar.
            </>
          )}
        </p>
        <p className="sobre-cta">
          {loggedIn ? (
            <>
              <Link to="/denuncia" className="btn primary">
                Nova denúncia
              </Link>
              <Link to="/" className="btn secondary">
                Ver painel público
              </Link>
            </>
          ) : (
            <>
              <Link to="/cadastro" className="btn primary">
                Criar conta
              </Link>
              <Link to="/login" className="btn secondary">
                Entrar
              </Link>
              <Link to="/" className="btn secondary">
                Estatísticas na página inicial
              </Link>
            </>
          )}
        </p>
      </section>
    </div>
  )
}
