import json
import os
import platform
import socket
import uuid

INSTANCE_BOOT_ID = str(uuid.uuid4())
INVOCATION_COUNT = 0


def lambda_handler(event, context):
    global INVOCATION_COUNT
    INVOCATION_COUNT += 1

    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = [line.strip() for line in f if 'model name' in line]
    except Exception:
        cpu_info = ["No disponible"]

    # Verificar persistencia en el disco efímero (/tmp)
    tmp_file = "/tmp/demo_state.txt"
    if not os.path.exists(tmp_file):
        with open(tmp_file, "w") as f:
            f.write(f"Creado en invocación 1 - ID: {INSTANCE_BOOT_ID}")
        disk_status = "Archivo recién creado (Cold Start)"
    else:
        with open(tmp_file, "r") as f:
            disk_status = f"Archivo persistente encontrado -> {f.read()}"

    response_data = {
        "mensaje": "Ejecución exitosa en entorno administrado de Lambda",
        "estado_instancia": {
            "id_unico_instancia": INSTANCE_BOOT_ID,
            "conteo_invocaciones_en_esta_instancia": INVOCATION_COUNT,
            "tipo_arranque": "COLD START" if INVOCATION_COUNT == 1 else "WARM START (Instancia reutilizada)",
            "estado_disco_tmp": disk_status
        },
        "infraestructura_oculta": {
            "hostname_interno": socket.gethostname(),
            "sistema_operativo": platform.platform(),
            "arquitectura": platform.machine(),
            "procesadores_asignados": os.cpu_count(),
            "modelo_cpu": cpu_info[0] if cpu_info else "N/A",
            "memoria_limite_mb": context.memory_limit_in_mb,
            "log_stream_name": context.log_stream_name
        }
    }

    return {
        'statusCode': 200,
        'body': json.dumps(response_data, indent=2, ensure_ascii=False)
    }
