import { Navigate, Route, Routes } from 'react-router-dom'
import { getToken } from './api/client'
import './App.css'
import Layout from './components/Layout'
import Denuncia from './pages/Denuncia'
import DenunciasMapa from './pages/DenunciasMapa'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Sobre from './pages/Sobre'
import VerifyEmail from './pages/VerifyEmail'

function PrivateRoute({ children }) {
  const token = getToken()
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/sobre" element={<Sobre />} />
        <Route path="/login" element={<Login />} />
        <Route path="/cadastro" element={<Register />} />
        <Route path="/verificar-email" element={<VerifyEmail />} />
        <Route
          path="/denuncia"
          element={
            <PrivateRoute>
              <Denuncia />
            </PrivateRoute>
          }
        />
        <Route
          path="/denuncia/:id/edit"
          element={
            <PrivateRoute>
              <Denuncia />
            </PrivateRoute>
          }
        />
        <Route
          path="/denuncias"
          element={
            <PrivateRoute>
              <DenunciasMapa />
            </PrivateRoute>
          }
        />
      </Route>
    </Routes>
  )
}
