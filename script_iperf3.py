import subprocess
import time
from datetime import datetime

# Configurações básicas
SERVIDOR = "10.10.10.10"       # IP do servidor iperf3
DURACAO = 300                  # duração de cada teste (segundos)
CONEXOES = 1                   # número de conexões paralelas
BANDA = "1G"                   # largura de banda alvo
TOTAL_TESTES = 30              # número total de testes
INTERVALO = 10                 # tempo de espera entre os testes (segundos)

# Arquivo de log resumido
ARQUIVO_LOG = "iperf3_resumo.log"

def executa_teste(indice):
    """
    Executa um teste do iperf3 e salva o resultado em JSON.
    """
    nome_arquivo = f"iperf3_1_1G_{indice:02d}.json"
    comando = [
        "iperf3",
        "-c", SERVIDOR,
        "-t", str(DURACAO),
        "-b", BANDA,
        "-J"
    ]

    print(f"\n🚀 Iniciando teste {indice}/{TOTAL_TESTES} ...")
    inicio = time.time()

    try:
        with open(nome_arquivo, "w") as saida_json:
            subprocess.run(comando, stdout=saida_json, stderr=subprocess.PIPE, check=True)
        fim = time.time()
        duracao_exec = fim - inicio

        # Lê o resultado JSON para extrair o throughput total
        import json
        with open(nome_arquivo) as f:
            dados = json.load(f)
            throughput = dados["end"]["sum_received"]["bits_per_second"] / 1_000_000  # Mbps

        resumo = f"{datetime.now()} - Teste {indice:02d}: {throughput:.2f} Mbps (durou {duracao_exec:.1f}s)\n"
        print(f"✅ {resumo}")

        with open(ARQUIVO_LOG, "a") as log:
            log.write(resumo)

    except subprocess.CalledProcessError as e:
        erro = f"{datetime.now()} - Teste {indice:02d} falhou: {e.stderr.decode(errors='ignore')}\n"
        print(f"❌ {erro}")
        with open(ARQUIVO_LOG, "a") as log:
            log.write(erro)

def main():
    print(f"=== Iniciando {TOTAL_TESTES} testes de iperf3 ===")
    for i in range(1, TOTAL_TESTES + 1):
        executa_teste(i)
        if i < TOTAL_TESTES:
            print(f"⏳ Aguardando {INTERVALO}s antes do próximo teste...")
            time.sleep(INTERVALO)
    print("🏁 Todos os testes finalizados!")

if __name__ == "__main__":
    main()
