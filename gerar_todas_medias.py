#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar todos os testes iperf3 dos diretórios p4emu e xdp
e gerar um relatório completo com todas as estatísticas.
"""

import json
import numpy as np
import os
import glob
from pathlib import Path


def processar_diretorio(diretorio_testes):
    """
    Processa um diretório de testes iperf3 e retorna as estatísticas.
    
    Args:
        diretorio_testes: Caminho do diretório contendo os arquivos JSON
        
    Returns:
        dict com as estatísticas do diretório ou None se houver erro
    """
    # Busca todos os arquivos JSON que correspondem ao padrão iperf3
    caminho_busca = os.path.join(diretorio_testes, "iperf3_*.json")
    arquivos = sorted(glob.glob(caminho_busca))
    
    if not arquivos:
        return None
    
    # Variáveis para coletar estatísticas
    dados_vazao = []
    lista_lost_packets = []
    lista_lost_percent = []
    lista_retransmits = []
    lista_total_packets = []
    protocolo = None
    vazao_alvo = None
    
    testes_validos = 0
    
    for arquivo in arquivos:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            if 'intervals' not in dados or 'end' not in dados:
                continue
            
            # Detecta o protocolo e vazão alvo
            if protocolo is None and 'start' in dados and 'test_start' in dados['start']:
                protocolo = dados['start']['test_start'].get('protocol', 'Unknown')
                vazao_alvo = dados['start']['test_start'].get('target_bitrate', 0)
            
            # Coleta vazão média do teste
            if 'sum_received' in dados['end']:
                vazao = dados['end']['sum_received'].get('bits_per_second', 0)
                dados_vazao.append(vazao)
                
                # Para UDP: lost_packets e lost_percent
                if protocolo == 'UDP':
                    lost_pkts = dados['end']['sum_received'].get('lost_packets', 0)
                    lost_pct = dados['end']['sum_received'].get('lost_percent', 0.0)
                    total_pkts = dados['end']['sum_received'].get('packets', 0)
                    lista_lost_packets.append(lost_pkts)
                    lista_lost_percent.append(lost_pct)
                    lista_total_packets.append(total_pkts)
            
            # Para TCP: retransmits
            if 'sum_sent' in dados['end']:
                if protocolo == 'TCP':
                    retrans = dados['end']['sum_sent'].get('retransmits', 0)
                    total_bytes = dados['end']['sum_sent'].get('bytes', 0)
                    lista_retransmits.append(retrans)
                    if total_bytes > 0:
                        estimated_packets = total_bytes / 1500
                        lista_total_packets.append(estimated_packets)
            
            testes_validos += 1
            
        except (FileNotFoundError, json.JSONDecodeError, Exception):
            continue
    
    if testes_validos == 0:
        return None
    
    # Calcula estatísticas
    resultado = {
        'diretorio': os.path.basename(diretorio_testes),
        'protocolo': protocolo,
        'vazao_alvo_mbps': vazao_alvo / 1_000_000 if vazao_alvo else 0,
        'testes_validos': testes_validos,
        'vazao_media_mbps': np.mean(dados_vazao) / 1_000_000 if dados_vazao else 0,
        'vazao_min_mbps': np.min(dados_vazao) / 1_000_000 if dados_vazao else 0,
        'vazao_max_mbps': np.max(dados_vazao) / 1_000_000 if dados_vazao else 0,
        'vazao_desvio_mbps': np.std(dados_vazao) / 1_000_000 if dados_vazao else 0,
    }
    
    # Adiciona estatísticas específicas por protocolo
    if protocolo == 'UDP' and lista_lost_packets:
        resultado['lost_packets_medio'] = np.mean(lista_lost_packets)
        resultado['lost_packets_total'] = sum(lista_lost_packets)
        resultado['lost_percent_medio'] = np.mean(lista_lost_percent)
        resultado['total_packets'] = sum(lista_total_packets)
        resultado['lost_percent_real'] = (sum(lista_lost_packets) / sum(lista_total_packets) * 100) if sum(lista_total_packets) > 0 else 0
    elif protocolo == 'TCP' and lista_retransmits:
        resultado['retransmits_medio'] = np.mean(lista_retransmits)
        resultado['retransmits_total'] = sum(lista_retransmits)
        resultado['retransmits_min'] = min(lista_retransmits)
        resultado['retransmits_max'] = max(lista_retransmits)
        resultado['packets_estimado'] = sum(lista_total_packets)
        resultado['retransmits_percent'] = (sum(lista_retransmits) / sum(lista_total_packets) * 100) if sum(lista_total_packets) > 0 else 0
    
    return resultado


def gerar_relatorio_completo():
    """
    Processa todos os diretórios de testes e gera um relatório completo.
    """
    print("=" * 80)
    print("📊 RELATÓRIO COMPLETO DE TESTES IPERF3")
    print("=" * 80)
    print()
    
    # Diretórios base
    diretorios_base = ['p4emu', 'xdp']
    
    # Armazena todos os resultados
    todos_resultados = []
    
    for dir_base in diretorios_base:
        if not os.path.exists(dir_base):
            print(f"⚠️  Diretório '{dir_base}' não encontrado, pulando...")
            continue
        
        print(f"\n{'='*80}")
        print(f"🔍 Processando diretório: {dir_base.upper()}")
        print(f"{'='*80}\n")
        
        # Lista todos os subdiretórios
        subdiretorios = sorted([d for d in Path(dir_base).iterdir() if d.is_dir()])
        
        if not subdiretorios:
            print(f"   Nenhum subdiretório encontrado em {dir_base}")
            continue
        
        for subdir in subdiretorios:
            resultado = processar_diretorio(str(subdir))
            
            if resultado is None:
                print(f"   ⚠️  {subdir.name}: Sem testes válidos")
                continue
            
            resultado['sistema'] = dir_base
            todos_resultados.append(resultado)
            
            # Imprime resultado formatado
            print(f"📁 {subdir.name}")
            print(f"   {'─'*74}")
            print(f"   Protocolo: {resultado['protocolo']}")
            print(f"   Vazão Alvo: {resultado['vazao_alvo_mbps']:.2f} Mbps")
            print(f"   Testes Válidos: {resultado['testes_validos']}")
            print(f"   ")
            print(f"   📈 VAZÃO:")
            print(f"      • Média: {resultado['vazao_media_mbps']:.2f} Mbps")
            print(f"      • Mínima: {resultado['vazao_min_mbps']:.2f} Mbps")
            print(f"      • Máxima: {resultado['vazao_max_mbps']:.2f} Mbps")
            print(f"      • Desvio Padrão: {resultado['vazao_desvio_mbps']:.2f} Mbps")
            
            if resultado['protocolo'] == 'UDP':
                print(f"   ")
                print(f"   📦 PACOTES PERDIDOS:")
                print(f"      • Média por teste: {resultado['lost_packets_medio']:.2f}")
                print(f"      • Total perdidos: {resultado['lost_packets_total']}")
                print(f"      • Total transmitidos: {int(resultado['total_packets'])}")
                print(f"      • Percentual real: {resultado['lost_percent_real']:.6f}%")
            elif resultado['protocolo'] == 'TCP':
                print(f"   ")
                print(f"   🔄 RETRANSMISSÕES:")
                print(f"      • Média por teste: {resultado['retransmits_medio']:.2f}")
                print(f"      • Total: {int(resultado['retransmits_total'])}")
                print(f"      • Mínimo: {resultado['retransmits_min']}")
                print(f"      • Máximo: {resultado['retransmits_max']}")
                print(f"      • Percentual: {resultado['retransmits_percent']:.6f}%")
            
            print()
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO GERAL")
    print("=" * 80)
    print(f"\nTotal de diretórios processados: {len(todos_resultados)}")
    
    # Agrupa por sistema
    for sistema in ['p4emu', 'xdp']:
        resultados_sistema = [r for r in todos_resultados if r['sistema'] == sistema]
        if resultados_sistema:
            print(f"\n{sistema.upper()}:")
            print(f"   • Total de testes: {sum(r['testes_validos'] for r in resultados_sistema)}")
            
            tcp_results = [r for r in resultados_sistema if r['protocolo'] == 'TCP']
            udp_results = [r for r in resultados_sistema if r['protocolo'] == 'UDP']
            
            if tcp_results:
                print(f"   • Testes TCP: {len(tcp_results)} diretórios")
                vazao_media_tcp = np.mean([r['vazao_media_mbps'] for r in tcp_results])
                retrans_total = sum(r.get('retransmits_total', 0) for r in tcp_results)
                print(f"      - Vazão média: {vazao_media_tcp:.2f} Mbps")
                print(f"      - Total de retransmissões: {int(retrans_total)}")
            
            if udp_results:
                print(f"   • Testes UDP: {len(udp_results)} diretórios")
                vazao_media_udp = np.mean([r['vazao_media_mbps'] for r in udp_results])
                lost_total = sum(r.get('lost_packets_total', 0) for r in udp_results)
                print(f"      - Vazão média: {vazao_media_udp:.2f} Mbps")
                print(f"      - Total de pacotes perdidos: {int(lost_total)}")
    
    print("\n" + "=" * 80)
    print("✅ Processamento concluído!")
    print("=" * 80)
    
    # Salva resultados em JSON
    output_file = "relatorio_completo_testes.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(todos_resultados, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")


if __name__ == "__main__":
    gerar_relatorio_completo()
