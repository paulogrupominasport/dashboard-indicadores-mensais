# 📋 Instruções de Implementação

## 1. Preparar Arquivos

### Local de Trabalho
```bash
# Criar diretório de trabalho
mkdir -p ~/dashboard-indicadores/
cd ~/dashboard-indicadores/

# Copiar arquivos
cp gerar_dados_CORRIGIDO.py gerar_dados.py
cp dados.json ./
cp base.xlsx ./  # seu arquivo Excel
```

## 2. Validar Script Corrigido

### Executar teste rápido
```bash
# Testar se script roda sem erros
python3 gerar_dados.py base.xlsx

# Saída esperada:
# OK -> dados.json
# estoque meses: {...}
# prevReal meses: {...}
# recs compras/exped/serv: 73 52 26
# VISAO meses: ['2026-01', '2026-02', ..., '2026-08']
```

### Se houver erro
```bash
# Ver detalhes do erro
python3 -u gerar_dados.py base.xlsx 2>&1 | tail -20

# Verificar se arquivo Excel está corrompido
python3 << 'EOF'
import pandas as pd
try:
    xls = pd.ExcelFile('base.xlsx')
    print("✓ Arquivo Excel OK")
    print("Abas:", xls.sheet_names)
except Exception as e:
    print("✗ Erro ao abrir Excel:", e)
EOF
```

---

## 3. Integração com Dashboard

### Para HTML/JavaScript Dashboard
```bash
# Copiar dados JSON
cp dados.json /var/www/dashboard/data/
# ou
cp dados.json /home/user/dashboard/assets/

# Verificar acesso no navegador
curl http://seu-servidor/dashboard/data/dados.json | head
```

### Para Dashboard em Python/Flask
```python
# Em seu app.py ou config.py
import json

# Carregar dados
with open('dados.json', 'r', encoding='utf-8') as f:
    DASHBOARD_DATA = json.load(f)

# Usar em templates
@app.route('/api/dados')
def get_dados():
    return DASHBOARD_DATA
```

### Para Power BI / Excel Pivot
```
1. Abrir Excel
2. Dados → De Arquivo → JSON
3. Selecionar dados.json
4. Importar → Tabela ou Pivot Table
```

---

## 4. Validar Dashboard Atualizado

### Checklist Visual
- [ ] Dashboard carrega sem erros no console
- [ ] Números de janeiro até agosto aparecem
- [ ] Gráficos são carregados (não há "NaN" ou "undefined")
- [ ] Filtros funcionam corretamente
- [ ] Usuários aparecem na lista de produtividade

### Verificar Números Específicos
```javascript
// No console do navegador (F12)
// Verificar dados carregados
console.log(data.DATA.expedicoes.length)  // Deve ser: 52
console.log(data.DATA.compras.length)     // Deve ser: 73
console.log(data.DATA.servicos.length)    // Deve ser: 26

// Somar valor de expedições
data.DATA.expedicoes.reduce((sum, r) => sum + r.valor, 0)
// Deve ser próximo de: 1000025976.87
```

---

## 5. Automatizar Execução Mensal

### Opção A: Cron Job (Linux/Mac)
```bash
# Editar crontab
crontab -e

# Adicionar linha (executar todo dia 1º do mês às 08:00)
0 8 1 * * cd ~/dashboard-indicadores && python3 gerar_dados.py base.xlsx && cp dados.json /var/www/dashboard/data/

# Adicionar log
0 8 1 * * cd ~/dashboard-indicadores && python3 gerar_dados.py base.xlsx >> /var/log/dashboard-update.log 2>&1
```

### Opção B: Task Scheduler (Windows)
```cmd
:: Criar arquivo atualizar_dashboard.bat
@echo off
cd C:\dashboard-indicadores
python gerar_dados.py base.xlsx
copy dados.json C:\www\dashboard\data\
echo Atualizado em %date% %time% >> log.txt
```

Depois agendar via Task Scheduler:
1. Win+R → `taskschd.msc`
2. Criar Tarefa Básica
3. Nome: "Atualizar Dashboard Indicadores"
4. Gatilho: Primeira do mês, 08:00
5. Ação: Executar script `atualizar_dashboard.bat`

