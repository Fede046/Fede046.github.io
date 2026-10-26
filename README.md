# Federico Malservigi

Il mio sito personale: https://fede046.github.io

- `site.yaml`: il sito in inglese (la pagina principale); `site.it.yaml`: i testi in italiano (`it.html`).
- `projects.yaml` / `projects.it.yaml`: la pagina dei progetti (`projects.html`, `projects.it.html`). Le schermate
  di Daycast in `inputs/daycast/` sono della sua modalità `--demo`: dati di esempio.
- `style.css`: i tocchi aggiunti al tema (ornamenti, capolettera, le radici dietro la pagina).
- `tools/radici.py`: genera le radici, `inputs/radici-pagina.svg` per la home e `radici-margini.svg` per le altre pagine.
- `inputs/`: foto, video e radici.
- `docs/`: il sito pubblicato, servito da GitHub Pages (branch `main`, cartella `/docs`).

Il sito è costruito con [Scroll Studio](https://github.com/Okohedeki/scroll-studio) (licenza MIT, il cui
avviso viaggia con il runtime in `docs/runtime/LICENSE.txt`). Dalla cartella di Scroll Studio:

```bash
studio build ../Fede046.github.io
studio publish ../Fede046.github.io --out ../Fede046.github.io/docs --flat
```
