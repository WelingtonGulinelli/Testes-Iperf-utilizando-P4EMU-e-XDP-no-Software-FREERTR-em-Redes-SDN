# Análise de Desempenho de Rede com iPerf3

Este projeto realiza testes de desempenho de rede utilizando a ferramenta **iPerf3** e fornece scripts Python para análise estatística e visualização dos resultados. Os testes comparam o desempenho de duas tecnologias de rede: **P4EMU** (emulador P4) e **XDP** (eXpress Data Path).

---

## 🎯 Visão Geral

O projeto visa comparar o desempenho de redes implementadas com **P4EMU** e **XDP** em diferentes cenários de vazão (throughput) e protocolos de transporte (TCP e UDP). Para cada configuração, são realizados **30 testes** repetidos para garantir confiabilidade estatística.

### Tecnologias Testadas

- **P4EMU**: Emulador de switches programáveis P4
- **XDP**: Framework de processamento de pacotes de alta performance do kernel Linux

### Protocolos Testados

- **TCP**: Protocolo orientado à conexão com controle de fluxo
- **UDP**: Protocolo sem conexão, ideal para aplicações de tempo real

### Vazões Testadas

- 500 Mbps
- 1 Gbps
- 2 Gbps
- 3 Gbps
- 4 Gbps
- 10 Gbps
- 25 Gbps

---

## 📊 Dados Coletados

### Formato dos Arquivos JSON

Cada teste gera um arquivo JSON com a estrutura do iPerf3, contendo:

#### Metadados do Teste
- **Protocolo**: TCP ou UDP
- **Duração**: 300 segundos (5 minutos)
- **Vazão alvo**: Configurada com o parâmetro `-b`
- **Número de conexões paralelas**: 1 conexão
- **Endereços IP**: Cliente e servidor

#### Dados por Intervalo (1 segundo)
Cada arquivo contém aproximadamente 300 intervalos com:
- `start` e `end`: Tempo do intervalo (segundos)
- `bits_per_second`: Taxa de transferência instantânea
- `bytes`: Total de bytes transferidos no intervalo
- `packets`: Número de pacotes (UDP)
- `lost_packets`: Pacotes perdidos (UDP)
- `retransmits`: Retransmissões (TCP)

#### Dados Agregados (end)
Estatísticas finais do teste completo:
- **sum_received**: Dados recebidos (vazão média, total de bytes/pacotes)
- **sum_sent**: Dados enviados
- **lost_packets** e **lost_percent**: Perda de pacotes (UDP)
- **retransmits**: Total de retransmissões (TCP)

### Arquivo `media_testes.json`

Este arquivo é gerado pelo script `gera_media_testes.py` e contém a **média dos 30 testes** para cada intervalo de 1 segundo, permitindo análise estatística mais confiável.

---

## 🔧 Scripts Disponíveis

### 1. `script_iperf3.py`

**Função**: Executa testes de desempenho de rede usando o iPerf3.

**Características**:
- Executa 30 testes consecutivos automaticamente
- Salva cada teste em um arquivo JSON individual
- Aguarda 10 segundos entre testes para evitar interferência
- Registra logs de execução
- Extrai e exibe a vazão de cada teste

**Configurações Principais**:
```python
SERVIDOR = "10.10.10.10"       # IP do servidor iperf3
DURACAO = 300                  # 5 minutos por teste
CONEXOES = 1                   # 1 conexão paralela
BANDA = "1G"                   # Vazão alvo (500M, 1G, 2G, etc.)
TOTAL_TESTES = 30              # Número de repetições
INTERVALO = 10                 # Segundos entre testes
```

**Como executar**:
```bash
# 1. Edite as configurações no arquivo
# 2. Execute o script
python script_iperf3.py
```

**Saídas**:
- `iperf3_1_1G_01.json`, `iperf3_1_1G_02.json`, ..., `iperf3_1_1G_30.json`
- `iperf3_resumo.log`: Log com resumo de cada teste

---

### 2. `gera_media_testes.py`

**Função**: Calcula a média dos 30 testes repetidos e gera um arquivo JSON consolidado.

**Características**:
- Analisa todos os arquivos JSON de um diretório
- Calcula a média de vazão para cada intervalo de tempo
- Calcula estatísticas de pacotes perdidos (UDP) ou retransmissões (TCP)
- Gera arquivo `media_testes.json` compatível com `analisar_vazao.py`

**Configurações**:
```python
DIRETORIO = "xdp/xdp_1_2G_udp"              # Diretório com os testes
PADRAO = "xdp_1_2G_*.json"                   # Padrão dos arquivos
SAIDA = "media_testes.json"                  # Arquivo de saída
```

**Como executar**:
```bash
# Edite o diretório no arquivo e execute
python gera_media_testes.py
```

**Saídas**:
- `media_testes.json`: Arquivo JSON com as médias calculadas
- Estatísticas impressas no console:
  - Vazão média geral
  - Pacotes perdidos (UDP) ou retransmissões (TCP)
  - Número de testes processados

---

### 3. `gerar_todas_medias.py`

**Função**: Processa automaticamente todos os diretórios de testes e gera um relatório completo.

**Características**:
- Varre os diretórios `p4emu/` e `xdp/` automaticamente
- Processa cada subdiretório e calcula estatísticas
- Gera relatório consolidado em formato JSON
- Exibe resumo comparativo no console

