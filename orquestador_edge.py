import json
import time
import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

CISCO_DEVICE = {
    'device_type': 'cisco_ios',
    'ip': '192.168.1.222',
    'username': 'gvln',
    'password': 'SantiagoGavilan',
    'secret': 'cisco_switch',
}

ips_bloqueadas = set()

def mitigar_amenaza_cisco(ip_atacante):
    if ip_atacante in ips_bloqueadas:
        return 
    
    print(f"[*] Iniciando protocolo de mitigación. Conectando a {CISCO_DEVICE['ip']}...")
    
    try:
        net_connect = ConnectHandler(**CISCO_DEVICE)
        net_connect.enable()
        config_commands = [
            f'access-list 199 deny ip host {ip_atacante} any log',
        ]
        
        output = net_connect.send_config_set(config_commands)
        # net_connect.send_command('write memory')
        net_connect.disconnect()
        
        print(f"[+] ÉXITO: La IP {ip_atacante} ha sido bloqueada en el hardware de red.")
        print(f"    Respuesta del switch: {output.splitlines()[-1]}")
        
        ips_bloqueadas.add(ip_atacante)

    except NetmikoAuthenticationException:
        print("[-] Error: Credenciales de SSH incorrectas para el switch Cisco.")
    except NetmikoTimeoutException:
        print("[-] Error: Tiempo de espera agotado.")
    except Exception as e:
        print(f"[-] Error inesperado al aplicar mitigación: {e}")


def seguir_log(ruta_archivo):
    """Generador que lee líneas nuevas en un archivo en tiempo real (Equivalente a tail -f)."""
    try:
        with open(ruta_archivo, 'r') as f:
            f.seek(0, os.SEEK_END)
            while True:
                linea = f.readline()
                if not linea:
                    time.sleep(0.1)
                    continue
                yield linea
    except FileNotFoundError:
        print(f"[-] Error Crítico: No se encontró el archivo de logs en: {ruta_archivo}")
    except PermissionError:
        print(f"[-] Error de Permisos: Ejecuta el script con 'sudo' para poder leer los logs.")

def procesar_alertas(ruta_log):
    print("[*] Orquestador Edge iniciado exitosamente.")
    print(f"[*] Escuchando eventos en tiempo real desde el puerto SPAN hacia {ruta_log}...\n")

    for linea_cruda in seguir_log(ruta_log):
        try:
            evento = json.loads(linea_cruda)

            if evento.get("event_type") == "alert":
                ip_origen = evento.get("src_ip")
                ip_destino = evento.get("dest_ip")
                puerto_destino = evento.get("dest_port")
                detalles_alerta = evento.get("alert", {}).get("signature", "Alerta de firma desconocida")
                severidad = evento.get("alert", {}).get("severity", 3)

                print(f"\n[!] AMENAZA DETECTADA [Severidad {severidad}]")
                print(f"    Origen: {ip_origen} ➔ Destino local: {ip_destino}:{puerto_destino}")
                print(f"    Firma de Suricata: {detalles_alerta}")

                IP_SERVIDOR = "192.168.1.200"

                if ip_origen == IP_SERVIDOR:
                    print("    [*] Acción: Omitida (Evitado auto-bloqueo del Servidor Principal).")
                
                # Gvln-S // change to 111.111 for test
                elif ip_origen.startswith("111.111.") or ip_origen.startswith("10.") or ip_origen.startswith("127."):
                    print(f"    [*] Acción: Omitida de forma segura (La IP {ip_origen} es local).")
                
                # 3. Si pasa los filtros, es una IP externa real atacando desde Internet
                else:
                    mitigar_amenaza_cisco(ip_origen)

                print("-" * 60)

        except json.JSONDecodeError:
            continue

if __name__ == "__main__":
    RUTA_EVE = "/var/log/suricata/eve.json"
    procesar_alertas(RUTA_EVE)