### Opção C: GitHub Actions (Cloud)
```yaml
# .github/workflows/update-dashboard.yml
name: Atualizar Dashboard
on:
  schedule:
    - cron: '0 8 1 * *'  # 1º de cada mês às 08:00 UTC

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Instalar dependências
        run: pip install pandas openpyxl
      - name: Gerar dados
        run: python gerar_dados.py base.xlsx
      - name: Fazer commit
        run: |
          git config user.name "Dashboard Bot"
          git config user.email "bot@dashboard.local"
          git add dados.json
          git commit -m "Atualizar dados - $(date +%Y-%m-%d)"
          git push
```

---

## 6. Monitorar Qualidade

### Verificação Mensal
```bash
#!/bin/bash
# verificar_dados.sh

python3 << 'EOF'
import json
import sys

with open('dados.json', 'r') as f:
    data = json.load(f)

# Validações
checks = {
    'expedições': len(data['DATA']['expedicoes']) > 0,
    'compras': len(data['DATA']['compras']) > 0,
    'meses': len(data['VISAO']['months']) >= 8,
    'usuários': len(set(
        u['u'] for m in data['VISAO']['months'].values() 
        for u in m['users']
    )) > 5,
    'valor_expedições': sum(r['valor'] for r in data['DATA']['expedicoes']) > 1000000,
}

print("Verificação de Integridade:")
for check, resultado in checks.items():
    status = "✓" if resultado else "✗"
    print(f"  {status} {check}")

# Alertas
if any(r['valor'] < 0 for r in data['DATA']['sobras']):
    print("\n⚠️  ALERTA: Sobra com valor negativo detectada!")

sys.exit(0 if all(checks.values()) else 1)
EOF
```

Adicionar ao cron:
```bash
# Verificar dados depois de atualizar
0 8 1 * * cd ~/dashboard-indicadores && python3 verificar_dados.sh || mail -s "ALERTA: Dashboard não validou" admin@empresa.com
```

---

## 7. Solução de Problemas

### Erro: "CFOp_Código" não encontrado
**Solução:** Verificar se coluna foi renomeada no Excel
```python
import pandas as pd
df = pd.read_excel('base.xlsx', sheet_name='Documentos Emitidos', nrows=1)
print(list(df.columns))  # Ver nomes exatos das colunas
```

### Erro: Valor negativo em sobras
**Investigação:**
1. Abrir Excel
2. Aba "Sobras"
3. Procurar por valores com "-" ou cores vermelhas
4. Verificar com usuário responsável

### Dashboard não atualiza
**Checklist:**
1. [ ] `dados.json` foi gerado sem erros
2. [ ] Arquivo foi copiado para local correto
3. [ ] Navegador foi atualizado (Ctrl+R)
4. [ ] Cache foi limpo (Ctrl+Shift+Del)
5. [ ] JSON é válido: `python3 -m json.tool dados.json > /dev/null`

---

## 8. Documentação de Mudanças

### Alterar gerar_dados.py
Se precisar fazer ajustes futuros:

```python
# Sempre adicionar comentário com data e razão
# 2026-09-09: Adicionado try/except para linhas com CFOP inválido (Issue #42)
try:
    cint=int(c)
except (ValueError, TypeError):
    continue  # Pular linha com dados inválidos

# 2026-09-09: Usar Data_Digitação em vez de Data_Emissão para Docs Lançados
compras,topCom = fin(dl,'Data_Digitação','CFoP_Código',...)
```

### Versionamento
```bash
# Manter histórico de mudanças
git log --oneline
# ou
cp gerar_dados.py gerar_dados_v1.0_2026-09-09.py
```

---

## ✅ Checklist de Implementação

- [ ] Script corrigido testado localmente
- [ ] Dados JSON gerados sem erros
- [ ] Números validados (comparar com números anteriores)
- [ ] Arquivo copiado para servidor/dashboard
- [ ] Dashboard recarregado e testado
- [ ] Agendamento de atualização mensal configurado
- [ ] Log de execução configurado
- [ ] Verificação de integridade configurada
- [ ] Documentação atualizada
- [ ] Usuários notificados sobre mudanças

---

**Pronto? Execute:** `python3 gerar_dados.py base.xlsx`
