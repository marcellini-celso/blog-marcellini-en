# Marcellini's Blog (EN)

This is the repository for my personal blog, created with [Quarto](https://quarto.org/). Here I share content on statistics, mathematics, programming, and physics, with a focus on clear explanations and practical examples.

---

## 📚 Featured posts

*A selection (most originals are currently in PT; EN versions are being added progressively):*

- [📘 🧮 Beauty is the First Test — G. H. Hardy and Mathematics as Art](https://blogdomarcellini.com.br/posts/matematica/beleza-matematica.html) _(PT)_
- [📘 🧮 Why is \( 0! = 1 \)?](https://blogdomarcellini.com.br/posts/matematica/fatorial-zero.html) _(PT)_
- [📘 🧬 100 Years of Quantum Mechanics (1925–2025)](https://blogdomarcellini.com.br/posts/fisica/100-anos-mecanica-quantica.html) _(PT)_
- [🧭 📚 🧬 Reading Guide — 100 Years of Quantum Mechanics Series](https://blogdomarcellini.com.br/posts/fisica/guia-100-anos-mecanica-quantica.html) _(PT)_
- [🎓 📊 Statistics Course: The Normal Distribution (Part 1)](https://blogdomarcellini.com.br/posts/estatistica/distribuicao-normal.html) _(PT)_
- [📘 👨‍💻 📄 Quarto Markdown Template – Part 2](https://blogdomarcellini.com.br/posts/programacao/outros-modelos-markdown.html) _(PT)_

---

## ⚙️ How this blog is built

- Built with [Quarto](https://quarto.org/)
- Published via **GitHub Pages**
- Code examples in **R**, **Python**, and **LaTeX**
- Theme: `cosmo`, with customizations in `styles.css`

---

## 🚀 Workflow to update and publish

### 1) Update content locally

Run the full-update script:

```bash
./update_all.sh



## Home page

The home uses assets/css/homepage.css and assets/css/banner-v2.css, matching the Portuguese edition, including its mobile banner. Featured links reflect the content currently available in English.

Run bash atualizar-ultimos-posts.sh to refresh the separate lists of six recent articles and six course lessons from source publication dates. This command is also called by atualizar_tudo.sh. The generator requires PyYAML and skips drafts and reading-guide indexes.
