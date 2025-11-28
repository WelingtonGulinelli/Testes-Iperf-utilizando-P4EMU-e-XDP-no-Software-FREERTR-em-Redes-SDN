# salvar como: analisar_vazao.py

import json
import matplotlib.pyplot as plt
import numpy as np

def plotar_grafico_vazao(arquivo_json="p4emu/p4emu_1_3G_udp/media_testes.json", arquivo_saida="p4emu/p4emu_1_3G_udp/p4emu_3G_udp.png"):
    """
    Lê um arquivo JSON de resultado do iperf3 e gera um gráfico de vazão (throughput)
    ao longo do tempo com estatísticas (mínima, máxima, média, variância e desvio padrão).
    
    A escala do eixo Y é padronizada de 600 a 1100 Mbps para facilitar comparações.
    """
    print(f"Lendo o arquivo de dados do iperf3: '{arquivo_json}'...")

    try:
        with open(arquivo_json, 'r') as f:
            dados = json.load(f)
    except FileNotFoundError:
        print(f"ERRO: O arquivo '{arquivo_json}' não foi encontrado.")
        return
    except json.JSONDecodeError:
        print(f"ERRO: O arquivo '{arquivo_json}' contém um JSON inválido. Verifique se o teste iperf3 foi concluído corretamente.")
        return

    # Valida se os dados de 'intervals' existem
    if 'intervals' not in dados:
        print("ERRO: O arquivo JSON não contém a seção 'intervals'. O teste pode ter falhado.")
        if 'error' in dados:
            print(f"Mensagem de erro do iperf3: {dados['error']}")
        return

    # Extrai os dados dos intervalos do teste
    intervalos = dados['intervals']
    tempo = [intervalo['sum']['start'] for intervalo in intervalos]
    bits_por_segundo = [intervalo['sum']['bits_per_second'] for intervalo in intervalos]

    # Converte bits por segundo para Megabits por segundo (Mbps) para melhor visualização
    mbps = np.array([bps / 1_000_000 for bps in bits_por_segundo])

    # Calcula estatísticas descritivas
    taxa_media_mbps = np.mean(mbps)
    taxa_maxima_mbps = np.max(mbps)
    taxa_minima_mbps = np.min(mbps)
    variancia_mbps = np.var(mbps)
    desvio_padrao_mbps = np.std(mbps)

    # --- Criação do Gráfico ---
    plt.figure(figsize=(14, 8))
    plt.plot(tempo, mbps, marker='o', linestyle='-', color='royalblue', 
             linewidth=2, markersize=4, label='Vazão (Mbps)')

    # Adiciona linha de média
    plt.axhline(y=taxa_media_mbps, color='green', linestyle='--', linewidth=2, 
                label=f'Média: {taxa_media_mbps:.2f} Mbps')

    # Adiciona faixa de variância (±1 desvio padrão)
    plt.fill_between(tempo, 
                      taxa_media_mbps - desvio_padrao_mbps, 
                      taxa_media_mbps + desvio_padrao_mbps, 
                      alpha=0.2, color='green', label='±1 Desvio Padrão')

    # --- Estilização e Rótulos ---
    plt.title('Desempenho de Vazão da Rede (Throughput) - Análise Completa', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Tempo (segundos)', fontsize=12)
    plt.ylabel('Vazão (Mbps)', fontsize=12)
    
    # Define escala padronizada do eixo Y (600 a 1100 Mbps)
    plt.ylim(1900, 3000)
    
    # Desabilita notação científica no eixo Y
    plt.gca().ticklabel_format(style='plain', axis='y', useOffset=False)
    
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    
    # Cria um texto com as estatísticas
    stats_text = (
        f'Estatísticas:\n'
        f'Mínima: {taxa_minima_mbps:.2f} Mbps\n'
        f'Máxima: {taxa_maxima_mbps:.2f} Mbps\n'
        f'Média: {taxa_media_mbps:.2f} Mbps\n'
        f'Variância: {variancia_mbps:.2f}\n'
        f'Desvio Padrão: {desvio_padrao_mbps:.2f} Mbps'
    )
    
    # Adiciona caixa de texto com as estatísticas no canto inferior direito
    plt.text(0.98, 0.02, stats_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Legenda no canto inferior esquerdo com fundo branco
    legend = plt.legend(loc='lower left', fontsize=10, frameon=True, facecolor='white', 
                       edgecolor='black', framealpha=1.0)
    plt.tight_layout()  # Ajusta o gráfico para caber na imagem

    # Salva a imagem do gráfico
    plt.savefig(arquivo_saida, dpi=300)
    plt.close()

    print(f"\n✓ Sucesso! Gráfico de vazão salvo em '{arquivo_saida}'")
    print(f"\n📊 ESTATÍSTICAS DA VAZÃO:")
    print(f"   Taxa mínima:      {taxa_minima_mbps:.2f} Mbps")
    print(f"   Taxa máxima:      {taxa_maxima_mbps:.2f} Mbps")
    print(f"   Taxa média:       {taxa_media_mbps:.2f} Mbps")
    print(f"   Variância:        {variancia_mbps:.2f}")
    print(f"   Desvio Padrão:    {desvio_padrao_mbps:.2f} Mbps")


if __name__ == "__main__":
    plotar_grafico_vazao()