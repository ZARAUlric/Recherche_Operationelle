import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HungarianSolver:
    def __init__(self, matrix: np.ndarray, mode: str = "min"):
        self.C_orig = np.array(matrix, dtype=float)
        self.n = self.C_orig.shape[0]
        # Étape 1 du PDF : On gère le Max en prenant le complément (ex: 100 - val) 
        # ou Max - val. Ici on utilise Max - val pour la minimisation.
        if mode == "max":
            self.C = np.max(self.C_orig) - self.C_orig
        else:
            self.C = self.C_orig.copy()
            
        self.row_covered = np.zeros(self.n, dtype=bool)
        self.col_covered = np.zeros(self.n, dtype=bool)
        self.marked = np.zeros((self.n, self.n), dtype=int) # 1: Encadré, 2: Barré (visuel)
        self.step = 1
        self.finished = False

    def run_next(self):
        if self.step == 1: self._step1()
        elif self.step == 2: self._step2()
        elif self.step == 3: self._step3()
        elif self.step == 4: self._step4()
        elif self.step == 5: self._step5()

    def _step1(self):
        """ PDF ETAPE 1 : Obtention des zéros par rangée et colonne. """
        # Moins le min par ligne
        self.C -= self.C.min(axis=1)[:, np.newaxis]
        # Moins le min par colonne
        self.C -= self.C.min(axis=0)[np.newaxis, :]
        self.step = 2

    def _step2(self):
        """ PDF ETAPE 2 : Détermination du couplage optimal (Encadrer/Barrer). """
        self.marked = np.zeros((self.n, self.n), dtype=int)
        temp_row_cov = np.zeros(self.n, dtype=bool)
        temp_col_cov = np.zeros(self.n, dtype=bool)

        while True:
            # a) Chercher la ligne avec le MOINS de zéros libres
            min_zeros = self.n + 1
            best_row = -1
            
            for r in range(self.n):
                if not temp_row_cov[r]:
                    count = 0
                    for c in range(self.n):
                        if self.C[r, c] == 0 and not temp_col_cov[c]:
                            count += 1
                    if 0 < count < min_zeros:
                        min_zeros = count
                        best_row = r
            
            if best_row == -1: break # Plus de zéros à traiter

            # b) Encadrer le premier zéro de cette ligne
            for c in range(self.n):
                if self.C[best_row, c] == 0 and not temp_col_cov[c]:
                    self.marked[best_row, c] = 1 # Encadrer
                    temp_row_cov[best_row] = True # Bloquer ligne
                    temp_col_cov[c] = True # Bloquer colonne
                    
                    # Barrer visuellement les autres zéros sur la même ligne/colonne
                    for i in range(self.n):
                        if self.C[best_row, i] == 0 and i != c: self.marked[best_row, i] = 2
                        if self.C[i, c] == 0 and i != best_row: self.marked[i, c] = 2
                    break
        
        # Vérification si l'affectation est complète
        if np.sum(self.marked == 1) == self.n:
            self.step = 5 # Terminé
            self.finished = True
        else:
            self.step = 3 # Passer au marquage des lignes/colonnes (couverture)
            
    def _step3(self):
        """ ETAPE 3 : Couverture par le nombre minimal de lignes. """
        # On utilise ici l'algorithme de marquage de Konig
        self.row_covered[:] = False
        self.col_covered[:] = False
        
        marked_rows = np.ones(self.n, dtype=bool) # Lignes sans zéro encadré
        for r in range(self.n):
            if 1 in self.marked[r, :]: marked_rows[r] = False
            
        marked_cols = np.zeros(self.n, dtype=bool)
        
        changed = True
        while changed:
            changed = False
            # Marquer colonnes ayant un zéro barré dans une ligne marquée
            for r in range(self.n):
                if marked_rows[r]:
                    for c in range(self.n):
                        if self.C[r, c] == 0 and not marked_cols[c]:
                            marked_cols[c] = True
                            changed = True
            # Marquer lignes ayant un zéro encadré dans une colonne marquée
            for c in range(self.n):
                if marked_cols[c]:
                    for r in range(self.n):
                        if self.marked[r, c] == 1 and not marked_rows[r]:
                            marked_rows[r] = True
                            changed = True
        
        # On couvre les lignes NON marquées et les colonnes MARQUÉES
        self.row_covered = ~marked_rows
        self.col_covered = marked_cols
        self.step = 4

    def _step4(self):
        """ PDF ETAPE 4 : Transformation de la matrice. """
        uncovered_vals = []
        for r in range(self.n):
            if not self.row_covered[r]:
                for c in range(self.n):
                    if not self.col_covered[c]:
                        uncovered_vals.append(self.C[r, c])
        
        if not uncovered_vals: return
        
        m = min(uncovered_vals)
        for r in range(self.n):
            for c in range(self.n):
                if not self.row_covered[r] and not self.col_covered[c]:
                    self.C[r, c] -= m
                if self.row_covered[r] and self.col_covered[c]:
                    self.C[r, c] += m
        self.step = 2 # Retour à l'encadrement

    def _step5(self):
        self.finished = True

# --- API ---

class MatrixInput(BaseModel):
    matrix: List[List[float]]
    mode: Optional[str] = "min"

class State:
    solver = None

@app.post("/init")
async def init_matrix(data: MatrixInput):
    State.solver = HungarianSolver(np.array(data.matrix), mode=data.mode)
    return {"status": "Initialisé", "matrix": State.solver.C.tolist()}

@app.get("/next")
async def next_step():
    if not State.solver: return {"error": "Init first"}
    State.solver.run_next()
    s = State.solver
    
    assignments = []
    total_cost = 0
    if s.finished:
        for r in range(s.n):
            for c in range(s.n):
                if s.marked[r, c] == 1:
                    cost = float(s.C_orig[r, c])
                    total_cost += cost
                    assignments.append({"worker": r+1, "job": c+1, "cost": cost})

    return {
        "matrix": s.C.tolist(),
        "row_covered": s.row_covered.tolist(),
        "col_covered": s.col_covered.tolist(),
        "marked": s.marked.tolist(), # 1: Encadré, 2: Barré
        "step": s.step,
        "finished": s.finished,
        "assignments": sorted(assignments, key=lambda x: x['worker']),
        "total_cost": total_cost
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)