# Exposure Fusion: studio e implementazione

Repository per lo studio e l'implementazione in Python dell'algoritmo
**Exposure Fusion** di Tom Mertens, Jan Kautz e Frank Van Reeth.

L'obiettivo e mostrare il procedimento algoritmico in modo esplicito: calcolo
delle mappe di peso, normalizzazione, costruzione delle piramidi Gaussiane e
Laplaciane, fusione multirisoluzione e ricostruzione dell'immagine finale.

## File principali

- `exposure_fusion_study.ipynb`: notebook principale da usare per presentare lo
  studio e l'implementazione. Usa il caso `venice_carnival`, scelto perche nel
  materiale del paper sono presenti anche le mappe dei pesi di riferimento.
- `exposure_fusion_core/`: package Python con l'implementazione riusabile.
- `main.py`: entry point CLI che richiama `exposure_fusion_core.cli`.
- `paper.md` e `paper.pdf`: relazione tecnica in formato Markdown/PDF.
- `paper_sets.toml`: descrizione dei dataset usati per paper e artefatti.
- `Justfile`: comandi di sviluppo per rigenerare risultati, asset e PDF.

I notebook storici `sample.ipynb` ed `exposure_fusion_clean.ipynb`, se presenti,
sono materiale intermedio e non sono l'entry point consigliato.

## Setup

Il progetto usa `uv` per gestire ambiente e dipendenze.

```bash
uv venv
source .venv/bin/activate
uv sync
```

Per generare `paper.pdf` servono anche `pandoc` e una distribuzione LaTeX con
`xelatex` disponibile nel `PATH`.

## Eseguire il notebook

Per aprire il notebook principale:

```bash
uv run jupyter lab exposure_fusion_study.ipynb
```

Il notebook e pensato per essere letto ed eseguito dall'inizio alla fine. Le
funzioni principali sono riscritte dentro il notebook per rendere chiaro il
percorso implementativo, invece di usare il package come black box.

## Eseguire l'implementazione da CLI

Esempio diretto su `venice_carnival`:

```bash
uv run python main.py \
  --inputs images/venice_carnival/A.jpg images/venice_carnival/B.jpg images/venice_carnival/C.jpg \
  --reference images/venice_carnival/result.jpg \
  --output-dir images/venice_carnival/out \
  --save-all \
  --save-process \
  --preview
```

La CLI salva, a seconda delle opzioni:

- input LDR in `out/ldr/`;
- mappe dei pesi in `out/weights/`;
- risultato finale `fused_image.jpg`;
- confronto con riferimento `comparison.jpg`;
- diagramma del processo `process_diagram.jpg`;
- anteprime aggregate quando si usa `--preview`.

## Comandi Just utili

Elenco completo:

```bash
just --list
```

Esecuzione dei dataset principali:

```bash
just fuse-venice-carnival
just process-venice-carnival

just fuse-venice-boat
just process-venice-boat

just fuse-living-room-window
just process-living-room-window
```

Rigenerare tutte le immagini necessarie al PDF:

```bash
just paper-assets
```

Generare il PDF della relazione:

```bash
just paper-pdf
```

Rigenerare asset e PDF insieme:

```bash
just paper
```

## Struttura dell'algoritmo

L'implementazione segue il nucleo del paper:

1. **Contrasto**: risposta assoluta di un filtro Laplaciano su grayscale.
2. **Saturazione**: deviazione standard dei canali RGB.
3. **Well-exposedness**: Gaussiana centrata in `0.5`, applicata ai canali RGB e
   moltiplicata sui canali.
4. **Peso finale**:

   ```text
   W = C^omega_C * S^omega_S * E^omega_E
   ```

5. **Normalizzazione pixel-wise** dei pesi lungo la sequenza di immagini.
6. **Fusione multirisoluzione**:
   - piramidi Laplaciane per le immagini;
   - piramidi Gaussiane per i pesi;
   - blending livello per livello;
   - collasso della piramide fusa.

## Note sull'uso di Codex

Parte del codice, del refactor del package, della relazione e della
documentazione e stata sviluppata con supporto di programmazione automatica
tramite Codex. Le scelte algoritmiche, la verifica dei risultati e
l'organizzazione finale del progetto sono state revisionate manualmente
dall'autore.
