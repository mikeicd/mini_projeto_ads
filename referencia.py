import subprocess


alg = ['cubic', 'reno']
BER = ['100000', '1000000']
e2e_delay = ['10000', '100000']
repeticao = 8
cmd_iperf_client="sudo himage pc1@i3f30 iperf -c 10.0.0.21 -y C -Z " + alg[0] + " > dados-" + alg[0] + ".csv"
##### execucao dos experimentos
#para cada uma das repeticoes faca
for rep in range(repeticao):
    for proto in alg:
        for ber in BER:
            for e2e in e2e_delay:
                subprocess.run("sudo vlink -BER " + ber + " pc1:pc2@i3f30 ", shell=True)
                

#configure o link usando o comando vlink
#execute o iperf cliente salvando os dados em arquivo separado (?)
#print(cmd_iperf_client)
subprocess.run(cmd_iperf_client, shell=True)