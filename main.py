import subprocess
import sys
import os
import time
import shutil
import argparse
import time
import logging
import pandas as pd

from process_data import process_data

logging.basicConfig()

current_directory = os.getcwd()

wait_time = 5


def start_project(args):
    file_path = args.file
    id = args.id
    logging.info("     INICIANDO PROJETO")

    docker = "docker pull imunes/template"

    sub = subprocess.Popen(docker.split())
    sub.wait()

    # Path to the IMUNES executable
    imunes_executable = None
    executable_name = "imunes"

    # Find the path of the executable
    imunes_executable = shutil.which(executable_name)

    if imunes_executable is not None:
        logging.info(f"Path to {executable_name}: {imunes_executable}")
    else:
        logging.info(
            f"{executable_name} not found. Make sure it is installed or check your system's PATH."
        )

    # Path to your IMUNES project topology file
    imn_file = file_path

    # Command to start the IMUNES project
    command = f"sudo {imunes_executable} -e {id} -b {imn_file}"

    # Execute the command
    subprocess.run(command, shell=True)


def start_ads(args):
    repeticoes = args.repeticoes
    id = args.id
    logging.info("     INICIANDO ADS")
    bw = "1000000000"
    alg = ["cubic", "reno"] if args.proto is None else [args.proto]
    BER = ["100000", "1000000"] if args.ber is None else [args.ber]
    e2e_delay = ["10000", "100000"] if args.delay is None else [args.delay]
    trafego_bg = ["500m", "750m"] if args.trafego is None else [args.trafego]
    
    logging.warning(alg)
    logging.warning(BER)
    logging.warning(e2e_delay)
    logging.warning(trafego_bg)
    

    headers = "rep,trafego,proto,ber,delay,time,addrsrc,portsrc,addrdest,portdest,nsei,nsei,transfbits,bps"
    headers_command_sv = f"echo '{headers}' >> data/server.csv"
    headers_command_cl = f"echo '{headers}' >> data/cliente.csv"
    sub = subprocess.Popen(
        headers_command_sv,
        shell=True,
        stdout=subprocess.PIPE,
        text=True,
    )

    sub = subprocess.Popen(
        headers_command_cl,
        shell=True,
        stdout=subprocess.PIPE,
        text=True,
    )

    for rep in range(repeticoes):
        for trafego in trafego_bg:
            for proto in alg:
                for ber in BER:
                    for e2e in e2e_delay:
                        ident = f"{rep},{trafego},{proto},{ber},{e2e}"

                        # Configuracao do link
                        cmd_link_router = f"sudo vlink -bw {bw} -BER {ber} -d {e2e} router1:router2@{id}"

                        # Configuracao trafego background
                        cmd_iperf_server_udp = (
                            f"sudo himage pc1@{id} iperf -s -u -t {wait_time+5}"
                        )
                        cmd_iperf_client_udp = f"sudo himage pc3@{id} iperf -c 10.0.0.20 -u -t {wait_time+3} -b {trafego}"

                        # Configuracao testes dados
                        ident_sv = f"echo -n '{ident},' >> data/server.csv"
                        ident_cl = f"echo -n '{ident},' >> data/cliente.csv"
                        cmd_iperf_server = f"sudo himage pc2@{id} iperf -s -t {wait_time+1} -Z {proto} -e -y C >> data/server.csv"
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
    parser.add_argument("-id", type=str, default=1234, help="Id of the IMUNES project.")
    parser.add_argument("-repeticoes", type=int, default=1, help="Tests repetitions.")
    parser.add_argument("-ber", type=str, default=None, help="BER.")
    parser.add_argument("-delay", type=str, default=None, help="Delay.")
    parser.add_argument("-trafego", type=str, default=None, help="Trafego e.g [500m].")
    parser.add_argument(
        "-proto", type=str, default=None, help="Protocolo [cubic,reno]."
    )
    parser.add_argument(
        "-clean", type=bool, default=False, help="Clean files"
    )

    args = parser.parse_args()

    if args.clean:
        try:
            command = f"rm {current_directory}/data/*csv"
            subprocess.Popen(command.split())
        except Exception as e:
            logging.warning(e)

    start_project(args)
    start_ads(args)
    # process_data('data/client.csv')

    command = f"sudo cleanupAll"
    subprocess.Popen(command.split())
