/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [size, setSize] = useState(4);
  const [matrix, setMatrix] = useState([]);
  const [mode, setMode] = useState('min');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const newMatrix = Array(size).fill(0).map(() => Array(size).fill(0));
    setMatrix(newMatrix);
    setStatus(null);
  }, [size]);

  const handleCellChange = (r, c, value) => {
    const newMatrix = [...matrix];
    newMatrix[r][c] = value === '' ? 0 : Number(value);
    setMatrix(newMatrix);
    setStatus(null);
  };

  const fillRandom = () => {
    const newMatrix = matrix.map(row => row.map(() => Math.floor(Math.random() * 50) + 1));
    setMatrix(newMatrix);
    setStatus(null);
  };

  /*const initAlgo = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/init', { matrix, mode });
      setStatus({ ...res.data, original_matrix: JSON.parse(JSON.stringify(matrix)) });
    } catch (e) {
      alert("Erreur : Vérifiez que le serveur Python (FastAPI) est lancé sur le port 8000");
    } finally {
      setLoading(false);
    }
  };*/
  const initAlgo = async () => {
    // If status exists → Réinitialiser
    if (status) {
      window.location.reload();
      return;
    }

    // Otherwise → Initialiser
    setLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/init', { matrix, mode });
      setStatus({ ...res.data, original_matrix: JSON.parse(JSON.stringify(matrix)) });
    } catch (e) {
      alert("Erreur : Vérifiez que le serveur Python (FastAPI) est lancé sur le port 8000");
    } finally {
      setLoading(false);
    }
  };

  const nextStep = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/next');
      setStatus(prev => ({ ...res.data, original_matrix: prev.original_matrix }));
    } catch (e) {
      alert("Erreur lors de l'appel de l'étape suivante");
    }
  };

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <div className="logo">
          <h2>OptiSolver</h2>
          <span>Algorithme Hongrois</span>
        </div>

        <div className="config-section">
          <div className="input-group">
            <label>Taille de la Matrice</label>
            <input type="number" min="2" max="10" value={size} onChange={(e) => setSize(Number(e.target.value))} />
          </div>

          <div className="input-group">
            <label>Objectif</label>
            <select value={mode} onChange={(e) => setMode(e.target.value)}>
              <option value="min">Minimisation</option>
              <option value="max">Maximisation</option>
            </select>
          </div>
          
          
        </div>

        <div className="control-actions">
          <button className="btn-primary" onClick={initAlgo} disabled={loading}>
            {status ? "Réinitialiser" : "Initialiser"}
          </button>
          
          {status && (
            <button className="btn-success" onClick={nextStep} disabled={status.finished}>
              {status.finished ? "Solution Trouvée" : "Étape Suivante"}
            </button>
          )}
        </div>
      </aside>

      <main className="main-content">
        <header className="top-bar">
          <div className="status-text">
            {status ? `Étape : ${status.step}` : "Configurez votre matrice"}
          </div>
          <div className="legend-pills">
            <span className="pill pill-box">Encadré</span>
            <span className="pill pill-cross">Barré</span>
            <span className="pill pill-cover">Couvert</span>
          </div>
        </header>

        <div className="matrix-wrapper">
          <table>
            <tbody>
              {matrix.map((row, i) => (
                <tr key={i} className={status?.row_covered?.[i] ? "row-covered" : ""}>
                  {row.map((val, j) => {
                    const currentVal = status?.matrix ? status.matrix[i][j] : val;
                    const mark = status?.marked?.[i]?.[j];
                    return (
                      <td key={j} className={`
                        ${status?.col_covered?.[j] ? "col-covered" : ""} 
                        ${mark === 1 ? "cell-selected" : ""} 
                        ${mark === 2 ? "cell-muted" : ""}
                      `}>
                        <input
                          type="number"
                          value={currentVal}
                          readOnly={!!status}
                          onChange={(e) => handleCellChange(i, j, e.target.value)}
                        />
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {status?.finished && (
          <div className="results-panel">
            <h3>Résultat Final</h3>
            <div className="assignments">
              {status.assignments.map((a, idx) => (
                <div key={idx} className="item">
                  Ouvrier {a.worker} ➔ Job {a.job}
                </div>
              ))}
            </div>
            <div className="total">Coût Total : {status.total_cost}</div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
