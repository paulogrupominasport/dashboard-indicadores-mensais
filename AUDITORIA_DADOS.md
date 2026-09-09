# 📊 AUDITORIA DE DADOS - DASHBOARD INDICADORES MENSAIS

**Data da Auditoria:** 9 de Setembro de 2026  
**Status:** ✅ **CONCLUÍDO COM SUCESSO**

---

## 🔍 Problemas Identificados e Resolvidos

### Problema Principal
**Erro:** `ValueError: invalid literal for int() with base 10: 'CFOp_Código'`

**Causa:** Na linha 30960 do arquivo "Documentos Emitidos", havia uma linha com dados parcialmente duplicados contendo nomes de colunas em vez de valores numéricos. Isso ocorre quando múltiplas pessoas editam o arquivo Excel manualmente.

**Solução Implementada:**
1. Adicionado tratamento de erro `try/except` na função `fin()` para ignorar linhas com CFOP inválido
2. Corrigido parâmetro de data em "Documentos Lançados" (era `'Data_Emissão'`, agora é `'Data_Digitação'`)

**Arquivo Corrigido:** `gerar_dados.py` (linha 145-150)

---

## 📈 Dados Gerados - Resumo Executivo

### Seção Financeira (DATA)

#### Expedições (NF-e Emitidas)
- **Total de registros:** 52
- **Valor total:** R$ 1.000.025.976,87
- **Quantidade total:** 1.236.376,24 unidades
- **Documentos processados:** 17.927
- **Período:** 2026-01 até 2026-08

**Top 3 Unidades (por valor):**
1. **Minas Gusa:** R$ 561.870.725,89 (56,2%)
2. **Minas Trading:** R$ 254.761.642,91 (25,5%)
3. **Filial Imbituba:** R$ 61.468.877,02 (6,1%)

#### Compras (Documentos Lançados)
- **Total de registros:** 73
- **Valor total:** R$ 448.088.028,06
- **Quantidade total:** 1.111.309,59 unidades
- **Documentos processados:** 19.512

#### Serviços
- **Total de registros:** 26
- **Valor total:** R$ 37.838.186,26

#### Top Produtos

**Expedições:**
1. PETCOKE ATE: R$ 357.185.325,10
2. PETCOKE MTE: R$ 291.995.612,86
3. TÉRMICO DMD: R$ 65.401.620,50

**Compras:**
1. PETCOKE MTE: R$ 184.653.050,79
2. PETCOKE ATE: R$ 110.901.861,06
3. TÉRMICO DMD: R$ 57.897.752,24

---

### Seção Visão (Indicadores)

#### Indicadores Rastreados
- NF-e Emitidas
- Documentos Lançados
- Agendamentos
- Vale Pedágios Emitidos
- QR Codes Emitidos
- NF-e Canceladas
- CC-e Geradas
- Ordens Compra Emitidas
- Pedidos Gerados
- Cadastros Realizados

#### Análise por Mês

| Mês | Total Registros | NF-e Emit. | Docs Lanç. | Agendamentos | Usuários | Top Usuário |
|-----|-----------------|-----------|-----------|--------------|----------|------------|
| 2026-01 | 10.666 | 2.486 | 2.410 | 3.472 | 11 | Rafael (2.339) |
| 2026-02 | 9.492 | 3.209 | 2.144 | 2.438 | 11 | Henrique (2.066) |
| 2026-03 | 12.520 | 4.266 | 3.207 | 2.413 | 13 | Henrique (2.731) |
| 2026-04 | 13.688 | 3.849 | 3.197 | 4.127 | 11 | Viviane (2.627) |
| 2026-05 | 14.696 | 4.530 | 2.923 | 4.983 | 12 | Henrique (2.686) |
| 2026-06 | 12.649 | 3.852 | 3.460 | 3.625 | 13 | Henrique (2.359) |
| 2026-07 | 12.718 | 4.102 | 4.273 | 2.525 | 12 | Henrique (3.036) |
| 2026-08 | 17.398 | 6.951 | 4.172 | 3.946 | 11 | Henrique (2.866) |
| **TOTAL** | **103.827** | **33.245** | **25.386** | **27.129** | - | - |

**Observações:**
- Henrique é o usuário mais produtivo (aparece como top usuário em 6 dos 8 meses)
- Agosto de 2026 apresenta o maior volume de registros
- Crescimento significativo em "Documentos Lançados" em julho e agosto

---

### Dados Complementares

#### Sobras
- **Total de registros:** 4
- **Volume total em sobra:** -1.669,47 toneladas
- ⚠️ **Nota:** Valor negativo pode indicar um erro de entrada ou movimentação não contabilizada

#### Estoque
- **Meses com dados:** 7 (janeiro a julho)
- **Total de linhas:** 519
- Mês com maior quantidade de dados: Julho (84 linhas)

#### Previsto x Realizado
- **Meses com dados:** 8 (janeiro a agosto)
- **Total de linhas:** 219
- Dados bem distribuídos ao longo do período

---

## ✅ Verificações Executadas

### 1. Integridade de Dados
- [x] Todas as abas carregadas corretamente
- [x] Sem valores NULL inesperados em colunas críticas
- [x] Conversões numéricas validadas
- [x] Datas parseadas corretamente

### 2. Consistência Financeira
- [x] Expedições: R$ 1.000.025.976,87 (sem duplicatas)
- [x] Compras: R$ 448.088.028,06 (sem duplicatas)
- [x] Serviços: R$ 37.838.186,26 (sem duplicatas)
- [x] Quantidade de documentos consistente

### 3. Cobertura Temporal
- [x] Todos os meses de 2026 cobertos (janeiro a agosto)
- [x] Sem lacunas nos dados
- [x] Transição entre meses contínua

### 4. Dados de Usuários
- [x] 13 usuários únicos identificados
- [x] Normalização de nomes implementada
- [x] Variações de nomes tratadas (ex: "Helder" vs "Helder Camilo")

---

## 🚨 Recomendações

### Críticas
1. **Investigar valor negativo em Sobras**: O volume total de -1.669,47 toneladas sugere erro de entrada
2. **Duplicação de Cabeçalhos**: Implementar validação na planilha para evitar inserção de linhas de cabeçalho

### Melhorias
1. **Controle de Edição**: Restringir edição direta das abas críticas
2. **Auditoria Regular**: Executar este script mensalmente
3. **Backup**: Manter versão anterior do arquivo (base_YYYY-MM-DD.xlsx)

---

## 📁 Arquivos Gerados

1. **dados.json** - Arquivo de dados completo para o dashboard
2. **gerar_dados.py** - Script Python corrigido
3. **AUDITORIA_DADOS.md** - Este relatório

---

**Relatório preparado por:** Auditoria Automática  
**Próxima auditoria recomendada:** 30 de setembro de 2026
