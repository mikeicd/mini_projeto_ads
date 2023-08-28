import subprocess
import sys
import os
import time
import shutil
import argparse
import time

wait_time = 5


def start_project(file_path, id):
    print("============== INICIANDO PROJETO ==============")
    # Path to the IMUNES executable
    imunes_executable = None
    executable_name = "imunes"

    # Find the path of the executable
    imunes_executable = shutil.which(executable_name)

    if imunes_executable is not None:
        print(f"Path to {executable_name}: {imunes_executable}")
    else:
        print(
            f"{executable_name} not found. Make sure it is installed or check your system's PATH."
        )

    # Path to your IMUNES project topology file
    imn_file = file_path

    # Command to start the IMUNES project
    command = f"sudo {imunes_executable} -e {id} -b {imn_file}"

    # Execute the command
    subprocess.run(command, shell=True)


def start_ads(repeticoes=1, id=1234):
    print("============== INICIANDO ADS ==============")
    bw = "1000000000"
    alg = ["cubic", "reno"]
    BER = ["100000", "1000000"]
    e2e_delay = ["10000", "100000"]
    trafego_bg = ["500m", "750m"]
    for rep in range(repeticoes):
        for trafego in trafego_bg:
            for proto in alg:
                for ber in BER:
                    for e2e in e2e_delay:
                        ident = f"{rep}-{trafego}-{proto}-b{ber}-d{e2e}"
                        
                        # Configuracao do link
                        cmd_link_router = f"sudo vlink -bw {bw} -BER {ber} -d {e2e} router1:router2@{id}"

                        # Configuracao trafego background
                        cmd_iperf_server_udp = (
                            f"sudo himage pc1@{id} iperf -s -u -t {wait_time+2}"
                        )
                        cmd_iperf_client_udp = f"sudo himage pc3@{id} iperf -c 10.0.0.20 -u -t {wait_time} -b {trafego}"

                        # Configuracao testes dados
                        ident_sv = f"echo -n '{ident},' >> data/server.csv"
                        ident_cl = f"echo -n '{ident},' >> data/cliente.csv"
                        cmd_iperf_server = f"sudo himage pc2@{id} iperf -s -t {wait_time} -Z {proto} -e -y C >> data/server.csv"
                        cmd_iperf_client = f"sudo himage pc4@{id} iperf -c 10.0.1.20 -t {wait_time} -e -Z {proto} -y C >> data/cliente.csv"

                        ### Rodando comandos
                                          
                        # Run identificadores das linhas
                        sub = subprocess.Popen(
                            ident_sv,
                            shell=True,
                            stdout=subprocess.PIPE,
                            text=True,
                        )
                        sub.wait()
                        sub = subprocess.Popen(
                            ident_cl,
                            shell=True,
                            stdout=subprocess.PIPE,
                            text=True,
                        )
                        sub.wait()

                        # Run Link
                        sub = subprocess.Popen(cmd_link_router.split())
                        sub.wait()

                        # Run trafego UDP
                        sub = subprocess.Popen(cmd_iperf_server_udp.split())
                        subprocess.Popen(cmd_iperf_client_udp.split())

                        # Run trafego TCP
                        subprocess.Popen(
                            cmd_iperf_server,
                            shell=True,
                            stdout=subprocess.PIPE,
                            text=True,
                        )
                        subprocess.Popen(
                            cmd_iperf_client,
                            shell=True,
                            stdout=subprocess.PIPE,
                            text=True,
                        )

                        sub.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project ADS Imunes")
    parser.add_argument("file", type=str, help="File of the IMUNES project (*.imn).")
    parser.add_argument("id", type=str, help="Id of the IMUNES project.")
    parser.add_argument("repeticoes", type=int, help="Tests repetitions.")
    args = parser.parse_args()

    if args.file:
        start_project(args.file, args.id)
        start_ads(args.repeticoes, args.id)

        command = f"sudo cleanupAll"
        subprocess.Popen(command.split())
