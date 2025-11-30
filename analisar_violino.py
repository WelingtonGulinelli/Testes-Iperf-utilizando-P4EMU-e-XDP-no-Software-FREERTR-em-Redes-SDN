# salvar como: analisar_violino.py

import json
import matplotlib.pyplot as plt
import numpy as np

def plotar_grafico_violino(arquivos_json, titulo="Comparação de Vazão - Gráfico de Violino", arquivo_saida="grafico_violino.png"):
    """
    Lê múltiplos arquivos JSON de resultado do iperf3 e gera um gráfico de violino
    comparando as distribuições de vazão (throughput) entre diferentes cenários.
    
    Args:
        arquivos_json (dict): Dicionário com labels como chaves e caminhos de arquivo como valores
                             Exemplo: {"P4EMU TCP": "p4emu/p4emu_1_1G_tcp/media_testes.json"}
        titulo (str): Título do gráfico
        arquivo_saida (str): Caminho para salvar o gráfico
    """
    print(f"Lendo os arquivos de dados do iperf3...")

    dados_vazao = []
    labels = []
    
    for label, arquivo_json in arquivos_json.items():
        try:
            with open(arquivo_json, 'r') as f:
                dados = json.load(f)
        except FileNotFoundError:
            print(f"AVISO: O arquivo '{arquivo_json}' não foi encontrado. Pulando...")
            continue
        except json.JSONDecodeError:
            print(f"AVISO: O arquivo '{arquivo_json}' contém um JSON inválido. Pulando...")
            continue

        # Valida se os dados de 'intervals' existem
        if 'intervals' not in dados:
            print(f"AVISO: O arquivo '{arquivo_json}' não contém a seção 'intervals'. Pulando...")
            continue

        # Extrai os dados dos intervalos do teste
        intervalos = dados['intervals']
        bits_por_segundo = [intervalo['sum']['bits_per_second'] for intervalo in intervalos]
        
        # Converte bits por segundo para Megabits por segundo (Mbps)
        mbps = np.array([bps / 1_000_000 for bps in bits_por_segundo])
        
        dados_vazao.append(mbps)
        labels.append(label)
        
        # Imprime estatísticas para cada dataset
        print(f"\n📊 Estatísticas para {label}:")
        print(f"   Mínima:       {np.min(mbps):.2f} Mbps")
        print(f"   Máxima:       {np.max(mbps):.2f} Mbps")
        print(f"   Média:        {np.mean(mbps):.2f} Mbps")
        print(f"   Mediana:      {np.median(mbps):.2f} Mbps")
        print(f"   Desvio Padrão: {np.std(mbps):.2f} Mbps")

    if not dados_vazao:
        print("ERRO: Nenhum arquivo válido foi encontrado.")
        return

    # --- Criação do Gráfico de Violino ---
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Cria o gráfico de violino
    parts = ax.violinplot(dados_vazao, positions=range(len(dados_vazao)), 
                          showmeans=True, showmedians=True, showextrema=True)
    
    # Estiliza os violinos
    for pc in parts['bodies']:
        pc.set_facecolor('royalblue')
        pc.set_alpha(0.7)
        pc.set_edgecolor('black')
        pc.set_linewidth(1.5)
    
    # Estiliza as linhas de estatísticas
    parts['cmeans'].set_color('red')
    parts['cmeans'].set_linewidth(2)
    parts['cmeans'].set_label('Média')
    
    parts['cmedians'].set_color('green')
    parts['cmedians'].set_linewidth(2)
    parts['cmedians'].set_label('Mediana')
    
    parts['cbars'].set_color('black')
    parts['cmaxes'].set_color('black')
    parts['cmins'].set_color('black')
    
    # Adiciona pontos individuais (opcional, para datasets pequenos)
    for i, data in enumerate(dados_vazao):
        if len(data) <= 50:  # Só mostra pontos se houver poucos dados
            y = data
            x = np.random.normal(i, 0.04, size=len(y))  # Adiciona jitter
            ax.scatter(x, y, alpha=0.3, s=20, color='darkblue')
    
    # --- Estilização e Rótulos ---
    ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Cenários de Teste', fontsize=12, fontweight='bold')
    ax.set_ylabel('Vazão (Mbps)', fontsize=12, fontweight='bold')
    
    # Define os labels no eixo X
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    
    # Desabilita notação científica no eixo Y
    ax.ticklabel_format(style='plain', axis='y', useOffset=False)
    
    # Adiciona grid
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    
    # Cria legenda customizada
    from matplotlib.lines import Line2D
    custom_lines = [
        Line2D([0], [0], color='red', linewidth=2),
        Line2D([0], [0], color='green', linewidth=2)
    ]
    ax.legend(custom_lines, ['Média', 'Mediana'], loc='upper right', 
              fontsize=10, frameon=True, facecolor='white', 
              edgecolor='black', framealpha=1.0)
    
    plt.tight_layout()

    # Salva a imagem do gráfico
    plt.savefig(arquivo_saida, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\n✓ Sucesso! Gráfico de violino salvo em '{arquivo_saida}'")


if __name__ == "__main__":
    # Exemplo de uso: Comparando diferentes cenários
    arquivos = {
        "P4EMU 3G TCP": "p4emu/p4emu_1_3G_tcp/media_testes.json",
        "P4EMU 3G UDP": "p4emu/p4emu_1_3G_udp/media_testes.json",
        "XDP 3G TCP": "xdp/xdp_1_3G_tcp/media_testes.json",
        "XDP 3G UDP": "xdp/xdp_1_3G_udp/media_testes.json",
    }
    
    plotar_grafico_violino(
        arquivos_json=arquivos,
        titulo="Comparação de Vazão: P4EMU vs XDP (3G)",
        arquivo_saida="violino_3g.png"
    )
