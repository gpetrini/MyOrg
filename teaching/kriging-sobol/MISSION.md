# Mission: Kriging & Sobol Sensitivity Analysis

## Why

Você trabalha com o ABM-WTR (modelo K+S com regime WTR) e o pipeline de análise
de sensibilidade (`KS-kriging-sobol-SA.R`) já está rodando. O problema é que,
ao apresentar os resultados para o orientador ou coautores, você precisa defender
*o que os números significam* — não apenas mostrá-los. Isso exige entender o que
um índice de Sobol de 0.6 quer dizer, quando confiar (ou não) numa superfície
Kriging, e por que o Q² importa antes de qualquer leitura.

## Success looks like

- Dado um PDF de output do script, conseguir explicar oralmente cada tabela e
  gráfico sem consultar nenhum material.
- Saber diagnosticar um Q² baixo: distinguir "preciso de mais replicatas" de
  "preciso de mais pontos de design".
- Conseguir justificar por que o índice *total* de Sobol é o reportável num
  modelo não-linear, e não o de primeira ordem.
- Entender o que muda (e o que não muda) se trocar o kernel do Kriging
  (Matérn 5/2 vs. Gaussiano).
- Ser capaz de escrever um parágrafo de metodologia para um paper descrevendo
  o pipeline completo.

## Constraints

- Formação em economia heterodoxa — matemática de nível pós-graduação, mas sem
  background em estatística espacial ou machine learning.
- Tempo curto por sessão; lições devem ser completáveis em 15–20 minutos.
- O contexto sempre é o ABM-WTR: exemplos abstratos sem conexão com o projeto
  têm valor limitado.

## Out of scope

- Implementar Kriging do zero em R ou Python (o pacote LSDsensitivity já faz isso).
- Comparar com outros meta-modelos (polinômio de caos, redes neurais, etc.).
- Análise de sensibilidade de Morris em profundidade (já coberta por outro script).
