import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { setToken } from '../api/client'
import { useColorMode } from '../context/ColorModeContext'
import { useAuth } from '../hooks/useAuth'
import { useUser } from '../hooks/useUser'

export default function Layout() {
  const navigate = useNavigate()
  const location = useLocation()
  const loggedIn = useAuth()
  const { user } = useUser()
  const { toggleDaltonismo, isDaltonismo } = useColorMode()
  const mainWide =
    location.pathname === '/' || location.pathname === '/denuncias' || location.pathname === '/sobre'
  const mainClass = mainWide ? 'main main--wide' : 'main'

  function logout() {
    setToken(null)
    navigate('/', { replace: true })
  }

  function irParaConteudo(e) {
    e.preventDefault()
    document.getElementById('conteudo-principal')?.focus()
  }

  const { pathname } = location

  return (
    <div className="app-shell">
      <a href="#conteudo-principal" className="skip-link" onClick={irParaConteudo}>
        Pular para o conteúdo
      </a>
      <header className="topbar">
        <Link
          to="/"
          className="brand"
          aria-label="EquiVoz — início"
          aria-current={pathname === '/' ? 'page' : undefined}
        >
          EquiVoz
        </Link>
        <nav className="nav" aria-label="Navegação principal">
          {loggedIn && user?.name ? (
            <span className="topbar-welcome" title={user.name}>
              Bem-vindo, {user.name}
            </span>
          ) : null}
          <Link to="/sobre" aria-current={pathname === '/sobre' ? 'page' : undefined}>
            Sobre
          </Link>
          {loggedIn ? (
            <>
              <Link
                to="/denuncia"
                aria-current={pathname === '/denuncia' ? 'page' : undefined}
              >
                Nova denúncia
              </Link>
              <Link
                to="/denuncias"
                aria-current={pathname === '/denuncias' ? 'page' : undefined}
              >
                Todas as denúncias
              </Link>
              <button type="button" className="linkish" onClick={logout}>
                Sair
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                aria-current={pathname === '/login' ? 'page' : undefined}
              >
                Entrar
              </Link>
              <Link
                to="/cadastro"
                className="pill"
                aria-current={pathname === '/cadastro' ? 'page' : undefined}
              >
                Cadastro
              </Link>
            </>
          )}
        </nav>
      </header>
      <button
        type="button"
        className="color-mode-fab"
        onClick={toggleDaltonismo}
        aria-pressed={isDaltonismo}
        aria-label={
          isDaltonismo
            ? 'Voltar às cores padrão do site'
            : 'Ativar paleta de cores mais distintas para daltonismo'
        }
        title={
          isDaltonismo
            ? 'Voltar às cores padrão'
            : 'Cores mais distintas para daltonismo (protanopia / deuteranopia)'
        }
      >
        {isDaltonismo ? 'Padrão' : 'Cores'}
      </button>
      <main id="conteudo-principal" className={mainClass} tabIndex={-1}>
        <Outlet />
      </main>
      <footer className="footer" role="contentinfo">
        <p>© {new Date().getFullYear()} EquiVoz. Todos os direitos reservados.</p>
      </footer>
    </div>
  )
}
