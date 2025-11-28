# salvar como: gera_media_testes.py

import json
import numpy as np
import os
import glob

def calcular_media_testes(diretorio_testes, padrao_arquivos="iperf3_*.json", arquivo_saida="media_testes.json"):
    """
    Analisa múltiplos arquivos JSON de testes iperf3 e calcula a média dos valores
    de vazão (throughput) ao longo do tempo, gerando um novo arquivo JSON compatível
    com o script analisar_vazao.py.
    
    Args:
        diretorio_testes: Diretório contendo os arquivos JSON dos testes
        padrao_arquivos: Padrão de nome dos arquivos a serem analisados
        arquivo_saida: Nome do arquivo de saída com as médias
    """
    
    # Busca todos os arquivos JSON que correspondem ao padrão
    caminho_busca = os.path.join(diretorio_testes, padrao_arquivos)
    arquivos = sorted(glob.glob(caminho_busca))
    
    if not arquivos:
        print(f"❌ ERRO: Nenhum arquivo encontrado no padrão '{caminho_busca}'")
        return
    
    print(f"📁 Encontrados {len(arquivos)} arquivos para análise:")
    for arq in arquivos:
        print(f"   • {os.path.basename(arq)}")
    
    # Dicionário para armazenar os dados de todos os testes
    # Chave: índice do intervalo, Valor: lista de bits_per_second de cada teste
    dados_por_intervalo = {}
    tempo_por_intervalo = {}
    
    # Listas para armazenar informações de pacotes perdidos e retransmissões
    lista_lost_packets = []
    lista_lost_percent = []
    lista_retransmits = []
    lista_total_packets = []
    protocolo = None
    
    # Lê todos os arquivos e coleta os dados
    testes_validos = 0
    for arquivo in arquivos:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # Valida se o arquivo contém os dados esperados
            if 'intervals' not in dados:
                print(f"⚠️  Pulando '{os.path.basename(arquivo)}': sem dados de intervalos")
                continue
            
            # Detecta o protocolo (UDP ou TCP) no primeiro arquivo válido
            if protocolo is None and 'start' in dados and 'test_start' in dados['start']:
                protocolo = dados['start']['test_start'].get('protocol', 'Unknown')
            
            # Coleta informações de pacotes perdidos (UDP) ou retransmissões (TCP)
            if 'end' in dados:
                if 'sum_received' in dados['end']:
                    # Para UDP: lost_packets e lost_percent
                    lost_pkts = dados['end']['sum_received'].get('lost_packets', 0)
                    lost_pct = dados['end']['sum_received'].get('lost_percent', 0.0)
                    total_pkts = dados['end']['sum_received'].get('packets', 0)
                    lista_lost_packets.append(lost_pkts)
                    lista_lost_percent.append(lost_pct)
                    lista_total_packets.append(total_pkts)
                
                if 'sum_sent' in dados['end']:
                    # Para TCP: retransmits e total de bytes para estimar pacotes
                    retrans = dados['end']['sum_sent'].get('retransmits', 0)
                    total_bytes = dados['end']['sum_sent'].get('bytes', 0)
                    lista_retransmits.append(retrans)
                    # Estima o total de pacotes assumindo MTU de 1500 bytes
                    if total_bytes > 0:
                        estimated_packets = total_bytes / 1500
                        lista_total_packets.append(estimated_packets)
            
            # Processa cada intervalo do teste
            for idx, intervalo in enumerate(dados['intervals']):
                if 'sum' not in intervalo:
                    continue
                
                # Inicializa listas se for o primeiro arquivo
                if idx not in dados_por_intervalo:
                    dados_por_intervalo[idx] = []
                    tempo_por_intervalo[idx] = intervalo['sum']['start']
                
                # Adiciona o bits_per_second deste intervalo
                bits_per_second = intervalo['sum']['bits_per_second']
                dados_por_intervalo[idx].append(bits_per_second)
            
            testes_validos += 1
            print(f"✅ Processado: {os.path.basename(arquivo)}")
            
        except FileNotFoundError:
            print(f"⚠️  Arquivo não encontrado: {arquivo}")
        except json.JSONDecodeError:
            print(f"⚠️  Erro ao decodificar JSON: {arquivo}")
        except Exception as e:
            print(f"⚠️  Erro ao processar {arquivo}: {e}")
    
    if testes_validos == 0:
        print("❌ ERRO: Nenhum teste válido foi processado!")
        return
    
    print(f"\n📊 Total de testes válidos processados: {testes_validos}")
    print(f"📊 Total de intervalos encontrados: {len(dados_por_intervalo)}")
    
    # Calcula as médias para cada intervalo
    intervalos_media = []
    for idx in sorted(dados_por_intervalo.keys()):
        valores = dados_por_intervalo[idx]
        media_bits_per_second = np.mean(valores)
        
        # Cria um intervalo no formato esperado pelo analisar_vazao.py
        intervalo_media = {
            "sum": {
                "start": tempo_por_intervalo[idx],
                "end": tempo_por_intervalo[idx] + 1.0,
                "seconds": 1.0,
                "bits_per_second": float(media_bits_per_second),
                "bytes": int(media_bits_per_second / 8),
                "retransmits": 0
            }
        }
        intervalos_media.append(intervalo_media)
    
    # Lê o primeiro arquivo válido para copiar metadados
    with open(arquivos[0], 'r', encoding='utf-8') as f:
        dados_base = json.load(f)
    
    # Cria o JSON de saída com a estrutura esperada
    resultado = {
        "start": dados_base.get("start", {}),
        "intervals": intervalos_media,
        "end": {
            "sum_received": {
                "bits_per_second": float(np.mean([i['sum']['bits_per_second'] for i in intervalos_media]))
            }
        }
    }
    
    # Adiciona informações sobre a agregação
    resultado["start"]["test_description"] = f"Média de {testes_validos} testes"
    
    # Salva o arquivo de saída
    caminho_saida = os.path.join(diretorio_testes, arquivo_saida)
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent='\t')
    
    print(f"\n✅ Arquivo de média gerado com sucesso: '{caminho_saida}'")
    print(f"📈 Média geral de vazão: {resultado['end']['sum_received']['bits_per_second']/1_000_000:.2f} Mbps")
    
    # Exibe informações sobre pacotes perdidos ou retransmissões
    if protocolo == 'UDP' and lista_lost_packets:
        media_lost_packets = np.mean(lista_lost_packets)
        media_lost_percent = np.mean(lista_lost_percent)
        total_lost = sum(lista_lost_packets)
        total_packets = sum(lista_total_packets)
        print(f"\n📦 Informações de Pacotes Perdidos (UDP):")
        print(f"   • Média de pacotes perdidos: {media_lost_packets:.2f}")
        print(f"   • Percentual médio de perda: {media_lost_percent:.4f}%")
        print(f"   • Total de pacotes perdidos: {total_lost}")
        print(f"   • Total de pacotes transmitidos: {int(total_packets)}")
        print(f"   • Total de testes analisados: {len(lista_lost_packets)}")
    elif protocolo == 'TCP' and lista_retransmits:
        media_retransmits = np.mean(lista_retransmits)
        total_retrans = sum(lista_retransmits)
        media_packets = np.mean(lista_total_packets) if lista_total_packets else 0
        percent_retrans = (total_retrans / sum(lista_total_packets) * 100) if lista_total_packets and sum(lista_total_packets) > 0 else 0
        print(f"\n🔄 Informações de Retransmissões (TCP):")
        print(f"   • Média de retransmissões: {media_retransmits:.2f}")
        print(f"   • Total de retransmissões: {int(total_retrans)}")
        print(f"   • Percentual de retransmissões: {percent_retrans:.6f}%")
        print(f"   • Média estimada de pacotes por teste: {int(media_packets)}")
        print(f"   • Total de testes analisados: {len(lista_retransmits)}")
    
    print(f"\n💡 Para gerar o gráfico, use:")
    print(f"   python analisar_vazao.py")
    print(f"   (atualize o arquivo_json para '{arquivo_saida}')")


if __name__ == "__main__":
    # Configurações padrão
    DIRETORIO = "xdp/xdp_1_2G_udp"
    PADRAO = "xdp_1_2G_*.json"
    SAIDA = "media_testes.json"
    
    print("=" * 70)
    print("📊 GERADOR DE MÉDIA DE TESTES IPERF3")
    print("=" * 70)
    print()
    
    calcular_media_testes(DIRETORIO, PADRAO, SAIDA)
    
    print()
    print("=" * 70)
