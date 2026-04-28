import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import Home from './Home'

vi.mock('../api/client', () => ({
  api: vi.fn(() =>
    Promise.resolve({
      total: 0,
      com_localizacao_mapa: 0,
      minhas: 0,
      por_tipo: [],
      por_mes: [],
      top_empresas: [],
    }),
  ),
  getToken: () => null,
  EQUIVOZ_AUTH_EVENT: 'equivoz-auth-changed',
}))

describe('Home', () => {
  it('renderiza título, links para entrar e criar conta e painel público', async () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'EquiVoz' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Entrar' })).toHaveAttribute('href', '/login')
    expect(screen.getByRole('link', { name: 'Criar conta' })).toHaveAttribute('href', '/cadastro')
    expect(await screen.findByText('Total no sistema')).toBeInTheDocument()
  })
})