**Como executar**:
```bash
python gerar_todas_medias.py
```

**Saídas**:
- `relatorio_completo_testes.json`: Arquivo com todas as estatísticas
- Relatório detalhado no console com:
  - Vazão média, mínima, máxima e desvio padrão
  - Estatísticas de perda de pacotes (UDP)
  - Estatísticas de retransmissões (TCP)
  - Resumo comparativo entre P4EMU e XDP

---

### 4. `analisar_vazao.py`

**Função**: Gera gráfico de linha mostrando a evolução da vazão ao longo do tempo.

**Características**:
- Lê arquivo `media_testes.json`
- Plota gráfico de vazão (Mbps) vs. tempo (segundos)
- Adiciona linha de média
- Exibe faixa de ±1 desvio padrão
- Calcula e exibe estatísticas descritivas
- Escala do eixo Y ajustável

**Configurações**:
```python
arquivo_json = "p4emu/p4emu_1_3G_udp/media_testes.json"
arquivo_saida = "p4emu/p4emu_1_3G_udp/p4emu_3G_udp.png"
```

**Como executar**:
```bash
# Edite os caminhos dos arquivos e execute
python analisar_vazao.py
```

**Saídas**:
- Gráfico PNG com:
  - Vazão ao longo do tempo
  - Linha de média
  - Faixa de variância (±1σ)
  - Caixa de estatísticas (mínima, máxima, média, variância, desvio padrão)

---

### 5. `analisar_violino.py`

**Função**: Gera gráfico de violino para comparar distribuições de vazão entre múltiplos cenários.

**Características**:
- Compara múltiplos arquivos `media_testes.json`
- Visualiza distribuição, média e mediana
- Ideal para comparar P4EMU vs XDP ou TCP vs UDP
- Exibe estatísticas para cada cenário

**Exemplo de uso**:
```python
arquivos = {
    "P4EMU 2G TCP": "p4emu/p4emu_1_2G_tcp/media_testes.json",
    "P4EMU 2G UDP": "p4emu/p4emu_1_2G_udp/media_testes.json",
    "XDP 2G TCP": "xdp/xdp_1_2G_tcp/media_testes.json",
    "XDP 2G UDP": "xdp/xdp_1_2G_udp/media_testes.json",
}

plotar_grafico_violino(
    arquivos_json=arquivos,
    titulo="Comparação de Vazão: P4EMU vs XDP (2G)",
    arquivo_saida="violino_2g.png"
)
```

**Como executar**:
```bash
# Edite o dicionário de arquivos e execute
python analisar_violino.py
```

**Saídas**:
- Gráfico de violino PNG mostrando:
  - Distribuição de vazão (formato de "violino")
  - Linha vermelha: média
  - Linha verde: mediana
  - Pontos individuais (se poucos dados)
  - Comparação visual entre cenários

---

## 📦 Requisitos

### Software Necessário

- **Python 3.7+**
- **iPerf3**: Ferramenta de teste de rede
  ```bash
  # macOS
  brew install iperf3
  
  # Linux (Debian/Ubuntu)
  sudo apt-get install iperf3
  ```

### Bibliotecas Python

```bash
pip install numpy matplotlib
```

Ou crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install numpy matplotlib
```

---

## 🚀 Como Usar

### Workflow Completo

#### 1. Executar Testes

```bash
# Configure o script_iperf3.py com as configurações desejadas
# (servidor, vazão, protocolo, etc.)
python script_iperf3.py
```

Este script irá:
- Executar 30 testes consecutivos
- Salvar cada teste em um arquivo JSON separado
- Gerar um log resumido

#### 2. Calcular Médias

**Opção A: Um diretório por vez**
```bash
# Edite gera_media_testes.py com o diretório desejado
python gera_media_testes.py
```

**Opção B: Todos os diretórios**
```bash
# Processa automaticamente todos os diretórios
python gerar_todas_medias.py
```

#### 3. Gerar Gráficos

**Gráfico de vazão individual:**
```bash
# Edite analisar_vazao.py com o arquivo de média
python analisar_vazao.py
```

**Gráfico comparativo (violino):**
```bash
# Edite analisar_violino.py com os arquivos a comparar
python analisar_violino.py
```


---



## 📝 Notas Adicionais

### Configuração do iPerf3

- **Servidor**: Execute `iperf3 -s` no host servidor
- **Cliente**: Os testes são executados automaticamente pelo `script_iperf3.py`

### Boas Práticas

1. **Execute os testes em horários consistentes** para evitar variações por carga de rede
2. **Aguarde entre séries de testes** para permitir que o sistema estabilize
3. **Documente as configurações** de hardware e software utilizadas
4. **Repita os testes** em dias diferentes para validar os resultados
5. **Monitore o uso de CPU e memória** durante os testes

### Resolução de Problemas

**Erro de conexão ao servidor iPerf3:**
- Verifique se o servidor está rodando: `iperf3 -s`
- Verifique o firewall e conectividade de rede

**Arquivo JSON inválido:**
- Pode indicar que um teste foi interrompido
- Verifique o `iperf3_resumo.log` para detalhes
- Remova arquivos corrompidos antes de calcular médias

**Gráficos não são gerados:**
- Verifique se as bibliotecas estão instaladas: `pip install numpy matplotlib`
- Confirme que o arquivo `media_testes.json` existe

---

## 👤 Autor

Welington Gulinelli Costa

**Data**: Novembro de 2025

---