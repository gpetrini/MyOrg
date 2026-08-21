# Kriging & Sobol Resources

## Knowledge

- [Distill: A Visual Exploration of Gaussian Processes — Görtler et al. (2019)](https://distill.pub/2019/visual-explorations-of-gaussian-processes/)
  Artigo interativo com animações. O melhor ponto de entrada visual para intuição
  sobre GPs: prior → posterior, kernels, incerteza. Use para: aula 1 (Kriging).

- [arXiv: An Intuitive Tutorial to Gaussian Process Regression — Wang (2024)](https://arxiv.org/abs/2401.15545)
  Tutorial com código que conecta a matemática à implementação. Use para:
  aprofundar após a lição visual; entender o que `kriging.model.lsd()` faz por dentro.

- [arXiv: Explaining and Connecting Kriging with GPR — Kersaudy et al. (2024)](https://arxiv.org/abs/2408.02331)
  Paper que unifica formalmente Kriging e GP. Use para: entender por que os
  dois nomes coexistem no código e na literatura.

- [LSDsensitivity — CRAN](https://cran.r-project.org/package=LSDsensitivity)
  Documentação oficial do pacote usado no ABM-WTR. Contém o manual das funções
  `kriging.model.lsd()`, `sobol.decomposition.lsd()`, etc. Use para: referência
  técnica ao ler ou modificar o script.

- [Global Sensitivity Analysis: The Primer — Saltelli et al. (2008, Wiley)](https://www.wiley.com/en-us/Global+Sensitivity+Analysis%3A+The+Primer-p-9780470059975)
  Livro-texto de referência para análise de sensibilidade global. Capítulos 2–3
  cobrem a decomposição ANOVA e os índices de Sobol. Use para: fundamentos
  matemáticos rigorosos; justificar escolhas metodológicas no paper.

- [JASSS: Which SA Method Should I Use for My ABM? — Ligmann-Zielinska et al.](https://jasss.soc.surrey.ac.uk/23/4/9.html)
  Revisão prática de métodos de SA especificamente para ABMs. Use para:
  contextualizar por que a abordagem Kriging+Sobol foi escolhida em vez de
  alternativas mais simples.

- [Towards Data Science: Sobol Sensitivity Analysis — Visual guide](https://towardsdatascience.com/sobol-sensitivity-analysis-a-simple-introduction-with-python-4b9f6f5f09fe)
  Explicação visual dos índices de primeira ordem vs. total com exemplos simples.
  Use para: lição 2 (Sobol), para construir intuição antes da matemática formal.

## Wisdom (Communities)

- [JASSS — Journal of Artificial Societies and Social Simulation](https://jasss.soc.surrey.ac.uk/)
  Periódico de referência para validação e SA de ABMs. Fóruns limitados, mas
  os papers têm seções de discussão abertas. Use para: encontrar casos aplicados.

- [r/MachineLearning](https://reddit.com/r/MachineLearning) e
  [r/statistics](https://reddit.com/r/statistics)
  Para questões sobre Gaussian Processes fora do contexto de ABMs.

## Gaps

- Não foi encontrado um tutorial específico para `LSDsensitivity` com
  exemplos passo a passo além do manual CRAN. Se o pacote tiver vignettes,
  verificar: `browseVignettes("LSDsensitivity")` em R.
