import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <h1>Sistema de Laudos</h1>
      <p>Ferramenta de Geolocalização - MVP</p>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          Count: {count}
        </button>
        <p>
          Status: ✅ Frontend está rodando!
        </p>
      </div>
    </div>
  )
}

export default App
